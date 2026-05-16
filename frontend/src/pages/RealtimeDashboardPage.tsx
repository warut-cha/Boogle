import { useState, useEffect } from 'react';
import { realtimeClient } from '../api/realtime-client';
import type { Incident, Finding, BobOutput, SSEEvent } from '../api/types';
import OverviewCards from '../components/OverviewCards';
import FindingsTable from '../components/FindingsTable';
import IncidentDetail from '../components/IncidentDetail';
import AttackPathGraph from '../components/AttackPathGraph';
import BobAnalysis from '../components/BobAnalysis';
import ReportViewer from '../components/ReportViewer';
import MemoryViewer from '../components/MemoryViewer';
import PRDraftViewer from '../components/PRDraftViewer';
import { Activity, Wifi, WifiOff, Play, Trash2 } from 'lucide-react';

export default function RealtimeDashboardPage() {
  const [findings, setFindings] = useState<Finding[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [bobOutput, setBobOutput] = useState<BobOutput | null>(null);
  const [loading, setLoading] = useState(true);
  const [connected, setConnected] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'findings' | 'incident' | 'analysis'>('overview');
  const [realtimeEvents, setRealtimeEvents] = useState<SSEEvent[]>([]);
  const [showEventLog, setShowEventLog] = useState(false);

  useEffect(() => {
    let mounted = true;

    const handleRealtimeEvent = (event: SSEEvent) => {
      if (!mounted) return;
      
      try {
        console.log('📡 Real-time event:', event);
        
        // Add to event log
        setRealtimeEvents(prev => [...prev.slice(-19), event]);

        switch (event.type) {
          case 'connected':
            setConnected(true);
            break;

          case 'finding_added':
            if (event.data) {
              setFindings(prev => [...prev, event.data]);
            }
            break;

          case 'incident_added':
            if (event.data) {
              setIncidents(prev => [...prev, event.data]);
              // Auto-select first incident
              setSelectedIncident(current => current || event.data);
            }
            break;

          case 'incident_updated':
            if (event.data && event.data.incident_id) {
              setIncidents(prev =>
                prev.map(inc =>
                  inc.incident_id === event.data.incident_id ? event.data : inc
                )
              );
              // Update selected incident if it's the one being updated
              setSelectedIncident(current => {
                if (current?.incident_id === event.data.incident_id) {
                  // Update Bob analysis if available
                  if (event.data.bob_analysis) {
                    setBobOutput(event.data.bob_analysis);
                  }
                  return event.data;
                }
                return current;
              });
            }
            break;

          case 'data_cleared':
            setFindings([]);
            setIncidents([]);
            setSelectedIncident(null);
            setBobOutput(null);
            break;

          case 'scan_complete':
            console.log('✅ Scan complete:', event.data);
            break;

          case 'scan_error':
            console.error('❌ Scan error:', event.data);
            break;
        }
      } catch (error) {
        console.error('Error handling real-time event:', error, event);
      }
    };

    // Connect to real-time updates
    realtimeClient.connect();

    // Subscribe to all events
    const unsubscribe = realtimeClient.on('all', handleRealtimeEvent);

    // Load initial data
    loadData().catch(error => {
      console.error('Error loading initial data:', error);
      setLoading(false);
    });

    // Cleanup on unmount
    return () => {
      mounted = false;
      unsubscribe();
      realtimeClient.disconnect();
    };
  }, []); // Empty dependency array - only run once

  const loadData = async () => {
    try {
      setLoading(true);
      const [findingsData, incidentsData] = await Promise.all([
        realtimeClient.getFindings(),
        realtimeClient.getIncidents()
      ]);
      
      setFindings(findingsData || []);
      setIncidents(incidentsData || []);
      
      if (incidentsData && incidentsData.length > 0) {
        setSelectedIncident(incidentsData[0]);
      }
    } catch (error) {
      console.error('Error loading data:', error);
      // Set empty arrays on error to prevent undefined issues
      setFindings([]);
      setIncidents([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSimulateAttack = async () => {
    try {
      await realtimeClient.simulateAttack();
      console.log('🎭 Attack simulation started');
    } catch (error) {
      console.error('Failed to start simulation:', error);
    }
  };

  const handleClearData = async () => {
    try {
      await realtimeClient.clearData();
      console.log('🗑️ Data cleared');
    } catch (error) {
      console.error('Failed to clear data:', error);
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

  return (
    <div style={{ padding: '2rem', maxWidth: '1600px', margin: '0 auto' }}>
      {/* Header with Real-time Status */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '2rem',
        padding: '1rem',
        backgroundColor: '#161b22',
        border: '1px solid #30363d',
        borderRadius: '6px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Activity size={24} color="#58a6ff" />
          <div>
            <h1 style={{
              fontSize: '1.5rem',
              fontWeight: 600,
              color: '#e6edf3',
              margin: 0
            }}>
              Bob Sentinel - Real-time Dashboard
            </h1>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              marginTop: '0.25rem'
            }}>
              {connected ? (
                <>
                  <Wifi size={14} color="#3fb950" />
                  <span style={{ fontSize: '0.875rem', color: '#3fb950' }}>
                    Live Updates Active
                  </span>
                </>
              ) : (
                <>
                  <WifiOff size={14} color="#f85149" />
                  <span style={{ fontSize: '0.875rem', color: '#f85149' }}>
                    Disconnected
                  </span>
                </>
              )}
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            onClick={handleSimulateAttack}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.5rem 1rem',
              backgroundColor: '#238636',
              color: '#ffffff',
              border: 'none',
              borderRadius: '6px',
              fontSize: '0.875rem',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'background-color 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#2ea043'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#238636'}
          >
            <Play size={16} />
            Simulate Attack
          </button>

          <button
            onClick={handleClearData}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.5rem 1rem',
              backgroundColor: '#21262d',
              color: '#e6edf3',
              border: '1px solid #30363d',
              borderRadius: '6px',
              fontSize: '0.875rem',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'background-color 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#30363d'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#21262d'}
          >
            <Trash2 size={16} />
            Clear Data
          </button>

          <button
            onClick={() => setShowEventLog(!showEventLog)}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#21262d',
              color: '#e6edf3',
              border: '1px solid #30363d',
              borderRadius: '6px',
              fontSize: '0.875rem',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'background-color 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#30363d'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#21262d'}
          >
            {showEventLog ? 'Hide' : 'Show'} Event Log
          </button>
        </div>
      </div>

      {/* Event Log */}
      {showEventLog && (
        <div style={{
          marginBottom: '2rem',
          padding: '1rem',
          backgroundColor: '#0d1117',
          border: '1px solid #30363d',
          borderRadius: '6px',
          maxHeight: '200px',
          overflowY: 'auto',
          fontFamily: 'monospace',
          fontSize: '0.75rem'
        }}>
          <h3 style={{
            fontSize: '0.875rem',
            fontWeight: 600,
            color: '#e6edf3',
            marginBottom: '0.5rem'
          }}>
            Real-time Event Log
          </h3>
          {realtimeEvents.map((event, index) => (
            <div key={index} style={{
              padding: '0.25rem 0',
              color: '#8b949e',
              borderBottom: index < realtimeEvents.length - 1 ? '1px solid #21262d' : 'none'
            }}>
              <span style={{ color: '#58a6ff' }}>[{new Date(event.timestamp).toLocaleTimeString()}]</span>
              {' '}
              <span style={{ color: '#3fb950' }}>{event.type}</span>
              {event.data && (
                <span style={{ color: '#8b949e' }}>
                  {' '}- {JSON.stringify(event.data).substring(0, 100)}...
                </span>
              )}
            </div>
          ))}
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
          { id: 'findings', label: `Findings (${findings.length})` },
          { id: 'incident', label: `Incidents (${incidents.length})` },
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
          
          {findings.length > 0 && (
            <div style={{ marginBottom: '2rem' }}>
              <h2 style={{
                fontSize: '1.25rem',
                fontWeight: 600,
                color: '#e6edf3',
                marginBottom: '1rem'
              }}>
                Recent Findings
              </h2>
              <FindingsTable findings={findings.slice(-5)} />
            </div>
          )}

          {selectedIncident && (
            <div style={{ marginBottom: '2rem' }}>
              <h2 style={{
                fontSize: '1.25rem',
                fontWeight: 600,
                color: '#e6edf3',
                marginBottom: '1rem'
              }}>
                Latest Incident
              </h2>
              <IncidentDetail incident={selectedIncident} />
            </div>
          )}

          {findings.length === 0 && incidents.length === 0 && (
            <div style={{
              textAlign: 'center',
              padding: '3rem',
              color: '#8b949e'
            }}>
              <p style={{ fontSize: '1.125rem', marginBottom: '1rem' }}>
                No security findings detected yet
              </p>
              <p style={{ fontSize: '0.875rem' }}>
                Click "Simulate Attack" to see real-time updates in action
              </p>
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
          {findings.length > 0 ? (
            <FindingsTable findings={findings} />
          ) : (
            <div style={{
              textAlign: 'center',
              padding: '3rem',
              color: '#8b949e',
              backgroundColor: '#161b22',
              border: '1px solid #30363d',
              borderRadius: '6px'
            }}>
              <p>No findings yet. Start a scan or simulate an attack to see results.</p>
            </div>
          )}
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

              {selectedIncident.related_memory && selectedIncident.related_memory.length > 0 && (
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
              textAlign: 'center',
              padding: '3rem',
              color: '#8b949e',
              backgroundColor: '#161b22',
              border: '1px solid #30363d',
              borderRadius: '6px'
            }}>
              <p>No incidents detected yet.</p>
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

      {/* Add CSS animation for loading spinner */}
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