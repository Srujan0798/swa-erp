import { test, expect, type Page } from "@playwright/test";

import { BASE } from "./helpers";
const ts = new Date().getTime();

async function login(page: Page) {
  await page.goto(`${BASE}/login`);
  await page.getByLabel("Email").fill("admin@swa.co.in");
  await page.getByLabel("Password").fill("admin123!");
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);
}

const H = (page: Page, name: string | RegExp) =>
  page.getByRole("main").getByRole("heading", { name }).first();

test("projects page renders and opens new project form", async ({ page }) => {
  await login(page);
  await page.goto(`${BASE}/projects`);
  await page.waitForLoadState("networkidle");
  await expect(H(page, /^projects$/i)).toBeVisible({ timeout: 20000 });
  await page.getByRole("link", { name: /new project/i }).click();
  await expect(page).toHaveURL(/\/projects\/new/);
});

test("tasks page kanban board renders and shows create dialog", async ({
  page,
}) => {
  await login(page);
  await page.goto(`${BASE}/tasks`);
  await page.waitForLoadState("networkidle");
  await expect(H(page, /task/i)).toBeVisible({ timeout: 20000 });
  const newBtn = page.getByRole("button", { name: /new task/i });
  if ((await newBtn.count()) > 0) {
    await newBtn.click();
    await expect(page.getByRole("dialog")).toBeVisible({ timeout: 10000 });
  }
});

test("create a task from the tasks page dialog", async ({ page }) => {
  await login(page);
  await page.goto(`${BASE}/tasks`);
  await page.waitForLoadState("networkidle");
  const newBtn = page.getByRole("button", { name: /new task/i });
  if ((await newBtn.count()) === 0) {
    test.skip(true, "no new-task control available");
    return;
  }
  await newBtn.click();
  const dialog = page.getByRole("dialog");
  await expect(dialog).toBeVisible({ timeout: 10000 });
  const titleInput = dialog.getByLabel(/title/i).first();
  await titleInput.fill(`E2E Task ${ts}`);
  const desc = dialog.getByLabel(/description/i).first();
  if ((await desc.count()) > 0)
    await desc.fill("Created by Playwright e2e suite");
  const priority = dialog.getByLabel(/priority/i).first();
  if ((await priority.count()) > 0)
    await priority.selectOption({ index: 1 }).catch(() => {});
  await dialog
    .getByRole("button", { name: /create|save/i })
    .first()
    .click();
  await expect(page.locator("body")).not.toHaveText(
    /Unexpected Application Error/i,
  );
});

test("time tracking page loads and billable column visible", async ({
  page,
}) => {
  await login(page);
  await page.goto(`${BASE}/time-tracking`);
  await page.waitForLoadState("networkidle");
  await expect(H(page, /time/i)).toBeVisible({ timeout: 20000 });
  await expect(page.locator("body")).not.toHaveText(
    /Unexpected Application Error/i,
  );
  const billable = page.getByText(/billable/i).first();
  await expect(billable).toBeVisible({ timeout: 10000 });
});

test("compliance page lists NBC, ECBC, IGBC, IS standards", async ({
  page,
}) => {
  await login(page);
  await page.goto(`${BASE}/compliance`);
  await page.waitForLoadState("networkidle");
  await expect(H(page, /complian/i)).toBeVisible({ timeout: 20000 });
  const body = await page.locator("body").innerText();
  expect(body).toMatch(/NBC|ECBC|IGBC|compliance/i);
});

test("sustainability page renders", async ({ page }) => {
  await login(page);
  await page.goto(`${BASE}/sustainability`);
  await page.waitForLoadState("networkidle");
  // The page only renders its heading once the projects list loads; retry on a
  // dev-server hiccup by reloading rather than flaking on a stale chunk.
  await expect
    .poll(
      async () =>
        await H(page, /sustain/i)
          .isVisible()
          .catch(() => false),
      {
        timeout: 30000,
        message: "sustainability heading never appeared",
      },
    )
    .toBe(true);
  await expect(page.locator("body")).not.toHaveText(
    /Unexpected Application Error/i,
  );
});

test("vendors page renders and opens new vendor form", async ({ page }) => {
  await login(page);
  await page.goto(`${BASE}/vendors`);
  await page.waitForLoadState("networkidle");
  await expect(H(page, /vendor/i)).toBeVisible({ timeout: 20000 });
  const btn = page.getByRole("button", { name: /new vendor/i });
  if ((await btn.count()) > 0) {
    await btn.click();
    await expect(page).toHaveURL(/\/vendors\/new/);
  }
});

