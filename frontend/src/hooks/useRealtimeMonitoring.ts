import { useEffect, useRef, useState } from "react";
import type { BobOutput, Finding, Incident } from "../api/types";
import {
  normalizeBobOutput,
  normalizeFinding,
  normalizeIncident,
} from "../api/normalize";

type RealtimeMessage =
  | {
      type: "attack_detected";
      finding?: Finding;
      findings?: Finding[];
      incident?: Incident;
      bob_analysis?: BobOutput | null;
    }
  | {
      type: "scan_completed";
      findings?: Finding[];
      incidents?: Incident[];
      bob_analysis?: BobOutput | null;
    }
  | {
      type: "new_finding";
      finding: Finding;
    }
  | {
      type: "new_incident";
      incident: Incident;
    }
  | {
      type: "bob_analysis";
      incident_id: string;
      analysis: BobOutput;
    }
  | {
      type: "reset";
      findings: [];
      incidents: [];
      bob_analysis: null;
    };

const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws";

export function useRealtimeMonitoring(
  onNewFinding: (finding: Finding) => void,
  onNewIncident: (incident: Incident) => void,
  onBobAnalysis: (incidentId: string, analysis: BobOutput) => void,
  onReset?: () => void
) {
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<number | null>(null);
  const reconnectAttemptsRef = useRef(0);

  const [isConnected, setIsConnected] = useState(false);
  const [newFindings, setNewFindings] = useState<Finding[]>([]);
  const [newIncidents, setNewIncidents] = useState<Incident[]>([]);

  const clearReconnectTimer = () => {
    if (reconnectTimerRef.current !== null) {
      window.clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
  };

  const addFinding = (finding: Finding) => {
    const normalized = normalizeFinding(finding);
    setNewFindings((prev) => [normalized, ...prev]);
    onNewFinding(normalized);
  };

  const addIncident = (incident: Incident) => {
    const normalized = normalizeIncident(incident);
    setNewIncidents((prev) => [normalized, ...prev]);
    onNewIncident(normalized);
    return normalized;
  };

  const connect = () => {
    clearReconnectTimer();

    if (socketRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    const socket = new WebSocket(WS_URL);
    socketRef.current = socket;

    socket.onopen = () => {
      setIsConnected(true);
      reconnectAttemptsRef.current = 0;

      socket.send(
        JSON.stringify({
          type: "client_connected",
          source: "bob_sentinel_dashboard",
        })
      );
    };

    socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data) as RealtimeMessage;

        if (message.type === "new_finding") {
          addFinding(message.finding);
          return;
        }

        if (message.type === "new_incident") {
          addIncident(message.incident);
          return;
        }

        if (message.type === "attack_detected") {
          let incidentId = "";

          if (message.finding) {
            addFinding(message.finding);
          }

          if (Array.isArray(message.findings)) {
            message.findings.forEach(addFinding);
          }

          if (message.incident) {
            const normalizedIncident = addIncident(message.incident);
            incidentId = normalizedIncident.incident_id;
          }

          if (message.bob_analysis && incidentId) {
            onBobAnalysis(incidentId, normalizeBobOutput(message.bob_analysis));
          }

          return;
        }

        if (message.type === "scan_completed") {
          const findings = (message.findings ?? []).map(normalizeFinding);
          const incidents = (message.incidents ?? []).map(normalizeIncident);

          findings.forEach(addFinding);
          incidents.forEach(addIncident);

          if (message.bob_analysis && incidents[0]) {
            onBobAnalysis(
              incidents[0].incident_id,
              normalizeBobOutput(message.bob_analysis)
            );
          }

          return;
        }

        if (message.type === "bob_analysis") {
          onBobAnalysis(message.incident_id, normalizeBobOutput(message.analysis));
          return;
        }

        if (message.type === "reset") {
          setNewFindings([]);
          setNewIncidents([]);
          onReset?.();
        }
      } catch (error) {
        console.error("Failed to parse WebSocket message:", error);
      }
    };

    socket.onerror = () => {
      setIsConnected(false);
    };

    socket.onclose = () => {
      setIsConnected(false);
      reconnectAttemptsRef.current += 1;

      if (reconnectAttemptsRef.current > 5) {
        console.warn("WebSocket reconnect stopped after 5 failed attempts.");
        return;
      }

      const delay = Math.min(1000 * reconnectAttemptsRef.current, 5000);

      reconnectTimerRef.current = window.setTimeout(() => {
        connect();
      }, delay);
    };
  };

  useEffect(() => {
    connect();

    return () => {
      clearReconnectTimer();

      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const reconnect = () => {
    reconnectAttemptsRef.current = 0;
    connect();
  };

  const clearNewFindings = () => {
    setNewFindings([]);
  };

  const clearNewIncidents = () => {
    setNewIncidents([]);
  };

  return {
    isConnected,
    newFindings,
    newIncidents,
    clearNewFindings,
    clearNewIncidents,
    reconnect,
  };
}