import { test, expect } from "@playwright/test";

test("dashboard shows stats for admin", async ({ page }) => {
  await page.goto("http://localhost:3000/login");
  await page.getByLabel("Email").fill("admin@swa.co.in");
  await page.getByLabel("Password").fill("admin123!");
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);
  await expect(page.getByText(/total active projects/i)).toBeVisible();
  await expect(page.getByText(/total estimated value/i)).toBeVisible();
  await expect(page.getByRole("heading", { name: /recent projects/i })).toBeVisible();
  await expect(page.getByRole("heading", { name: /recent clients/i })).toBeVisible();
});