import axios from 'axios';
import type { Finding, Incident, BobOutput } from './types';

const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000';

// API client functions
export const apiClient = {
  async getFindings(): Promise<Finding[]> {
    const response = await axios.get(`${API_BASE_URL}/api/findings`);
    return response.data;
  },

  async getIncidents(): Promise<Incident[]> {
    const response = await axios.get(`${API_BASE_URL}/api/incidents`);
    return response.data;
  },

  async getIncident(id: string): Promise<Incident> {
    const response = await axios.get(`${API_BASE_URL}/api/incidents/${id}`);
    return response.data;
  },

  async getBobAnalysis(incidentId: string): Promise<BobOutput> {
    const response = await axios.get(`${API_BASE_URL}/api/incidents/${incidentId}/bob-analysis`);
    return response.data;
  },

  // Real-time monitoring - poll for updates
  async pollForUpdates(lastTimestamp?: string): Promise<{
    findings: Finding[];
    incidents: Incident[];
    hasUpdates: boolean;
  }> {
    const params = lastTimestamp ? { since: lastTimestamp } : {};
    const response = await axios.get(`${API_BASE_URL}/api/updates`, { params });
    return response.data;
  },

  // Trigger security scan
  async triggerScan(paths: string[], useMock: boolean = true, useBob: boolean = true): Promise<{
    status: string;
    message: string;
    paths: string[];
  }> {
    const response = await axios.post(`${API_BASE_URL}/api/scan`, {
      paths,
      use_mock: useMock,
      use_bob: useBob
    });
    return response.data;
  }
};

// Made with Bob
