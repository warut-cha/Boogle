import { useEffect, useRef, useState, useCallback } from 'react';
import type { Finding, Incident, BobOutput } from '../api/types';

const WS_URL = (import.meta as any).env?.VITE_WS_URL || 'ws://localhost:8000/ws';

interface RealtimeUpdate {
  type: 'initial_data' | 'new_finding' | 'new_incident' | 'bob_analysis' | 'pong';
  data?: any;
  timestamp: string;
}

interface UseRealtimeMonitoringReturn {
  isConnected: boolean;
  newFindings: Finding[];
  newIncidents: Incident[];
  clearNewFindings: () => void;
  clearNewIncidents: () => void;
  reconnect: () => void;
}

export function useRealtimeMonitoring(
  onNewFinding?: (finding: Finding) => void,
  onNewIncident?: (incident: Incident) => void,
  onBobAnalysis?: (incidentId: string, analysis: BobOutput) => void
): UseRealtimeMonitoringReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [newFindings, setNewFindings] = useState<Finding[]>([]);
  const [newIncidents, setNewIncidents] = useState<Incident[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const heartbeatIntervalRef = useRef<number | null>(null);

  const clearNewFindings = useCallback(() => {
    setNewFindings([]);
  }, []);

  const clearNewIncidents = useCallback(() => {
    setNewIncidents([]);
  }, []);

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('✅ WebSocket connected');
        setIsConnected(true);

        // Start heartbeat
        heartbeatIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send('ping');
          }
        }, 30000); // Send ping every 30 seconds
      };

      ws.onmessage = (event) => {
        try {
          const update: RealtimeUpdate = JSON.parse(event.data);
          console.log('📨 WebSocket message:', update.type);

          switch (update.type) {
            case 'initial_data':
              console.log('📊 Received initial data');
              break;

            case 'new_finding':
              const finding = update.data as Finding;
              setNewFindings(prev => [...prev, finding]);
              if (onNewFinding) {
                onNewFinding(finding);
              }
              // Show browser notification
              if ('Notification' in window && Notification.permission === 'granted') {
                new Notification('🔍 New Security Finding', {
                  body: `${finding.finding_type} detected in ${finding.repo_name}`,
                  icon: '/favicon.ico'
                });
              }
              break;

            case 'new_incident':
              const incident = update.data as Incident;
              setNewIncidents(prev => [...prev, incident]);
              if (onNewIncident) {
                onNewIncident(incident);
              }
              // Show browser notification
              if ('Notification' in window && Notification.permission === 'granted') {
                new Notification('🚨 New Security Incident', {
                  body: `${incident.severity.toUpperCase()}: ${incident.title}`,
                  icon: '/favicon.ico'
                });
              }
              break;

            case 'bob_analysis':
              if (onBobAnalysis && update.data) {
                onBobAnalysis(update.data.incident_id, update.data.analysis);
              }
              // Show browser notification
              if ('Notification' in window && Notification.permission === 'granted') {
                new Notification('🤖 Bob Analysis Complete', {
                  body: 'AI analysis and remediation plan ready',
                  icon: '/favicon.ico'
                });
              }
              break;

            case 'pong':
              // Heartbeat response
              break;
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('🔌 WebSocket disconnected');
        setIsConnected(false);

        // Clear heartbeat
        if (heartbeatIntervalRef.current) {
          clearInterval(heartbeatIntervalRef.current);
          heartbeatIntervalRef.current = null;
        }

        // Attempt to reconnect after 5 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('🔄 Attempting to reconnect...');
          connect();
        }, 5000);
      };
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
    }
  }, [onNewFinding, onNewIncident, onBobAnalysis]);

  const reconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    connect();
  }, [connect]);

  useEffect(() => {
    // Request notification permission
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission().then(permission => {
        console.log('Notification permission:', permission);
      });
    }

    connect();

    return () => {
      // Cleanup
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  return {
    isConnected,
    newFindings,
    newIncidents,
    clearNewFindings,
    clearNewIncidents,
    reconnect
  };
}

// Made with Bob
