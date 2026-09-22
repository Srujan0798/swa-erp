// Shared E2E helpers. Tests run against the isolated scratch stack
// (scripts/run_e2e.sh) via E2E_BASE_URL / E2E_API_URL; defaults target the
// local dev server.
export const BASE = process.env.E2E_BASE_URL || "http://localhost:3100";
export const API = process.env.E2E_API_URL || "http://localhost:8100";
