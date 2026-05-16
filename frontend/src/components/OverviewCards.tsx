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

export default function OverviewCards({ incidents = [], findings = [], bobAnalysisGenerated }: OverviewCardsProps) {
  // Ensure arrays are defined with fallback to empty arrays
  const safeIncidents = incidents || [];
  const safeFindings = findings || [];
  
  const criticalIncidents = safeIncidents.filter(i => i?.severity === 'critical').length;
  const highSeverityFindings = safeFindings.filter(f => f?.severity_hint === 'high' || f?.severity_hint === 'critical').length;
  
  const avgConfidence = safeIncidents.length > 0
    ? Math.round(safeIncidents.reduce((sum, i) => sum + (i?.confidence_score || 0), 0) / safeIncidents.length * 100)
    : 0;

  const totalTests = safeIncidents.reduce((sum, i) => {
    return sum + (i?.findings?.length > 0 ? 3 : 0); // Mock: 3 tests per incident
  }, 0);

  const affectedRepos = new Set(safeIncidents.flatMap(i => i?.affected_repos || [])).size;

  const aiMemories = safeIncidents.reduce((sum, i) => sum + (i?.related_memory?.length || 0), 0);

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
        value={safeFindings.length}
        subtitle={`${highSeverityFindings} high/critical`}
        color="#f85149"
      />
      <Card
        icon={<Activity size={24} />}
        title="Correlated Incidents"
        value={safeIncidents.length}
        subtitle={`${criticalIncidents} critical`}
        color="#ff7b72"
      />
      <Card
        icon={<Database size={24} />}
        title="Confidence Score"
        value={`${avgConfidence}%`}
        subtitle="Average across incidents"
        color="#a371f7"
      />
      <Card
        icon={<FileCode size={24} />}
        title="Tests Generated"
        value={totalTests}
        subtitle="Security regression tests"
        color="#56d364"
      />
      <Card
        icon={<GitPullRequest size={24} />}
        title="PR Drafts"
        value={bobAnalysisGenerated ? safeIncidents.length : 0}
        subtitle="Ready for review"
        color="#d29922"
      />
    </div>
  );
}

// Made with Bob
