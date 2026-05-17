import type { ReactNode, CSSProperties } from "react";
import {
  Activity,
  AlertTriangle,
  Database,
  FileCode,
  GitPullRequest,
  Shield,
  TrendingUp,
  TrendingDown,
  Minus,
} from "lucide-react";
import type { BobOutput, Finding, Incident } from "../api/types";

interface OverviewCardsProps {
  incidents: Incident[];
  findings: Finding[];
  bobOutput: BobOutput | null;
}

interface CardProps {
  icon: ReactNode;
  title: string;
  value: string | number;
  subtitle?: string;
  color: string;
  trend?: "up" | "down" | "stable";
  change?: string;
}

const severityColors = {
  critical: "#ff0040",
  high: "#ff6b35",
  medium: "#ffd700",
  low: "#00bfff",
  info: "#6c757d",
};

const glassPanel: CSSProperties = {
  background: "rgba(15, 20, 35, 0.7)",
  backdropFilter: "blur(10px)",
  border: "1px solid rgba(0, 255, 255, 0.1)",
  borderRadius: "12px",
  boxShadow: "0 8px 32px rgba(0, 0, 0, 0.3)",
};

const cardStyle: CSSProperties = {
  ...glassPanel,
  padding: "1.5rem",
  minHeight: "160px",
  position: "relative",
  overflow: "hidden",
  transition: "all 0.3s ease",
};

function Card({ icon, title, value, subtitle, color, trend, change }: CardProps) {
  return (
    <div 
      style={cardStyle}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = "translateY(-4px)";
        e.currentTarget.style.boxShadow = `0 12px 40px rgba(0, 0, 0, 0.4), 0 0 20px ${color}20`;
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = "translateY(0)";
        e.currentTarget.style.boxShadow = "0 8px 32px rgba(0, 0, 0, 0.3)";
      }}
    >
      {/* Glow effect */}
      <div style={{
        position: "absolute",
        top: 0,
        right: 0,
        width: "80px",
        height: "80px",
        background: `radial-gradient(circle, ${color}30 0%, transparent 70%)`,
        pointerEvents: "none",
      }} />
      
      {/* Icon */}
      <div style={{ 
        marginBottom: "1rem",
        color: color,
        opacity: 0.8,
      }}>
        {icon}
      </div>

      {/* Value */}
      <div style={{
        fontSize: "2.5rem",
        fontWeight: 600,
        color: color,
        lineHeight: 1,
        marginBottom: "0.5rem",
        textShadow: `0 0 20px ${color}40`,
      }}>
        {value}
      </div>

      {/* Title */}
      <div style={{
        color: "#e6edf3",
        fontSize: "0.875rem",
        fontWeight: 500,
        marginBottom: "0.5rem",
        textTransform: "uppercase",
        letterSpacing: "0.5px",
      }}>
        {title}
      </div>

      {/* Trend indicator */}
      {trend && change && (
        <div style={{ 
          display: "flex", 
          alignItems: "center", 
          gap: "0.25rem", 
          fontSize: "0.75rem",
          color: trend === "up" ? "#ff0040" : trend === "down" ? "#00ff88" : "#6c757d",
          marginBottom: "0.5rem",
        }}>
          {trend === "up" && <TrendingUp size={14} />}
          {trend === "down" && <TrendingDown size={14} />}
          {trend === "stable" && <Minus size={14} />}
          {change}
        </div>
      )}

      {/* Subtitle */}
      {subtitle && (
        <div style={{
          color: "#8b949e",
          fontSize: "0.75rem",
          borderTop: "1px solid rgba(255, 255, 255, 0.05)",
          paddingTop: "0.75rem",
        }}>
          {subtitle}
        </div>
      )}

      {/* Mini sparkline */}
      <svg 
        width="100%" 
        height="30" 
        style={{ 
          position: "absolute",
          bottom: "0.5rem",
          left: 0,
          opacity: 0.3,
          pointerEvents: "none",
        }}
      >
        <polyline
          points="0,20 20,15 40,18 60,10 80,12 100,8"
          fill="none"
          stroke={color}
          strokeWidth="2"
        />
      </svg>
    </div>
  );
}

export default function OverviewCards({
  incidents,
  findings,
  bobOutput,
}: OverviewCardsProps) {
  const criticalIncidents = incidents.filter(
    (incident) => incident.severity === "critical"
  ).length;

  const highSeverityFindings = findings.filter(
    (finding) =>
      finding.severity_hint === "high" || finding.severity_hint === "critical"
  ).length;

  const avgConfidence =
    incidents.length > 0
      ? Math.round(
          (incidents.reduce((sum, incident) => sum + incident.confidence_score, 0) /
            incidents.length) *
            100
        )
      : 0;

  const affectedRepos = new Set(
    incidents.flatMap((incident) => incident.affected_repos ?? [])
  ).size;

  const generatedTestsCount = bobOutput?.generated_security_tests?.length ?? 0;
  const prDraftsCount = bobOutput?.pr_draft ? 1 : 0;

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
        gap: "1rem",
        marginBottom: "1.5rem",
        padding: "0 1rem",
      }}
    >
      <Card
        icon={<Shield size={24} />}
        title="New Detections"
        value={findings.length}
        subtitle={affectedRepos === 0 ? "No repositories loaded" : `Monitoring ${affectedRepos} repositories`}
        color="#00bfff"
        trend="up"
        change="+12%"
      />

      <Card
        icon={<AlertTriangle size={24} />}
        title="High Severity Findings"
        value={highSeverityFindings}
        subtitle={`${findings.length} total findings detected`}
        color={severityColors.high}
        trend="up"
        change="+5%"
      />

      <Card
        icon={<Activity size={24} />}
        title="Correlated Incidents"
        value={incidents.length}
        subtitle={`${criticalIncidents} critical incidents`}
        color={severityColors.critical}
        trend="stable"
        change="0%"
      />

      <Card
        icon={<Database size={24} />}
        title="AI Confidence Score"
        value={`${avgConfidence}%`}
        subtitle="Average across all incidents"
        color="#00ff88"
        trend="up"
        change="+2%"
      />

      <Card
        icon={<FileCode size={24} />}
        title="Tests Generated"
        value={generatedTestsCount}
        subtitle="Security regression tests"
        color={severityColors.medium}
        trend="down"
        change="-3%"
      />

      <Card
        icon={<GitPullRequest size={24} />}
        title="PR Drafts Ready"
        value={prDraftsCount}
        subtitle={prDraftsCount > 0 ? "Ready for review" : "No PR draft yet"}
        color={severityColors.low}
        trend="stable"
        change="0%"
      />
    </div>
  );
}

// Made with Bob
