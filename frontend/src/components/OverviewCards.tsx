import type { ReactNode, CSSProperties } from "react";
import {
  Activity,
  AlertTriangle,
  Database,
  FileCode,
  GitPullRequest,
  Shield,
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
}

const cardStyle: CSSProperties = {
  backgroundColor: "#161b22",
  border: "1px solid #30363d",
  borderRadius: "8px",
  padding: "1.5rem",
  minHeight: "140px",
};

function Card({ icon, title, value, subtitle, color }: CardProps) {
  return (
    <div style={cardStyle}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "0.75rem",
          marginBottom: "1.5rem",
        }}
      >
        <span style={{ color }}>{icon}</span>
        <span style={{ color: "#8b949e", fontWeight: 600 }}>{title}</span>
      </div>

      <div style={{ color: "#e6edf3", fontSize: "2rem", fontWeight: 700 }}>
        {value}
      </div>

      {subtitle && (
        <div style={{ color: "#8b949e", fontSize: "0.875rem", marginTop: "0.5rem" }}>
          {subtitle}
        </div>
      )}
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
        gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
        gap: "1rem",
        marginBottom: "2rem",
      }}
    >
      <Card
        icon={<Shield size={28} />}
        title="Repos Scanned"
        value={affectedRepos}
        subtitle={affectedRepos === 0 ? "No repositories loaded" : "Active monitoring"}
        color="#58a6ff"
      />

      <Card
        icon={<AlertTriangle size={28} />}
        title="Total Findings"
        value={findings.length}
        subtitle={`${highSeverityFindings} high/critical`}
        color="#f85149"
      />

      <Card
        icon={<Activity size={28} />}
        title="Correlated Incidents"
        value={incidents.length}
        subtitle={`${criticalIncidents} critical`}
        color="#ff7b72"
      />

      <Card
        icon={<Database size={28} />}
        title="Confidence Score"
        value={`${avgConfidence}%`}
        subtitle="Average across incidents"
        color="#a371f7"
      />

      <Card
        icon={<FileCode size={28} />}
        title="Tests Generated"
        value={generatedTestsCount}
        subtitle="Security regression tests"
        color="#56d364"
      />

      <Card
        icon={<GitPullRequest size={28} />}
        title="PR Drafts"
        value={prDraftsCount}
        subtitle={prDraftsCount > 0 ? "Ready for review" : "No PR draft yet"}
        color="#d29922"
      />
    </div>
  );
}