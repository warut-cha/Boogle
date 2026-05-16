import axios from 'axios';
import type { Finding, Incident, BobOutput } from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Event types for SSE
export type SSEEventType = 
  | 'connected'
  | 'heartbeat'
  | 'finding_added'
  | 'incident_added'
  | 'incident_updated'
  | 'data_cleared'
  | 'scan_complete'
  | 'scan_error'
  | 'demo_progress'
  | 'demo_complete';

export interface SSEEvent {
  type: SSEEventType;
  data?: any;
  timestamp: string;
}

export type EventCallback = (event: SSEEvent) => void;

/**
 * Real-time API client with Server-Sent Events support
 */
class RealtimeAPIClient {
  private eventSource: EventSource | null = null;
  private listeners: Map<SSEEventType | 'all', Set<EventCallback>> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 2000;

  /**
   * Connect to SSE endpoint for real-time updates
   */
  connect(): void {
    if (this.eventSource) {
      console.warn('Already connected to SSE');
      return;
    }

    console.log('🔌 Connecting to real-time updates...');
    this.eventSource = new EventSource(`${API_BASE_URL}/api/events`);

    this.eventSource.onopen = () => {
      console.log('✅ Connected to real-time updates');
      this.reconnectAttempts = 0;
    };

    this.eventSource.onmessage = (event) => {
      try {
        const data: SSEEvent = JSON.parse(event.data);
        this.handleEvent(data);
      } catch (error) {
        console.error('Failed to parse SSE event:', error, event.data);
        // Don't crash on parse errors, just log them
      }
    };

    this.eventSource.onerror = (error) => {
      console.error('SSE connection error:', error);
      
      // Close existing connection
      if (this.eventSource) {
        this.eventSource.close();
        this.eventSource = null;
      }

      // Notify listeners of disconnection
      this.handleEvent({
        type: 'heartbeat',
        data: { status: 'disconnected' },
        timestamp: new Date().toISOString()
      });

      // Attempt reconnection with exponential backoff
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
        console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
        setTimeout(() => this.connect(), delay);
      } else {
        console.error('Max reconnection attempts reached. Please refresh the page.');
      }
    };
  }

  /**
   * Disconnect from SSE endpoint
   */
  disconnect(): void {
    if (this.eventSource) {
      console.log('🔌 Disconnecting from real-time updates...');
      this.eventSource.close();
      this.eventSource = null;
    }
  }

  /**
   * Subscribe to specific event type or all events
   */
  on(eventType: SSEEventType | 'all', callback: EventCallback): () => void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }
    this.listeners.get(eventType)!.add(callback);

    // Return unsubscribe function
    return () => {
      this.listeners.get(eventType)?.delete(callback);
    };
  }

  /**
   * Handle incoming SSE event
   */
  private handleEvent(event: SSEEvent): void {
    try {
      // Notify specific event listeners
      const specificListeners = this.listeners.get(event.type);
      if (specificListeners) {
        specificListeners.forEach(callback => {
          try {
            callback(event);
          } catch (error) {
            console.error(`Error in event listener for ${event.type}:`, error);
          }
        });
      }

      // Notify 'all' event listeners
      const allListeners = this.listeners.get('all');
      if (allListeners) {
        allListeners.forEach(callback => {
          try {
            callback(event);
          } catch (error) {
            console.error('Error in "all" event listener:', error);
          }
        });
      }
    } catch (error) {
      console.error('Error handling event:', error, event);
    }
  }

  /**
   * Get all findings
   */
  async getFindings(): Promise<Finding[]> {
    const response = await axios.get(`${API_BASE_URL}/api/findings`);
    return response.data;
  }

  /**
   * Get all incidents
   */
  async getIncidents(): Promise<Incident[]> {
    const response = await axios.get(`${API_BASE_URL}/api/incidents`);
    return response.data;
  }

  /**
   * Get specific incident
   */
  async getIncident(id: string): Promise<Incident> {
    const response = await axios.get(`${API_BASE_URL}/api/incidents/${id}`);
    return response.data;
  }

  /**
   * Trigger Bob AI analysis for an incident
   */
  async analyzewithBob(incidentId: string): Promise<BobOutput> {
    const response = await axios.post(`${API_BASE_URL}/api/incidents/${incidentId}/analyze-with-bob`);
    return response.data;
  }

  /**
   * Trigger a new security scan
   */
  async triggerScan(paths: string[] = ['./mock-repos'], useMock = false, useBob = true): Promise<void> {
    await axios.post(`${API_BASE_URL}/api/scan`, {
      paths,
      use_mock: useMock,
      use_bob: useBob
    });
  }

  /**
   * Simulate an attack for demo purposes
   */
  async simulateAttack(): Promise<void> {
    await axios.post(`${API_BASE_URL}/api/demo/simulate-attack`);
  }

  /**
   * Clear all data
   */
  async clearData(): Promise<void> {
    await axios.post(`${API_BASE_URL}/api/clear`);
  }

  /**
   * Check server health
   */
  async healthCheck(): Promise<any> {
    const response = await axios.get(`${API_BASE_URL}/api/health`);
    return response.data;
  }
}

// Export singleton instance
export const realtimeClient = new RealtimeAPIClient();

// Export class for testing
export { RealtimeAPIClient };

// Made with Bob
