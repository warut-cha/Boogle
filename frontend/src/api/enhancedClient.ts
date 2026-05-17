import axios, { AxiosError, AxiosInstance } from "axios";
import type { BobOutput, Finding, Incident, ResetResponse } from "./types";
import {
  normalizeBobOutput,
  normalizeFinding,
  normalizeIncident,
} from "./normalize";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const WS_BASE_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000";

// Storage keys
const FINDINGS_STORAGE_KEY = "bob_sentinel_findings";
const INCIDENTS_STORAGE_KEY = "bob_sentinel_incidents";
const BOB_OUTPUT_STORAGE_KEY = "bob_sentinel_bob_output";

// Retry configuration
const MAX_RETRIES = 3;
const RETRY_DELAY_MS = 1000;
const RETRY_BACKOFF_MULTIPLIER = 2;

/**
 * Enhanced API client with retry logic, error handling, and caching
 */
class EnhancedAPIClient {
  private axiosInstance: AxiosInstance;
  private requestCache: Map<string, { data: any; timestamp: number }>;
  private cacheTTL: number = 30000; // 30 seconds

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        "Content-Type": "application/json",
      },
    });

    this.requestCache = new Map();

    // Add request interceptor for logging
    this.axiosInstance.interceptors.request.use(
      (config) => {
        console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error("[API] Request error:", error);
        return Promise.reject(error);
      }
    );

    // Add response interceptor for error handling
    this.axiosInstance.interceptors.response.use(
      (response) => {
        console.log(`[API] Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        this.handleResponseError(error);
        return Promise.reject(error);
      }
    );
  }

  /**
   * Handle API response errors with detailed logging
   */
  private handleResponseError(error: AxiosError): void {
    if (error.response) {
      // Server responded with error status
      console.error(
        `[API] Server error: ${error.response.status}`,
        error.response.data
      );
    } else if (error.request) {
      // Request made but no response received
      console.error("[API] No response received:", error.message);
    } else {
      // Error in request setup
      console.error("[API] Request setup error:", error.message);
    }
  }

  /**
   * Retry a request with exponential backoff
   */
  private async retryRequest<T>(
    requestFn: () => Promise<T>,
    retries: number = MAX_RETRIES
  ): Promise<T> {
    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        return await requestFn();
      } catch (error) {
        lastError = error as Error;

        if (attempt < retries) {
          const delay = RETRY_DELAY_MS * Math.pow(RETRY_BACKOFF_MULTIPLIER, attempt);
          console.warn(
            `[API] Retry attempt ${attempt + 1}/${retries} after ${delay}ms`
          );
          await this.sleep(delay);
        }
      }
    }

    throw lastError;
  }

  /**
   * Sleep utility for retry delays
   */
  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Get cached data if available and not expired
   */
  private getCachedData<T>(key: string): T | null {
    const cached = this.requestCache.get(key);
    if (cached && Date.now() - cached.timestamp < this.cacheTTL) {
      console.log(`[API] Using cached data for: ${key}`);
      return cached.data as T;
    }
    return null;
  }

  /**
   * Cache data with timestamp
   */
  private setCachedData(key: string, data: any): void {
    this.requestCache.set(key, {
      data,
      timestamp: Date.now(),
    });
  }

  /**
   * Load data from localStorage
   */
  private loadFromStorage<T>(key: string, fallback: T): T {
    try {
      const raw = localStorage.getItem(key);
      if (!raw) return fallback;
      return JSON.parse(raw) as T;
    } catch {
      return fallback;
    }
  }

  /**
   * Save data to localStorage
   */
  private saveToStorage<T>(key: string, value: T): void {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error("[Storage] Failed to save:", error);
    }
  }

  /**
   * Get all findings with retry and fallback
   */
  async getFindings(): Promise<Finding[]> {
    const cacheKey = "findings";
    const cached = this.getCachedData<Finding[]>(cacheKey);
    if (cached) return cached;

    try {
      const response = await this.retryRequest(() =>
        this.axiosInstance.get("/api/findings")
      );

      const findings = Array.isArray(response.data)
        ? response.data.map(normalizeFinding)
        : [];

      this.setCachedData(cacheKey, findings);
      this.saveToStorage(FINDINGS_STORAGE_KEY, findings);
      return findings;
    } catch (error) {
      console.warn(
        "[API] Failed to load findings from backend. Using local storage.",
        error
      );
      return this.loadFromStorage<Finding[]>(FINDINGS_STORAGE_KEY, []);
    }
  }

  /**
   * Get all incidents with retry and fallback
   */
  async getIncidents(): Promise<Incident[]> {
    const cacheKey = "incidents";
    const cached = this.getCachedData<Incident[]>(cacheKey);
    if (cached) return cached;

    try {
      const response = await this.retryRequest(() =>
        this.axiosInstance.get("/api/incidents")
      );

      const incidents = Array.isArray(response.data)
        ? response.data.map(normalizeIncident)
        : [];

      this.setCachedData(cacheKey, incidents);
      this.saveToStorage(INCIDENTS_STORAGE_KEY, incidents);
      return incidents;
    } catch (error) {
      console.warn(
        "[API] Failed to load incidents from backend. Using local storage.",
        error
      );
      return this.loadFromStorage<Incident[]>(INCIDENTS_STORAGE_KEY, []);
    }
  }

  /**
   * Get a specific incident by ID
   */
  async getIncident(id: string): Promise<Incident> {
    const response = await this.retryRequest(() =>
      this.axiosInstance.get(`/api/incidents/${id}`)
    );
    return normalizeIncident(response.data);
  }

  /**
   * Get Bob analysis for an incident
   */
  async getBobAnalysis(incidentId: string): Promise<BobOutput> {
    try {
      const response = await this.retryRequest(() =>
        this.axiosInstance.get(`/api/incidents/${incidentId}/bob-analysis`)
      );

      const bobOutput = normalizeBobOutput(response.data);
      this.saveToStorage(BOB_OUTPUT_STORAGE_KEY, bobOutput);
      return bobOutput;
    } catch (error) {
      console.warn(
        "[API] Failed to load Bob analysis. Using local storage.",
        error
      );

      const stored = this.loadFromStorage<BobOutput | null>(
        BOB_OUTPUT_STORAGE_KEY,
        null
      );

      if (stored) {
        return normalizeBobOutput(stored);
      }

      throw error;
    }
  }

  /**
   * Trigger Bob analysis for an incident
   */
  async analyzeWithBob(incidentId: string): Promise<BobOutput> {
    const response = await this.retryRequest(() =>
      this.axiosInstance.post(`/api/incidents/${incidentId}/analyze-with-bob`)
    );

    const bobOutput = normalizeBobOutput(response.data);
    this.saveToStorage(BOB_OUTPUT_STORAGE_KEY, bobOutput);
    return bobOutput;
  }

  /**
   * Poll for updates since a timestamp
   */
  async pollForUpdates(
    lastTimestamp?: string
  ): Promise<{ findings: Finding[]; incidents: Incident[]; hasUpdates: boolean }> {
    const params = lastTimestamp ? { since: lastTimestamp } : {};
    const response = await this.axiosInstance.get("/api/updates", { params });

    return {
      findings: Array.isArray(response.data?.findings)
        ? response.data.findings.map(normalizeFinding)
        : [],
      incidents: Array.isArray(response.data?.incidents)
        ? response.data.incidents.map(normalizeIncident)
        : [],
      hasUpdates: Boolean(response.data?.hasUpdates),
    };
  }

  /**
   * Trigger a new security scan
   */
  async triggerScan(
    paths: string[],
    useMock: boolean = true,
    useBob: boolean = true
  ): Promise<{
    status: string;
    message: string;
    run_id: string;
    paths: string[];
    new_findings: Finding[];
    new_incidents: Incident[];
    bob_analysis: BobOutput | null;
    total_findings: number;
    total_incidents: number;
  }> {
    const response = await this.retryRequest(() =>
      this.axiosInstance.post("/api/scan", {
        paths,
        use_mock: useMock,
        use_bob: useBob,
      })
    );

    // Clear cache after scan
    this.requestCache.clear();

    return {
      ...response.data,
      new_findings: Array.isArray(response.data?.new_findings)
        ? response.data.new_findings.map(normalizeFinding)
        : [],
      new_incidents: Array.isArray(response.data?.new_incidents)
        ? response.data.new_incidents.map(normalizeIncident)
        : [],
      bob_analysis: response.data?.bob_analysis
        ? normalizeBobOutput(response.data.bob_analysis)
        : null,
    };
  }

  /**
   * Clear all data (backend and local storage)
   */
  async clearAllData(): Promise<ResetResponse> {
    // Clear local storage
    localStorage.removeItem(FINDINGS_STORAGE_KEY);
    localStorage.removeItem(INCIDENTS_STORAGE_KEY);
    localStorage.removeItem(BOB_OUTPUT_STORAGE_KEY);

    // Clear cache
    this.requestCache.clear();

    try {
      const response = await this.axiosInstance.delete("/api/reset");
      return response.data;
    } catch (error) {
      console.warn(
        "[API] Backend reset failed. Local data was still cleared.",
        error
      );

      return {
        status: "local_only",
        message: "Local data cleared. Backend reset endpoint unavailable.",
      };
    }
  }

  /**
   * Check API health
   */
  async checkHealth(): Promise<{
    status: string;
    service: string;
    uptime_seconds?: number;
    findings_count?: number;
    incidents_count?: number;
  }> {
    const response = await this.axiosInstance.get("/api/health");
    return response.data;
  }

  /**
   * Get API metrics
   */
  async getMetrics(): Promise<any> {
    const response = await this.axiosInstance.get("/api/metrics");
    return response.data;
  }
}

// Export singleton instance
export const enhancedApiClient = new EnhancedAPIClient();

// Export WebSocket URL for real-time connections
export const WS_URL = `${WS_BASE_URL}/ws`;

// Made with Bob
