import { FileText, Download } from 'lucide-react';

interface ReportViewerProps {
  report: string | null;
}

export default function ReportViewer({ report }: ReportViewerProps) {
  if (!report) {
    return (
      <div style={{
        backgroundColor: '#161b22',
        border: '1px solid #30363d',
        borderRadius: '8px',
        padding: '2rem',
        textAlign: 'center',
        color: '#8b949e'
      }}>
        No incident report available
      </div>
    );
  }

  // Simple markdown-like rendering
  const renderMarkdown = (text: string) => {
    const lines = text.split('\n');
    const elements: JSX.Element[] = [];
    
    lines.forEach((line, index) => {
      if (line.startsWith('## ')) {
        elements.push(
          <h2 key={index} style={{ 
            fontSize: '1.5rem', 
            fontWeight: 600, 
            color: '#e6edf3', 
            marginTop: index > 0 ? '2rem' : '0',
            marginBottom: '1rem',
            borderBottom: '1px solid #30363d',
            paddingBottom: '0.5rem'
          }}>
            {line.replace('## ', '')}
          </h2>
        );
      } else if (line.startsWith('### ')) {
        elements.push(
          <h3 key={index} style={{ 
            fontSize: '1.25rem', 
            fontWeight: 600, 
            color: '#e6edf3', 
            marginTop: '1.5rem',
            marginBottom: '0.75rem'
          }}>
            {line.replace('### ', '')}
          </h3>
        );
      } else if (line.startsWith('#### ')) {
        elements.push(
          <h4 key={index} style={{ 
            fontSize: '1.125rem', 
            fontWeight: 600, 
            color: '#e6edf3', 
            marginTop: '1rem',
            marginBottom: '0.5rem'
          }}>
            {line.replace('#### ', '')}
          </h4>
        );
      } else if (line.startsWith('**') && line.endsWith('**')) {
        elements.push(
          <p key={index} style={{ 
            fontSize: '0.875rem', 
            color: '#e6edf3', 
            margin: '0.5rem 0',
            fontWeight: 600
          }}>
            {line.replace(/\*\*/g, '')}
          </p>
        );
      } else if (line.startsWith('- ')) {
        elements.push(
          <li key={index} style={{ 
            fontSize: '0.875rem', 
            color: '#8b949e', 
            marginLeft: '1.5rem',
            marginBottom: '0.25rem',
            lineHeight: '1.6'
          }}>
            {line.replace('- ', '')}
          </li>
        );
      } else if (line.startsWith('1. ') || line.match(/^\d+\. /)) {
        elements.push(
          <li key={index} style={{ 
            fontSize: '0.875rem', 
            color: '#8b949e', 
            marginLeft: '1.5rem',
            marginBottom: '0.25rem',
            lineHeight: '1.6',
            listStyleType: 'decimal'
          }}>
            {line.replace(/^\d+\. /, '')}
          </li>
        );
      } else if (line.startsWith('---')) {
        elements.push(
          <hr key={index} style={{ 
            border: 'none',
            borderTop: '1px solid #30363d',
            margin: '1.5rem 0'
          }} />
        );
      } else if (line.trim() === '') {
        elements.push(<div key={index} style={{ height: '0.5rem' }} />);
      } else if (line.trim()) {
        elements.push(
          <p key={index} style={{ 
            fontSize: '0.875rem', 
            color: '#8b949e', 
            margin: '0.5rem 0',
            lineHeight: '1.6'
          }}>
            {line}
          </p>
        );
      }
    });

    return elements;
  };

  const handleDownload = () => {
    const blob = new Blob([report], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'incident-report.md';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
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
          <FileText size={20} color="#58a6ff" />
          <h2 style={{ fontSize: '1.125rem', fontWeight: 600, color: '#e6edf3', margin: 0 }}>
            Incident Report
          </h2>
        </div>
        <button
          onClick={handleDownload}
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
          <Download size={16} />
          Download Report
        </button>
      </div>
      
      <div style={{
        padding: '1.5rem',
        maxHeight: '600px',
        overflowY: 'auto'
      }}>
        {renderMarkdown(report)}
      </div>
    </div>
  );
}

// Made with Bob
