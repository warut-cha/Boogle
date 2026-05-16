import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../api/client';
import type { Incident, Finding, BobOutput } from '../api/types';
import { useRealtimeMonitoring } from '../hooks/useRealtimeMonitoring';
import OverviewCards from '../components/OverviewCards';
import FindingsTable from '../components/FindingsTable';
import IncidentDetail from '../components/IncidentDetail';
import AttackPathGraph from '../components/AttackPathGraph';
import BobAnalysis from '../components/BobAnalysis';
import ReportViewer from '../components/ReportViewer';
import MemoryViewer from '../components/MemoryViewer';
import PRDraftViewer from '../components/PRDraftViewer';
import { Wifi, WifiOff, Bell } from 'lucide-react';

export default function DashboardPage() {
  const [findings, setFindings] = useState<Finding[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [bobOutput, setBobOutput] = useState<BobOutput | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'findings' | 'incident' | 'analysis'>('overview');
  const [showNotification, setShowNotification] = useState(false);
  const [notificationMessage, setNotificationMessage] = useState('');

  // Real-time monitoring callbacks
  const handleNewFinding = useCallback((finding: Finding) => {
    setFindings(prev => [finding, ...prev]);
    setNotificationMessage(`New ${finding.severity_hint} severity finding detected!`);
    setShowNotification(true);
    setTimeout(() => setShowNotification(false), 5000);
  }, []);

  const handleNewIncident = useCallback((incident: Incident) => {
    setIncidents(prev => [incident, ...prev]);
    // Set as selected incident if none is selected
    setSelectedIncident(prev => prev || incident);
    setNotificationMessage(`New ${incident.severity} incident: ${incident.title}`);
    setShowNotification(true);
    setTimeout(() => setShowNotification(false), 5000);
  }, []);

  const handleBobAnalysis = useCallback((incidentId: string, analysis: BobOutput) => {
    setBobOutput(analysis);
    setNotificationMessage('Bob AI analysis completed!');
    setShowNotification(true);
    setTimeout(() => setShowNotification(false), 5000);
  }, []);

  // Initialize real-time monitoring
  const { isConnected, newFindings, newIncidents, clearNewFindings, clearNewIncidents, reconnect } =
    useRealtimeMonitoring(handleNewFinding, handleNewIncident, handleBobAnalysis);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [findingsData, incidentsData] = await Promise.all([
        apiClient.getFindings(),
        apiClient.getIncidents()
      ]);
      
      setFindings(findingsData);
      setIncidents(incidentsData);
      
      if (incidentsData.length > 0) {
        setSelectedIncident(incidentsData[0]);
        // Auto-load Bob analysis for the first incident
        const bobData = await apiClient.getBobAnalysis(incidentsData[0].incident_id);
        setBobOutput(bobData);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '80vh',
        color: '#8b949e'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            width: '48px',
            height: '48px',
            border: '4px solid #30363d',
            borderTopColor: '#58a6ff',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 1rem'
          }} />
          <p>Loading Bob Sentinel Dashboard...</p>
        </div>
      </div>
    );
  }

  const handleTriggerScan = async () => {
    try {
      setNotificationMessage('Starting security scan...');
      setShowNotification(true);
      
      const result = await apiClient.triggerScan(['./mock-repos'], true, true);
      
      setNotificationMessage('Scan started! Watch for real-time updates...');
      setTimeout(() => setShowNotification(false), 3000);
      
      console.log('Scan triggered:', result);
    } catch (error) {
      console.error('Failed to trigger scan:', error);
      setNotificationMessage('Failed to start scan. Check backend connection.');
      setTimeout(() => setShowNotification(false), 5000);
    }
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '1600px', margin: '0 auto' }}>
      {/* Real-time Status Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '1rem',
        padding: '0.75rem 1rem',
        backgroundColor: '#161b22',
        border: '1px solid #30363d',
        borderRadius: '8px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            {isConnected ? (
              <>
                <Wifi size={16} style={{ color: '#56d364' }} />
                <span style={{ fontSize: '0.875rem', color: '#56d364', fontWeight: 500 }}>
                  Real-time Monitoring Active
                </span>
              </>
            ) : (
              <>
                <WifiOff size={16} style={{ color: '#f85149' }} />
                <span style={{ fontSize: '0.875rem', color: '#f85149', fontWeight: 500 }}>
                  Disconnected
                </span>
                <button
                  onClick={reconnect}
                  style={{
                    padding: '0.25rem 0.75rem',
                    backgroundColor: '#21262d',
                    border: '1px solid #30363d',
                    borderRadius: '4px',
                    color: '#58a6ff',
                    fontSize: '0.75rem',
                    cursor: 'pointer'
                  }}
                >
                  Reconnect
                </button>
              </>
            )}
          </div>
          {(newFindings.length > 0 || newIncidents.length > 0) && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Bell size={16} style={{ color: '#d29922' }} />
              <span style={{ fontSize: '0.875rem', color: '#d29922' }}>
                {newFindings.length > 0 && `${newFindings.length} new finding${newFindings.length > 1 ? 's' : ''}`}
                {newFindings.length > 0 && newIncidents.length > 0 && ', '}
                {newIncidents.length > 0 && `${newIncidents.length} new incident${newIncidents.length > 1 ? 's' : ''}`}
              </span>
              <button
                onClick={() => {
                  clearNewFindings();
                  clearNewIncidents();
                }}
                style={{
                  padding: '0.25rem 0.75rem',
                  backgroundColor: '#21262d',
                  border: '1px solid #30363d',
                  borderRadius: '4px',
                  color: '#8b949e',
                  fontSize: '0.75rem',
                  cursor: 'pointer'
                }}
              >
                Clear
              </button>
            </div>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button
            onClick={handleTriggerScan}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#238636',
              border: 'none',
              borderRadius: '6px',
              color: '#ffffff',
              fontSize: '0.875rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              transition: 'background-color 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#2ea043'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#238636'}
          >
            <span>🔍</span>
            Run Security Scan
          </button>
          <div style={{ fontSize: '0.75rem', color: '#8b949e' }}>
            Last updated: {new Date().toLocaleTimeString()}
          </div>
        </div>
      </div>

      {/* Notification Toast */}
      {showNotification && (
        <div style={{
          position: 'fixed',
          top: '2rem',
          right: '2rem',
          padding: '1rem 1.5rem',
          backgroundColor: '#161b22',
          border: '1px solid #58a6ff',
          borderRadius: '8px',
          boxShadow: '0 8px 24px rgba(0, 0, 0, 0.5)',
          zIndex: 1000,
          animation: 'slideIn 0.3s ease-out'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <Bell size={20} style={{ color: '#58a6ff' }} />
            <span style={{ color: '#e6edf3', fontSize: '0.875rem' }}>
              {notificationMessage}
            </span>
          </div>
        </div>
      )}

      {/* Navigation Tabs */}
      <div style={{
        display: 'flex',
        gap: '0.5rem',
        marginBottom: '2rem',
        borderBottom: '1px solid #30363d',
        paddingBottom: '0'
      }}>
        {[
          { id: 'overview', label: 'Overview' },
          { id: 'findings', label: 'Findings' },
          { id: 'incident', label: 'Incident Analysis' },
          { id: 'analysis', label: 'Bob AI Analysis' }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as typeof activeTab)}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: 'transparent',
              border: 'none',
              borderBottom: activeTab === tab.id ? '2px solid #58a6ff' : '2px solid transparent',
              color: activeTab === tab.id ? '#58a6ff' : '#8b949e',
              fontSize: '0.875rem',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s',
              marginBottom: '-1px'
            }}
            onMouseOver={(e) => {
              if (activeTab !== tab.id) {
                e.currentTarget.style.color = '#e6edf3';
              }
            }}
            onMouseOut={(e) => {
              if (activeTab !== tab.id) {
                e.currentTarget.style.color = '#8b949e';
              }
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div>
          <OverviewCards
            incidents={incidents}
            findings={findings}
            bobAnalysisGenerated={bobOutput !== null}
          />
          
          <div style={{ marginBottom: '2rem' }}>
            <h2 style={{
              fontSize: '1.25rem',
              fontWeight: 600,
              color: '#e6edf3',
              marginBottom: '1rem'
            }}>
              Recent Findings
            </h2>
            <FindingsTable findings={findings.slice(0, 5)} />
          </div>

          {selectedIncident && (
            <div style={{ marginBottom: '2rem' }}>
              <h2 style={{
                fontSize: '1.25rem',
                fontWeight: 600,
                color: '#e6edf3',
                marginBottom: '1rem'
              }}>
                Critical Incident
              </h2>
              <IncidentDetail incident={selectedIncident} />
            </div>
          )}
        </div>
      )}

      {/* Findings Tab */}
      {activeTab === 'findings' && (
        <div>
          <h2 style={{
            fontSize: '1.5rem',
            fontWeight: 600,
            color: '#e6edf3',
            marginBottom: '1.5rem'
          }}>
            All Security Findings
          </h2>
          <FindingsTable findings={findings} />
        </div>
      )}

      {/* Incident Analysis Tab */}
      {activeTab === 'incident' && (
        <div>
          <h2 style={{
            fontSize: '1.5rem',
            fontWeight: 600,
            color: '#e6edf3',
            marginBottom: '1.5rem'
          }}>
            Incident Analysis
          </h2>
          
          {selectedIncident ? (
            <>
              <div style={{ marginBottom: '2rem' }}>
                <IncidentDetail incident={selectedIncident} />
              </div>

              <div style={{ marginBottom: '2rem' }}>
                <h3 style={{
                  fontSize: '1.25rem',
                  fontWeight: 600,
                  color: '#e6edf3',
                  marginBottom: '1rem'
                }}>
                  Attack Path
                </h3>
                <AttackPathGraph attackPath={selectedIncident.attack_path} />
              </div>

              <div style={{ marginBottom: '2rem' }}>
                <h3 style={{
                  fontSize: '1.25rem',
                  fontWeight: 600,
                  color: '#e6edf3',
                  marginBottom: '1rem'
                }}>
                  Related Findings
                </h3>
                <FindingsTable findings={selectedIncident.findings} />
              </div>

              {selectedIncident.related_memory.length > 0 && (
                <div>
                  <h3 style={{
                    fontSize: '1.25rem',
                    fontWeight: 600,
                    color: '#e6edf3',
                    marginBottom: '1rem'
                  }}>
                    AI Memory Patterns
                  </h3>
                  <MemoryViewer memories={selectedIncident.related_memory} />
                </div>
              )}
            </>
          ) : (
            <div style={{
              backgroundColor: '#161b22',
              border: '1px solid #30363d',
              borderRadius: '8px',
              padding: '3rem',
              textAlign: 'center',
              color: '#8b949e'
            }}>
              <p style={{ fontSize: '1.125rem', marginBottom: '0.5rem' }}>No incidents detected yet</p>
              <p style={{ fontSize: '0.875rem' }}>Run a security scan to detect and correlate security incidents</p>
            </div>
          )}
        </div>
      )}

      {/* Bob AI Analysis Tab */}
      {activeTab === 'analysis' && (
        <div>
          <h2 style={{
            fontSize: '1.5rem',
            fontWeight: 600,
            color: '#e6edf3',
            marginBottom: '1.5rem'
          }}>
            IBM Bob AI Analysis & Remediation
          </h2>

          <div style={{ marginBottom: '2rem' }}>
            <BobAnalysis bobOutput={bobOutput} />
          </div>

          {bobOutput && (
            <>
              <div style={{ marginBottom: '2rem' }}>
                <h3 style={{
                  fontSize: '1.25rem',
                  fontWeight: 600,
                  color: '#e6edf3',
                  marginBottom: '1rem'
                }}>
                  Incident Report
                </h3>
                <ReportViewer report={bobOutput.incident_report} />
              </div>

              <div style={{ marginBottom: '2rem' }}>
                <h3 style={{
                  fontSize: '1.25rem',
                  fontWeight: 600,
                  color: '#e6edf3',
                  marginBottom: '1rem'
                }}>
                  AI Memory Created
                </h3>
                <MemoryViewer memories={[bobOutput.ai_memory]} />
              </div>

              <div>
                <h3 style={{
                  fontSize: '1.25rem',
                  fontWeight: 600,
                  color: '#e6edf3',
                  marginBottom: '1rem'
                }}>
                  Pull Request Draft
                </h3>
                <PRDraftViewer prDraft={bobOutput.pr_draft} />
              </div>
            </>
          )}
        </div>
      )}

      {/* Add CSS animations */}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        @keyframes slideIn {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
}

// Made with Bob
