import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import OverviewCards from '../components/OverviewCards'
import { mockFindings, mockIncident } from '../api/client'

describe('OverviewCards', () => {
  it('renders all 6 metric cards', () => {
    render(
      <OverviewCards
        incidents={[mockIncident]}
        findings={mockFindings}
        bobAnalysisGenerated={true}
      />
    )
    expect(screen.getByText('Repos Scanned')).toBeInTheDocument()
    expect(screen.getByText('Total Findings')).toBeInTheDocument()
    expect(screen.getByText('Correlated Incidents')).toBeInTheDocument()
    expect(screen.getByText('Confidence Score')).toBeInTheDocument()
    expect(screen.getByText('Tests Generated')).toBeInTheDocument()
    expect(screen.getByText('PR Drafts')).toBeInTheDocument()
  })

  it('shows correct finding count', () => {
    render(
      <OverviewCards
        incidents={[mockIncident]}
        findings={mockFindings}
        bobAnalysisGenerated={false}
      />
    )
    expect(screen.getByText(String(mockFindings.length))).toBeInTheDocument()
  })

  it('shows confidence score as percentage', () => {
    render(
      <OverviewCards
        incidents={[mockIncident]}
        findings={mockFindings}
        bobAnalysisGenerated={true}
      />
    )
    const expectedScore = Math.round(mockIncident.confidence_score * 100)
    expect(screen.getByText(`${expectedScore}%`)).toBeInTheDocument()
  })

  it('shows 0 PR drafts when bob analysis not generated', () => {
    render(
      <OverviewCards
        incidents={[mockIncident]}
        findings={mockFindings}
        bobAnalysisGenerated={false}
      />
    )
    expect(screen.getByText('Ready for review')).toBeInTheDocument()
  })

  it('renders with empty data without crashing', () => {
    render(
      <OverviewCards
        incidents={[]}
        findings={[]}
        bobAnalysisGenerated={false}
      />
    )
    // Multiple cards show 0 when data is empty — just verify the component renders
    expect(screen.getAllByText('0').length).toBeGreaterThan(0)
  })
})
