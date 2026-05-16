import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect } from 'vitest'
import DashboardPage from '../pages/DashboardPage'

describe('DashboardPage', () => {
  it('shows loading spinner initially', () => {
    render(<DashboardPage />)
    expect(screen.getByText(/loading bob sentinel/i)).toBeInTheDocument()
  })

  it('renders all 4 navigation tabs after loading', async () => {
    render(<DashboardPage />)
    await waitFor(() => {
      expect(screen.getByText('Overview')).toBeInTheDocument()
      expect(screen.getByText('Findings')).toBeInTheDocument()
      expect(screen.getByText('Incident Analysis')).toBeInTheDocument()
      expect(screen.getByText('Bob AI Analysis')).toBeInTheDocument()
    })
  })

  it('shows overview content by default', async () => {
    render(<DashboardPage />)
    await waitFor(() => {
      expect(screen.getByText('Recent Findings')).toBeInTheDocument()
    })
  })

  it('switches to Findings tab', async () => {
    const user = userEvent.setup()
    render(<DashboardPage />)
    await waitFor(() => screen.getByText('Findings'))
    await user.click(screen.getByText('Findings'))
    expect(screen.getByText('All Security Findings')).toBeInTheDocument()
  })

  it('switches to Incident Analysis tab', async () => {
    const user = userEvent.setup()
    render(<DashboardPage />)
    await waitFor(() => screen.getByText('Incident Analysis'))
    await user.click(screen.getByText('Incident Analysis'))
    expect(screen.getByText('Attack Path')).toBeInTheDocument()
  })

  it('switches to Bob AI Analysis tab', async () => {
    const user = userEvent.setup()
    render(<DashboardPage />)
    await waitFor(() => screen.getByText('Bob AI Analysis'))
    await user.click(screen.getByText('Bob AI Analysis'))
    expect(screen.getByText('IBM Bob AI Analysis & Remediation')).toBeInTheDocument()
  })
})
