# Deployment

## Dev (now)
See `runbook.md` for local dev setup via docker-compose.

## Staging / Production (filled in by wave-8)

Placeholder. To be designed in wave-8 (Reports + Deliverables) once we know real load patterns from staging tests.

### Target architecture (tentative)
- Single VPS (4 vCPU / 8GB RAM / 100GB SSD) on Hetzner or DigitalOcean
- Docker Compose with reverse proxy (Caddy or Nginx + Certbot for SSL)
- Postgres on same VPS with daily pg_dump to S3-compatible storage (e.g., Backblaze B2)
- Redis on same VPS (data is non-critical; queue jobs lost-OK)
- MinIO on same VPS for documents (mountable to host filesystem)
- Sentry SaaS for error tracking
- Uptime monitoring via Uptime Kuma or BetterStack

### When to migrate to k8s
- > 100 concurrent users
- > 5,000 projects
- Multi-region needed
- Team larger than 5 engineers

Until then: docker-compose is sufficient.
