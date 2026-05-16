import { Shield, AlertTriangle, Activity, FileCode, Database, GitPullRequest } from 'lucide-react';
import type { Incident, Finding } from '../api/types';

interface OverviewCardsProps {
  incidents: Incident[];
  findings: Finding[];
  bobAnalysisGenerated: boolean;
}

interface CardProps {
  icon: React.ReactNode;
  title: string;
  value: string | number;
  subtitle?: string;
  color: string;
}

const Card = ({ icon, title, value, subtitle, color }: CardProps) => (
  <div style={{
    backgroundColor: '#161b22',
    border: '1px solid #30363d',
    borderRadius: '8px',
    padding: '1.5rem',
    display: 'flex',
    flexDirection: 'column',
    gap: '0.75rem'
  }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
      <div style={{ color }}>
        {icon}
      </div>
      <span style={{ fontSize: '0.875rem', color: '#8b949e', fontWeight: 500 }}>
        {title}
      </span>
    </div>
    <div>
      <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#e6edf3' }}>
        {value}
      </div>
      {subtitle && (
        <div style={{ fontSize: '0.75rem', color: '#8b949e', marginTop: '0.25rem' }}>
          {subtitle}
        </div>
      )}
    </div>
  </div>
);

export default function OverviewCards({ incidents, findings, bobAnalysisGenerated }: OverviewCardsProps) {
  const criticalIncidents = incidents.filter(i => i.severity === 'critical').length;
  
  // Count findings by severity
  const criticalFindings = findings.filter(f => f.severity_hint === 'critical').length;
  const highFindings = findings.filter(f => f.severity_hint === 'high').length;
  const mediumFindings = findings.filter(f => f.severity_hint === 'medium').length;
  
  // Build severity breakdown string
  const severityBreakdown = [
    criticalFindings > 0 ? `${criticalFindings} critical` : null,
    highFindings > 0 ? `${highFindings} high` : null,
    mediumFindings > 0 ? `${mediumFindings} medium` : null
  ].filter(Boolean).join(' · ') || 'No high-severity findings';
  
  const avgConfidence = incidents.length > 0
    ? Math.round(incidents.reduce((sum, i) => sum + i.confidence_score, 0) / incidents.length * 100)
    : 0;

  // Count Bob analyses - if bobAnalysisGenerated is true, we have 1 analysis
  const bobAnalysesCount = bobAnalysisGenerated ? 1 : 0;

  const affectedRepos = new Set(incidents.flatMap(i => i.affected_repos)).size;

  const aiMemories = incidents.reduce((sum, i) => sum + i.related_memory.length, 0);

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
      gap: '1rem',
      marginBottom: '2rem'
    }}>
      <Card
        icon={<Shield size={24} />}
        title="Repos Scanned"
        value={affectedRepos || 2}
        subtitle="Active monitoring"
        color="#58a6ff"
      />
      <Card
        icon={<AlertTriangle size={24} />}
        title="Total Findings"
        value={findings.length}
        subtitle={severityBreakdown}
        color="#f85149"
      />
      <Card
        icon={<Activity size={24} />}
        title="Correlated Incidents"
        value={incidents.length}
        subtitle={`${criticalIncidents} critical`}
        color="#ff7b72"
      />
      <Card
        icon={<Database size={24} />}
        title="Avg Confidence"
        value={`${avgConfidence}%`}
        subtitle="Average across incidents"
        color="#a371f7"
      />
      <Card
        icon={<FileCode size={24} />}
        title="Bob Analyses"
        value={bobAnalysesCount}
        subtitle="AI-powered analysis"
        color="#56d364"
      />
      <Card
        icon={<GitPullRequest size={24} />}
        title="AI Memories"
        value={aiMemories}
        subtitle="Security patterns learned"
        color="#d29922"
      />
    </div>
  );
}

// Made with Bob
