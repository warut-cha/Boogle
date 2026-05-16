import { AlertTriangle, CheckCircle, XCircle, TrendingUp } from 'lucide-react';
import type { Incident } from '../api/types';
import { getSeverityColor } from '../utils/severity';

interface IncidentDetailProps {
  incident: Incident;
}

export default function IncidentDetail({ incident }: IncidentDetailProps) {
  const confidencePercentage = Math.round(incident.confidence_score * 100);

  return (
    <div style={{
      backgroundColor: '#161b22',
      border: '1px solid #30363d',
      borderRadius: '8px',
      overflow: 'hidden'
    }}>
      <div style={{
        padding: '1.5rem',
        borderBottom: '1px solid #30363d',
        backgroundColor: '#0d1117'
      }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem' }}>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
              <AlertTriangle size={24} color={getSeverityColor(incident.severity)} />
              <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#e6edf3', margin: 0 }}>
                {incident.title}
              </h2>
            </div>
            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
              <span style={{
                display: 'inline-block',
                padding: '0.25rem 0.75rem',
                borderRadius: '1rem',
                fontSize: '0.75rem',
                fontWeight: 600,
                textTransform: 'uppercase',
                backgroundColor: `${getSeverityColor(incident.severity)}20`,
                color: getSeverityColor(incident.severity)
              }}>
                {incident.severity} (Level {incident.severity_level})
              </span>
              <span style={{
                fontSize: '0.875rem',
                color: '#8b949e',
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
            <TrendingUp size={18} color="#a371f7" />
            <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#e6edf3', margin: 0 }}>
              Confidence Assessment
            </h3>
          </div>
          
          <div style={{ marginBottom: '1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '0.875rem', color: '#8b949e' }}>Confidence Score</span>
              <span style={{ fontSize: '0.875rem', fontWeight: 600, color: '#a371f7' }}>
                {confidencePercentage}%
              </span>
            </div>
            <div style={{
              width: '100%',
              height: '8px',
              backgroundColor: '#21262d',
              borderRadius: '4px',
              overflow: 'hidden'
            }}>
              <div style={{
                width: `${confidencePercentage}%`,
                height: '100%',
                backgroundColor: '#a371f7',
                transition: 'width 0.3s ease'
              }} />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <CheckCircle size={16} color="#56d364" />
                <span style={{ fontSize: '0.875rem', fontWeight: 600, color: '#e6edf3' }}>
                  Supporting Evidence
                </span>
              </div>
              <ul style={{ margin: 0, paddingLeft: '1.5rem', listStyle: 'disc' }}>
                {incident.confidence_reasons.map((reason, index) => (
                  <li key={index} style={{ fontSize: '0.875rem', color: '#8b949e', marginBottom: '0.25rem' }}>
                    {reason}
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <XCircle size={16} color="#f85149" />
                <span style={{ fontSize: '0.875rem', fontWeight: 600, color: '#e6edf3' }}>
                  Limitations
                </span>
              </div>
              <ul style={{ margin: 0, paddingLeft: '1.5rem', listStyle: 'disc' }}>
                {incident.confidence_limitations.map((limitation, index) => (
                  <li key={index} style={{ fontSize: '0.875rem', color: '#8b949e', marginBottom: '0.25rem' }}>
                    {limitation}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Affected Assets */}
        <div style={{ marginBottom: '2rem' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#e6edf3', marginBottom: '0.75rem' }}>
            Affected Assets
          </h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <div>
              <div style={{ fontSize: '0.75rem', color: '#8b949e', marginBottom: '0.5rem', textTransform: 'uppercase', fontWeight: 600 }}>
                Repositories
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                {incident.affected_repos.map((repo, index) => (
                  <span key={index} style={{
                    fontSize: '0.875rem',
                    color: '#58a6ff',
                    fontFamily: 'monospace',
                    padding: '0.25rem 0.5rem',
                    backgroundColor: '#21262d',
                    borderRadius: '4px',
                    display: 'inline-block'
                  }}>
                    {repo}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <div style={{ fontSize: '0.75rem', color: '#8b949e', marginBottom: '0.5rem', textTransform: 'uppercase', fontWeight: 600 }}>
                Files
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                {incident.affected_files.map((file, index) => (
                  <span key={index} style={{
                    fontSize: '0.875rem',
                    color: '#e6edf3',
                    fontFamily: 'monospace',
                    padding: '0.25rem 0.5rem',
                    backgroundColor: '#21262d',
                    borderRadius: '4px',
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
                <div style={{ fontSize: '0.75rem', color: '#8b949e', marginBottom: '0.5rem', textTransform: 'uppercase', fontWeight: 600 }}>
                  Endpoints
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                  {incident.affected_endpoints.map((endpoint, index) => (
                    <span key={index} style={{
                      fontSize: '0.875rem',
                      color: '#d29922',
                      fontFamily: 'monospace',
                      padding: '0.25rem 0.5rem',
                      backgroundColor: '#21262d',
                      borderRadius: '4px',
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
                <div style={{ fontSize: '0.75rem', color: '#8b949e', marginBottom: '0.5rem', textTransform: 'uppercase', fontWeight: 600 }}>
                  Database Tables
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                  {incident.affected_database_tables.map((table, index) => (
                    <span key={index} style={{
                      fontSize: '0.875rem',
                      color: '#a371f7',
                      fontFamily: 'monospace',
                      padding: '0.25rem 0.5rem',
                      backgroundColor: '#21262d',
                      borderRadius: '4px',
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
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#e6edf3', marginBottom: '0.75rem' }}>
            Related Findings
          </h3>
          <div style={{
            fontSize: '0.875rem',
            color: '#8b949e',
            backgroundColor: '#21262d',
            padding: '0.75rem 1rem',
            borderRadius: '6px',
            border: '1px solid #30363d'
          }}>
            {incident.findings.length} findings correlated into this incident
          </div>
        </div>
      </div>
    </div>
  );
}

// Made with Bob
