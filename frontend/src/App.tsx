import { useState } from 'react'
import RealtimeDashboardPage from './pages/RealtimeDashboardPage'

function App() {
  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#0f1419' }}>
      <header style={{
        backgroundColor: '#161b22',
        borderBottom: '1px solid #30363d',
        padding: '1rem 2rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <h1 style={{ 
            fontSize: '1.5rem', 
            fontWeight: 'bold',
            color: '#58a6ff',
            margin: 0
          }}>
            🛡️ Bob Sentinel
          </h1>
          <span style={{ 
            fontSize: '0.875rem', 
            color: '#8b949e',
            padding: '0.25rem 0.75rem',
            backgroundColor: '#21262d',
            borderRadius: '1rem'
          }}>
            Autonomous DevSecOps Assistant
          </span>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <span style={{ fontSize: '0.875rem', color: '#8b949e' }}>
            Powered by IBM Bob
          </span>
        </div>
      </header>
      <main>
        <RealtimeDashboardPage />
      </main>
    </div>
  )
}

export default App

// Made with Bob
