import { GitPullRequest, GitBranch, FileText, Copy, CheckCircle } from 'lucide-react';
import { useState } from 'react';
import type { PRDraft } from '../api/types';

interface PRDraftViewerProps {
  prDraft: PRDraft | null;
}

export default function PRDraftViewer({ prDraft }: PRDraftViewerProps) {
  const [copied, setCopied] = useState(false);

  if (!prDraft) {
    return (
      <div style={{
        backgroundColor: '#161b22',
        border: '1px solid #30363d',
        borderRadius: '8px',
        padding: '2rem',
        textAlign: 'center',
        color: '#8b949e'
      }}>
        No PR draft available
      </div>
    );
  }

  const handleCopyDescription = () => {
    navigator.clipboard.writeText(prDraft.pr_description);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

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
          <GitPullRequest size={20} color="#56d364" />
          <h2 style={{ fontSize: '1.125rem', fontWeight: 600, color: '#e6edf3', margin: 0 }}>
            Pull Request Draft
          </h2>
        </div>
        <button
          onClick={handleCopyDescription}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.5rem 1rem',
            backgroundColor: '#21262d',
            border: '1px solid #30363d',
            borderRadius: '6px',
            color: '#e6edf3',
            fontSize: '0.875rem',
            cursor: 'pointer',
            transition: 'background-color 0.2s'
          }}
          onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#30363d'}
          onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#21262d'}
        >
          {copied ? (
            <>
              <CheckCircle size={16} color="#56d364" />
              Copied!
            </>
          ) : (
            <>
              <Copy size={16} />
              Copy Description
            </>
          )}
        </button>
      </div>

      <div style={{ padding: '1.5rem' }}>
        {/* Branch Name */}
        <div style={{ marginBottom: '1.5rem' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            marginBottom: '0.5rem'
          }}>
            <GitBranch size={16} color="#58a6ff" />
            <span style={{
              fontSize: '0.875rem',
              fontWeight: 600,
              color: '#8b949e',
              textTransform: 'uppercase'
            }}>
              Branch Name
            </span>
          </div>
          <div style={{
            padding: '0.75rem 1rem',
            backgroundColor: '#0d1117',
            border: '1px solid #30363d',
            borderRadius: '6px',
            fontFamily: 'monospace',
            fontSize: '0.875rem',
            color: '#58a6ff'
          }}>
            {prDraft.branch_name}
          </div>
        </div>

        {/* PR Title */}
        <div style={{ marginBottom: '1.5rem' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            marginBottom: '0.5rem'
          }}>
            <FileText size={16} color="#56d364" />
            <span style={{
              fontSize: '0.875rem',
              fontWeight: 600,
              color: '#8b949e',
              textTransform: 'uppercase'
            }}>
              PR Title
            </span>
          </div>
          <div style={{
            padding: '0.75rem 1rem',
            backgroundColor: '#0d1117',
            border: '1px solid #30363d',
            borderRadius: '6px',
            fontSize: '1rem',
            fontWeight: 600,
            color: '#e6edf3'
          }}>
            {prDraft.pr_title}
          </div>
        </div>

        {/* PR Description */}
        <div style={{ marginBottom: '1.5rem' }}>
          <div style={{
            fontSize: '0.875rem',
            fontWeight: 600,
            color: '#8b949e',
            textTransform: 'uppercase',
            marginBottom: '0.5rem'
          }}>
            PR Description
          </div>
          <div style={{
            padding: '1rem',
            backgroundColor: '#0d1117',
            border: '1px solid #30363d',
            borderRadius: '6px',
            fontSize: '0.875rem',
            color: '#8b949e',
            lineHeight: '1.6',
            whiteSpace: 'pre-wrap',
            fontFamily: 'monospace',
            maxHeight: '400px',
            overflowY: 'auto'
          }}>
            {prDraft.pr_description}
          </div>
        </div>

        {/* Files to Change */}
        <div>
          <div style={{
            fontSize: '0.875rem',
            fontWeight: 600,
            color: '#8b949e',
            textTransform: 'uppercase',
            marginBottom: '0.5rem'
          }}>
            Files to Change ({prDraft.files_to_change.length})
          </div>
          <div style={{
            padding: '1rem',
            backgroundColor: '#0d1117',
            border: '1px solid #30363d',
            borderRadius: '6px'
          }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {prDraft.files_to_change.map((file, index) => (
                <div
                  key={index}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    padding: '0.5rem 0.75rem',
                    backgroundColor: '#161b22',
                    borderRadius: '4px',
                    border: '1px solid #21262d'
                  }}
                >
                  <div style={{
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    backgroundColor: file.includes('test') ? '#56d364' : '#d29922',
                    flexShrink: 0
                  }} />
                  <span style={{
                    fontSize: '0.875rem',
                    color: '#e6edf3',
                    fontFamily: 'monospace'
                  }}>
                    {file}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{
          marginTop: '1.5rem',
          padding: '1rem',
          backgroundColor: '#0d1117',
          border: '1px solid #30363d',
          borderRadius: '6px',
          display: 'flex',
          gap: '1rem',
          alignItems: 'center'
        }}>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: '0.875rem', fontWeight: 600, color: '#e6edf3', marginBottom: '0.25rem' }}>
              Ready to Create PR
            </div>
            <div style={{ fontSize: '0.75rem', color: '#8b949e' }}>
              Review the changes and create a pull request in your repository
            </div>
          </div>
          <button
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#238636',
              border: 'none',
              borderRadius: '6px',
              color: '#ffffff',
              fontSize: '0.875rem',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'background-color 0.2s',
              whiteSpace: 'nowrap'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#2ea043'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#238636'}
          >
            Create PR →
          </button>
        </div>
      </div>
    </div>
  );
}

// Made with Bob
