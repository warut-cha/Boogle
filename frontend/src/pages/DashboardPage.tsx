import type { CSSProperties } from "react";
import { useCallback, useEffect, useState } from "react";
import { 
  Bell, 
  Wifi, 
  WifiOff, 
  Search,
  Clock,
  User,
  Shield,
  AlertTriangle,
  Activity,
  FileText,
  Code,
  Database,
  Settings,
  Brain,
  ChevronRight,
  TrendingUp,
  TrendingDown,
  Minus,
  Zap,
  Target,
  GitBranch
} from "lucide-react";
import { apiClient } from "../api/client";
import type { BobOutput, Finding, Incident } from "../api/types";
import {
  normalizeBobOutput,
  normalizeFinding,
  normalizeIncident,
} from "../api/normalize";
import { useRealtimeMonitoring } from "../hooks/useRealtimeMonitoring";

import AttackPathGraph from "../components/AttackPathGraph";
import BobAnalysis from "../components/BobAnalysis";

type ActiveSection = "dashboard" | "incidents" | "attack-graph" | "logs" | "api-security" | "code-analysis" | "ai-memory" | "settings";
type TimeRange = "1h" | "24h" | "7d" | "custom";

// Severity color mapping
const severityColors = {
  critical: "#ff0040",
  high: "#ff6b35",
  medium: "#ffd700",
  low: "#00bfff",
  info: "#6c757d",
};

// Glassmorphism panel style
const glassPanel: CSSProperties = {
  background: "rgba(15, 20, 35, 0.7)",
  backdropFilter: "blur(10px)",
  border: "1px solid rgba(0, 255, 255, 0.1)",
  borderRadius: "12px",
  boxShadow: "0 8px 32px rgba(0, 0, 0, 0.3)",
};

const pageStyle: CSSProperties = {
  minHeight: "100vh",
  backgroundColor: "transparent",
  color: "#e6edf3",
  display: "flex",
  flexDirection: "column",
};

const topNavStyle: CSSProperties = {
  ...glassPanel,
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  padding: "1rem 2rem",
  margin: "1rem 1rem 0 1rem",
  borderRadius: "12px",
};

const mainLayoutStyle: CSSProperties = {
  display: "flex",
  flex: 1,
  gap: "1rem",
  padding: "1rem",
  overflow: "hidden",
};

const sidebarStyle: CSSProperties = {
  ...glassPanel,
  width: "240px",
  padding: "1.5rem 0",
  display: "flex",
  flexDirection: "column",
  gap: "0.5rem",
};

const contentAreaStyle: CSSProperties = {
  flex: 1,
  display: "flex",
  flexDirection: "column",
  gap: "1rem",
  overflow: "auto",
  paddingRight: "0.5rem",
};

