import { test, expect } from "@playwright/test";

test("admin can log in and reach dashboard", async ({ page }) => {
  await page.goto("http://localhost:3000/login");
  await page.getByLabel("Email").fill("admin@swa.co.in");
  await page.getByLabel("Password").fill("admin123!");
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);
  await expect(page.getByRole("heading", { name: /welcome to swa erp/i })).toBeVisible();
});

test("invalid credentials show error", async ({ page }) => {
  await page.goto("http://localhost:3000/login");
  await page.getByLabel("Email").fill("admin@swa.co.in");
  await page.getByLabel("Password").fill("wrong");
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page.getByText(/invalid credentials/i)).toBeVisible();
});

test("non-admin gets blocked from /users", async ({ page }) => {
  await page.goto("http://localhost:3000/login");
  await page.getByLabel("Email").fill("pm@swa.co.in");
  await page.getByLabel("Password").fill("pm123!");
  await page.getByRole("button", { name: /sign in/i }).click();
  await page.goto("http://localhost:3000/users");
  await page.waitForURL(url => !url.pathname.includes("/users"));
  const url = page.url();
  expect(url.includes("/users")).toBe(false);
});

test("logout returns to login", async ({ page }) => {
  await page.goto("http://localhost:3000/login");
  await page.getByLabel("Email").fill("admin@swa.co.in");
  await page.getByLabel("Password").fill("admin123!");
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);
  await page.getByRole("button", { name: /logout/i }).click();
  await expect(page).toHaveURL(/\/login/);
});