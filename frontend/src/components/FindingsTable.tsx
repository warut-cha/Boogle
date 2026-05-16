import { AlertCircle, Shield, Database, Activity, Server, FileText } from 'lucide-react';
import type { Finding } from '../api/types';

interface FindingsTableProps {
  findings: Finding[];
}

const getSeverityColor = (severity: string): string => {
  switch (severity) {
    case 'critical': return '#c9190b';
    case 'high': return '#c9190b';
    case 'medium': return '#f0ab00';
    case 'low': return '#0066cc';
    default: return '#6a6e73';
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

export default function FindingsTable({ findings }: FindingsTableProps) {
  if (findings.length === 0) {
    return (
      <div style={{
        backgroundColor: '#ffffff',
        border: '1px solid #d2d2d2',
        borderRadius: '0',
        padding: '2rem',
        textAlign: 'center',
        color: '#6a6e73'
      }}>
        No findings detected
      </div>
    );
  }

  return (
    <div style={{
      backgroundColor: '#ffffff',
      border: '1px solid #d2d2d2',
      borderRadius: '0',
      overflow: 'hidden',
      boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
    }}>
      <div style={{
        padding: '1rem 1.5rem',
        borderBottom: '1px solid #d2d2d2',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        backgroundColor: '#f5f5f5'
      }}>
        <h2 style={{ fontSize: '1rem', fontWeight: 600, color: '#151515', margin: 0 }}>
          Most recent detections
        </h2>
        <span style={{
          fontSize: '0.875rem',
          color: '#6a6e73',
          backgroundColor: '#ffffff',
          padding: '0.25rem 0.75rem',
          borderRadius: '3px',
          border: '1px solid #d2d2d2'
        }}>
          {findings.length} total
        </span>
      </div>
      
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#f5f5f5', borderBottom: '1px solid #d2d2d2' }}>
              <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, color: '#6a6e73', textTransform: 'uppercase' }}>
                Severity
              </th>
              <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, color: '#6a6e73', textTransform: 'uppercase' }}>
                Tactic & Technique
              </th>
              <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, color: '#6a6e73', textTransform: 'uppercase' }}>
                Detect Time
              </th>
              <th style={{ padding: '0.75rem 1rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: 600, color: '#6a6e73', textTransform: 'uppercase' }}>
                Host
              </th>
            </tr>
          </thead>
          <tbody>
            {findings.map((finding, index) => (
              <tr
                key={finding.finding_id}
                style={{
                  borderBottom: index < findings.length - 1 ? '1px solid #f0f0f0' : 'none',
                  backgroundColor: '#ffffff'
                }}
              >
                <td style={{ padding: '1rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <div style={{
                      width: '32px',
                      height: '32px',
                      borderRadius: '50%',
                      backgroundColor: getSeverityColor(finding.severity_hint),
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: '#ffffff',
                      fontSize: '0.75rem',
                      fontWeight: 600
                    }}>
                      {getCategoryIcon(finding.category)}
                    </div>
                    <div>
                      <div style={{ fontSize: '0.875rem', color: '#151515', fontWeight: 600 }}>
                        High
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#6a6e73' }}>
                        +1 other
                      </div>
                    </div>
                  </div>
                </td>
                <td style={{ padding: '1rem' }}>
                  <div style={{ fontSize: '0.875rem', color: '#151515', marginBottom: '0.25rem' }}>
                    {finding.finding_type.replace(/_/g, ' ')}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#6a6e73' }}>
                    {finding.evidence.substring(0, 50)}...
                  </div>
                </td>
                <td style={{ padding: '1rem', fontSize: '0.875rem', color: '#151515' }}>
                  {new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                </td>
                <td style={{ padding: '1rem', fontSize: '0.875rem', color: '#151515' }}>
                  {finding.repo_name}
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
