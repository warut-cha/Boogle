import { AlertTriangle, CheckCircle, XCircle, TrendingUp } from 'lucide-react';
import type { Incident } from '../api/types';

interface IncidentDetailProps {
  incident: Incident;
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

export default function IncidentDetail({ incident }: IncidentDetailProps) {
  const confidencePercentage = Math.round(incident.confidence_score * 100);

  return (
    <div style={{
      backgroundColor: '#ffffff',
      border: '1px solid #d2d2d2',
      borderRadius: '0',
      overflow: 'hidden',
      boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
    }}>
      <div style={{
        padding: '1.5rem',
        borderBottom: '1px solid #d2d2d2',
        backgroundColor: '#f5f5f5'
      }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem' }}>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
              <AlertTriangle size={24} color={getSeverityColor(incident.severity)} />
              <h2 style={{ fontSize: '1.125rem', fontWeight: 600, color: '#151515', margin: 0 }}>
                {incident.title}
              </h2>
            </div>
            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
              <span style={{
                display: 'inline-block',
                padding: '0.25rem 0.75rem',
                borderRadius: '3px',
                fontSize: '0.75rem',
                fontWeight: 600,
                textTransform: 'uppercase',
                backgroundColor: getSeverityColor(incident.severity),
                color: '#ffffff'
              }}>
                {incident.severity} (Level {incident.severity_level})
              </span>
              <span style={{
                fontSize: '0.875rem',
                color: '#6a6e73',
                fontFamily: 'monospace'
              }}>
                {incident.incident_id}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div style={{ padding: '1.5rem' }}>
        {/* Confidence Score */}
        <div style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <TrendingUp size={18} color="#0066cc" />
            <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#151515', margin: 0 }}>
              Confidence Assessment
            </h3>
          </div>
          
          <div style={{ marginBottom: '1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '0.875rem', color: '#6a6e73' }}>Confidence Score</span>
              <span style={{ fontSize: '0.875rem', fontWeight: 600, color: '#0066cc' }}>
                {confidencePercentage}%
              </span>
            </div>
            <div style={{
              width: '100%',
              height: '8px',
              backgroundColor: '#f0f0f0',
              borderRadius: '0',
              overflow: 'hidden'
            }}>
              <div style={{
                width: `${confidencePercentage}%`,
                height: '100%',
                backgroundColor: '#0066cc',
                transition: 'width 0.3s ease'
              }} />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <CheckCircle size={16} color="#3e8635" />
                <span style={{ fontSize: '0.875rem', fontWeight: 600, color: '#151515' }}>
                  Supporting Evidence
                </span>
              </div>
              <ul style={{ margin: 0, paddingLeft: '1.5rem', listStyle: 'disc' }}>
                {incident.confidence_reasons.map((reason, index) => (
                  <li key={index} style={{ fontSize: '0.875rem', color: '#6a6e73', marginBottom: '0.25rem' }}>
                    {reason}
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <XCircle size={16} color="#c9190b" />
                <span style={{ fontSize: '0.875rem', fontWeight: 600, color: '#151515' }}>
                  Limitations
                </span>
              </div>
              <ul style={{ margin: 0, paddingLeft: '1.5rem', listStyle: 'disc' }}>
                {incident.confidence_limitations.map((limitation, index) => (
                  <li key={index} style={{ fontSize: '0.875rem', color: '#6a6e73', marginBottom: '0.25rem' }}>
                    {limitation}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Affected Assets */}
        <div style={{ marginBottom: '2rem' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#151515', marginBottom: '0.75rem' }}>
            Affected Assets
          </h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <div>
              <div style={{ fontSize: '0.75rem', color: '#6a6e73', marginBottom: '0.5rem', textTransform: 'uppercase', fontWeight: 600 }}>
                Repositories
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                {incident.affected_repos.map((repo, index) => (
                  <span key={index} style={{
                    fontSize: '0.875rem',
                    color: '#0066cc',
                    fontFamily: 'monospace',
                    padding: '0.25rem 0.5rem',
                    backgroundColor: '#f0f0f0',
                    borderRadius: '3px',
                    display: 'inline-block'
                  }}>
                    {repo}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <div style={{ fontSize: '0.75rem', color: '#6a6e73', marginBottom: '0.5rem', textTransform: 'uppercase', fontWeight: 600 }}>
                Files
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                {incident.affected_files.map((file, index) => (
                  <span key={index} style={{
                    fontSize: '0.875rem',
                    color: '#151515',
                    fontFamily: 'monospace',
                    padding: '0.25rem 0.5rem',
                    backgroundColor: '#f0f0f0',
                    borderRadius: '3px',
                    display: 'inline-block',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                  }}>
                    {file}
                  </span>
                ))}
              </div>
            </div>

            {incident.affected_endpoints.length > 0 && (
              <div>
                <div style={{ fontSize: '0.75rem', color: '#6a6e73', marginBottom: '0.5rem', textTransform: 'uppercase', fontWeight: 600 }}>
                  Endpoints
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                  {incident.affected_endpoints.map((endpoint, index) => (
                    <span key={index} style={{
                      fontSize: '0.875rem',
                      color: '#f0ab00',
                      fontFamily: 'monospace',
                      padding: '0.25rem 0.5rem',
                      backgroundColor: '#f0f0f0',
                      borderRadius: '3px',
                      display: 'inline-block'
                    }}>
                      {endpoint}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {incident.affected_database_tables.length > 0 && (
              <div>
                <div style={{ fontSize: '0.75rem', color: '#6a6e73', marginBottom: '0.5rem', textTransform: 'uppercase', fontWeight: 600 }}>
                  Database Tables
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                  {incident.affected_database_tables.map((table, index) => (
                    <span key={index} style={{
                      fontSize: '0.875rem',
                      color: '#0066cc',
                      fontFamily: 'monospace',
                      padding: '0.25rem 0.5rem',
                      backgroundColor: '#f0f0f0',
                      borderRadius: '3px',
                      display: 'inline-block'
                    }}>
                      {table}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Related Findings */}
        <div>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#151515', marginBottom: '0.75rem' }}>
            Related Findings
          </h3>
          <div style={{
            fontSize: '0.875rem',
            color: '#6a6e73',
            backgroundColor: '#f5f5f5',
            padding: '0.75rem 1rem',
            borderRadius: '3px',
            border: '1px solid #d2d2d2'
          }}>
            {incident.findings.length} findings correlated into this incident
          </div>
        </div>
      </div>
    </div>
  );
}

// Made with Bob
