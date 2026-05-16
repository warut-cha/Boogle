import { AlertCircle, Shield, Database, Activity, Server, FileText } from 'lucide-react';
import type { Finding } from '../api/types';

interface FindingsTableProps {
  findings: Finding[];
}

const getSeverityColor = (severity: string): string => {
  switch (severity) {
    case 'critical': return '#f85149';
    case 'high': return '#ff7b72';
    case 'medium': return '#d29922';
    case 'low': return '#58a6ff';
    default: return '#8b949e';
  }
};

const getCategoryIcon = (category: string) => {
  switch (category) {
    case 'secret_exposure': return <Shield size={16} />;
    case 'legacy_api': return <Activity size={16} />;
    case 'runtime_behavior': return <Activity size={16} />;
    case 'database_activity': return <Database size={16} />;
    case 'infrastructure': return <Server size={16} />;
    case 'logging': return <FileText size={16} />;
    default: return <AlertCircle size={16} />;
  }
};

export default function FindingsTable({ findings = [] }: FindingsTableProps) {
  const safeFindings = findings || [];
  
  if (safeFindings.length === 0) {
    return (
      <div style={{
        backgroundColor: '#161b22',
        border: '1px solid #30363d',
        borderRadius: '8px',
        padding: '2rem',
        textAlign: 'center',
        color: '#8b949e'
      }}>
        No findings detected
      </div>
    );
  }

  return (
    <div style={{
      backgroundColor: '#161b22',
      border: '1px solid #30363d',
      borderRadius: '8px',
      overflow: 'hidden'
    }}>
      <div style={{
        padding: '1rem 1.5rem',
        borderBottom: '1px solid #30363d',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <h2 style={{ fontSize: '1.125rem', fontWeight: 600, color: '#e6edf3', margin: 0 }}>
          Security Findings
        </h2>
        <span style={{
          fontSize: '0.875rem',
          color: '#8b949e',
          backgroundColor: '#21262d',
          padding: '0.25rem 0.75rem',
          borderRadius: '1rem'
        }}>
          {safeFindings.length} total
        </span>
      </div>
      
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#0d1117', borderBottom: '1px solid #30363d' }}>
              <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, color: '#8b949e', textTransform: 'uppercase' }}>
                ID
              </th>
              <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, color: '#8b949e', textTransform: 'uppercase' }}>
                Type
              </th>
              <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, color: '#8b949e', textTransform: 'uppercase' }}>
                Severity
              </th>
              <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, color: '#8b949e', textTransform: 'uppercase' }}>
                Repository
              </th>
              <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, color: '#8b949e', textTransform: 'uppercase' }}>
                File
              </th>
              <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, color: '#8b949e', textTransform: 'uppercase' }}>
                Evidence
              </th>
              <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, color: '#8b949e', textTransform: 'uppercase' }}>
                Source
              </th>
            </tr>
          </thead>
          <tbody>
            {safeFindings.map((finding, index) => (
              <tr 
                key={finding.finding_id}
                style={{
                  borderBottom: index < findings.length - 1 ? '1px solid #21262d' : 'none',
                  backgroundColor: index % 2 === 0 ? '#0d1117' : 'transparent'
                }}
              >
                <td style={{ padding: '1rem', fontSize: '0.875rem', color: '#58a6ff', fontFamily: 'monospace' }}>
                  {finding.finding_id}
                </td>
                <td style={{ padding: '1rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ color: '#8b949e' }}>
                      {getCategoryIcon(finding.category)}
                    </span>
                    <span style={{ fontSize: '0.875rem', color: '#e6edf3' }}>
                      {finding.finding_type.replace(/_/g, ' ')}
                    </span>
                  </div>
                </td>
                <td style={{ padding: '1rem' }}>
                  <span style={{
                    display: 'inline-block',
                    padding: '0.25rem 0.75rem',
                    borderRadius: '1rem',
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    textTransform: 'uppercase',
                    backgroundColor: `${getSeverityColor(finding.severity_hint)}20`,
                    color: getSeverityColor(finding.severity_hint)
                  }}>
                    {finding.severity_hint}
                  </span>
                </td>
                <td style={{ padding: '1rem', fontSize: '0.875rem', color: '#e6edf3' }}>
                  {finding.repo_name}
                </td>
                <td style={{ padding: '1rem', fontSize: '0.875rem', color: '#8b949e', fontFamily: 'monospace' }}>
                  {finding.file || '-'}
                  {finding.line && <span style={{ color: '#58a6ff' }}>:{finding.line}</span>}
                </td>
                <td style={{ padding: '1rem', fontSize: '0.875rem', color: '#e6edf3', maxWidth: '300px' }}>
                  <div style={{ 
                    overflow: 'hidden', 
                    textOverflow: 'ellipsis', 
                    whiteSpace: 'nowrap' 
                  }}>
                    {finding.evidence}
                  </div>
                  {finding.masked_value && (
                    <div style={{ 
                      fontSize: '0.75rem', 
                      color: '#8b949e', 
                      fontFamily: 'monospace',
                      marginTop: '0.25rem'
                    }}>
                      {finding.masked_value}
                    </div>
                  )}
                </td>
                <td style={{ padding: '1rem', fontSize: '0.75rem', color: '#8b949e' }}>
                  {finding.source.replace(/_/g, ' ')}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// Made with Bob
