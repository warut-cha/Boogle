import { AlertCircle, Shield, Database, Activity, Server, FileText, Clock } from 'lucide-react';
import type { Finding } from '../api/types';
import { theme, getSeverityColor } from '../styles/theme';

interface FindingsTableProps {
  findings: Finding[];
}


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
        backgroundColor: theme.colors.background.primary,
        border: `1px solid ${theme.colors.border.subtle}`,
        borderRadius: theme.borderRadius.base,
        padding: theme.spacing[8],
        textAlign: 'center',
        color: theme.colors.text.secondary,
        boxShadow: theme.shadows.base,
      }}>
        <Shield size={48} color={theme.colors.gray[400]} style={{ margin: '0 auto 1rem' }} />
        <p style={{
          fontSize: theme.typography.fontSize.base,
          fontWeight: theme.typography.fontWeight.medium,
          margin: 0,
        }}>
          No findings detected
        </p>
        <p style={{
          fontSize: theme.typography.fontSize.sm,
          color: theme.colors.text.tertiary,
          marginTop: theme.spacing[2],
        }}>
          Run a security scan to detect vulnerabilities
        </p>
      </div>
    );
  }

  return (
    <div
      className="animate-fade-in"
      style={{
        backgroundColor: theme.colors.background.primary,
        border: `1px solid ${theme.colors.border.subtle}`,
        borderRadius: theme.borderRadius.base,
        overflow: 'hidden',
        boxShadow: theme.shadows.md,
        transition: `all ${theme.transitions.base}`,
      }}
    >
      <div style={{
        padding: `${theme.spacing[5]} ${theme.spacing[6]}`,
        borderBottom: `1px solid ${theme.colors.border.subtle}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: `linear-gradient(135deg, ${theme.colors.background.primary} 0%, ${theme.colors.background.secondary} 100%)`,
      }}>
        <h2 style={{
          fontSize: theme.typography.fontSize.lg,
          fontWeight: theme.typography.fontWeight.semibold,
          color: theme.colors.text.primary,
          margin: 0,
          display: 'flex',
          alignItems: 'center',
          gap: theme.spacing[2],
        }}>
          <AlertCircle size={20} color={theme.colors.primary[500]} />
          Recent Security Findings
        </h2>
        <span style={{
          fontSize: theme.typography.fontSize.xs,
          color: theme.colors.text.inverse,
          backgroundColor: theme.colors.primary[500],
          padding: `${theme.spacing[1]} ${theme.spacing[3]}`,
          borderRadius: theme.borderRadius.full,
          fontWeight: theme.typography.fontWeight.semibold,
          letterSpacing: theme.typography.letterSpacing.wide,
        }}>
          {findings.length} TOTAL
        </span>
      </div>
      
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{
              backgroundColor: theme.colors.background.secondary,
              borderBottom: `2px solid ${theme.colors.border.subtle}`
            }}>
              <th style={{
                padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
                textAlign: 'left',
                fontSize: theme.typography.fontSize.xs,
                fontWeight: theme.typography.fontWeight.semibold,
                color: theme.colors.text.secondary,
                textTransform: 'uppercase',
                letterSpacing: theme.typography.letterSpacing.wider,
              }}>
                Severity
              </th>
              <th style={{
                padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
                textAlign: 'left',
                fontSize: theme.typography.fontSize.xs,
                fontWeight: theme.typography.fontWeight.semibold,
                color: theme.colors.text.secondary,
                textTransform: 'uppercase',
                letterSpacing: theme.typography.letterSpacing.wider,
              }}>
                Finding Type & Evidence
              </th>
              <th style={{
                padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
                textAlign: 'left',
                fontSize: theme.typography.fontSize.xs,
                fontWeight: theme.typography.fontWeight.semibold,
                color: theme.colors.text.secondary,
                textTransform: 'uppercase',
                letterSpacing: theme.typography.letterSpacing.wider,
              }}>
                Detected
              </th>
              <th style={{
                padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
                textAlign: 'left',
                fontSize: theme.typography.fontSize.xs,
                fontWeight: theme.typography.fontWeight.semibold,
                color: theme.colors.text.secondary,
                textTransform: 'uppercase',
                letterSpacing: theme.typography.letterSpacing.wider,
              }}>
                Repository
              </th>
            </tr>
          </thead>
          <tbody>
            {findings.map((finding, index) => (
              <tr
                key={finding.finding_id}
                style={{
                  borderBottom: index < findings.length - 1 ? `1px solid ${theme.colors.border.subtle}` : 'none',
                  backgroundColor: theme.colors.background.primary,
                  transition: `all ${theme.transitions.fast}`,
                  cursor: 'pointer',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = theme.colors.background.secondary;
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = theme.colors.background.primary;
                }}
              >
                <td style={{ padding: theme.spacing[4] }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing[3] }}>
                    <div style={{
                      width: '40px',
                      height: '40px',
                      borderRadius: '50%',
                      backgroundColor: `${getSeverityColor(finding.severity_hint)}20`,
                      border: `2px solid ${getSeverityColor(finding.severity_hint)}`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: getSeverityColor(finding.severity_hint),
                      fontSize: theme.typography.fontSize.base,
                      fontWeight: theme.typography.fontWeight.semibold,
                    }}>
                      {getCategoryIcon(finding.category)}
                    </div>
                    <div>
                      <div style={{
                        fontSize: theme.typography.fontSize.sm,
                        color: theme.colors.text.primary,
                        fontWeight: theme.typography.fontWeight.semibold,
                        textTransform: 'capitalize',
                      }}>
                        {finding.severity_hint}
                      </div>
                      <div style={{
                        fontSize: theme.typography.fontSize.xs,
                        color: theme.colors.text.tertiary,
                      }}>
                        {finding.category.replace(/_/g, ' ')}
                      </div>
                    </div>
                  </div>
                </td>
                <td style={{ padding: theme.spacing[4] }}>
                  <div style={{
                    fontSize: theme.typography.fontSize.sm,
                    color: theme.colors.text.primary,
                    marginBottom: theme.spacing[1],
                    fontWeight: theme.typography.fontWeight.medium,
                  }}>
                    {finding.finding_type.replace(/_/g, ' ')}
                  </div>
                  <div style={{
                    fontSize: theme.typography.fontSize.xs,
                    color: theme.colors.text.secondary,
                    fontFamily: theme.typography.fontFamily.mono,
                    backgroundColor: theme.colors.background.secondary,
                    padding: `${theme.spacing[1]} ${theme.spacing[2]}`,
                    borderRadius: theme.borderRadius.sm,
                    display: 'inline-block',
                    maxWidth: '400px',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}>
                    {finding.evidence.substring(0, 60)}...
                  </div>
                </td>
                <td style={{
                  padding: theme.spacing[4],
                  fontSize: theme.typography.fontSize.sm,
                  color: theme.colors.text.secondary,
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing[2] }}>
                    <Clock size={14} color={theme.colors.text.tertiary} />
                    {new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                  </div>
                </td>
                <td style={{
                  padding: theme.spacing[4],
                  fontSize: theme.typography.fontSize.sm,
                  color: theme.colors.primary[500],
                  fontFamily: theme.typography.fontFamily.mono,
                  fontWeight: theme.typography.fontWeight.medium,
                }}>
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
