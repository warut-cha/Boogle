import {
  Activity,
  AlertTriangle,
  Database,
  FileCode,
  GitPullRequest,
  Shield,
} from "lucide-react";
import type { BobOutput, Finding, Incident } from "../api/types";
import { theme } from "../styles/theme";
import AnimatedMetricCard from "./charts/AnimatedMetricCard";

interface OverviewCardsProps {
  incidents: Incident[];
  findings: Finding[];
  bobOutput: BobOutput | null;
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
        gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
        gap: theme.spacing[6],
        marginBottom: theme.spacing[6],
        padding: `0 ${theme.spacing[8]}`,
      }}
    >
      <AnimatedMetricCard
        icon={<Shield size={24} />}
        title="New detections"
        value={findings.length}
        subtitle={affectedRepos === 0 ? "No repositories loaded" : `Monitoring ${affectedRepos} ${affectedRepos === 1 ? 'repository' : 'repositories'}`}
        color={theme.colors.primary[500]}
        trend={findings.length > 0 ? { value: 12, isPositive: false } : undefined}
      />

      <AnimatedMetricCard
        icon={<AlertTriangle size={24} />}
        title="High severity findings"
        value={highSeverityFindings}
        subtitle={`${findings.length} total findings detected`}
        color={theme.colors.error[500]}
        trend={highSeverityFindings > 0 ? { value: 8, isPositive: false } : undefined}
      />

      <AnimatedMetricCard
        icon={<Activity size={24} />}
        title="Correlated incidents"
        value={incidents.length}
        subtitle={`${criticalIncidents} critical ${criticalIncidents === 1 ? 'incident' : 'incidents'}`}
        color={theme.colors.primary[600]}
        trend={incidents.length > 0 ? { value: 5, isPositive: false } : undefined}
      />

      <AnimatedMetricCard
        icon={<Database size={24} />}
        title="Confidence score"
        value={avgConfidence}
        suffix="%"
        subtitle="Average across all incidents"
        color={theme.colors.primary[500]}
        trend={avgConfidence > 0 ? { value: 3, isPositive: true } : undefined}
      />

      <AnimatedMetricCard
        icon={<FileCode size={24} />}
        title="Tests generated"
        value={generatedTestsCount}
        subtitle="Security regression tests"
        color={theme.colors.success[500]}
        trend={generatedTestsCount > 0 ? { value: 15, isPositive: true } : undefined}
      />

      <AnimatedMetricCard
        icon={<GitPullRequest size={24} />}
        title="PR drafts ready"
        value={prDraftsCount}
        subtitle={prDraftsCount > 0 ? "Ready for review" : "No PR draft yet"}
        color={theme.colors.warning[500]}
      />
    </div>
  );
}