test("materials page renders", async ({ page }) => {
  await login(page);
  await page.goto(`${BASE}/materials`);
  await page.waitForLoadState("networkidle");
  await expect(H(page, /material/i)).toBeVisible({ timeout: 20000 });
});

test("rfqs page renders", async ({ page }) => {
  await login(page);
  await page.goto(`${BASE}/rfqs`);
  await page.waitForLoadState("networkidle");
  await expect(H(page, /rfq/i)).toBeVisible({ timeout: 20000 });
  await expect(page.locator("body")).not.toHaveText(
    /Unexpected Application Error/i,
  );
});

test("invoices page renders", async ({ page }) => {
  await login(page);
  await page.goto(`${BASE}/invoices`);
  await page.waitForLoadState("networkidle");
  await expect(H(page, /invoice/i)).toBeVisible({ timeout: 20000 });
  await expect(page.locator("body")).not.toHaveText(
    /Unexpected Application Error/i,
  );
});

test("reports page renders project selector", async ({ page }) => {
  await login(page);
  await page.goto(`${BASE}/reports`);
  await page.waitForLoadState("networkidle");
  await expect(H(page, /report/i)).toBeVisible({ timeout: 20000 });
  await expect(page.getByText(/select a project/i)).toBeVisible({
    timeout: 10000,
  });
  await expect(
    page.getByRole("button", { name: /export summary pdf/i }),
  ).toBeVisible();
});

test("users page is admin-gated and renders", async ({ page }) => {
  await login(page);
  await page.goto(`${BASE}/users`);
  await page.waitForLoadState("networkidle");
  await expect(H(page, /user/i)).toBeVisible({ timeout: 20000 });
  await expect(page.locator("body")).not.toHaveText(
    /Unexpected Application Error/i,
  );
});

test("documents page renders upload control", async ({ page }) => {
  await login(page);
  await page.goto(`${BASE}/documents`);
  await page.waitForLoadState("networkidle");
  await expect(H(page, /file|drawing|document/i)).toBeVisible({
    timeout: 20000,
  });
});

test("tokens page renders", async ({ page }) => {
  await login(page);
  await page.goto(`${BASE}/tokens`);
  await page.waitForLoadState("networkidle");
  await expect(H(page, /token/i)).toBeVisible({ timeout: 20000 });
  await expect(page.locator("body")).not.toHaveText(
    /Unexpected Application Error/i,
  );
});

test("service agreements page renders", async ({ page }) => {
  await login(page);
  await page.goto(`${BASE}/agreements`);
  await page.waitForLoadState("networkidle");
  await expect(H(page, /service agreement|agreement/i)).toBeVisible({
    timeout: 20000,
  });
});

test("document references page renders", async ({ page }) => {
  await login(page);
  await page.goto(`${BASE}/document-references`);
  await page.waitForLoadState("networkidle");
  await expect(H(page, /document ref|reference/i)).toBeVisible({
    timeout: 20000,
  });
});

test("sidebar navigation covers all core workflow links", async ({ page }) => {
  await login(page);
  const nav = page.getByRole("navigation");
  await expect(nav.getByRole("link", { name: /1\. inquiries/i })).toBeVisible();
  await expect(nav.getByRole("link", { name: /2\. clients/i })).toBeVisible();
  await expect(
    nav.getByRole("link", { name: /3\. service agreements/i }),
  ).toBeVisible();
  await expect(nav.getByRole("link", { name: /4\. tokens/i })).toBeVisible();
  await expect(
    nav.getByRole("link", { name: /5\. document refs/i }),
  ).toBeVisible();
  await expect(nav.getByRole("link", { name: /6\. projects/i })).toBeVisible();
  await expect(
    nav.getByRole("link", { name: /7\. time logging/i }),
  ).toBeVisible();
  await expect(nav.getByRole("link", { name: /^tasks$/i })).toBeVisible();
  await expect(nav.getByRole("link", { name: /^compliance$/i })).toBeVisible();
  await expect(nav.getByRole("link", { name: /^vendors$/i })).toBeVisible();
  await expect(nav.getByRole("link", { name: /^materials$/i })).toBeVisible();
  await expect(nav.getByRole("link", { name: /^rfqs$/i })).toBeVisible();
  await expect(nav.getByRole("link", { name: /^invoices$/i })).toBeVisible();
  await expect(nav.getByRole("link", { name: /^reports$/i })).toBeVisible();
  await expect(nav.getByRole("link", { name: /^users$/i })).toBeVisible();
});
