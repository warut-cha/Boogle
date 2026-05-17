import { useEffect, useRef, useState, useCallback } from "react";
import type { Finding, Incident, BobOutput } from "../api/types";
import { normalizeFinding, normalizeIncident, normalizeBobOutput } from "../api/normalize";

const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws";

// Reconnection configuration
const RECONNECT_DELAY_MS = 1000;
const MAX_RECONNECT_DELAY_MS = 30000;
const RECONNECT_BACKOFF_MULTIPLIER = 1.5;
const HEARTBEAT_INTERVAL_MS = 30000;

export type WebSocketMessage =
  | { type: "connected"; message: string; timestamp: string }
  | { type: "new_finding"; finding: Finding; timestamp: string }
  | { type: "new_incident"; incident: Incident; timestamp: string }
  | {
      type: "scan_completed";
      run_id: string;
      findings: Finding[];
      incidents: Incident[];
      bob_analysis: BobOutput | null;
      timestamp: string;
    }
  | {
      type: "bob_analysis";
      incident_id: string;
      analysis: BobOutput;
      timestamp: string;
    }
  | { type: "reset"; timestamp: string }
  | { type: "pong"; timestamp: string };

export type ConnectionState = "connecting" | "connected" | "disconnected" | "error";

interface UseEnhancedWebSocketReturn {
  connectionState: ConnectionState;
  lastMessage: WebSocketMessage | null;
  sendMessage: (message: any) => void;
  reconnect: () => void;
  disconnect: () => void;
}

/**
 * Enhanced WebSocket hook with automatic reconnection and heartbeat
 */
export function useEnhancedWebSocket(
  onMessage?: (message: WebSocketMessage) => void
): UseEnhancedWebSocketReturn {
  const [connectionState, setConnectionState] = useState<ConnectionState>("disconnected");
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectDelayRef = useRef<number>(RECONNECT_DELAY_MS);
  const shouldReconnectRef = useRef<boolean>(true);
  const messageQueueRef = useRef<any[]>([]);

  /**
   * Clear all timers
   */
  const clearTimers = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
      heartbeatIntervalRef.current = null;
    }
  }, []);

  /**
   * Start heartbeat to keep connection alive
   */
  const startHeartbeat = useCallback(() => {
    clearTimers();

    heartbeatIntervalRef.current = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        console.log("[WebSocket] Sending heartbeat");
        wsRef.current.send(JSON.stringify({ type: "ping" }));
      }
    }, HEARTBEAT_INTERVAL_MS);
  }, [clearTimers]);

  /**
   * Process queued messages after connection
   */
  const processMessageQueue = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN && messageQueueRef.current.length > 0) {
      console.log(`[WebSocket] Processing ${messageQueueRef.current.length} queued messages`);
      
      messageQueueRef.current.forEach((msg) => {
        wsRef.current?.send(JSON.stringify(msg));
      });
      
      messageQueueRef.current = [];
    }
  }, []);

  /**
   * Handle incoming WebSocket messages
   */
  const handleMessage = useCallback(
    (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data) as WebSocketMessage;
        console.log("[WebSocket] Message received:", data.type);

        // Normalize data based on message type
        let normalizedMessage = data;

        if (data.type === "new_finding" && "finding" in data) {
          normalizedMessage = {
            ...data,
            finding: normalizeFinding(data.finding),
          };
        } else if (data.type === "new_incident" && "incident" in data) {
          normalizedMessage = {
            ...data,
            incident: normalizeIncident(data.incident),
          };
        } else if (data.type === "scan_completed") {
          normalizedMessage = {
            ...data,
            findings: data.findings.map(normalizeFinding),
            incidents: data.incidents.map(normalizeIncident),
            bob_analysis: data.bob_analysis ? normalizeBobOutput(data.bob_analysis) : null,
          };
        } else if (data.type === "bob_analysis" && "analysis" in data) {
          normalizedMessage = {
            ...data,
            analysis: normalizeBobOutput(data.analysis),
          };
        }

        setLastMessage(normalizedMessage);
        onMessage?.(normalizedMessage);
      } catch (error) {
        console.error("[WebSocket] Failed to parse message:", error);
      }
    },
    [onMessage]
  );

  /**
   * Connect to WebSocket server
   */
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.log("[WebSocket] Already connected");
      return;
    }

    console.log("[WebSocket] Connecting to:", WS_URL);
    setConnectionState("connecting");

    try {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log("[WebSocket] Connected successfully");
        setConnectionState("connected");
        reconnectDelayRef.current = RECONNECT_DELAY_MS;
        startHeartbeat();
        processMessageQueue();
      };

      ws.onmessage = handleMessage;

      ws.onerror = (error) => {
        console.error("[WebSocket] Error:", error);
        setConnectionState("error");
      };

      ws.onclose = (event) => {
        console.log("[WebSocket] Disconnected:", event.code, event.reason);
        setConnectionState("disconnected");
        clearTimers();

        // Attempt reconnection if not manually closed
        if (shouldReconnectRef.current && event.code !== 1000) {
          const delay = Math.min(
            reconnectDelayRef.current,
            MAX_RECONNECT_DELAY_MS
          );

          console.log(`[WebSocket] Reconnecting in ${delay}ms...`);

          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectDelayRef.current *= RECONNECT_BACKOFF_MULTIPLIER;
            connect();
          }, delay);
        }
      };
    } catch (error) {
      console.error("[WebSocket] Connection failed:", error);
      setConnectionState("error");
    }
  }, [handleMessage, startHeartbeat, processMessageQueue, clearTimers]);

  /**
   * Send a message through WebSocket
   */
  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.log("[WebSocket] Sending message:", message.type);
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn("[WebSocket] Not connected. Queueing message:", message.type);
      messageQueueRef.current.push(message);
    }
  }, []);

  /**
   * Manually reconnect
   */
  const reconnect = useCallback(() => {
    console.log("[WebSocket] Manual reconnect requested");
    shouldReconnectRef.current = true;
    reconnectDelayRef.current = RECONNECT_DELAY_MS;

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    clearTimers();
    connect();
  }, [connect, clearTimers]);

  /**
   * Manually disconnect
   */
  const disconnect = useCallback(() => {
    console.log("[WebSocket] Manual disconnect requested");
    shouldReconnectRef.current = false;
    clearTimers();

    if (wsRef.current) {
      wsRef.current.close(1000, "Manual disconnect");
      wsRef.current = null;
    }

    setConnectionState("disconnected");
  }, [clearTimers]);

  /**
   * Connect on mount, cleanup on unmount
   */
  useEffect(() => {
    shouldReconnectRef.current = true;
    connect();

    return () => {
      shouldReconnectRef.current = false;
      clearTimers();

      if (wsRef.current) {
        wsRef.current.close(1000, "Component unmount");
        wsRef.current = null;
      }
    };
  }, [connect, clearTimers]);

  return {
    connectionState,
    lastMessage,
    sendMessage,
    reconnect,
    disconnect,
  };
}

// Made with Bob
