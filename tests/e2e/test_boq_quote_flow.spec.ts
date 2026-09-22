import { test, expect, type Page } from "@playwright/test";

const BASE = "http://localhost:3100";
let projectCode = "";
let projectId = "";

test.describe("BOQ & Quote flow", () => {
  test.beforeEach(async ({ page, request }) => {
    // Self-sufficient setup: ensure a fresh project exists via the API so the
    // flow never depends on ambient seed data.
    const login = await request.post("http://localhost:8100/api/auth/login", {
      data: { email: "admin@swa.local", password: "admin123!" },
    });
    const { access_token } = await login.json();
    const headers = { Authorization: `Bearer ${access_token}` };
    const code = `E2E-${Date.now()}`;
    const client = await request.post("http://localhost:8100/api/clients", {
      headers,
      data: {
        name: "E2E Client",
        code: `${code}-C`,
        primary_email: "e2e@example.com",
      },
    });
    const clientId = (await client.json()).id;
    const proj = await request.post("http://localhost:8100/api/projects", {
      headers,
      data: { name: "E2E Project", code: `${code}-P`, client_id: clientId },
    });
    expect(proj.status(), `project create failed: ${await proj.text()}`).toBe(
      201,
    );
    const project = await proj.json();
    projectCode = project.code;
    projectId = project.id;

    await page.goto(`${BASE}/login`);
    await page.getByLabel("Email").fill("admin@swa.local");
    await page.getByLabel("Password").fill("admin123!");
    await page.getByRole("button", { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/dashboard/);
  });

  // Navigate to the freshly created project's detail via its unique code row.
  // Falls back to a direct URL if the list query errored to its empty state.
  async function openProjectDetail(page: Page) {
    await page.goto(`${BASE}/projects`);
    const row = page
      .getByRole("main")
      .locator("tr")
      .filter({ hasText: projectCode });
    if ((await row.count()) > 0) {
      await row.getByRole("link", { name: /view/i }).click();
    } else {
      await page.goto(`${BASE}/projects/${projectId}`);
    }
    await expect(page).toHaveURL(new RegExp(`/projects/${projectId}$`));
    await expect(
      page.getByRole("main").getByRole("heading", { name: /^e2e project$/i }),
    ).toBeVisible({ timeout: 20000 });
  }

  async function uploadBoq(page: Page) {
    await openProjectDetail(page);
    await page.getByRole("tab", { name: /boqs/i }).click();
    await page.locator('input[type="file"]').setInputFiles({
      name: "test-boq.json",
      mimeType: "application/json",
      buffer: Buffer.from(
        JSON.stringify([
          {
            line_number: 1,
            description: "Civil Works",
            unit: "sqm",
            quantity: 100,
            rate: 500,
          },
        ]),
      ),
    });
    await page.getByRole("button", { name: /upload boq/i }).click();
    await expect(page.getByText("v1")).toBeVisible({ timeout: 10000 });
  }

  async function createQuote(page: Page) {
    await uploadBoq(page);
    await page.getByRole("tab", { name: /quotes/i }).click();
    await page.getByRole("button", { name: /new quote/i }).click();
    await page.getByRole("combobox").first().click();
    await page.getByRole("option").first().click();
    await page.getByRole("button", { name: /create quote/i }).click();
    await expect(page.getByText("Draft").first()).toBeVisible({
      timeout: 10000,
    });
  }

  test("admin can upload BOQ and generate quote", async ({ page }) => {
    await createQuote(page);
  });

  test("quote approval workflow", async ({ page }) => {
    await createQuote(page);

    // Open the draft quote from the list.
    const quoteRow = page
      .locator("table tbody tr")
      .filter({ hasText: "Draft" })
      .first();
    await expect(quoteRow).toBeVisible({ timeout: 10000 });
    await quoteRow.locator("button").first().click();
    await expect(
      page.getByRole("button", { name: /submit for approval/i }),
    ).toBeVisible({
      timeout: 10000,
    });

    // Draft → Pending Approval → Approved → Sent → Accepted.
    await page.getByRole("button", { name: /submit/i }).click();
    await expect(page.getByText("Pending Approval")).toBeVisible({
      timeout: 10000,
    });

    const approveBtn = page.getByRole("button", { name: /^approve$/i });
    await expect(approveBtn).toBeVisible({ timeout: 10000 });
    await approveBtn.click();
    await expect(page.getByText("Approved", { exact: true })).toBeVisible({
      timeout: 10000,
    });

    const sendBtn = page.getByRole("button", { name: /send to client/i });
    await expect(sendBtn).toBeVisible({ timeout: 10000 });
    await sendBtn.click();
    await expect(page.getByText("Sent", { exact: true })).toBeVisible({
      timeout: 10000,
    });

    const acceptBtn = page.getByRole("button", { name: /record: accepted/i });
    await expect(acceptBtn).toBeVisible({ timeout: 10000 });
    await acceptBtn.click();
    await expect(page.getByText("Accepted", { exact: true })).toBeVisible({
      timeout: 10000,
    });
  });
});
