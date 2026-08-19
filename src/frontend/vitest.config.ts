import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/vitest.setup.ts"],
    include: ["src/**/*.{test,spec}.{ts,tsx}"],
    coverage: {
      provider: "v8",
      reporter: ["text", "text-summary", "html"],
      reportsDirectory: "coverage",
      all: true,
      include: ["src/**/*.{ts,tsx}"],
      exclude: [
        "src/main.tsx",
        "src/vitest.setup.ts",
        "**/*.d.ts",
        "src/**/*.{test,spec}.{ts,tsx}",
      ],
      thresholds: {
        statements: 60,
        branches: 50,
        functions: 60,
        lines: 60,
      },
    },
  },
});
