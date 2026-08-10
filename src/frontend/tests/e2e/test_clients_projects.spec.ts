import { test, expect } from "@playwright/test";

test("admin can create a client", async ({ page }) => {
  await page.goto("http://localhost:3100/login");
  await page.getByLabel("Email").fill("admin@swa.co.in");
  await page.getByLabel("Password").fill("admin123!");
  await page.getByRole("button", { name: /sign in/i }).click();
  await page.goto("http://localhost:3100/clients/new");
  await page.getByLabel("Name").fill("Test Client Corp");
  await page.getByLabel("Code").fill("TCC-001");
  await page.getByLabel("Primary Email").fill("test@client.com");
  await page.getByRole("button", { name: /save/i }).click();
  await expect(page.getByText("Test Client Corp")).toBeVisible();
});

test("admin can create a project and transition it", async ({ page }) => {
  await page.goto("http://localhost:3100/login");
  await page.getByLabel("Email").fill("admin@swa.co.in");
  await page.getByLabel("Password").fill("admin123!");
  await page.getByRole("button", { name: /sign in/i }).click();
  await page.goto("http://localhost:3100/projects/new");
  await page.getByLabel("Name").fill("Test Project");
  await page.getByLabel("Code").fill("TP-001");
  await page.getByLabel("Client").selectOption({ index: 0 });
  await page.getByRole("button", { name: /save/i }).click();
  await expect(page.getByText("Test Project")).toBeVisible();
  await expect(page.getByText("Lead")).toBeVisible();
  await page.getByLabel("Next Status").selectOption("Quote");
  await page.getByRole("button", { name: /transition/i }).click();
  await expect(page.getByText("Quote")).toBeVisible();
});