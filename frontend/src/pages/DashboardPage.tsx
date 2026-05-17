import type { CSSProperties } from "react";
import { useCallback, useEffect, useState } from "react";
import { Bell, Wifi, WifiOff, RefreshCw, Trash2, Zap } from "lucide-react";
import { apiClient } from "../api/client";
import type { BobOutput, Finding, Incident } from "../api/types";
import {
  normalizeBobOutput,
  normalizeFinding,
  normalizeIncident,
} from "../api/normalize";
import { useRealtimeMonitoring } from "../hooks/useRealtimeMonitoring";
import { theme, gradients } from "../styles/theme";

import OverviewCards from "../components/OverviewCards";
import FindingsTable from "../components/FindingsTable";
import IncidentDetail from "../components/IncidentDetail";
import AttackPathGraph from "../components/AttackPathGraph";
import BobAnalysis from "../components/BobAnalysis";
import ReportViewer from "../components/ReportViewer";
import MemoryViewer from "../components/MemoryViewer";
import PRDraftViewer from "../components/PRDraftViewer";
import SeverityChart from "../components/charts/SeverityChart";
import TimelineChart from "../components/charts/TimelineChart";

type ActiveTab = "overview" | "findings" | "incident" | "analysis";

const pageStyle: CSSProperties = {
  minHeight: "100vh",
  backgroundColor: theme.colors.background.secondary,
  color: theme.colors.text.primary,
  padding: "0",
  fontFamily: theme.typography.fontFamily.sans,
};

const headerStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  padding: `${theme.spacing[4]} ${theme.spacing[8]}`,
  background: gradients.primary,
  color: theme.colors.text.inverse,
  marginBottom: "0",
  boxShadow: theme.shadows.md,
  position: "sticky",
  top: 0,
  zIndex: theme.zIndex.sticky,
};

const statusBarStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  backgroundColor: theme.colors.background.primary,
  border: `1px solid ${theme.colors.border.subtle}`,
  borderRadius: "0",
  padding: `${theme.spacing[4]} ${theme.spacing[8]}`,
  marginBottom: "0",
  boxShadow: theme.shadows.sm,
};

const tabButtonBase: CSSProperties = {
  padding: `${theme.spacing[3]} ${theme.spacing[6]}`,
  backgroundColor: "transparent",
  border: "none",
  borderBottom: "3px solid transparent",
  color: theme.colors.text.secondary,
  fontSize: theme.typography.fontSize.sm,
  fontWeight: theme.typography.fontWeight.semibold,
  cursor: "pointer",
  transition: `all ${theme.transitions.base}`,
  letterSpacing: theme.typography.letterSpacing.wide,
};

