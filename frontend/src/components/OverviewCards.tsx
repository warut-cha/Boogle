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
  backgroundColor: "#ffffff",
  border: "1px solid #d2d2d2",
  borderRadius: "0",
  padding: "1.5rem",
  minHeight: "160px",
  boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
};

function Card({ icon, title, value, subtitle, color }: CardProps) {
  return (
    <div style={cardStyle}>
      <div style={{ marginBottom: "1rem" }}>
        <div style={{
          color: "#0066cc",
          fontSize: "4rem",
          fontWeight: 300,
          lineHeight: 1,
          marginBottom: "0.5rem"
        }}>
          {value}
        </div>
        <div style={{
          color: "#151515",
          fontSize: "0.875rem",
          fontWeight: 600,
          marginBottom: "0.25rem"
        }}>
          {title}
        </div>
      </div>

      {subtitle && (
        <div style={{
          color: "#6a6e73",
          fontSize: "0.8rem",
          borderTop: "1px solid #f0f0f0",
          paddingTop: "0.75rem"
        }}>
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
        gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
        gap: "1.5rem",
        marginBottom: "1.5rem",
      }}
    >
      <Card
        icon={<Shield size={24} />}
        title="New detections"
        value={findings.length}
        subtitle={affectedRepos === 0 ? "No repositories loaded" : `Monitoring ${affectedRepos} repositories`}
        color="#0066cc"
      />

      <Card
        icon={<AlertTriangle size={24} />}
        title="High severity findings"
        value={highSeverityFindings}
        subtitle={`${findings.length} total findings detected`}
        color="#c9190b"
      />

      <Card
        icon={<Activity size={24} />}
        title="Correlated incidents"
        value={incidents.length}
        subtitle={`${criticalIncidents} critical incidents`}
        color="#0066cc"
      />

      <Card
        icon={<Database size={24} />}
        title="Confidence score"
        value={`${avgConfidence}%`}
        subtitle="Average across all incidents"
        color="#0066cc"
      />

      <Card
        icon={<FileCode size={24} />}
        title="Tests generated"
        value={generatedTestsCount}
        subtitle="Security regression tests"
        color="#3e8635"
      />

      <Card
        icon={<GitPullRequest size={24} />}
        title="PR drafts ready"
        value={prDraftsCount}
        subtitle={prDraftsCount > 0 ? "Ready for review" : "No PR draft yet"}
        color="#f0ab00"
      />
    </div>
  );
}