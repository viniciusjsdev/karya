# Render Standard

Use Render as an optional backend hosting target for Django APIs.

## When to Use

Use Render when:

- the project needs a hosted Django backend
- the user wants less VPS maintenance
- the backend should deploy from Git or Docker
- a managed web service is enough for the MVP

Do not make Render mandatory. It is one supported backend host alongside Railway, Fly.io, VPS/container hosts and others.

## Deployment Paths

Supported paths:

- native Python web service
- Docker web service
- `render.yaml` Blueprint
- Terraform with the official `render-oss/render` provider

Prefer Docker when the project already has production Dockerfiles or needs reproducible OS-level dependencies. Prefer native Python runtime when the backend is simple and the project wants the fastest Render setup.

Prefer Terraform when the approved infrastructure decision coordinates Render with Vercel and Supabase in one stateful declarative workflow. Do not manage the same Render service with both Terraform and `render.yaml`.

## Django Requirements

Document or configure:

- `DATABASE_URL`
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS`
- `RENDER_EXTERNAL_HOSTNAME` handling when useful
- `PORT` handling, defaulting to Render's expected web service port behavior
- `gunicorn` or ASGI-compatible production server command
- migration command
- static file strategy, usually WhiteNoise for simple Django apps
- health check path
- CORS origins for Vercel preview/production domains

## Native Python Runtime

For native Python runtime, document:

- backend root directory in a monorepo
- Python version
- build command, often install dependencies plus `collectstatic`
- start command, usually gunicorn
- pre-deploy command for migrations when configured

## Docker Runtime

For Docker runtime, document:

- Dockerfile path, usually `backend/Dockerfile.prod`
- Docker build context
- start command or Docker `CMD`
- `.dockerignore`
- no secrets in Docker build args

Render can pass service env vars as Docker build args. Do not reference build args that contain secrets in Dockerfiles because they can be captured in images or layers.

## Blueprints

Use `render.yaml` when the project selects provider-native Render Blueprint IaC instead of Terraform for that service.

Rules:

- define web service and optional database/env groups
- use `sync: false` for dashboard-provided secrets
- use `generateValue: true` for generated secrets when appropriate
- do not hardcode API keys, database passwords or service role keys
- document that `sync: false` values are prompted during initial Blueprint creation and may need manual updates later

## Terraform

When Terraform is selected:

- use the official `render-oss/render` provider and pin a reviewed compatible version
- import existing services by service ID before reconciling them
- configure the backend root/Dockerfile path, build/start/pre-deploy commands, health check and custom domains supported by the pinned provider
- use provider authentication environment variables or an approved CI secret store
- keep secrets out of committed HCL and recognize that Terraform-managed secret values remain in state
- record `render.yaml` resources as separate ownership or remove the duplicate management path
- review replacement, plan/billing and domain changes before apply

## Database Choice

If the project uses Supabase Postgres, Render should receive `DATABASE_URL` from Supabase and should not create a second Render Postgres database unless explicitly requested.

If the project uses Render Postgres, document that Supabase Auth/Storage assumptions no longer apply unless Supabase is still used for those services.

## Validation

Before claiming Render readiness, document or attempt:

- build command
- start command
- migration/pre-deploy command
- health check path
- required env vars
- logs location
- CORS behavior from Vercel frontend to Render backend
