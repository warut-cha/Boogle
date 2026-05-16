import { Brain, Target, Shield, Wrench, FileCode } from 'lucide-react';
import type { BobOutput } from '../api/types';

interface BobAnalysisProps {
  bobOutput: BobOutput | null;
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

const getFixTypeIcon = (type: string) => {
  switch (type) {
    case 'immediate_action': return '🚨';
    case 'code_fix': return '💻';
    case 'api_fix': return '🌐';
    case 'config_fix': return '⚙️';
    case 'test_fix': return '🧪';
    default: return '🔧';
  }
};

export default function BobAnalysis({ bobOutput }: BobAnalysisProps) {
  if (!bobOutput) {
    return (
      <div style={{
        backgroundColor: '#161b22',
        border: '1px solid #30363d',
        borderRadius: '8px',
        padding: '2rem',
        textAlign: 'center'
      }}>
        <Brain size={48} color="#8b949e" style={{ margin: '0 auto 1rem' }} />
        <p style={{ color: '#8b949e', margin: 0 }}>
          No IBM Bob analysis available yet
        </p>
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
        padding: '1.5rem',
        borderBottom: '1px solid #30363d',
        background: 'linear-gradient(135deg, #161b22 0%, #1c2128 100%)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
          <Brain size={24} color="#58a6ff" />
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#e6edf3', margin: 0 }}>
            IBM Bob AI Analysis
          </h2>
        </div>
        <p style={{ fontSize: '0.875rem', color: '#8b949e', margin: 0 }}>
          Advanced reasoning and automated remediation recommendations
        </p>
      </div>

      <div style={{ padding: '1.5rem' }}>
        {/* Attack Type & Target */}
        <div style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <Shield size={18} color="#f85149" />
                <span style={{ fontSize: '0.875rem', fontWeight: 600, color: '#8b949e', textTransform: 'uppercase' }}>
                  Attack Type
                </span>
              </div>
              <p style={{ fontSize: '1rem', color: '#e6edf3', margin: 0, fontWeight: 500 }}>
                {bobOutput.attack_type}
              </p>
            </div>

            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <Target size={18} color="#d29922" />
                <span style={{ fontSize: '0.875rem', fontWeight: 600, color: '#8b949e', textTransform: 'uppercase' }}>
                  Target
                </span>
              </div>
              <p style={{ fontSize: '1rem', color: '#e6edf3', margin: 0, fontWeight: 500 }}>
                {bobOutput.target}
              </p>
            </div>
          </div>
        </div>

        {/* Confidence Assessment */}
        <div style={{ marginBottom: '2rem' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#e6edf3', marginBottom: '0.75rem' }}>
            Confidence Assessment
          </h3>
          <div style={{
            padding: '1rem',
            backgroundColor: '#0d1117',
            border: '1px solid #30363d',
            borderRadius: '6px',
            borderLeft: `4px solid ${getSeverityColor(bobOutput.severity)}`
          }}>
            <p style={{ fontSize: '0.875rem', color: '#e6edf3', margin: 0, lineHeight: '1.6' }}>
              {bobOutput.confidence_assessment}
            </p>
          </div>
        </div>

        {/* Recommended Fixes */}
        <div style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <Wrench size={18} color="#56d364" />
            <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#e6edf3', margin: 0 }}>
              Recommended Fixes
            </h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {bobOutput.recommended_fixes.map((fix, index) => (
              <div
                key={index}
                style={{
                  padding: '1rem',
                  backgroundColor: '#0d1117',
                  border: '1px solid #30363d',
                  borderRadius: '6px',
                  display: 'flex',
                  gap: '0.75rem'
                }}
              >
                <div style={{ fontSize: '1.25rem', flexShrink: 0 }}>
                  {getFixTypeIcon(fix.type)}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    color: '#8b949e',
                    textTransform: 'uppercase',
                    marginBottom: '0.25rem'
                  }}>
                    {fix.type.replace(/_/g, ' ')}
                  </div>
                  <p style={{ fontSize: '0.875rem', color: '#e6edf3', margin: 0, lineHeight: '1.5' }}>
                    {fix.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Generated Security Tests */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <FileCode size={18} color="#a371f7" />
            <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#e6edf3', margin: 0 }}>
              Generated Security Tests
            </h3>
          </div>
          <div style={{
            padding: '1rem',
            backgroundColor: '#0d1117',
            border: '1px solid #30363d',
            borderRadius: '6px'
          }}>
            <div style={{ fontSize: '0.875rem', color: '#8b949e', marginBottom: '0.5rem' }}>
              {bobOutput.generated_security_tests.length} test{bobOutput.generated_security_tests.length !== 1 ? 's' : ''} generated to prevent regression
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {bobOutput.generated_security_tests.map((test, index) => (
                <div
                  key={index}
                  style={{
                    padding: '0.75rem',
                    backgroundColor: '#161b22',
                    borderRadius: '4px',
                    border: '1px solid #21262d'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '0.5rem' }}>
                    <div>
                      <div style={{
                        fontSize: '0.875rem',
                        fontWeight: 600,
                        color: '#58a6ff',
                        fontFamily: 'monospace',
                        marginBottom: '0.25rem'
                      }}>
                        {test.name}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#8b949e' }}>
                        {test.purpose}
                      </div>
                    </div>
                    <div style={{
                      fontSize: '0.75rem',
                      color: '#8b949e',
                      fontFamily: 'monospace',
                      backgroundColor: '#21262d',
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px'
                    }}>
                      {test.file}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Made with Bob
