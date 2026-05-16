import { Database, AlertCircle, CheckCircle, TrendingUp } from 'lucide-react';
import type { AIMemory } from '../api/types';

interface MemoryViewerProps {
  memories: AIMemory[];
}

export default function MemoryViewer({ memories }: MemoryViewerProps) {
  if (memories.length === 0) {
    return (
      <div style={{
        backgroundColor: '#161b22',
        border: '1px solid #30363d',
        borderRadius: '8px',
        padding: '2rem',
        textAlign: 'center',
        color: '#8b949e'
      }}>
        No AI memory patterns available
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Database size={20} color="#a371f7" />
          <h2 style={{ fontSize: '1.125rem', fontWeight: 600, color: '#e6edf3', margin: 0 }}>
            AI Memory & Prevention Rules
          </h2>
        </div>
        <span style={{
          fontSize: '0.875rem',
          color: '#8b949e',
          backgroundColor: '#21262d',
          padding: '0.25rem 0.75rem',
          borderRadius: '1rem'
        }}>
          {memories.length} pattern{memories.length !== 1 ? 's' : ''}
        </span>
      </div>

      <div style={{ padding: '1.5rem' }}>
        {memories.map((memory, index) => (
          <div
            key={index}
            style={{
              marginBottom: index < memories.length - 1 ? '1.5rem' : 0,
              padding: '1.5rem',
              backgroundColor: '#0d1117',
              border: '1px solid #30363d',
              borderRadius: '8px',
              borderLeft: '4px solid #a371f7'
            }}
          >
            {/* Memory Type & Pattern */}
            <div style={{ marginBottom: '1rem' }}>
              <div style={{
                display: 'inline-block',
                padding: '0.25rem 0.75rem',
                borderRadius: '1rem',
                fontSize: '0.75rem',
                fontWeight: 600,
                textTransform: 'uppercase',
                backgroundColor: '#a371f720',
                color: '#a371f7',
                marginBottom: '0.5rem'
              }}>
                {memory.memory_type.replace(/_/g, ' ')}
              </div>
              <h3 style={{
                fontSize: '1rem',
                fontWeight: 600,
                color: '#e6edf3',
                margin: '0.5rem 0'
              }}>
                {memory.incident_pattern.replace(/_/g, ' ')}
              </h3>
            </div>

            {/* Root Cause */}
            <div style={{ marginBottom: '1rem' }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                marginBottom: '0.5rem'
              }}>
                <AlertCircle size={16} color="#f85149" />
                <span style={{
                  fontSize: '0.875rem',
                  fontWeight: 600,
                  color: '#e6edf3'
                }}>
                  Root Cause
                </span>
              </div>
              <p style={{
                fontSize: '0.875rem',
                color: '#8b949e',
                margin: 0,
                lineHeight: '1.6'
              }}>
                {memory.root_cause}
              </p>
            </div>

            {/* Signals to Watch */}
            <div style={{ marginBottom: '1rem' }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                marginBottom: '0.5rem'
              }}>
                <TrendingUp size={16} color="#d29922" />
                <span style={{
                  fontSize: '0.875rem',
                  fontWeight: 600,
                  color: '#e6edf3'
                }}>
                  Signals to Watch
                </span>
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {memory.signals_to_watch.map((signal, idx) => (
                  <span
                    key={idx}
                    style={{
                      fontSize: '0.75rem',
                      color: '#d29922',
                      backgroundColor: '#d2992220',
                      padding: '0.25rem 0.75rem',
                      borderRadius: '1rem',
                      border: '1px solid #d2992240'
                    }}
                  >
                    {signal}
                  </span>
                ))}
              </div>
            </div>

            {/* Prevention Rule */}
            <div style={{ marginBottom: '1rem' }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                marginBottom: '0.5rem'
              }}>
                <CheckCircle size={16} color="#56d364" />
                <span style={{
                  fontSize: '0.875rem',
                  fontWeight: 600,
                  color: '#e6edf3'
                }}>
                  Prevention Rule
                </span>
              </div>
              <p style={{
                fontSize: '0.875rem',
                color: '#8b949e',
                margin: 0,
                lineHeight: '1.6',
                padding: '0.75rem',
                backgroundColor: '#161b22',
                borderRadius: '4px',
                border: '1px solid #21262d'
              }}>
                {memory.prevention_rule}
              </p>
            </div>

            {/* Recommended Tests */}
            <div style={{ marginBottom: memory.severity_escalation_conditions ? '1rem' : 0 }}>
              <div style={{
                fontSize: '0.875rem',
                fontWeight: 600,
                color: '#e6edf3',
                marginBottom: '0.5rem'
              }}>
                Recommended Tests
              </div>
              <ul style={{
                margin: 0,
                paddingLeft: '1.5rem',
                listStyle: 'disc'
              }}>
                {memory.recommended_tests.map((test, idx) => (
                  <li
                    key={idx}
                    style={{
                      fontSize: '0.875rem',
                      color: '#8b949e',
                      marginBottom: '0.25rem',
                      lineHeight: '1.6'
                    }}
                  >
                    {test}
                  </li>
                ))}
              </ul>
            </div>

            {/* Severity Escalation Conditions */}
            {memory.severity_escalation_conditions && memory.severity_escalation_conditions.length > 0 && (
              <div>
                <div style={{
                  fontSize: '0.875rem',
                  fontWeight: 600,
                  color: '#e6edf3',
                  marginBottom: '0.5rem'
                }}>
                  Severity Escalation Conditions
                </div>
                <ul style={{
                  margin: 0,
                  paddingLeft: '1.5rem',
                  listStyle: 'disc'
                }}>
                  {memory.severity_escalation_conditions.map((condition, idx) => (
                    <li
                      key={idx}
                      style={{
                        fontSize: '0.875rem',
                        color: '#f85149',
                        marginBottom: '0.25rem',
                        lineHeight: '1.6'
                      }}
                    >
                      {condition}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// Made with Bob
