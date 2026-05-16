import type { CSSProperties } from "react";
import { useCallback, useEffect, useState } from "react";
import { Bell, Wifi, WifiOff } from "lucide-react";
import { apiClient } from "../api/client";
import type { BobOutput, Finding, Incident } from "../api/types";
import {
  normalizeBobOutput,
  normalizeFinding,
  normalizeIncident,
} from "../api/normalize";
import { useRealtimeMonitoring } from "../hooks/useRealtimeMonitoring";

import OverviewCards from "../components/OverviewCards";
import FindingsTable from "../components/FindingsTable";
import IncidentDetail from "../components/IncidentDetail";
import AttackPathGraph from "../components/AttackPathGraph";
import BobAnalysis from "../components/BobAnalysis";
import ReportViewer from "../components/ReportViewer";
import MemoryViewer from "../components/MemoryViewer";
import PRDraftViewer from "../components/PRDraftViewer";

type ActiveTab = "overview" | "findings" | "incident" | "analysis";

const pageStyle: CSSProperties = {
  minHeight: "100vh",
  backgroundColor: "#f5f5f5",
  color: "#151515",
  padding: "0",
};

const headerStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  padding: "0.75rem 2rem",
  backgroundColor: "#3c3f42",
  color: "#ffffff",
  marginBottom: "0",
};

const statusBarStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  backgroundColor: "#ffffff",
  border: "1px solid #d2d2d2",
  borderRadius: "0",
  padding: "1rem 2rem",
  marginBottom: "0",
};

const tabButtonBase: CSSProperties = {
  padding: "0.75rem 1.5rem",
  backgroundColor: "transparent",
  border: "none",
  borderBottom: "2px solid transparent",
  color: "#6a6e73",
  fontSize: "0.875rem",
  fontWeight: 600,
  cursor: "pointer",
};

const sectionStyle: CSSProperties = {
  marginTop: "1.5rem",
  padding: "0 2rem",
};

function mergeById<T extends Record<string, unknown>>(
  current: T[],
  incoming: T[],
  idKey: keyof T
): T[] {
  const map = new Map<string, T>();

  for (const item of current) {
    const id = String(item[idKey]);
    map.set(id, item);
  }

  for (const item of incoming) {
    const id = String(item[idKey]);
    map.set(id, item);
  }

  return Array.from(map.values());
}