const rightPanelStyle: CSSProperties = {
  ...glassPanel,
  width: "380px",
  padding: "1.5rem",
  display: "flex",
  flexDirection: "column",
  maxHeight: "calc(100vh - 120px)",
  overflow: "hidden",
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
  const [activeSection, setActiveSection] = useState<ActiveSection>("dashboard");
  const [timeRange, setTimeRange] = useState<TimeRange>("24h");
  const [aiMode, setAiMode] = useState(true);
  const [showNotification, setShowNotification] = useState(false);
  const [notificationMessage, setNotificationMessage] = useState("");
  const [aiQuestion, setAiQuestion] = useState("");

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
      setFindings((prev) => mergeById(prev, [normalized], "finding_id"));
      notify(`🚨 New ${normalized.severity_hint} severity finding detected!`, 5000);
    },
    [notify]
  );

  const handleNewIncident = useCallback(
    (incident: Incident) => {
      const normalized = normalizeIncident(incident);
      setIncidents((prev) => mergeById(prev, [normalized], "incident_id"));
      setSelectedIncident(normalized);
      notify(`⚠️ New ${normalized.severity} incident: ${normalized.title}`, 5000);
    },
    [notify]
  );

  const handleBobAnalysis = useCallback(
    (_incidentId: string, analysis: BobOutput) => {
      setBobOutput(normalizeBobOutput(analysis));
      notify("🤖 Bob AI analysis completed!", 5000);
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
      setActiveSection("dashboard");
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
      notify("🔍 Starting security scan...", 3000);
      const result = await apiClient.triggerScan(["./mock-repos"], true, true);
      
      if (!isConnected) {
        setFindings((prev) => mergeById(prev, result.new_findings, "finding_id"));
        setIncidents((prev) => mergeById(prev, result.new_incidents, "incident_id"));
        if (result.new_incidents.length > 0) {
          setSelectedIncident(result.new_incidents[0]);
        }
        if (result.bob_analysis) {
          setBobOutput(result.bob_analysis);
        }
      }
      notify(`✅ Scan completed: ${result.run_id}`, 3000);
    } catch (error) {
      console.error("Failed to trigger scan:", error);
      notify("❌ Failed to start scan. Check backend connection.", 5000);
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
    setActiveSection("dashboard");
    clearNewFindings();
    clearNewIncidents();
    notify("🗑️ Dashboard data cleared.", 3000);
  };

  // Calculate KPIs
  const activeThreats = incidents.filter(i => i.severity === "critical" || i.severity === "high").length;
  const criticalIncidents = incidents.filter(i => i.severity === "critical").length;
  const leakedSecrets = findings.filter(f => f.category === "secret_exposure").length;
  const suspiciousAPI = findings.filter(f => f.finding_type === "deprecated_api").length;
  const anomalousSessions = findings.filter(f => f.finding_type === "runtime_anomaly" || f.finding_type === "database_anomaly").length;
  const avgConfidence = incidents.length > 0
    ? Math.round((incidents.reduce((sum, i) => sum + i.confidence_score, 0) / incidents.length) * 100)
    : 0;

  if (loading) {
    return (
      <main style={pageStyle}>
        <div style={{ 
          display: "flex", 
          alignItems: "center", 
          justifyContent: "center", 
          height: "100vh",
          fontSize: "1.2rem",
          color: "#00bfff"
        }}>
          <Activity className="animate-pulse" size={32} style={{ marginRight: "1rem" }} />
          Loading AI Security Analyst Dashboard...
        </div>
      </main>
    );
  }

  const sidebarItems = [
    { id: "dashboard" as ActiveSection, icon: Shield, label: "Dashboard" },
    { id: "incidents" as ActiveSection, icon: AlertTriangle, label: "Incidents" },
    { id: "attack-graph" as ActiveSection, icon: GitBranch, label: "Attack Graph" },
    { id: "logs" as ActiveSection, icon: FileText, label: "Logs Explorer" },
    { id: "api-security" as ActiveSection, icon: Activity, label: "API Security" },
    { id: "code-analysis" as ActiveSection, icon: Code, label: "Code Analysis" },
    { id: "ai-memory" as ActiveSection, icon: Brain, label: "AI Memory" },
    { id: "settings" as ActiveSection, icon: Settings, label: "Settings" },
  ];

  const suggestedPrompts = [
    "Summarize today's threats",
    "Show highest risk incidents",
    "Explain this attack chain",
    "Generate fix for leaked API key"
  ];

  return (
    <main style={pageStyle}>
      {/* Top Navigation Bar */}
      <nav style={topNavStyle}>
        <div style={{ display: "flex", alignItems: "center", gap: "2rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
            <Shield size={28} style={{ color: "#00bfff" }} />
            <div>
              <h1 style={{ fontSize: "1.25rem", fontWeight: 600, margin: 0 }}>
                AI Security Analyst
              </h1>
              <div style={{ fontSize: "0.75rem", color: "#6c757d", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                {isConnected ? (
                  <>
                    <Wifi size={12} style={{ color: "#00ff88" }} />
                    <span style={{ color: "#00ff88" }}>Live Monitoring</span>
                  </>
                ) : (
                  <>
                    <WifiOff size={12} style={{ color: "#ff0040" }} />
                    <span style={{ color: "#ff0040" }}>Alerting</span>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Global Search */}
          <div style={{
            display: "flex",
            alignItems: "center",
            background: "rgba(0, 0, 0, 0.3)",
            border: "1px solid rgba(0, 255, 255, 0.2)",
            borderRadius: "8px",
            padding: "0.5rem 1rem",
            minWidth: "300px",
          }}>
            <Search size={16} style={{ color: "#6c757d", marginRight: "0.5rem" }} />
            <input
              type="text"
              placeholder="Search incidents, logs, secrets..."
              style={{
                background: "transparent",
                border: "none",
                outline: "none",
                color: "#e6edf3",
                fontSize: "0.875rem",
                width: "100%",
              }}
            />
          </div>

          {/* Time Range Selector */}
          <div style={{ display: "flex", gap: "0.5rem" }}>
            {(["1h", "24h", "7d", "custom"] as TimeRange[]).map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                style={{
                  padding: "0.5rem 1rem",
                  background: timeRange === range ? "rgba(0, 191, 255, 0.2)" : "rgba(0, 0, 0, 0.3)",
                  border: timeRange === range ? "1px solid #00bfff" : "1px solid rgba(255, 255, 255, 0.1)",
                  borderRadius: "6px",
                  color: timeRange === range ? "#00bfff" : "#e6edf3",
                  fontSize: "0.75rem",
                  cursor: "pointer",
                  transition: "all 0.2s",
                }}
              >
                <Clock size={12} style={{ display: "inline", marginRight: "0.25rem" }} />
                {range === "custom" ? "Custom" : `Last ${range}`}
              </button>
            ))}
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          {/* Notifications */}
          <button
            style={{
              position: "relative",
              background: "rgba(0, 0, 0, 0.3)",
              border: "1px solid rgba(255, 255, 255, 0.1)",
              borderRadius: "8px",
              padding: "0.5rem",
              cursor: "pointer",
              color: "#e6edf3",
            }}
          >
            <Bell size={18} />
            {(newFindings.length + newIncidents.length) > 0 && (
              <span style={{
                position: "absolute",
                top: "-4px",
                right: "-4px",
                background: "#ff0040",
                borderRadius: "50%",
                width: "18px",
                height: "18px",
                fontSize: "0.65rem",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 600,
              }}>
                {newFindings.length + newIncidents.length}
              </span>
            )}
          </button>

          {/* AI Mode Toggle */}
          <button
            onClick={() => setAiMode(!aiMode)}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
              padding: "0.5rem 1rem",
              background: aiMode ? "rgba(0, 191, 255, 0.2)" : "rgba(0, 0, 0, 0.3)",
              border: aiMode ? "1px solid #00bfff" : "1px solid rgba(255, 255, 255, 0.1)",
              borderRadius: "8px",
              color: aiMode ? "#00bfff" : "#e6edf3",
              fontSize: "0.75rem",
              cursor: "pointer",
              fontWeight: 600,
            }}
          >
            <Brain size={16} />
            AI Mode {aiMode ? "ON" : "OFF"}
          </button>

          {/* User Profile */}
          <button
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
              background: "rgba(0, 0, 0, 0.3)",
              border: "1px solid rgba(255, 255, 255, 0.1)",
              borderRadius: "8px",
              padding: "0.5rem 1rem",
              cursor: "pointer",
              color: "#e6edf3",
            }}
          >
            <User size={18} />
            <span style={{ fontSize: "0.875rem" }}>Security Analyst</span>
          </button>
        </div>
      </nav>

      {/* Notification Toast */}
      {showNotification && (
        <div
          style={{
            position: "fixed",
            top: "6rem",
            right: "2rem",
            ...glassPanel,
            padding: "1rem 1.5rem",
            color: "#e6edf3",
            zIndex: 1000,
            minWidth: "300px",
            animation: "slideIn 0.3s ease-out",
          }}
        >
          {notificationMessage}
        </div>
      )}

      {/* Main Layout */}
      <div style={mainLayoutStyle}>
        {/* Left Sidebar Navigation */}
        <aside style={sidebarStyle}>
          {sidebarItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeSection === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveSection(item.id)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "0.75rem",
                  padding: "0.75rem 1.5rem",
                  background: isActive ? "rgba(0, 191, 255, 0.15)" : "transparent",
                  border: "none",
                  borderLeft: isActive ? "3px solid #00bfff" : "3px solid transparent",
                  color: isActive ? "#00bfff" : "#8b949e",
                  fontSize: "0.875rem",
                  fontWeight: isActive ? 600 : 400,
                  cursor: "pointer",
                  transition: "all 0.2s",
                  textAlign: "left",
                }}
              >
                <Icon size={18} />
                {item.label}
              </button>
            );
          })}
        </aside>

        {/* Main Content Area */}
        <div style={contentAreaStyle}>
          {activeSection === "dashboard" && (
            <>
              {/* KPI Summary Cards */}
              <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                gap: "1rem",
              }}>
                {[
                  { label: "Active Threats", value: activeThreats, color: severityColors.critical, trend: "up", change: "+12%" },
                  { label: "Critical Incidents", value: criticalIncidents, color: severityColors.high, trend: "up", change: "+5%" },
                  { label: "Leaked Secrets", value: leakedSecrets, color: severityColors.medium, trend: "down", change: "-3%" },
                  { label: "Suspicious API Activity", value: suspiciousAPI, color: severityColors.low, trend: "stable", change: "0%" },
                  { label: "Anomalous Sessions", value: anomalousSessions, color: severityColors.info, trend: "down", change: "-8%" },
                  { label: "AI Confidence Score", value: `${avgConfidence}%`, color: "#00ff88", trend: "up", change: "+2%" },
                ].map((kpi, idx) => (
                  <div key={idx} style={{
                    ...glassPanel,
                    padding: "1.25rem",
                    position: "relative",
                    overflow: "hidden",
                  }}>
                    <div style={{
                      position: "absolute",
                      top: 0,
                      right: 0,
                      width: "60px",
                      height: "60px",
                      background: `radial-gradient(circle, ${kpi.color}20 0%, transparent 70%)`,
                    }} />
                    <div style={{ fontSize: "0.75rem", color: "#8b949e", marginBottom: "0.5rem" }}>
                      {kpi.label}
                    </div>
                    <div style={{ display: "flex", alignItems: "baseline", gap: "0.5rem", marginBottom: "0.5rem" }}>
                      <div style={{ fontSize: "2rem", fontWeight: 600, color: kpi.color }}>
                        {kpi.value}
                      </div>
                      <div style={{ display: "flex", alignItems: "center", gap: "0.25rem", fontSize: "0.75rem", color: kpi.trend === "up" ? "#ff0040" : kpi.trend === "down" ? "#00ff88" : "#6c757d" }}>
                        {kpi.trend === "up" && <TrendingUp size={14} />}
                        {kpi.trend === "down" && <TrendingDown size={14} />}
                        {kpi.trend === "stable" && <Minus size={14} />}
                        {kpi.change}
                      </div>
                    </div>
                    {/* Mini sparkline */}
                    <svg width="100%" height="30" style={{ opacity: 0.5 }}>
                      <polyline
                        points="0,20 20,15 40,18 60,10 80,12 100,8"
                        fill="none"
                        stroke={kpi.color}
                        strokeWidth="2"
                      />
                    </svg>
                  </div>
                ))}
              </div>

              {/* Real-time Security Event Feed */}
              <div style={{ ...glassPanel, padding: "1.5rem" }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1rem" }}>
                  <h2 style={{ fontSize: "1.125rem", fontWeight: 600, display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <Zap size={20} style={{ color: "#ffd700" }} />
                    Real-Time Security Events
                  </h2>
                  <div style={{ display: "flex", gap: "0.5rem" }}>
                    <button
                      onClick={handleTriggerScan}
                      style={{
                        padding: "0.5rem 1rem",
                        background: "rgba(0, 191, 255, 0.2)",
                        border: "1px solid #00bfff",
                        borderRadius: "6px",
                        color: "#00bfff",
                        fontSize: "0.75rem",
                        cursor: "pointer",
                        fontWeight: 600,
                      }}
                    >
                      🔍 Run Scan
                    </button>
                    <button
                      onClick={handleClearAll}
                      style={{
                        padding: "0.5rem 1rem",
                        background: "rgba(255, 0, 64, 0.1)",
                        border: "1px solid rgba(255, 0, 64, 0.3)",
                        borderRadius: "6px",
                        color: "#ff0040",
                        fontSize: "0.75rem",
                        cursor: "pointer",
                        fontWeight: 600,
                      }}
                    >
                      Clear All
                    </button>
                  </div>
                </div>
                <div style={{ maxHeight: "300px", overflowY: "auto" }}>
                  {findings.slice(0, 10).map((finding, idx) => (
                    <div
                      key={finding.finding_id}
                      style={{
                        padding: "1rem",
                        background: "rgba(0, 0, 0, 0.2)",
                        border: `1px solid ${severityColors[finding.severity_hint as keyof typeof severityColors] || severityColors.info}40`,
                        borderRadius: "8px",
                        marginBottom: "0.75rem",
                        cursor: "pointer",
                        transition: "all 0.2s",
                      }}
                    >
                      <div style={{ display: "flex", alignItems: "start", justifyContent: "space-between", marginBottom: "0.5rem" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                          <span style={{
                            padding: "0.25rem 0.75rem",
                            background: `${severityColors[finding.severity_hint as keyof typeof severityColors] || severityColors.info}20`,
                            border: `1px solid ${severityColors[finding.severity_hint as keyof typeof severityColors] || severityColors.info}`,
                            borderRadius: "4px",
                            fontSize: "0.7rem",
                            fontWeight: 600,
                            color: severityColors[finding.severity_hint as keyof typeof severityColors] || severityColors.info,
                            textTransform: "uppercase",
                          }}>
                            {finding.severity_hint}
                          </span>
                          <span style={{ fontSize: "0.875rem", fontWeight: 600 }}>
                            {finding.finding_type.replace(/_/g, " ").toUpperCase()}
                          </span>
                        </div>
                        <span style={{ fontSize: "0.75rem", color: "#6c757d" }}>
                          {new Date(finding.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                      <div style={{ fontSize: "0.875rem", color: "#e6edf3", marginBottom: "0.5rem" }}>
                        {finding.evidence}
                      </div>
                      <div style={{ display: "flex", alignItems: "center", gap: "1rem", fontSize: "0.75rem", color: "#8b949e" }}>
                        <span>📁 {finding.file || "N/A"}</span>
                        <span>Source: {finding.source}</span>
                      </div>
                    </div>
                  ))}
                  {findings.length === 0 && (
                    <div style={{ textAlign: "center", padding: "2rem", color: "#6c757d" }}>
                      No security events detected. Run a scan to start monitoring.
                    </div>
                  )}
                </div>
              </div>

              {/* Incident Correlation Panel */}
              {selectedIncident && (
                <div style={{ ...glassPanel, padding: "1.5rem" }}>
                  <h2 style={{ fontSize: "1.125rem", fontWeight: 600, marginBottom: "1rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <Target size={20} style={{ color: "#ff0040" }} />
                    Incident Correlation: {selectedIncident.title}
                  </h2>
                  <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "1.5rem" }}>
                    <div>
                      <div style={{ marginBottom: "1rem" }}>
                        <div style={{ fontSize: "0.75rem", color: "#8b949e", marginBottom: "0.5rem" }}>
                          Attack Chain Timeline
                        </div>
                        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
                          {selectedIncident.findings?.slice(0, 5).map((f, idx) => (
                            <div key={idx} style={{ display: "flex", alignItems: "center" }}>
                              <div style={{
                                padding: "0.5rem 1rem",
                                background: `${severityColors[f.severity_hint as keyof typeof severityColors] || severityColors.info}20`,
                                border: `1px solid ${severityColors[f.severity_hint as keyof typeof severityColors] || severityColors.info}`,
                                borderRadius: "6px",
                                fontSize: "0.75rem",
                              }}>
                                {f.finding_type.split("_")[0]}
                              </div>
                              {idx < (selectedIncident.findings?.length || 0) - 1 && (
                                <ChevronRight size={16} style={{ color: "#6c757d", margin: "0 0.25rem" }} />
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                      <div style={{ marginBottom: "1rem" }}>
                        <div style={{ fontSize: "0.75rem", color: "#8b949e", marginBottom: "0.5rem" }}>
                          AI-Generated Explanation
                        </div>
                        <div style={{ fontSize: "0.875rem", color: "#e6edf3", lineHeight: 1.6 }}>
                          {selectedIncident.title} - Confidence: {Math.round(selectedIncident.confidence_score * 100)}%
                        </div>
                      </div>
                      {selectedIncident.attack_path && (
                        <div>
                          <div style={{ fontSize: "0.75rem", color: "#8b949e", marginBottom: "0.5rem" }}>
                            Attack Path Graph
                          </div>
                          <AttackPathGraph attackPath={selectedIncident.attack_path} />
                        </div>
                      )}
                    </div>
                    <div>
                      <div style={{ marginBottom: "1.5rem" }}>
                        <div style={{ fontSize: "0.75rem", color: "#8b949e", marginBottom: "0.5rem" }}>
                          Risk Score
                        </div>
                        <div style={{ position: "relative", height: "120px" }}>
                          <svg width="100%" height="100%" viewBox="0 0 100 100">
                            <circle
                              cx="50"
                              cy="50"
                              r="40"
                              fill="none"
                              stroke="rgba(255, 255, 255, 0.1)"
                              strokeWidth="8"
                            />
                            <circle
                              cx="50"
                              cy="50"
                              r="40"
                              fill="none"
                              stroke={severityColors[selectedIncident.severity as keyof typeof severityColors] || severityColors.info}
                              strokeWidth="8"
                              strokeDasharray={`${selectedIncident.confidence_score * 251} 251`}
                              strokeLinecap="round"
                              transform="rotate(-90 50 50)"
                            />
                            <text
                              x="50"
                              y="50"
                              textAnchor="middle"
                              dy="0.3em"
                              fontSize="20"
                              fontWeight="600"
                              fill={severityColors[selectedIncident.severity as keyof typeof severityColors] || severityColors.info}
                            >
                              {Math.round(selectedIncident.confidence_score * 100)}
                            </text>
                          </svg>
                        </div>
                      </div>
                      <div>
                        <div style={{ fontSize: "0.75rem", color: "#8b949e", marginBottom: "0.5rem" }}>
                          Confidence
                        </div>
                        <div style={{ fontSize: "1.5rem", fontWeight: 600, color: "#00ff88" }}>
                          {Math.round(selectedIncident.confidence_score * 100)}%
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Logs Explorer Table */}
              <div style={{ ...glassPanel, padding: "1.5rem" }}>
                <h2 style={{ fontSize: "1.125rem", fontWeight: 600, marginBottom: "1rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <FileText size={20} style={{ color: "#00bfff" }} />
                  Logs Explorer
                </h2>
                <div style={{ overflowX: "auto" }}>
                  <table style={{ width: "100%", fontSize: "0.875rem", borderCollapse: "collapse" }}>
                    <thead>
                      <tr style={{ borderBottom: "1px solid rgba(255, 255, 255, 0.1)" }}>
                        <th style={{ padding: "0.75rem", textAlign: "left", color: "#8b949e", fontWeight: 600 }}>Timestamp</th>
                        <th style={{ padding: "0.75rem", textAlign: "left", color: "#8b949e", fontWeight: 600 }}>Source System</th>
                        <th style={{ padding: "0.75rem", textAlign: "left", color: "#8b949e", fontWeight: 600 }}>Event Type</th>
                        <th style={{ padding: "0.75rem", textAlign: "left", color: "#8b949e", fontWeight: 600 }}>Severity</th>
                        <th style={{ padding: "0.75rem", textAlign: "left", color: "#8b949e", fontWeight: 600 }}>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {findings.slice(0, 8).map((finding) => (
                        <tr key={finding.finding_id} style={{ borderBottom: "1px solid rgba(255, 255, 255, 0.05)" }}>
                          <td style={{ padding: "0.75rem" }}>{new Date(finding.timestamp).toLocaleString()}</td>
                          <td style={{ padding: "0.75rem" }}>{finding.source || "Unknown"}</td>
                          <td style={{ padding: "0.75rem" }}>{finding.finding_type}</td>
                          <td style={{ padding: "0.75rem" }}>
                            <span style={{
                              padding: "0.25rem 0.5rem",
                              background: `${severityColors[finding.severity_hint as keyof typeof severityColors] || severityColors.info}20`,
                              border: `1px solid ${severityColors[finding.severity_hint as keyof typeof severityColors] || severityColors.info}`,
                              borderRadius: "4px",
                              fontSize: "0.7rem",
                              fontWeight: 600,
                              color: severityColors[finding.severity_hint as keyof typeof severityColors] || severityColors.info,
                            }}>
                              {finding.severity_hint}
                            </span>
                          </td>
                          <td style={{ padding: "0.75rem", color: "#ffd700" }}>Open</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}

          {activeSection === "incidents" && (
            <div style={{ ...glassPanel, padding: "1.5rem" }}>
              <h2 style={{ fontSize: "1.25rem", fontWeight: 600, marginBottom: "1rem" }}>
                All Incidents
              </h2>
              {incidents.map((incident) => (
                <div
                  key={incident.incident_id}
                  onClick={() => setSelectedIncident(incident)}
                  style={{
                    padding: "1rem",
                    background: selectedIncident?.incident_id === incident.incident_id ? "rgba(0, 191, 255, 0.1)" : "rgba(0, 0, 0, 0.2)",
                    border: `1px solid ${severityColors[incident.severity as keyof typeof severityColors] || severityColors.info}40`,
                    borderRadius: "8px",
                    marginBottom: "0.75rem",
                    cursor: "pointer",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
                    <span style={{ fontWeight: 600 }}>{incident.title}</span>
                    <span style={{
                      padding: "0.25rem 0.75rem",
                      background: `${severityColors[incident.severity as keyof typeof severityColors] || severityColors.info}20`,
                      border: `1px solid ${severityColors[incident.severity as keyof typeof severityColors] || severityColors.info}`,
                      borderRadius: "4px",
                      fontSize: "0.7rem",
                      fontWeight: 600,
                      color: severityColors[incident.severity as keyof typeof severityColors] || severityColors.info,
                    }}>
                      {incident.severity}
                    </span>
                  </div>
                  <div style={{ fontSize: "0.875rem", color: "#8b949e" }}>
                    Confidence: {Math.round(incident.confidence_score * 100)}% | {incident.findings.length} findings
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeSection === "attack-graph" && selectedIncident?.attack_path && (
            <div style={{ ...glassPanel, padding: "1.5rem" }}>
              <h2 style={{ fontSize: "1.25rem", fontWeight: 600, marginBottom: "1rem" }}>
                Attack Path Visualization
              </h2>
              <AttackPathGraph attackPath={selectedIncident.attack_path} />
            </div>
          )}

          {activeSection === "code-analysis" && bobOutput && (
            <div style={{ ...glassPanel, padding: "1.5rem" }}>
              <h2 style={{ fontSize: "1.25rem", fontWeight: 600, marginBottom: "1rem" }}>
                Bob AI Code Analysis
              </h2>
              <BobAnalysis bobOutput={bobOutput} />
            </div>
          )}
        </div>

        {/* Right Panel - AI Security Analyst Chat */}
        <aside style={rightPanelStyle}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1rem" }}>
            <Brain size={24} style={{ color: "#00bfff" }} />
            <h2 style={{ fontSize: "1.125rem", fontWeight: 600 }}>AI Security Analyst</h2>
          </div>
          
          <div style={{ 
            flex: 1, 
            overflowY: "auto", 
            marginBottom: "1rem",
            padding: "1rem",
            background: "rgba(0, 0, 0, 0.2)",
            borderRadius: "8px",
          }}>
            {bobOutput ? (
              <div>
                <div style={{ marginBottom: "1rem", padding: "1rem", background: "rgba(0, 191, 255, 0.1)", borderRadius: "8px", borderLeft: "3px solid #00bfff" }}>
                  <div style={{ fontSize: "0.75rem", color: "#00bfff", marginBottom: "0.5rem", fontWeight: 600 }}>
                    AI ANALYSIS
                  </div>
                  <div style={{ fontSize: "0.875rem", lineHeight: 1.6 }}>
                    {bobOutput.confidence_assessment}
                  </div>
                </div>
                {bobOutput.recommended_fixes && bobOutput.recommended_fixes.length > 0 && (
                  <div style={{ marginBottom: "1rem" }}>
                    <div style={{ fontSize: "0.75rem", color: "#8b949e", marginBottom: "0.5rem", fontWeight: 600 }}>
                      RECOMMENDED FIXES
                    </div>
                    {bobOutput.recommended_fixes.map((fix, idx) => (
                      <div key={idx} style={{
                        padding: "0.75rem",
                        background: "rgba(0, 255, 136, 0.05)",
                        border: "1px solid rgba(0, 255, 136, 0.2)",
                        borderRadius: "6px",
                        marginBottom: "0.5rem",
                        fontSize: "0.875rem",
                      }}>
                        {idx + 1}. {fix.description}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div style={{ textAlign: "center", color: "#6c757d", padding: "2rem 0" }}>
                <Brain size={48} style={{ opacity: 0.3, marginBottom: "1rem" }} />
                <div>No AI analysis available yet.</div>
                <div style={{ fontSize: "0.875rem", marginTop: "0.5rem" }}>
                  Run a security scan to generate insights.
                </div>
              </div>
            )}
          </div>

          <div style={{ marginBottom: "1rem" }}>
            <div style={{ fontSize: "0.75rem", color: "#8b949e", marginBottom: "0.5rem", fontWeight: 600 }}>
              SUGGESTED PROMPTS
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              {suggestedPrompts.map((prompt, idx) => (
                <button
                  key={idx}
                  onClick={() => setAiQuestion(prompt)}
                  style={{
                    padding: "0.75rem",
                    background: "rgba(0, 0, 0, 0.3)",
                    border: "1px solid rgba(0, 255, 255, 0.2)",
                    borderRadius: "6px",
                    color: "#e6edf3",
                    fontSize: "0.75rem",
                    cursor: "pointer",
                    textAlign: "left",
                    transition: "all 0.2s",
                  }}
                >
                  💡 {prompt}
                </button>
              ))}
            </div>
          </div>

          <div style={{ display: "flex", gap: "0.5rem" }}>
            <input
              type="text"
              value={aiQuestion}
              onChange={(e) => setAiQuestion(e.target.value)}
              placeholder="Ask AI about threats..."
              style={{
                flex: 1,
                padding: "0.75rem",
                background: "rgba(0, 0, 0, 0.3)",
                border: "1px solid rgba(0, 255, 255, 0.2)",
                borderRadius: "8px",
                color: "#e6edf3",
                fontSize: "0.875rem",
                outline: "none",
              }}
            />
            <button
              style={{
                padding: "0.75rem 1.5rem",
                background: "rgba(0, 191, 255, 0.2)",
                border: "1px solid #00bfff",
                borderRadius: "8px",
                color: "#00bfff",
                fontSize: "0.875rem",
                cursor: "pointer",
                fontWeight: 600,
              }}
            >
              Ask
            </button>
          </div>
        </aside>
      </div>
    </main>
  );
}

// Made with Bob
