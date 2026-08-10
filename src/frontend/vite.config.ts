import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    // SWA-specific host ports (avoid clashing with other apps on 3000/8000)
    port: 3100,
    strictPort: true,
    proxy: {
      "/api": "http://localhost:8100",
      "/healthz": "http://localhost:8100",
    },
  },
});