export default function DashboardPage() {
  const [findings, setFindings] = useState<Finding[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [bobOutput, setBobOutput] = useState<BobOutput | null>(null);

  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<ActiveTab>("overview");

  const [showNotification, setShowNotification] = useState(false);
  const [notificationMessage, setNotificationMessage] = useState("");

  const notify = useCallback((message: string, duration = 4000) => {
    setNotificationMessage(message);
    setShowNotification(true);

    window.setTimeout(() => {
      setShowNotification(false);
    }, duration);
  }, []);

  const handleNewFinding = useCallback(
    (finding: Finding) => {
      const normalized = normalizeFinding(finding);

      setFindings((prev) =>
        mergeById(prev, [normalized], "finding_id")
      );

      notify(`New ${normalized.severity_hint} severity finding detected!`, 5000);
    },
    [notify]
  );

  const handleNewIncident = useCallback(
    (incident: Incident) => {
      const normalized = normalizeIncident(incident);

      setIncidents((prev) =>
        mergeById(prev, [normalized], "incident_id")
      );

      setSelectedIncident(normalized);

      notify(`New ${normalized.severity} incident: ${normalized.title}`, 5000);
    },
    [notify]
  );

  const handleBobAnalysis = useCallback(
    (_incidentId: string, analysis: BobOutput) => {
      setBobOutput(normalizeBobOutput(analysis));
      notify("Bob AI analysis completed!", 5000);
    },
    [notify]
  );

  const {
    isConnected,
    newFindings,
    newIncidents,
    clearNewFindings,
    clearNewIncidents,
    reconnect,
  } = useRealtimeMonitoring(
    handleNewFinding,
    handleNewIncident,
    handleBobAnalysis,
    () => {
      setFindings([]);
      setIncidents([]);
      setSelectedIncident(null);
      setBobOutput(null);
      setActiveTab("overview");
    }
  );

  const loadData = useCallback(async () => {
    try {
      setLoading(true);

      const [findingsData, incidentsData] = await Promise.all([
        apiClient.getFindings(),
        apiClient.getIncidents(),
      ]);

      const normalizedFindings = findingsData.map(normalizeFinding);
      const normalizedIncidents = incidentsData.map(normalizeIncident);

      setFindings(normalizedFindings);
      setIncidents(normalizedIncidents);

      if (normalizedIncidents.length > 0) {
        const firstIncident = normalizedIncidents[0];
        setSelectedIncident(firstIncident);

        try {
          const bobData = await apiClient.getBobAnalysis(firstIncident.incident_id);
          setBobOutput(normalizeBobOutput(bobData));
        } catch {
          setBobOutput(null);
        }
      } else {
        setSelectedIncident(null);
        setBobOutput(null);
      }
    } catch (error) {
      console.error("Error loading data:", error);
      notify("Failed to load dashboard data. Check backend connection.", 5000);
    } finally {
      setLoading(false);
    }
  }, [notify]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleTriggerScan = async () => {
    try {
      notify("Starting security scan...", 3000);

      const result = await apiClient.triggerScan(["./mock-repos"], true, true);

      /**
       * If WebSocket is connected, the backend broadcast will update the UI.
       * If WebSocket is disconnected, use the REST response as fallback.
       */
      if (!isConnected) {
        setFindings((prev) =>
          mergeById(prev, result.new_findings, "finding_id")
        );

        setIncidents((prev) =>
          mergeById(prev, result.new_incidents, "incident_id")
        );

        if (result.new_incidents.length > 0) {
          setSelectedIncident(result.new_incidents[0]);
        }

        if (result.bob_analysis) {
          setBobOutput(result.bob_analysis);
        }
      }

      notify(`Scan completed: ${result.run_id}`, 3000);
    } catch (error) {
      console.error("Failed to trigger scan:", error);
      notify("Failed to start scan. Check backend connection.", 5000);
    }
  };

  const handleClearAll = async () => {
    try {
      await apiClient.clearAllData();
    } catch (error) {
      console.warn("Clear endpoint failed. Frontend state will still be cleared.", error);
    }

    setFindings([]);
    setIncidents([]);
    setSelectedIncident(null);
    setBobOutput(null);
    setActiveTab("overview");

    clearNewFindings();
    clearNewIncidents();

    notify("Dashboard data cleared.", 3000);
  };

  if (loading) {
    return (
      <main style={pageStyle}>
        <div style={{ paddingTop: "3rem", color: "#8b949e" }}>
          Loading Jeff Dashboard...
        </div>
      </main>
    );
  }

  const tabs: { id: ActiveTab; label: string }[] = [
    { id: "overview", label: "Overview" },
    { id: "findings", label: "Findings" },
    { id: "incident", label: "Incident Analysis" },
    { id: "analysis", label: "Bob AI Analysis" },
  ];

  return (
    <main style={pageStyle}>
      <header style={headerStyle}>
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          <div style={{
            width: "32px",
            height: "32px",
            backgroundColor: "#ee0000",
            borderRadius: "4px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "1.2rem"
          }}>
            🛡️
          </div>
          <h1 style={{ margin: 0, color: "#ffffff", fontSize: "1.125rem", fontWeight: 400 }}>
            Detections Dashboard
          </h1>
        </div>

        <span style={{ color: "#d2d2d2", fontSize: "0.875rem" }}>
          Powered by IBM Bob
        </span>
      </header>

      <section style={statusBarStyle}>
        <div style={{ display: "flex", alignItems: "center", gap: "1.5rem" }}>
          {isConnected ? (
            <span
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.5rem",
                color: "#3e8635",
                fontSize: "0.875rem",
              }}
            >
              <Wifi size={16} /> Real-time Monitoring Active
            </span>
          ) : (
            <span
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.5rem",
                color: "#c9190b",
                fontSize: "0.875rem",
              }}
            >
              <WifiOff size={16} /> Disconnected
              <button
                onClick={reconnect}
                style={{
                  marginLeft: "0.5rem",
                  padding: "0.25rem 0.75rem",
                  backgroundColor: "#0066cc",
                  border: "none",
                  borderRadius: "3px",
                  color: "#fff",
                  fontSize: "0.75rem",
                  cursor: "pointer",
                }}
              >
                Reconnect
              </button>
            </span>
          )}

          {(newFindings.length > 0 || newIncidents.length > 0) && (
            <span
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.5rem",
                color: "#f0ab00",
                fontSize: "0.875rem",
              }}
            >
              <Bell size={16} />
              {newFindings.length > 0 &&
                `${newFindings.length} new finding${newFindings.length > 1 ? "s" : ""}`}
              {newFindings.length > 0 && newIncidents.length > 0 && ", "}
              {newIncidents.length > 0 &&
                `${newIncidents.length} new incident${newIncidents.length > 1 ? "s" : ""}`}
            </span>
          )}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          <button
            onClick={handleTriggerScan}
            style={{
              padding: "0.5rem 1rem",
              backgroundColor: "#0066cc",
              border: "none",
              borderRadius: "3px",
              color: "#fff",
              fontSize: "0.875rem",
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            🔍 Run Security Scan
          </button>

          <button
            onClick={handleClearAll}
            style={{
              padding: "0.5rem 1rem",
              backgroundColor: "#ffffff",
              border: "1px solid #d2d2d2",
              borderRadius: "3px",
              color: "#151515",
              fontSize: "0.875rem",
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            Clear Dashboard
          </button>

          <span style={{ color: "#6a6e73", fontSize: "0.875rem" }}>
            Last updated: {new Date().toLocaleTimeString()}
          </span>
        </div>
      </section>

      {showNotification && (
        <div
          style={{
            position: "fixed",
            top: "1.5rem",
            right: "1.5rem",
            backgroundColor: "#ffffff",
            border: "1px solid #0066cc",
            borderRadius: "3px",
            padding: "1rem 1.5rem",
            color: "#151515",
            boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
            zIndex: 1000,
          }}
        >
          🔔 {notificationMessage}
        </div>
      )}

      <nav
        style={{
          display: "flex",
          borderBottom: "1px solid #d2d2d2",
          marginBottom: "0",
          backgroundColor: "#ffffff",
          padding: "0 2rem",
        }}
      >
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              ...tabButtonBase,
              borderBottomColor: activeTab === tab.id ? "#0066cc" : "transparent",
              color: activeTab === tab.id ? "#0066cc" : "#6a6e73",
            }}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      {activeTab === "overview" && (
        <section>
          <OverviewCards
            findings={findings}
            incidents={incidents}
            bobOutput={bobOutput}
          />

          <div style={sectionStyle}>
            <h2>Recent Findings</h2>
            <FindingsTable findings={findings.slice(0, 5)} />
          </div>

          {selectedIncident && (
            <div style={sectionStyle}>
              <h2>Critical Incident</h2>
              <IncidentDetail incident={selectedIncident} />
            </div>
          )}
        </section>
      )}

      {activeTab === "findings" && (
        <section>
          <h2>All Security Findings</h2>
          <FindingsTable findings={findings} />
        </section>
      )}

      {activeTab === "incident" && (
        <section>
          <h2>Incident Analysis</h2>

          {selectedIncident ? (
            <>
              <IncidentDetail incident={selectedIncident} />

              <div style={sectionStyle}>
                <h3>Attack Path</h3>
                {selectedIncident.attack_path?.nodes?.length > 0 ? (
                  <AttackPathGraph attackPath={selectedIncident.attack_path} />
                ) : (
                  <p style={{ color: "#8b949e" }}>No attack path available.</p>
                )}
              </div>

              <div style={sectionStyle}>
                <h3>Related Findings</h3>
                <FindingsTable findings={selectedIncident.findings ?? []} />
              </div>

              {(selectedIncident.related_memory?.length ?? 0) > 0 && (
                <div style={sectionStyle}>
                  <h3>AI Memory Patterns</h3>
                  <MemoryViewer memories={selectedIncident.related_memory ?? []} />
                </div>
              )}
            </>
          ) : (
            <div style={{ color: "#8b949e", padding: "2rem 0" }}>
              <h3>No incidents detected yet</h3>
              <p>Run a security scan to detect and correlate security incidents.</p>
            </div>
          )}
        </section>
      )}

      {activeTab === "analysis" && (
        <section>
          <h2>IBM Bob AI Analysis & Remediation</h2>

          <BobAnalysis bobOutput={bobOutput} />

          {bobOutput && (
            <>
              <div style={sectionStyle}>
                <h3>Incident Report</h3>
                <ReportViewer report={bobOutput.incident_report} />
              </div>

              <div style={sectionStyle}>
                <h3>AI Memory Created</h3>
                <MemoryViewer memories={[bobOutput.ai_memory]} />
              </div>

              <div style={sectionStyle}>
                <h3>Pull Request Draft</h3>
                <PRDraftViewer prDraft={bobOutput.pr_draft} />
              </div>
            </>
          )}
        </section>
      )}
    </main>
  );
}