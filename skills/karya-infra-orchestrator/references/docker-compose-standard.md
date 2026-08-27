# Docker Compose Standard

`docker-compose.yml` is for local development.

Use services that actually exist:

- `frontend` when `/frontend` exists
- `backend` when `/backend` exists
- `db` when using local Postgres

Use:

- named volumes for persistent db data
- shared network
- `.env` interpolation
- healthchecks where practical
- explicit ports

Avoid:

- hardcoded secrets
- production-only settings in local Compose
- assuming Vercel runs Dockerfiles

`docker-compose.prod.yml` is optional until production or VPS deployment is requested.

