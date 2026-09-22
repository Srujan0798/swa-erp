import { test, expect, beforeEach, describe, it } from '@playwright/test'

// Login helper
async function login(page: any) {
  await page.goto('/login')
  await page.fill('input[placeholder="Email"]', 'admin@swa.co.in')
  await page.fill('input[placeholder="Password"]', 'admin123!')
  await page.click('button:has-text("Sign In")')
  await page.waitForURL('/dashboard')
}

describe('SWA-ERP Full UI Test Suite', () => {
  let browser: any

  beforeAll(async ({ browser: _browser }) => {
    browser = _browser
  })

  // ===== INQUIRIES PAGE =====
  describe('Inquiries', () => {
    test('inquiries page loads and has create button', async ({ browser }) => {
      const page = await browser.newPage()
      await page.goto('/inquiries')
      await expect(page).toHaveTitle(/Inquiries/)
      await expect(page.locator('h1')).toContainText('Inquiries')
      await expect(page.locator('button:has-text("New Inquiry")')).toBeVisible()
      await page.close()
    })

    test('can create new inquiry', async ({ browser }) => {
      const page = await browser.newPage()
      await page.goto('/inquiries')
      await page.click('button:has-text("New Inquiry")')
      await expect(page).toHaveURL(/.*\/inquiries\/new/)
      await page.fill('input[placeholder="Title"]', 'TEST-INQ-001')
      await page.fill('input[placeholder="Client"]', 'TEST-CLIENT')
      await page.click('button:has-text("Create")')
      await expect(page.locator('text=TEST-INQ-001')).toBeVisible()
      await page.close()
    })
  })

  // ===== CLIENTS PAGE =====
  describe('Clients', () => {
    test('clients page loads', async ({ browser }) => {
      const page = await browser.newPage()
      await page.goto('/clients')
      await expect(page).toHaveTitle(/Clients/)
      await expect(page.locator('h1')).toContainText('Clients')
      await expect(page.locator('button:has-text("New Client")')).toBeVisible()
      await page.close()
    })

    test('can create new client', async ({ browser }) => {
      const page = await browser.newPage()
      await page.goto('/clients')
      await page.click('button:has-text("New Client")')
      await expect(page).toHaveURL(/.*\/clients\/new/)
      await page.fill('input[placeholder="Company Name"]', 'Test Corp Pte Ltd')
      await page.fill('input[placeholder="Email"]', 'test@testcorp.com')
      await page.selectOption('select[placeholder="Country"]', 'Singapore')
      await page.click('button:has-text("Create")')
      await expect(page.locator('text=Test Corp')).toBeVisible()
      await page.close()
    })
  })

  // ===== PROJECTS PAGE =====
  describe('Projects', () => {
    test('projects page loads', async ({ browser }) => {
      const page = await browser.newPage()
      await page.goto('/projects')
      await expect(page).toHaveTitle(/Projects/)
      await expect(page.locator('h1')).toContainText('Projects')
      await expect(page.locator('button:has-text("New Project")')).toBeVisible()
      await page.close()
    })

    test('can create new project', async ({ browser }) => {
      const page = await browser.newPage()
      await page.goto('/projects')
      await page.click('button:has-text("New Project")')
      await expect(page).toHaveURL(/.*\/projects\/new/)
      await page.fill('input[placeholder="Project Name"]', 'TEST-PROJECT')
      await page.selectOption('select[placeholder="Client"]', 'Test Client')
      await page.fill('input[placeholder="Budget"]', '50000')
      await page.click('button:has-text("Create")')
      await expect(page.locator('text=TEST-PROJECT')).toBeVisible()
      await page.close()
    })
  })

  // ===== QUOTES/BOQ PAGE =====
  describe('Quotes / BOQ', () => {
    test('quotes page loads', async ({ browser }) => {
      const page = await browser.newPage()
      await page.goto('/quotes')
      await expect(page).toHaveTitle(/Quotes/)
      await expect(page.locator('h1')).toContainText('Quotes')
      await expect(page.locator('button:has-text("New Quote")')).toBeVisible()
      await page.close()
    })

    test('can create new quote', async ({ browser }) => {
      const page = await browser.newPage()
      await page.goto('/quotes')
      await page.click('button:has-text("New Quote")')
      await expect(page).toHaveURL(/.*\/quotes\/new/)
      await page.fill('input[placeholder="Quote Number"]', 'Q-001')
      await page.selectOption('select[placeholder="Project"]', 'Test Project')
      await page.click('button:has-text("Create")')
      await expect(page.locator('text=Q-001')).toBeVisible()
      await page.close()
    })
  })

  // ===== TASKS PAGE =====
  describe('Tasks', () => {
    test('tasks page loads', async ({ browser }) => {
      const page = await browser.newPage()
      await page.goto('/tasks')
      await expect(page).toHaveTitle(/Tasks/)
      await expect(page.locator('h1')).toContainText('Tasks')
      await expect(page.locator('button:has-text("New Task")')).toBeVisible()
      await page.close()
    })

    test('can create new task', async ({ browser }) => {
      const page = await browser.newPage()
      await page.goto('/tasks')
      await page.click('button:has-text("New Task")')
      await expect(page).toHaveURL(/.*\/tasks\/new/)
      await page.fill('input[placeholder="Title"]', 'TEST-TASK')
      await page.fill('input[placeholder="Description"]', 'Test task description')
      await page.selectOption('select[placeholder="Priority"]', 'high')
      await page.click('button:has-text("Create")')
      await expect(page.locator('text=TEST-TASK')).toBeVisible()
      await page.close()
    })
  })

  // ===== TIME TRACKING PAGE =====
  describe('Time Tracking', () => {
    test('time tracking page loads', async ({ browser }) => {
      const page = await browser.newPage()
      await page.goto('/time-tracking')
      await expect(page).toHaveTitle(/Time Tracking/)
      await expect(page.locator('h1')).toContainText('Time Tracking')
      await expect(page.locator('button:has-text("New Entry")')).toBeVisible()
      await page.close()
    })

    test('can log time entry', async ({ browser }) => {
      const page = await browser.newPage()
      await page.goto('/time-tracking')
      await page.click('button:has-text("New Entry")')
      await expect(page).toHaveURL(/.*\/time-tracking\/new/)
      await page.fill('input[placeholder="Date"]', new Date().toISOString().split('T')[0])
      await page.fill('input[placeholder="Hours"]', '2.5')
      await page.fill('input[placeholder="Description"]', 'Test time entry')
      await page.toggle('input[placeholder="Billable"]')
      await page.selectOption('select[placeholder="Work Type"]', 'Development')
      await page.click('button:has-text("Submit")')
      await expect(page.locator('text=2.5')).toBeVisible()
      await page.close()
    })
  })

  // ===== FINANCIALS / INVOICES PAGE =====
  describe('Financials / Invoices', () => {
    test('invoices page loads', async ({ browser }) => {
      const page = await browser.newPage()
      await page.goto('/invoices')
      await expect(page).toHaveTitle(/Invoices/)
      await expect(page.locator('h1')).toContainText('Invoices')
      await expect(page.locator('button:has-text("New Invoice")')).toBeVisible()
      await page.close()
    })

    test('can create new invoice', async ({ browser }) => {
      const page = await browser.newPage()
      await page.goto('/invoices')
      await page.click('button:has-text("New Invoice")')
      await expect(page).toHaveURL(/.*\/invoices\/new/)
      await page.fill('input[placeholder="Invoice Number"]', 'INV-TEST-001')
      await page.fill('input[placeholder="Amount"]', '10000')
      await page.selectOption('select[placeholder="Project"]', 'Test Project')
      await page.click('button:has-text("Create")')
      await expect(page.locator('text=INV-TEST-001')).toBeVisible()
      await page.close()
    })
  })

  // ===== VENDORS PAGE =====
  describe('Vendors', () => {
    test('vendors page loads', async ({ browser }) => {
      const page = await browser.newPage()
      await page.goto('/vendors')
      await expect(page).toHaveTitle(/Vendors/)
      await expect(page.locator('h1')).toContainText('Vendors')
      await expect(page.locator('button:has-text("New Vendor")')).toBeVisible()
      await page.close()
    })

    test('can create new vendor', async ({ browser }) => {
      const page = await browser.newPage()
      await page.goto('/vendors')
      await page.click('button:has-text("New Vendor")')
      await expect(page).toHaveURL(/.*\/vendors\/new/)
      await page.fill('input[placeholder="Company Name"]', 'Test Vendor Pte Ltd')
      await page.fill('input[placeholder="Contact"]', 'John Doe')
      await page.fill('input[placeholder="Email"]', 'vendor@testvendor.com')
      await page.selectOption('select[placeholder="Country"]', 'Singapore')
      await page.click('button:has-text("Create")')
      await expect(page.locator('text=Test Vendor')).toBeVisible()
      await page.close()
    })
  })

  // ===== COMPLIANCE PAGE =====
  describe('Compliance', () => {
    test('compliance page loads', async ({ browser }) => {
      const page = await browser.newPage()
      await page.goto('/compliance')
      await expect(page).toHaveTitle(/Compliance/)
      await expect(page.locator('h1')).toContainText('Compliance')
      await expect(page.locator('text:has-text("NBC")')).toBeVisible()
      await expect(page.locator('text:has-text("ECBC")')).toBeVisible()
      await expect(page.locator('text:has-text("IGBC")')).toBeVisible()
      await expect(page.locator('text:has-text("IS")')).toBeVisible()
      await page.close()
    })
  })

  // ===== DASHBOARD PAGE =====
  describe('Dashboard', () => {
    test('dashboard page loads', async ({ browser }) => {
      const page = await browser.newPage()
      await page.goto('/dashboard')
      await expect(page).toHaveTitle(/Dashboard/)
      await expect(page.locator('h1')).toContainText('Dashboard')
      await expect(page.locator('text:has-text("Inquiry")')).toBeVisible()
      await expect(page.locator('text:has-text("Project")')).toBeVisible()
      await expect(page.locator('text:has-text("Task")')).toBeVisible()
      await page.close()
    })

    test('dashboard stats cards visible', async ({ browser }) => {
      const page = await browser.newPage()
      await page.goto('/dashboard')
      await expect(page.locator('.stat-card')).toHaveCount(5)
      await expect(page.locator('.stat-number')).toBeVisible()
      await page.close()
    })
  })

  // ===== DOCUMENTS PAGE =====
  describe('Documents', () => {
    test('documents page loads', async ({ browser }) => {
      const page = await browser.newPage()
      await page.goto('/documents')
      await expect(page).toHaveTitle(/Documents/)
      await expect(page.locator('h1')).toContainText('Documents')
      await expect(page.locator('button:has-text("Upload")')).toBeVisible()
      await page.close()
    })
  })

  // ===== INQUIRY DETAIL PAGE =====
  describe('Inquiry Detail', () => {
    test('inquiry detail page loads', async ({ browser }) => {
      const page = await browser.newPage()
      await page.goto('/inquiries/1')
      await expect(page).toHaveTitle(/Inquiry Detail/)
      await expect(page.locator('h1')).toBeVisible()
      await expect(page.locator('text:has-text("Status")')).toBeVisible()
      await page.close()
    })
  })

  // ===== PROJECT DETAIL PAGE =====
  describe('Project Detail', () => {
    test('project detail page loads', async ({ browser }) => {
      const page = await browser.newPage()
      await page.goto('/projects/1')
      await expect(page).toHaveTitle(/Project Detail/)
      await expect(page.locator('h1')).toBeVisible()
      await expect(page.locator('text:has-text("Tasks")')).toBeVisible()
      await expect(page.locator('text:has-text("Compliance")')).toBeVisible()
      await page.close()
    })
  })

  // ===== CLIENT DETAIL PAGE =====
  describe('Client Detail', () => {
    test('client detail page loads', async ({ browser }) => {
      const page = await browser.newPage()
      await page.goto('/clients/1')
      await expect(page).toHaveTitle(/Client Detail/)
      await expect(page.locator('h1')).toBeVisible()
      await expect(page.locator('text:has-text("Projects")')).toBeVisible()
      await expect(page.locator('text:has-text("Contacts")')).toBeVisible()
      await page.close()
    })
  })

  // ===== SETTINGS / USER PAGE =====
  describe('Users / Settings', () => {
    test('users page loads', async ({ browser }) => {
      const page = await browser.newPage()
      await page.goto('/users')
      await expect(page).toHaveTitle(/Users/)
      await expect(page.locator('h1')).toContainText('Users')
      await expect(page.locator('button:has-text("New User")')).toBeVisible()
      await page.close()
    })
  })

  // ===== SUSTAINABILITY PAGE =====
  describe('Sustainability', () => {
    test('sustainability page loads', async ({ browser }) => {
      const page = await browser.newPage()
      await page.goto('/sustainability')
      await expect(page).toHaveTitle(/Sustainability/)
      await expect(page.locator('h1')).toContainText('Sustainability')
      await expect(page.locator('text:has-text("NBC")')).toBeVisible()
      await expect(page.locator('text:has-text("ECBC")')).toBeVisible()
      await page.close()
    })
  })

  // ===== TOKENS PAGE =====
  describe('Tokens', () => {
    test('tokens page loads', async ({ browser }) => {
      const page = await browser.newPage()
      await page.goto('/tokens')
      await expect(page).toHaveTitle(/Tokens/)
      await expect(page.locator('h1')).toContainText('Tokens')
      await expect(page.locator('button:has-text("Generate")')).toBeVisible()
      await page.close()
    })
  })

  // ===== AGREEMENTS PAGE =====
  describe('Agreements', () => {
    test('agreements page loads', async ({ browser }) => {
      const page = await browser.newPage()
      await page.goto('/agreements')
      await expect(page).toHaveTitle(/Agreements/)
      await expect(page.locator('h1')).toContainText('Agreements')
      await expect(page.locator('button:has-text("New Agreement")')).toBeVisible()
      await page.close()
    })
  })

  // ===== RFQs PAGE =====
  describe('RFQs', () => {
    test('RFQs page loads', async ({ browser }) => {
      const page = await browser.newPage()
      await page.goto('/rfqs')
      await expect(page).toHaveTitle(/RFQs/)
      await expect(page.locator('h1')).toContainText('RFQs')
      await expect(page.locator('button:has-text("New RFQ")')).toBeVisible()
      await page.close()
    })
  })

  // ===== REPORTS PAGE =====
  describe('Reports', () => {
    test('reports page loads', async ({ browser }) => {
      const page = await browser.newPage()
      await page.goto('/reports')
      await expect(page).toHaveTitle(/Reports/)
      await expect(page.locator('h1')).toContainText('Reports')
      await expect(page.locator('text:has-time-tracking')).toBeVisible()
      await expect(page.locator('text:has-text("compliance"))).toBeVisible()
      await page.close()
    })
  })
})