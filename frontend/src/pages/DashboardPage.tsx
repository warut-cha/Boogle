import { useState, useEffect } from 'react';
import { apiClient, SCENARIOS } from '../api/client';
import type { Incident, Finding, BobOutput } from '../api/types';
import OverviewCards from '../components/OverviewCards';
import FindingsTable from '../components/FindingsTable';
import IncidentDetail from '../components/IncidentDetail';
import AttackPathGraph from '../components/AttackPathGraph';
import BobAnalysis from '../components/BobAnalysis';
import ReportViewer from '../components/ReportViewer';
import MemoryViewer from '../components/MemoryViewer';
import PRDraftViewer from '../components/PRDraftViewer';
import ScanInput from '../components/ScanInput';
import { SEVERITY_COLORS } from '../utils/severity';

export default function DashboardPage() {
  const [mode, setMode] = useState<'demo' | 'live'>('demo');
  const [selectedScenarioId, setSelectedScenarioId] = useState('inc-001');
  const [findings, setFindings] = useState<Finding[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [bobOutput, setBobOutput] = useState<BobOutput | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'findings' | 'incident' | 'analysis'>('overview');

  useEffect(() => {
    if (mode === 'demo') {
      loadData(selectedScenarioId);
    }
  }, [selectedScenarioId, mode]);

  const loadData = async (scenarioId: string) => {
    try {
      setLoading(true);
      setBobOutput(null);
      const [findingsData, incidentsData] = await Promise.all([
        apiClient.getFindings(scenarioId, true),
        apiClient.getIncidents(scenarioId, true)
      ]);

      setFindings(findingsData);
      setIncidents(incidentsData);

      if (incidentsData.length > 0) {
        setSelectedIncident(incidentsData[0]);
        const bobData = await apiClient.getBobAnalysis(incidentsData[0].incident_id, scenarioId, true);
        setBobOutput(bobData);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadLiveData = async () => {
    try {
      setLoading(true);
      const [findingsData, incidentsData] = await Promise.all([
        apiClient.getFindings('', false),
        apiClient.getIncidents('', false)
      ]);

      setFindings(findingsData);
      setIncidents(incidentsData);

      if (incidentsData.length > 0) {
        setSelectedIncident(incidentsData[0]);
        const bobData = await apiClient.getBobAnalysis(incidentsData[0].incident_id, '', false);
        setBobOutput(bobData);
      } else {
        setSelectedIncident(null);
        setBobOutput(null);
      }
    } catch (error) {
      console.error('Error loading live data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleScenarioSwitch = (scenarioId: string) => {
    setSelectedScenarioId(scenarioId);
    setActiveTab('overview');
  };

  const handleModeSwitch = (newMode: 'demo' | 'live') => {
    setMode(newMode);
    // Reset all data when switching modes
    setFindings([]);
    setIncidents([]);
    setSelectedIncident(null);
    setBobOutput(null);
    setActiveTab('overview');
    
    if (newMode === 'demo') {
      loadData(selectedScenarioId);
    } else {
      setLoading(false);
    }
  };

  const handleScanComplete = (result: { findings_count: number; incidents_count: number }) => {
    // After scan completes, load the fresh data from backend
    loadLiveData();
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
          <p>Loading scenario...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: '2rem', maxWidth: '1600px', margin: '0 auto' }}>

      {/* Mode Toggle */}
      <div style={{
        marginBottom: '2rem',
        padding: '1.25rem',
        backgroundColor: '#161b22',
        border: '1px solid #30363d',
        borderRadius: '8px'
      }}>
        <div style={{
          fontSize: '0.75rem',
          fontWeight: 600,
          color: '#8b949e',
          textTransform: 'uppercase',
          letterSpacing: '0.08em',
          marginBottom: '0.875rem'
        }}>
          Mode Selection
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button
            onClick={() => handleModeSwitch('demo')}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'flex-start',
              padding: '0.75rem 1.25rem',
              backgroundColor: mode === 'demo' ? '#1c2128' : 'transparent',
              border: `1px solid ${mode === 'demo' ? '#58a6ff' : '#30363d'}`,
              borderRadius: '6px',
              color: mode === 'demo' ? '#e6edf3' : '#8b949e',
              cursor: 'pointer',
              transition: 'all 0.15s',
              minWidth: '200px',
              textAlign: 'left'
            }}
            onMouseOver={(e) => {
              if (mode !== 'demo') {
                e.currentTarget.style.borderColor = '#58a6ff';
                e.currentTarget.style.color = '#e6edf3';
              }
            }}
            onMouseOut={(e) => {
              if (mode !== 'demo') {
                e.currentTarget.style.borderColor = '#30363d';
                e.currentTarget.style.color = '#8b949e';
              }
            }}
          >
            <span style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.25rem' }}>
              Demo Mode
            </span>
            <span style={{ fontSize: '0.75rem', color: '#6e7681' }}>
              Predefined scenarios
            </span>
          </button>
          <button
            onClick={() => handleModeSwitch('live')}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'flex-start',
              padding: '0.75rem 1.25rem',
              backgroundColor: mode === 'live' ? '#1c2128' : 'transparent',
              border: `1px solid ${mode === 'live' ? '#58a6ff' : '#30363d'}`,
              borderRadius: '6px',
              color: mode === 'live' ? '#e6edf3' : '#8b949e',
              cursor: 'pointer',
              transition: 'all 0.15s',
              minWidth: '200px',
              textAlign: 'left'
            }}
            onMouseOver={(e) => {
              if (mode !== 'live') {
                e.currentTarget.style.borderColor = '#58a6ff';
                e.currentTarget.style.color = '#e6edf3';
              }
            }}
            onMouseOut={(e) => {
              if (mode !== 'live') {
                e.currentTarget.style.borderColor = '#30363d';
                e.currentTarget.style.color = '#8b949e';
              }
            }}
          >
            <span style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.25rem' }}>
              Live Scan
            </span>
            <span style={{ fontSize: '0.75rem', color: '#6e7681' }}>
              Scan real repositories
            </span>
          </button>
        </div>
      </div>

      {/* Scan Input - Only show in Live mode */}
      {mode === 'live' && (
        <ScanInput onScanComplete={handleScanComplete} />
      )}

      {/* Scenario Selector - Only show in Demo mode */}
      {mode === 'demo' && (
        <div style={{
          marginBottom: '2rem',
          padding: '1.25rem',
          backgroundColor: '#161b22',
          border: '1px solid #30363d',
          borderRadius: '8px'
        }}>
          <div style={{
            fontSize: '0.75rem',
            fontWeight: 600,
            color: '#8b949e',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            marginBottom: '0.875rem'
          }}>
            Demo Scenario
          </div>
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          {SCENARIOS.map((s) => {
            const isActive = selectedScenarioId === s.id;
            const color = SEVERITY_COLORS[s.severity] ?? '#8b949e';
            return (
              <button
                key={s.id}
                onClick={() => handleScenarioSwitch(s.id)}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'flex-start',
                  padding: '0.75rem 1.25rem',
                  backgroundColor: isActive ? '#1c2128' : 'transparent',
                  border: `1px solid ${isActive ? color : '#30363d'}`,
                  borderRadius: '6px',
                  color: isActive ? '#e6edf3' : '#8b949e',
                  cursor: 'pointer',
                  transition: 'all 0.15s',
                  minWidth: '200px',
                  textAlign: 'left'
                }}
                onMouseOver={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.borderColor = '#58a6ff';
                    e.currentTarget.style.color = '#e6edf3';
                  }
                }}
                onMouseOut={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.borderColor = '#30363d';
                    e.currentTarget.style.color = '#8b949e';
                  }
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                  <span style={{
                    display: 'inline-block',
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    backgroundColor: isActive ? color : '#484f58',
                    flexShrink: 0
                  }} />
                  <span style={{ fontSize: '0.875rem', fontWeight: 600 }}>{s.label}</span>
                  <span style={{
                    fontSize: '0.65rem',
                    fontWeight: 600,
                    textTransform: 'uppercase',
                    color: color,
                    opacity: isActive ? 1 : 0.6,
                    border: `1px solid ${color}`,
                    borderRadius: '3px',
                    padding: '0 4px'
                  }}>
                    {s.severity}
                  </span>
                </div>
                <span style={{ fontSize: '0.75rem', color: '#6e7681' }}>{s.subtitle}</span>
              </button>
            );
          })}
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
              if (activeTab !== tab.id) e.currentTarget.style.color = '#e6edf3';
            }}
            onMouseOut={(e) => {
              if (activeTab !== tab.id) e.currentTarget.style.color = '#8b949e';
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
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#e6edf3', marginBottom: '1rem' }}>
              Recent Findings
            </h2>
            <FindingsTable findings={findings.slice(0, 5)} />
          </div>

          {selectedIncident && (
            <div style={{ marginBottom: '2rem' }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#e6edf3', marginBottom: '1rem' }}>
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
          <h2 style={{ fontSize: '1.5rem', fontWeight: 600, color: '#e6edf3', marginBottom: '1.5rem' }}>
            All Security Findings
          </h2>
          <FindingsTable findings={findings} />
        </div>
      )}

      {/* Incident Analysis Tab */}
      {activeTab === 'incident' && selectedIncident && (
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 600, color: '#e6edf3', marginBottom: '1.5rem' }}>
            Incident Analysis
          </h2>

          <div style={{ marginBottom: '2rem' }}>
            <IncidentDetail incident={selectedIncident} />
          </div>

          <div style={{ marginBottom: '2rem' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#e6edf3', marginBottom: '1rem' }}>
              Attack Path
            </h3>
            <AttackPathGraph attackPath={selectedIncident.attack_path} />
          </div>

          <div style={{ marginBottom: '2rem' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#e6edf3', marginBottom: '1rem' }}>
              Related Findings
            </h3>
            <FindingsTable findings={selectedIncident.findings} />
          </div>

          {selectedIncident.related_memory.length > 0 && (
            <div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#e6edf3', marginBottom: '1rem' }}>
                AI Memory Patterns
              </h3>
              <MemoryViewer memories={selectedIncident.related_memory} />
            </div>
          )}
        </div>
      )}

      {/* Bob AI Analysis Tab */}
      {activeTab === 'analysis' && (
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 600, color: '#e6edf3', marginBottom: '1.5rem' }}>
            IBM Bob AI Analysis & Remediation
          </h2>

          <div style={{ marginBottom: '2rem' }}>
            <BobAnalysis bobOutput={bobOutput} />
          </div>

          {bobOutput && (
            <>
              <div style={{ marginBottom: '2rem' }}>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#e6edf3', marginBottom: '1rem' }}>
                  Incident Report
                </h3>
                <ReportViewer report={bobOutput.incident_report} />
              </div>

              <div style={{ marginBottom: '2rem' }}>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#e6edf3', marginBottom: '1rem' }}>
                  AI Memory Created
                </h3>
                <MemoryViewer memories={[bobOutput.ai_memory]} />
              </div>

              <div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#e6edf3', marginBottom: '1rem' }}>
                  Pull Request Draft
                </h3>
                <PRDraftViewer prDraft={bobOutput.pr_draft} />
              </div>
            </>
          )}
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
