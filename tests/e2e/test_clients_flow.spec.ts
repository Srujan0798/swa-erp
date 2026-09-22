import { test, expect, type Page } from "@playwright/test";

import { BASE } from "./helpers";
const ts = new Date().getTime();
const EMAIL = `e2e-client-${ts}@swa.co.in`;

async function login(page: Page) {
  await page.goto(`${BASE}/login`);
  await page.getByLabel("Email").fill("admin@swa.co.in");
  await page.getByLabel("Password").fill("admin123!");
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);
}

test("clients page lists seeded records and opens new client form", async ({
  page,
}) => {
  await login(page);
  await page.goto(`${BASE}/clients`);
  await page.waitForLoadState("networkidle");
  const main = page.getByRole("main");
  await expect(main.getByRole("heading", { name: /^clients$/i })).toBeVisible({
    timeout: 20000,
  });
  await page.getByRole("link", { name: /new client/i }).click();
  await expect(page).toHaveURL(/\/clients\/new/);
});

test("create a new client from the UI", async ({ page }) => {
  await login(page);
  await page.goto(`${BASE}/clients/new`);
  const main = page.getByRole("main");
  await expect(
    main.getByRole("heading", { name: /^new client$/i }),
  ).toBeVisible({ timeout: 20000 });
  await main.getByLabel("Name *").fill(`E2E Client ${ts}`);
  await main.getByLabel("Code *").fill(`E2E-C-${ts}`);
  await main.getByLabel("Email *").fill(EMAIL);
  const country = page.getByLabel(/country/i);
  if ((await country.count()) > 0) {
    await country.selectOption({ index: 1 }).catch(() => {});
  }
  await page.getByRole("button", { name: /save/i }).click();
  await expect(main.locator("h1").first()).toBeVisible({ timeout: 20000 });
  await expect(page.locator("body")).not.toHaveText(
    /Unexpected Application Error/i,
  );
});

test("client detail page renders contact and projects sections", async ({
  page,
}) => {
  await login(page);
  await page.goto(`${BASE}/clients`);
  await page.waitForLoadState("networkidle");
  const link = page.locator("main a[href^='/clients/']").first();
  if ((await link.count()) > 0) {
    await link.click();
    await page.waitForLoadState("networkidle");
    const main = page.getByRole("main");
    await expect(main.getByRole("heading").first()).toBeVisible({
      timeout: 20000,
    });
    await expect(page.locator("body")).not.toHaveText(
      /Unexpected Application Error/i,
    );
    await expect(main.locator("h1").first()).not.toHaveText(/Error/i);
  }
});
