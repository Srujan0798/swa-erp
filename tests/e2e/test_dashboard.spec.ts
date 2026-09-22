import { test, expect } from "@playwright/test";

test("dashboard shows workflow chain and stats for admin", async ({ page }) => {
  await page.goto("http://localhost:3100/login");
  await page.getByLabel("Email").fill("admin@swa.local");
  await page.getByLabel("Password").fill("admin123!");
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);
  const main = page.getByRole("main");
  await expect(main.getByText(/SWA operations/i)).toBeVisible();
  await expect(main.getByText(/total active projects/i)).toBeVisible();
  await expect(main.getByText(/total estimated value/i)).toBeVisible();
  await expect(main.getByText(/in quote stage/i)).toBeVisible();
  await expect(main.getByText(/in execution/i)).toBeVisible();
  // Core workflow chain is rendered on the dashboard.
  for (const step of [
    "Inquiry",
    "Client",
    "Project",
    "Service Agreement",
    "Token",
    "Document Ref",
    "Time log",
  ]) {
    await expect(main.getByText(new RegExp(step)).first()).toBeVisible();
  }
});
