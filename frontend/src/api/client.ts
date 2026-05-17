import axios from "axios";
import type { BobOutput, Finding, Incident, ResetResponse } from "./types";
import {
  normalizeBobOutput,
  normalizeFinding,
  normalizeIncident,
} from "./normalize";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const FINDINGS_STORAGE_KEY = "bob_sentinel_findings";
const INCIDENTS_STORAGE_KEY = "bob_sentinel_incidents";
const BOB_OUTPUT_STORAGE_KEY = "bob_sentinel_bob_output";

function loadStoredJson<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return fallback;
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

function saveStoredJson<T>(key: string, value: T): void {
  localStorage.setItem(key, JSON.stringify(value));
}

function clearStoredDashboardData(): void {
  localStorage.removeItem(FINDINGS_STORAGE_KEY);
  localStorage.removeItem(INCIDENTS_STORAGE_KEY);
  localStorage.removeItem(BOB_OUTPUT_STORAGE_KEY);
}

export const apiClient = {
  async getFindings(): Promise<Finding[]> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/findings`);
      const findings = Array.isArray(response.data)
        ? response.data.map(normalizeFinding)
        : [];

      saveStoredJson(FINDINGS_STORAGE_KEY, findings);
      return findings;
    } catch (error) {
      console.warn(
        "Failed to load findings from backend. Falling back to local storage.",
        error
      );

      return loadStoredJson<Finding[]>(FINDINGS_STORAGE_KEY, []);
    }
  },

  async getIncidents(): Promise<Incident[]> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/incidents`);
      const incidents = Array.isArray(response.data)
        ? response.data.map(normalizeIncident)
        : [];

      saveStoredJson(INCIDENTS_STORAGE_KEY, incidents);
      return incidents;
    } catch (error) {
      console.warn(
        "Failed to load incidents from backend. Falling back to local storage.",
        error
      );

      return loadStoredJson<Incident[]>(INCIDENTS_STORAGE_KEY, []);
    }
  },

  async getIncident(id: string): Promise<Incident> {
    const response = await axios.get(`${API_BASE_URL}/api/incidents/${id}`);
    return normalizeIncident(response.data);
  },

  async getBobAnalysis(incidentId: string): Promise<BobOutput> {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/incidents/${incidentId}/bob-analysis`
      );

      const bobOutput = normalizeBobOutput(response.data);
      saveStoredJson(BOB_OUTPUT_STORAGE_KEY, bobOutput);
      return bobOutput;
    } catch (error) {
      console.warn(
        "Failed to load Bob analysis from backend. Falling back to local storage.",
        error
      );

      const stored = loadStoredJson<BobOutput | null>(BOB_OUTPUT_STORAGE_KEY, null);

      if (stored) {
        return normalizeBobOutput(stored);
      }

      throw error;
    }
  },

  async analyzeWithBob(incidentId: string): Promise<BobOutput> {
    const response = await axios.post(
      `${API_BASE_URL}/api/incidents/${incidentId}/analyze-with-bob`
    );

    const bobOutput = normalizeBobOutput(response.data);
    saveStoredJson(BOB_OUTPUT_STORAGE_KEY, bobOutput);
    return bobOutput;
  },

  async pollForUpdates(
    lastTimestamp?: string
  ): Promise<{ findings: Finding[]; incidents: Incident[]; hasUpdates: boolean }> {
    const params = lastTimestamp ? { since: lastTimestamp } : {};
    const response = await axios.get(`${API_BASE_URL}/api/updates`, { params });

    return {
      findings: Array.isArray(response.data?.findings)
        ? response.data.findings.map(normalizeFinding)
        : [],
      incidents: Array.isArray(response.data?.incidents)
        ? response.data.incidents.map(normalizeIncident)
        : [],
      hasUpdates: Boolean(response.data?.hasUpdates),
    };
  },
  
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
    const response = await axios.post(`${API_BASE_URL}/api/scan`, {
      paths,
      use_mock: useMock,
      use_bob: useBob,
    });

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
  },

  async clearAllData(): Promise<ResetResponse> {
    clearStoredDashboardData();

    try {
      const response = await axios.delete(`${API_BASE_URL}/api/reset`);
      return response.data;
    } catch (error) {
      console.warn(
        "Backend reset failed. Local dashboard data was still cleared.",
        error
      );

      return {
        status: "local_only",
        message: "Local dashboard data cleared. Backend reset endpoint unavailable.",
      };
    }
  },
  async simulateAttack(): Promise<{
  status: string;
  message: string;
  incident_id: string;
  }> {
  const response = await axios.post(`${API_BASE_URL}/api/simulate-attack`);
  return response.data;
},
};