---
name: karya-infra-orchestrator
description: Use this skill when creating or normalizing Karya infrastructure for a monorepo with frontend, backend, Docker, Docker Compose, Terraform, Render, Supabase and Vercel. It creates local container orchestration, provider-scoped Terraform for declarative cloud infrastructure, frontend/backend Dockerfiles, environment contracts, deployment guidance and validation commands. Do not use this skill for frontend UI refactors or backend business logic.
---

# Karya Infra Orchestrator

## Purpose

Create and normalize infrastructure for Karya projects.

The standard repository may have:

```txt
frontend/
backend/
supabase/
infra/terraform/
docs/
.agents/skills/
.codex/
docker-compose.yml
docker-compose.prod.yml
Makefile
.env.example
AGENTS.md
README.md
```

## Core Principle

Local must be easy. Production and infrastructure ownership must be explicit. Vercel must not be confused with a generic Docker host.

Use Docker for local orchestration and backend deployability. Use Vercel for frontend deployment from `/frontend`. Use Supabase for managed Postgres/Auth/Storage when configured. Use Render as a supported backend hosting option when the project needs managed Django web service hosting without managing a VPS.

Use Terraform when the project wants Render, Vercel and Supabase resources coordinated through one declarative workflow. Terraform is optional, must not take over an existing resource silently, and must not share management of the same resource with a provider-native manifest or dashboard workflow.

Do not promise one production path. Support local/full Docker, VPS/full-stack container deployment, Vercel-native frontend deployment, backend container deployment on Render or similar hosts, Render native Python deployment when appropriate, and Supabase-managed services.

## Modes

### Local / Full Docker

Use for local development and full-stack smoke testing:

- frontend container
- backend container
- local db container when not using remote Supabase
- shared Docker network
- hot reload when practical

### Cloud Split

Use for common MVP deployment:

- frontend on Vercel from `/frontend`
- backend on Render, VPS, Railway, Fly.io or compatible host
- Supabase as managed Postgres/Auth/Storage

### Declarative Cloud Split

Use when Terraform is requested or the approved infrastructure decision selects it:

- Terraform root under `infra/terraform/`
- official `render-oss/render`, `vercel/vercel` and `supabase/supabase` providers only when each platform is used
- one declared owner for every managed resource
- imports for existing resources before reconciliation
- remote state for shared or production environments
- reviewed `terraform plan` before any explicitly approved apply

## Load References

Read the relevant references before changing files:

- `references/root-architecture-standard.md`
- `references/docker-compose-standard.md`
- `references/frontend-docker-standard.md`
- `references/backend-docker-standard.md`
- `references/supabase-standard.md`
- `references/vercel-standard.md`
- `references/render-standard.md`
- `references/terraform-standard.md` when Terraform is selected or requested
- `references/env-standard.md`
- `references/validation-checklist.md`

Run `scripts/scan-infra.mjs` after changes when possible.

## Root Architecture

Expected root:

```txt
/
  frontend/
  backend/
  supabase/
  infra/
    terraform/
  docs/
  .agents/
    skills/
  .codex/
  docker-compose.yml
  docker-compose.override.yml
  docker-compose.prod.yml
  Makefile
  .env.example
  AGENTS.md
  README.md
```

## Docker Compose Standard

Create `docker-compose.yml` for local development.

Required services when available:

```txt
frontend
backend
db
```

`db` is optional when the project uses remote Supabase only. If included, clearly label it as a local development fallback.

Recommended ports:

```txt
frontend: 5173 or app-specific dev port
backend: 8000
db: 5432
```

Use named volumes for database data, a shared network and healthchecks where practical.

Do not put secrets directly in compose files. Read from root `.env`.

## Frontend Docker Standard

Create:

```txt
frontend/Dockerfile
frontend/Dockerfile.prod
frontend/.dockerignore
```

Development Dockerfile should:

- use Node LTS image
- install dependencies with npm by default
- support Vite/TanStack/React dev server
- bind to `0.0.0.0`
- expose the correct dev port
- preserve hot reload when mounted via Compose

Production Dockerfile should:

- build static frontend
- serve using nginx or another lightweight static server when running outside Vercel
- not be required for Vercel native deploy

Important: Vercel deployment should use the `/frontend` root directory and framework build command/output directory, not the frontend Dockerfile, unless the deployment platform explicitly supports custom containers.

## Backend Docker Standard

Create:

```txt
backend/Dockerfile
backend/Dockerfile.prod
backend/.dockerignore
backend/entrypoint.sh
```

