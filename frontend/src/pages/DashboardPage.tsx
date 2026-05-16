import { useState, useEffect } from 'react';
import { apiClient, mockIncident, mockBobOutput } from '../api/client';
import type { Incident, Finding, BobOutput } from '../api/types';
import OverviewCards from '../components/OverviewCards';
import FindingsTable from '../components/FindingsTable';
import IncidentDetail from '../components/IncidentDetail';
import AttackPathGraph from '../components/AttackPathGraph';
import BobAnalysis from '../components/BobAnalysis';
import ReportViewer from '../components/ReportViewer';
import MemoryViewer from '../components/MemoryViewer';
import PRDraftViewer from '../components/PRDraftViewer';

export default function DashboardPage() {
  const [findings, setFindings] = useState<Finding[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [bobOutput, setBobOutput] = useState<BobOutput | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'findings' | 'incident' | 'analysis'>('overview');

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

  return (
    <div style={{ padding: '2rem', maxWidth: '1600px', margin: '0 auto' }}>
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
      {activeTab === 'incident' && selectedIncident && (
        <div>
          <h2 style={{
            fontSize: '1.5rem',
            fontWeight: 600,
            color: '#e6edf3',
            marginBottom: '1.5rem'
          }}>
            Incident Analysis
          </h2>
          
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
