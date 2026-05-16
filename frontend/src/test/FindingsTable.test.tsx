import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import FindingsTable from '../components/FindingsTable'
import { mockFindings } from '../api/client'

describe('FindingsTable', () => {
  it('renders empty state when no findings', () => {
    render(<FindingsTable findings={[]} />)
    expect(screen.getByText('No findings detected')).toBeInTheDocument()
  })

  it('renders table headers when findings exist', () => {
    render(<FindingsTable findings={mockFindings} />)
    expect(screen.getByText('ID')).toBeInTheDocument()
    expect(screen.getByText('Type')).toBeInTheDocument()
    expect(screen.getByText('Severity')).toBeInTheDocument()
    expect(screen.getByText('Repository')).toBeInTheDocument()
    expect(screen.getByText('Evidence')).toBeInTheDocument()
  })

  it('shows correct total findings count', () => {
    render(<FindingsTable findings={mockFindings} />)
    expect(screen.getByText(`${mockFindings.length} total`)).toBeInTheDocument()
  })

  it('renders each finding ID', () => {
    render(<FindingsTable findings={mockFindings} />)
    for (const finding of mockFindings) {
      expect(screen.getByText(finding.finding_id)).toBeInTheDocument()
    }
  })

  it('renders finding severity badges', () => {
    render(<FindingsTable findings={mockFindings} />)
    expect(screen.getAllByText('high').length).toBeGreaterThan(0)
    expect(screen.getAllByText('medium').length).toBeGreaterThan(0)
  })

  it('renders masked value when present', () => {
    render(<FindingsTable findings={mockFindings} />)
    const findingWithMask = mockFindings.find(f => f.masked_value)
    if (findingWithMask?.masked_value) {
      expect(screen.getByText(findingWithMask.masked_value)).toBeInTheDocument()
    }
  })

  it('shows dash for findings with no file', () => {
    render(<FindingsTable findings={mockFindings} />)
    const noFileFinding = mockFindings.find(f => !f.file)
    expect(noFileFinding).toBeDefined()
    expect(screen.getAllByText('-').length).toBeGreaterThan(0)
  })
})