Development backend should install Python dependencies, run Django development server, expose port `8000`, and mount source for fast development.

Production backend should use a slim Python image, install only required dependencies, run migrations explicitly or through a controlled entrypoint, collect static files if needed, run gunicorn, expose port `8000`, and use environment variables.

Do not hardcode secrets.

## Render Standard

Use Render when the MVP needs a hosted Django API without managing a VPS.

Supported Render backend paths:

- native Python web service
- Docker web service built from `backend/Dockerfile.prod`
- `render.yaml` Blueprint when the project selects provider-native Render IaC
- Terraform-managed web service when cross-provider declarative infrastructure is selected

For Django on Render, document:

- service root or Dockerfile path for monorepos
- build command
- start command
- pre-deploy command for migrations when used
- `DATABASE_URL`
- `DJANGO_SECRET_KEY` or equivalent
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS` including `.onrender.com` host and custom domains
- `RENDER_EXTERNAL_HOSTNAME` handling when used
- static file strategy such as WhiteNoise or external object storage
- `WEB_CONCURRENCY` or worker strategy
- health check path
- environment groups and secret handling

If generating `render.yaml`, never hardcode secrets. Use `sync: false`, `generateValue: true`, Render environment groups, or dashboard-managed values for secrets.

Do not manage the same Render service with both Terraform and `render.yaml`. Record which mechanism owns each service and import an existing service before Terraform manages it.

Do not put Render-only assumptions into local Docker Compose. Keep Render deployment docs separate from local development docs.

## Environment Standard

Create:

```txt
.env.example
frontend/.env.example
backend/.env.example
```

Root `.env.example` should include:

```env
COMPOSE_PROJECT_NAME=karya_project

FRONTEND_PORT=5173
BACKEND_PORT=8000

VITE_API_BASE_URL=http://localhost:8000/api

DJANGO_SETTINGS_MODULE=config.settings.local
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,backend

DATABASE_URL=postgresql://postgres:postgres@db:5432/app

SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
```

Never commit real secrets.

## Supabase Standard

Create when Supabase is part of the stack:

```txt
supabase/
  migrations/
  seed.sql
  config.toml
```

Use Supabase when the product needs managed Postgres, Auth, Storage, Realtime or Edge Functions.

For Django-backed products:

- Django can connect to Supabase Postgres through `DATABASE_URL`.
- Django migrations own backend domain tables by default.
- Supabase migrations can be used for Auth/Storage/RLS-specific resources.
- If Supabase SQL migrations are the source of truth for all schema, document that decision clearly.

Do not create conflicting schema ownership silently.

For local Supabase development, prefer Supabase CLI structure and migrations. Keep `supabase/config.toml`, migrations and seed files versioned when generated.

Supabase CLI uses Docker for the local stack. Do not duplicate Supabase services inside the app Compose file unless there is a documented reason. On untrusted public networks, document binding the local Supabase stack to localhost and never expose the local Supabase stack publicly.

Production readiness must be documented rather than assumed. Include a Supabase checklist covering Security Advisor, RLS, SSL enforcement, network restrictions, MFA, access control, custom SMTP/Auth email settings, Auth rate limits, CAPTCHA/abuse prevention when relevant, indexes/performance review, load testing for expected launch traffic, backups/PITR when needed, and secret handling.

The Supabase anon key may be used by frontend code only when RLS and policies are correctly designed. The service role key must stay server-side only and must never appear in `frontend/.env.example`, Vercel frontend env vars, client code or logs.

## Vercel Standard

Frontend deploy target:

```txt
Root Directory: frontend
Build Command: npm run build
Output Directory: dist or framework-specific output
```

Create `frontend/vercel.json` only when needed.

For monorepos, document that the Vercel project root directory should be `frontend`. When using Vercel CLI with a monorepo, run linking/deploy commands from the monorepo root and select the intended Vercel project.

Prefer Vercel's framework/build auto-detection. Override build command, install command or output directory only when the detected values are wrong.

Document Vercel environments separately:

- Development
- Preview
- Production

Frontend variables prefixed with `VITE_` are exposed to browser code at build/runtime and must not contain secrets. Put backend/API secrets only in backend/server environments.

Do not configure backend Django as a Vercel frontend deployment. Vercel supports Django through Vercel Functions, but that is an explicit alternative path with function/runtime limitations and a separate migration/static-file strategy. The Karya default is to prepare Django as a container for a container-friendly host.

## Terraform Standard

When Terraform is selected, create a provider-scoped root under `infra/terraform/` and follow `references/terraform-standard.md`.

Required decisions before generation:

- environments and account/team/organization ownership
- create vs import for each Render, Vercel and Supabase resource
- one management source per resource
- state backend, locking, encryption and access for shared/production state
- which non-secret values Terraform wires across providers
- which secrets remain in provider dashboards or an approved secret store

For Django-backed Supabase projects, keep domain tables under Django migrations by default. Terraform may manage Supabase projects, settings and branches, but must not run Django migrations, issue domain DDL, or introduce a PostgreSQL provider to own application tables unless an explicit schema-ownership decision changes that boundary.

Generate and review configuration through `fmt`, `init`, `validate` and `plan`. Never run `terraform apply`, `destroy`, state mutation or live imports without explicit approval. Treat plan files and state as sensitive artifacts.

## Makefile Standard

Create root `Makefile` with commands:

```makefile
up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

