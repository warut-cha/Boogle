import { test, expect } from '@playwright/test'

test.describe('Bob Sentinel Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000')
    // Wait for loading to finish
    await page.waitForSelector('text=Overview', { timeout: 10000 })
  })

  test('page title and header are visible', async ({ page }) => {
    await expect(page.getByText('Bob Sentinel')).toBeVisible()
    await expect(page.getByText('Autonomous DevSecOps Assistant')).toBeVisible()
  })

  test('all navigation tabs are present', async ({ page }) => {
    await expect(page.getByRole('button', { name: 'Overview' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Findings' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Incident Analysis' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Bob AI Analysis' })).toBeVisible()
  })

  test('overview tab shows metrics cards', async ({ page }) => {
    await expect(page.getByText('Total Findings')).toBeVisible()
    await expect(page.getByText('Correlated Incidents')).toBeVisible()
    await expect(page.getByText('Confidence Score').first()).toBeVisible()
    await expect(page.getByText('Recent Findings')).toBeVisible()
  })

  test('findings tab shows security findings table', async ({ page }) => {
    await page.getByRole('button', { name: 'Findings' }).click()
    await expect(page.getByText('All Security Findings')).toBeVisible()
    await expect(page.getByText('FIND-001')).toBeVisible()
    await expect(page.getByText('FIND-002')).toBeVisible()
  })

  test('findings table shows severity badges', async ({ page }) => {
    await page.getByRole('button', { name: 'Findings' }).click()
    await expect(page.getByText('high').first()).toBeVisible()
    await expect(page.getByText('medium').first()).toBeVisible()
  })

  test('incident analysis tab shows attack path', async ({ page }) => {
    await page.getByRole('button', { name: 'Incident Analysis' }).click()
    await expect(page.getByRole('heading', { name: 'Attack Path', exact: true })).toBeVisible()
    await expect(page.getByText('AI Memory Patterns')).toBeVisible()
  })

  test('bob AI analysis tab shows analysis and report', async ({ page }) => {
    await page.getByRole('button', { name: 'Bob AI Analysis' }).click()
    await expect(page.getByText('IBM Bob AI Analysis & Remediation')).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Incident Report', exact: true }).first()).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Pull Request Draft', exact: true }).first()).toBeVisible()
  })

  test('incident detail shows critical severity', async ({ page }) => {
    await expect(page.getByText('Critical Incident')).toBeVisible()
    await expect(page.getByText(/credential leakage/i)).toBeVisible()
  })
})
