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
  backgroundColor: "#0f1419",
  color: "#e6edf3",
  padding: "0 1.5rem 2rem",
};

const headerStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  padding: "1rem 0",
  borderBottom: "1px solid #30363d",
  marginBottom: "1.5rem",
};

const statusBarStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  backgroundColor: "#161b22",
  border: "1px solid #30363d",
  borderRadius: "8px",
  padding: "1rem",
  marginBottom: "1.5rem",
};

const tabButtonBase: CSSProperties = {
  padding: "0.75rem 1.5rem",
  backgroundColor: "transparent",
  border: "none",
  borderBottom: "2px solid transparent",
  color: "#8b949e",
  fontSize: "0.875rem",
  fontWeight: 600,
  cursor: "pointer",
};

const sectionStyle: CSSProperties = {
  marginTop: "2rem",
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
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <span style={{ fontSize: "1.8rem" }}>🛡️</span>
          <h1 style={{ margin: 0, color: "#58a6ff" }}>Jeff</h1>
          <span
            style={{
              backgroundColor: "#21262d",
              color: "#8b949e",
              borderRadius: "999px",
              padding: "0.35rem 0.75rem",
            }}
          >
            Autonomous DevSecOps Assistant
          </span>
        </div>

        <span style={{ color: "#8b949e", fontSize: "0.875rem" }}>
          Powered by IBM Bob
        </span>
      </header>

      <section style={statusBarStyle}>
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          {isConnected ? (
            <span
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.5rem",
                color: "#3fb950",
              }}
            >
              <Wifi size={18} /> Real-time Monitoring Active
            </span>
          ) : (
            <span
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.5rem",
                color: "#f85149",
              }}
            >
              <WifiOff size={18} /> Disconnected
              <button onClick={reconnect}>Reconnect</button>
            </span>
          )}

          {(newFindings.length > 0 || newIncidents.length > 0) && (
            <span
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.75rem",
                color: "#d29922",
              }}
            >
              <Bell size={18} />
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
              padding: "0.75rem 1.25rem",
              backgroundColor: "#238636",
              border: "none",
              borderRadius: "6px",
              color: "#fff",
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            🔍 Run Security Scan
          </button>

          <button
            onClick={handleClearAll}
            style={{
              padding: "0.75rem 1.25rem",
              backgroundColor: "#21262d",
              border: "1px solid #30363d",
              borderRadius: "6px",
              color: "#e6edf3",
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            Clear Dashboard
          </button>

          <span style={{ color: "#8b949e", fontSize: "0.875rem" }}>
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
            backgroundColor: "#161b22",
            border: "1px solid #58a6ff",
            borderRadius: "8px",
            padding: "1rem 1.5rem",
            color: "#e6edf3",
            zIndex: 1000,
          }}
        >
          🔔 {notificationMessage}
        </div>
      )}

      <nav
        style={{
          display: "flex",
          borderBottom: "1px solid #30363d",
          marginBottom: "2rem",
        }}
      >
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              ...tabButtonBase,
              borderBottomColor: activeTab === tab.id ? "#58a6ff" : "transparent",
              color: activeTab === tab.id ? "#58a6ff" : "#8b949e",
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