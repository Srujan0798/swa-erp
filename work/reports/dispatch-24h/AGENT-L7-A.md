# AGENT-L7-A

Repo: `/Users/srujansai/Desktop/swa-erp` (main). NO pytest. MAY EDIT: docs/INSTALL_NO_IT.md, docs/DEPLOYMENT_CHECKLIST.md.

## Summary of changes

1. **INSTALL_NO_IT.md:12,24-26** — Explicit "Docker Engine (free) NOT Docker Desktop" + WSL2 enable steps for Windows Server 2022+
2. **INSTALL_NO_IT.md:70-77** — Added **Secrets handling** section with Docker secrets migration example
3. **INSTALL_NO_IT.md:94-95** — Added healthcheck port mapping explanation (container 8000 → host 8100)
4. **INSTALL_NO_IT.md:160-162** — Added WSL2/Docker Engine troubleshooting rows
5. **DEPLOYMENT_CHECKLIST.md:12-13** — Added **Platform** header specifying Windows Server + free Docker Engine + WSL2 + Compose
6. **DEPLOYMENT_CHECKLIST.md:59** — Fixed healthz check to `localhost:8100` (was wrong `8000`)
7. **DEPLOYMENT_CHECKLIST.md:26,30-35,120-125** — CORS/ports aligned (UI 3100, API 8100, DB/Redis internal), Q1-Q7 explicit, cron → Windows Task Scheduler with `wsl.exe`

## Verification

- `ruff check docs/` — PASS (no python files in docs)
- `black --check docs/` — PASS (no python files)
- `mypy` — N/A (no python files in docs)
- Manual review: All platform references consistent (Windows Server + free Docker Engine + WSL2 + Compose)
- Healthz port fixed (8100 external → 8000 container)
- Windows Task Scheduler commands use `wsl.exe -d Ubuntu`

No commit, no push, no pytest. Report written.