const sectionStyle: CSSProperties = {
  marginTop: theme.spacing[6],
  padding: `0 ${theme.spacing[8]}`,
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
        <div style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          minHeight: "100vh",
          gap: theme.spacing[4]
        }}>
          <div className="animate-spin" style={{
            width: "48px",
            height: "48px",
            border: `4px solid ${theme.colors.border.subtle}`,
            borderTopColor: theme.colors.primary[500],
            borderRadius: "50%"
          }} />
          <div style={{
            color: theme.colors.text.secondary,
            fontSize: theme.typography.fontSize.lg,
            fontWeight: theme.typography.fontWeight.medium
          }}>
            Loading Dashboard...
          </div>
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
    <main style={pageStyle} className="animate-fade-in">
      <header style={headerStyle}>
        <div style={{ display: "flex", alignItems: "center", gap: theme.spacing[4] }}>
          <div style={{
            width: "48px",
            height: "48px",
            background: "rgba(255, 255, 255, 0.2)",
            backdropFilter: "blur(10px)",
            borderRadius: theme.borderRadius.base,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "1.5rem",
            boxShadow: theme.shadows.md,
          }}>
            🛡️
          </div>
          <div>
            <h1 style={{
              margin: 0,
              color: theme.colors.text.inverse,
              fontSize: theme.typography.fontSize["2xl"],
              fontWeight: theme.typography.fontWeight.semibold,
              letterSpacing: theme.typography.letterSpacing.tight,
            }}>
              Security Detections Dashboard
            </h1>
            <p style={{
              margin: 0,
              color: "rgba(255, 255, 255, 0.8)",
              fontSize: theme.typography.fontSize.xs,
              fontWeight: theme.typography.fontWeight.regular,
            }}>
              Real-time threat detection and AI-powered analysis
            </p>
          </div>
        </div>

        <div style={{
          display: "flex",
          alignItems: "center",
          gap: theme.spacing[3],
          background: "rgba(255, 255, 255, 0.1)",
          padding: `${theme.spacing[2]} ${theme.spacing[4]}`,
          borderRadius: theme.borderRadius.base,
          backdropFilter: "blur(10px)",
        }}>
          <Zap size={16} />
          <span style={{
            fontSize: theme.typography.fontSize.xs,
            fontWeight: theme.typography.fontWeight.medium,
          }}>
            Powered by IBM Bob AI
          </span>
        </div>
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
            className="btn btn-primary"
            style={{
              display: "flex",
              alignItems: "center",
              gap: theme.spacing[2],
              padding: `${theme.spacing[3]} ${theme.spacing[5]}`,
              background: gradients.primary,
              border: "none",
              borderRadius: theme.borderRadius.sm,
              color: theme.colors.text.inverse,
              fontSize: theme.typography.fontSize.sm,
              fontWeight: theme.typography.fontWeight.semibold,
              cursor: "pointer",
              boxShadow: theme.shadows.base,
              transition: `all ${theme.transitions.base}`,
            }}
          >
            <RefreshCw size={16} />
            Run Security Scan
          </button>

          <button
            onClick={handleClearAll}
            className="btn btn-secondary"
            style={{
              display: "flex",
              alignItems: "center",
              gap: theme.spacing[2],
              padding: `${theme.spacing[3]} ${theme.spacing[5]}`,
              backgroundColor: theme.colors.background.primary,
              border: `1px solid ${theme.colors.border.subtle}`,
              borderRadius: theme.borderRadius.sm,
              color: theme.colors.text.primary,
              fontSize: theme.typography.fontSize.sm,
              fontWeight: theme.typography.fontWeight.semibold,
              cursor: "pointer",
              transition: `all ${theme.transitions.base}`,
            }}
          >
            <Trash2 size={16} />
            Clear Dashboard
          </button>

          <span style={{
            color: theme.colors.text.secondary,
            fontSize: theme.typography.fontSize.xs,
            fontFamily: theme.typography.fontFamily.mono,
          }}>
            Last updated: {new Date().toLocaleTimeString()}
          </span>
        </div>
      </section>

      {showNotification && (
        <div
          className="animate-slide-in-down"
          style={{
            position: "fixed",
            top: theme.spacing[6],
            right: theme.spacing[6],
            backgroundColor: theme.colors.background.primary,
            border: `2px solid ${theme.colors.primary[500]}`,
            borderRadius: theme.borderRadius.base,
            padding: `${theme.spacing[4]} ${theme.spacing[6]}`,
            color: theme.colors.text.primary,
            boxShadow: theme.shadows.xl,
            zIndex: theme.zIndex.tooltip,
            minWidth: "300px",
            display: "flex",
            alignItems: "center",
            gap: theme.spacing[3],
          }}
        >
          <Bell size={20} color={theme.colors.primary[500]} />
          <span style={{
            flex: 1,
            fontSize: theme.typography.fontSize.sm,
            fontWeight: theme.typography.fontWeight.medium,
          }}>
            {notificationMessage}
          </span>
        </div>
      )}

      <nav
        style={{
          display: "flex",
          borderBottom: `2px solid ${theme.colors.border.subtle}`,
          marginBottom: "0",
          backgroundColor: theme.colors.background.primary,
          padding: `0 ${theme.spacing[8]}`,
          boxShadow: theme.shadows.sm,
        }}
      >
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              ...tabButtonBase,
              borderBottomColor: activeTab === tab.id ? theme.colors.primary[500] : "transparent",
              color: activeTab === tab.id ? theme.colors.primary[500] : theme.colors.text.secondary,
              transform: activeTab === tab.id ? "translateY(2px)" : "translateY(0)",
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

          {/* Data Visualization Section */}
          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(500px, 1fr))",
            gap: theme.spacing[6],
            padding: `0 ${theme.spacing[8]}`,
            marginTop: theme.spacing[6],
          }}>
            <TimelineChart findings={findings} incidents={incidents} />
            <SeverityChart findings={findings} />
          </div>

          <div style={sectionStyle}>
            <h2 style={{
              fontSize: theme.typography.fontSize.xl,
              fontWeight: theme.typography.fontWeight.semibold,
              color: theme.colors.text.primary,
              marginBottom: theme.spacing[4],
            }}>
              Recent Findings
            </h2>
            <FindingsTable findings={findings.slice(0, 5)} />
          </div>

          {selectedIncident && (
            <div style={sectionStyle}>
              <h2 style={{
                fontSize: theme.typography.fontSize.xl,
                fontWeight: theme.typography.fontWeight.semibold,
                color: theme.colors.text.primary,
                marginBottom: theme.spacing[4],
              }}>
                Critical Incident
              </h2>
              <IncidentDetail incident={selectedIncident} />
            </div>
          )}
        </section>
      )}

      {activeTab === "findings" && (
        <section style={sectionStyle}>
          <h2 style={{
            fontSize: theme.typography.fontSize.xl,
            fontWeight: theme.typography.fontWeight.semibold,
            color: theme.colors.text.primary,
            marginBottom: theme.spacing[4],
          }}>
            All Security Findings
          </h2>
          
          <div style={{ marginBottom: theme.spacing[6] }}>
            <SeverityChart findings={findings} />
          </div>
          
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