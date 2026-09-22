import { test, expect, type Page, type Browser } from "@playwright/test";

let browser: Browser;
let page: Page;
const BASE = "http://localhost:3100";

test.beforeAll(async ({ browser: b }) => {
  browser = b;
  page = await browser.newPage();
  await page.goto(`${BASE}/login`);
  await page.getByLabel("Email").fill("admin@swa.co.in");
  await page.getByLabel("Password").fill("admin123!");
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);
});

test.afterAll(async () => {
  if (page) await page.close();
});

// Exact h1 text per route (from page sources). Anchored so sub-headings
// never produce strict-mode violations, and scoped to <main>.
const ROUTES: { path: string; heading: string }[] = [
  { path: "/dashboard", heading: "SWA operations" },
  { path: "/inquiries", heading: "Inquiries" },
  { path: "/clients", heading: "Clients" },
  { path: "/agreements", heading: "Service Agreements" },
  { path: "/tokens", heading: "Tokens" },
  { path: "/document-references", heading: "Document References" },
  { path: "/projects", heading: "Projects" },
  { path: "/time-tracking", heading: "Time logging" },
  { path: "/documents", heading: "File documents" },
  { path: "/tasks", heading: "Tasks" },
  { path: "/sustainability", heading: "Sustainability Metrics" },
  { path: "/compliance", heading: "Compliance" },
  { path: "/vendors", heading: "Vendors" },
  { path: "/materials", heading: "Materials" },
  { path: "/rfqs", heading: "RFQs" },
  { path: "/invoices", heading: "Invoices" },
  { path: "/reports", heading: "Reports" },
  { path: "/users", heading: "Users" },
];

for (const r of ROUTES) {
  test(`renders ${r.path}`, async () => {
    await page.goto(`${BASE}${r.path}`);
    await page.waitForLoadState("networkidle");
    const main = page.getByRole("main");
    await expect(
      main.getByRole("heading", { name: new RegExp(`^${r.heading}$`, "i") }),
    ).toBeVisible({ timeout: 20000 });
    await expect(main.locator("h1").first()).not.toHaveText(
      /Unexpected Application Error/i,
    );
    await expect(main.locator("h1").first()).not.toHaveText(/^Error/i);
  });
}

test("login form pre-fills seeded admin credentials", async () => {
  const p = await browser.newPage();
  await p.goto(`${BASE}/login`);
  await expect(p.getByLabel("Email")).toHaveValue("admin@swa.co.in");
  await expect(p.getByLabel("Password")).toHaveValue("admin123!");
  await p.close();
});

test("invalid credentials show error", async () => {
  const p = await browser.newPage();
  await p.goto(`${BASE}/login`);
  await p.getByLabel("Email").fill("nobody@swa.co.in");
  await p.getByLabel("Password").fill("wrongpw");
  await p.getByRole("button", { name: /sign in/i }).click();
  await expect(p.getByText(/invalid credentials/i)).toBeVisible();
  await p.close();
});

test("logout returns to login", async () => {
  await page.getByRole("button", { name: /logout/i }).click();
  await expect(page).toHaveURL(/\/login/);
  // Re-login so later tests in the file keep a valid session.
  await page.getByLabel("Email").fill("admin@swa.co.in");
  await page.getByLabel("Password").fill("admin123!");
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);
});

test("dashboard shows live stats", async () => {
  await page.goto(`${BASE}/dashboard`);
  await page.waitForLoadState("networkidle");
  const main = page.getByRole("main");
  await expect(main.getByText(/total active projects/i)).toBeVisible({
    timeout: 15000,
  });
  await expect(main.getByText(/total estimated value/i)).toBeVisible();
  await expect(main.getByText(/in quote stage/i)).toBeVisible();
  await expect(main.getByText(/in execution/i)).toBeVisible();
});
