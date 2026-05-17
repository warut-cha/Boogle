import { useState } from 'react';
import { apiClient } from '../api/client';

interface ScanInputProps {
  onScanComplete: (result: { findings_count: number; incidents_count: number }) => void;
}

export default function ScanInput({ onScanComplete }: ScanInputProps) {
  const [scanPath, setScanPath] = useState(() => localStorage.getItem('lastScanPath') || '');
  const [isScanning, setIsScanning] = useState(false);
  const [scanResult, setScanResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleScan = async () => {
    if (!scanPath.trim()) {
      setError('Please enter a path to scan');
      return;
    }

    localStorage.setItem('lastScanPath', scanPath);
    
    setIsScanning(true);
    setError(null);
    setScanResult(null);

    try {
      const result = await apiClient.runScan({
        paths: [scanPath],
        use_mock: false,
        use_bob: true
      });

      setScanResult(result);
      onScanComplete({
        findings_count: result.findings_count || 0,
        incidents_count: result.incidents_count || 0
      });
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Scan failed');
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div style={{
      backgroundColor: '#161b22',
      border: '1px solid #30363d',
      borderRadius: '6px',
      padding: '1.5rem',
      marginBottom: '2rem'
    }}>
      <h2 style={{
        fontSize: '1.25rem',
        fontWeight: 600,
        color: '#e6edf3',
        marginBottom: '1rem'
      }}>
        🔍 Scan Repository
      </h2>

      <div style={{ marginBottom: '1rem' }}>
        <label style={{
          display: 'block',
          fontSize: '0.875rem',
          fontWeight: 500,
          color: '#8b949e',
          marginBottom: '0.5rem'
        }}>
          Repository Path
        </label>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <input
            type="text"
            value={scanPath}
            onChange={(e) => setScanPath(e.target.value)}
            placeholder="Enter path to scan (e.g., ./mock-repos or /path/to/your/repo)"
            disabled={isScanning}
            style={{
              flex: 1,
              padding: '0.5rem 0.75rem',
              backgroundColor: '#0d1117',
              border: '1px solid #30363d',
              borderRadius: '6px',
              color: '#e6edf3',
              fontSize: '0.875rem',
              outline: 'none'
            }}
            onFocus={(e) => e.target.style.borderColor = '#58a6ff'}
            onBlur={(e) => e.target.style.borderColor = '#30363d'}
          />
          <button
            onClick={handleScan}
            disabled={isScanning}
            style={{
              padding: '0.5rem 1.5rem',
              backgroundColor: isScanning ? '#30363d' : '#238636',
              color: '#ffffff',
              border: 'none',
              borderRadius: '6px',
              fontSize: '0.875rem',
              fontWeight: 600,
              cursor: isScanning ? 'not-allowed' : 'pointer',
              transition: 'background-color 0.2s',
              whiteSpace: 'nowrap'
            }}
            onMouseOver={(e) => {
              if (!isScanning) e.currentTarget.style.backgroundColor = '#2ea043';
            }}
            onMouseOut={(e) => {
              if (!isScanning) e.currentTarget.style.backgroundColor = '#238636';
            }}
          >
            {isScanning ? '⏳ Scanning...' : '🚀 Scan Now'}
          </button>
        </div>
        <p style={{
          fontSize: '0.75rem',
          color: '#8b949e',
          marginTop: '0.5rem'
        }}>
          Enter a relative path (e.g., ./mock-repos) or absolute path (e.g., /Users/you/project)
        </p>
      </div>

      {isScanning && (
        <div style={{
          padding: '1rem',
          backgroundColor: '#0d1117',
          border: '1px solid #30363d',
          borderRadius: '6px',
          marginTop: '1rem'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            color: '#58a6ff'
          }}>
            <div style={{
              width: '20px',
              height: '20px',
              border: '3px solid #30363d',
              borderTopColor: '#58a6ff',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite'
            }} />
            <span style={{ fontSize: '0.875rem' }}>
              Running security analysis pipeline...
            </span>
          </div>
          <div style={{
            marginTop: '0.75rem',
            fontSize: '0.75rem',
            color: '#8b949e',
            lineHeight: '1.5'
          }}>
            <div>→ Scanning for security findings...</div>
            <div>→ Correlating into incidents...</div>
            <div>→ Running Bob AI analysis...</div>
          </div>
        </div>
      )}

      {error && (
        <div style={{
          padding: '1rem',
          backgroundColor: '#1c1917',
          border: '1px solid #f85149',
          borderRadius: '6px',
          marginTop: '1rem'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'flex-start',
            gap: '0.75rem'
          }}>
            <span style={{ color: '#f85149', fontSize: '1.25rem' }}>⚠️</span>
            <div>
              <div style={{
                fontSize: '0.875rem',
                fontWeight: 600,
                color: '#f85149',
                marginBottom: '0.25rem'
              }}>
                Scan Failed
              </div>
              <div style={{
                fontSize: '0.875rem',
                color: '#e6edf3'
              }}>
                {error}
              </div>
            </div>
          </div>
        </div>
      )}

      {scanResult && !isScanning && (
        <div style={{
          padding: '1rem',
          backgroundColor: '#0d1117',
          border: '1px solid #238636',
          borderRadius: '6px',
          marginTop: '1rem'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'flex-start',
            gap: '0.75rem'
          }}>
            <span style={{ color: '#3fb950', fontSize: '1.25rem' }}>✅</span>
            <div style={{ flex: 1 }}>
              <div style={{
                fontSize: '0.875rem',
                fontWeight: 600,
                color: '#3fb950',
                marginBottom: '0.5rem'
              }}>
                Scan Complete!
              </div>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: '1rem',
                fontSize: '0.875rem',
                color: '#e6edf3'
              }}>
                <div>
                  <div style={{ color: '#8b949e', marginBottom: '0.25rem' }}>Findings</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 600, color: '#58a6ff' }}>
                    {scanResult.findings_count || 0}
                  </div>
                </div>
                <div>
                  <div style={{ color: '#8b949e', marginBottom: '0.25rem' }}>Incidents</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 600, color: '#f85149' }}>
                    {scanResult.incidents_count || 0}
                  </div>
                </div>
                <div>
                  <div style={{ color: '#8b949e', marginBottom: '0.25rem' }}>Bob Analyses</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 600, color: '#3fb950' }}>
                    {scanResult.bob_analysis_count || 0}
                  </div>
                </div>
              </div>
              <div style={{
                marginTop: '0.75rem',
                padding: '0.5rem',
                backgroundColor: '#161b22',
                borderRadius: '4px',
                fontSize: '0.75rem',
                color: '#8b949e'
              }}>
                💡 Refresh the page or switch tabs to see the new results
              </div>
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

// Made with Bob