frontend-shell:
	docker compose exec frontend sh

backend-shell:
	docker compose exec backend sh

backend-check:
	docker compose run --rm backend python manage.py check

backend-test:
	docker compose run --rm backend python manage.py test

backend-migrate:
	docker compose run --rm backend python manage.py migrate

build:
	docker compose build

prod-build:
	docker compose -f docker-compose.prod.yml build
```

Use npm for frontend commands unless the project has a documented package-manager exception. Adapt backend commands to the available backend tooling.

When Terraform is selected, also add safe convenience targets for `terraform-fmt`, `terraform-init-local`, `terraform-validate` and `terraform-plan`. Do not add an unattended apply/destroy target.

## Documentation

Create or update:

```txt
docs/architecture/root-architecture.md
docs/architecture/infra-architecture.md
docs/architecture/deploy.md
README.md
```

Docs must explain how to run locally, stop containers, run migrations, run tests, connect frontend/backend, connect backend/Supabase/Postgres, configure Vercel, required env vars, and what is local-only vs production.

If Render is chosen or requested, docs must also explain how the Django backend is deployed on Render, whether it uses Docker or native Python runtime, how migrations run, how env vars are configured, and how Vercel frontend CORS/API URLs point to the Render backend.

If Terraform is selected, docs must also include a resource ownership matrix, create/import decisions, state backend and recovery process, provider authentication names without credential values, plan/apply approval flow, migration ownership, and any intentionally dashboard-managed settings.

## Validation Workflow

After creating or changing infra, run when possible:

```bash
docker compose config
docker compose build
docker compose up -d
docker compose ps
docker compose logs --tail=100
docker compose run --rm backend python manage.py check
docker compose down
```

If frontend exists:

```bash
docker compose run --rm frontend npm run build
```

If backend exists:

```bash
docker compose run --rm backend python manage.py test
```

If Supabase CLI is configured:

```bash
supabase status
```

If Terraform is configured:

```bash
terraform -chdir=infra/terraform fmt -check -recursive
terraform -chdir=infra/terraform init -backend=false
terraform -chdir=infra/terraform validate
terraform -chdir=infra/terraform providers
```

After remote state and authentication are approved:

```bash
terraform -chdir=infra/terraform init -reconfigure
terraform -chdir=infra/terraform plan -detailed-exitcode
```

Run authenticated planning only when credentials and a safe state decision are available. Interpret detailed exit code `0` as no changes, `2` as planned changes and `1` as failure. Review every create, update, replacement and destroy before requesting apply approval.

Do not claim infra works unless validation was attempted.

## Architecture Scan

Run:

```bash
node scripts/scan-infra.mjs
```

or the installed skill script path from the target project.

The script should check root Compose, frontend/backend Dockerfiles, env examples, obvious secrets, Makefile, docs, Vercel guidance, Supabase structure and Terraform ownership/state hygiene when applicable.

## Definition of Done

Work is done only when:

- root architecture is present
- frontend Docker files exist when frontend exists
- backend Docker files exist when backend exists
- root Compose exists
- production Compose exists if requested
- env examples exist
- secrets are not committed
- Supabase structure exists when applicable
- Vercel deployment guidance exists when frontend exists
- Render deployment guidance exists when Render is chosen or requested
- Terraform root, provider pins, lockfile, ownership documentation and state hygiene exist when Terraform is selected
- existing cloud resources are imported rather than recreated when Terraform adopts them
- no Render service is jointly managed by Terraform and `render.yaml`
- Django migrations remain the owner of backend domain tables unless an explicit approved decision says otherwise
- Makefile exists
- docs are updated
- Docker config/build/up validation was attempted
- Terraform fmt/init/validate and a safe plan were attempted when Terraform is selected
- failures are reported honestly
