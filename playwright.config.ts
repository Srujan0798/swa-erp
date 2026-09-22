import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 1,
  workers: process.env.CI ? 1 : 1,
  timeout: 60_000,
  reporter: "line",
  use: {
    // E2E runs against an isolated scratch stack (scripts/run_e2e.sh) via
    // E2E_BASE_URL; default is the local dev server on :3100.
    baseURL: process.env.E2E_BASE_URL || "http://localhost:3100",
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: {
    command: process.env.E2E_WEB_CMD || "npm --prefix src/frontend run dev",
    url: process.env.E2E_BASE_URL || "http://localhost:3100",
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});
