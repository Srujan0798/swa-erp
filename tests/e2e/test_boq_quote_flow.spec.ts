import { test, expect } from "@playwright/test";

test.describe("BOQ & Quote flow", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("http://localhost:3000/login");
    await page.getByLabel("Email").fill("admin@swa.co.in");
    await page.getByLabel("Password").fill("admin123!");
    await page.getByRole("button", { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test("admin can upload BOQ and generate quote", async ({ page }) => {
    await page.goto("http://localhost:3000/projects");
    const projectRow = page.locator("table tbody tr").first();
    await projectRow.getByRole("link", { name: /view|open|details/i }).first().click();
    await expect(page).toHaveURL(/\/projects\/[a-f0-9-]+/);

    await page.getByRole("tab", { name: /boqs/i }).click();

    await page.locator('input[type="file"]').setInputFiles({
      name: "test-boq.json",
      mimeType: "application/json",
      buffer: Buffer.from(JSON.stringify([
        { line_number: 1, description: "Civil Works", unit: "sqm", quantity: 100, rate: 500 },
      ])),
    });
    await page.getByRole("button", { name: /upload boq/i }).click();
    await expect(page.getByText("v1")).toBeVisible({ timeout: 10000 });

    await page.getByRole("tab", { name: /quotes/i }).click();
    await page.getByRole("button", { name: /new quote/i }).click();

    await page.getByRole("combobox").first().click();
    await page.getByRole("option").first().click();
    await page.getByRole("button", { name: /create quote/i }).click();
    await expect(page.getByText("Draft")).toBeVisible({ timeout: 10000 });
  });

  test("quote approval workflow", async ({ page }) => {
    await page.goto("http://localhost:3000/projects");
    const projectRow = page.locator("table tbody tr").first();
    await projectRow.getByRole("link", { name: /view|open|details/i }).first().click();
    await expect(page).toHaveURL(/\/projects\/[a-f0-9-]+/);

    await page.getByRole("tab", { name: /quotes/i }).click();
    const quoteRow = page.locator("table tbody tr").first();
    if (await quoteRow.isVisible()) {
      await quoteRow.getByRole("button", { name: /view|details/i }).first().click();

      const submitBtn = page.getByRole("button", { name: /submit/i });
      if (await submitBtn.isVisible()) {
        await submitBtn.click();
        await expect(page.getByText("Pending Approval")).toBeVisible({ timeout: 10000 });
      }

      const approveBtn = page.getByRole("button", { name: /approve/i });
      if (await approveBtn.isVisible()) {
        await approveBtn.click();
        await expect(page.getByText("Approved")).toBeVisible({ timeout: 10000 });
      }

      const sendBtn = page.getByRole("button", { name: /send to client/i });
      if (await sendBtn.isVisible()) {
        await sendBtn.click();
        await expect(page.getByText("Sent")).toBeVisible({ timeout: 10000 });
      }

      const acceptBtn = page.getByRole("button", { name: /record: accepted/i });
      if (await acceptBtn.isVisible()) {
        await acceptBtn.click();
        await expect(page.getByText("Accepted")).toBeVisible({ timeout: 10000 });
      }
    }
  });
});
