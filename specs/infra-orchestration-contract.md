# Infra Orchestration Contract

## Producer

`karya-infra-orchestrator`

## Required Inputs

- frontend project path and npm/package-manager exception, if any
- backend project path and runtime
- frontend dev/build commands
- backend run/check/test commands
- expected frontend and backend ports
- database decision: local Postgres, Supabase Postgres or another provider
- Supabase usage decision for Auth, Storage, Realtime or Edge Functions
- Terraform selection decision and target environments
- create/import decision and declared owner for existing Render, Vercel and Supabase resources
- Terraform state backend, access and recovery decision for shared/production environments
- deployment preference, if known

## Required Outputs

- `docker-compose.yml` for local development
- `docker-compose.prod.yml` when full-stack container deployment is requested
- `frontend/Dockerfile`
- `frontend/Dockerfile.prod`
- `frontend/.dockerignore`
- `backend/Dockerfile`
- `backend/Dockerfile.prod`
- `backend/.dockerignore`
- `backend/entrypoint.sh`
- root `.env.example`
- service `.env.example` files
- `Makefile`
- `docs/architecture/infra-architecture.md`
- `docs/architecture/deploy.md`
- validation notes
- `infra/terraform/` with provider-scoped HCL and `.terraform.lock.hcl` when Terraform is selected
- Terraform ownership/import/state/plan notes when Terraform is selected

## Supabase Expectations

When Supabase is used, the output should document:

- whether Django migrations or Supabase migrations own domain tables
- how Supabase CLI files are versioned
- where migrations and seed SQL live
- whether the local Supabase stack is bound to localhost on untrusted networks
- how local development connects to Supabase or local Postgres
- required production checks for Security Advisor, RLS, SSL, network restrictions, MFA, access control, Auth SMTP/rate limits, abuse prevention, indexes, performance, load testing and backups/PITR when needed
- how service role keys are kept server-side only
- whether the frontend uses Supabase directly and, if so, why the anon key is safe with RLS/policies

## Deployment Modes

The skill must support multiple modes without presenting one as mandatory:

- local full-stack Docker
- VPS or compatible host running containers
- Vercel-native frontend from `frontend/`
- backend container deployment
- Render backend web service deployment when chosen
- Supabase-managed Postgres/Auth/Storage
- Terraform-managed Render/Vercel/Supabase cloud resources when explicitly selected

## Terraform Expectations

When Terraform is selected, the output should:

- use `infra/terraform/` as the declarative root
- use official `render-oss/render`, `vercel/vercel` and `supabase/supabase` providers only for selected platforms
- verify and pin reviewed compatible Terraform/provider versions and commit `.terraform.lock.hcl`
- maintain one declared owner for every resource
- import existing resources before reconciliation
- prohibit joint ownership of the same Render service by Terraform and `render.yaml`
- document Vercel GitHub integration authorization as a human prerequisite
- keep Django migrations as the default owner of backend domain tables
- keep Terraform out of Django ORM migrations and application-table DDL
- use remote encrypted, access-controlled state with recovery ownership for shared/production environments
- keep state, plans, provider credentials and secret variable files out of Git
- document that sensitive values can remain in Terraform state
- validate formatting, initialization, providers and configuration before an authenticated plan
- require explicit approval for live imports, state mutation, apply, destroy, replacement, billing or plan changes

Terraform is optional and must not become a prerequisite for local Docker or non-Terraform deployment paths.

## Vercel Expectations

When Vercel is used, the output should document:

- `frontend` as the Vercel project root directory for monorepos
- build command and output directory, using npm by default and Vercel auto-detection unless overrides are needed
- Development, Preview and Production environment variables
- which frontend variables are public/browser-exposed
- backend API URL per environment
- CORS requirements for Vercel preview and production domains
- why Django is not deployed as a Vercel frontend project

If Django on Vercel Functions is explicitly chosen, document runtime/function limitations, static files and migration strategy instead of treating it as the default path.

## Render Expectations

When Render is chosen for the backend, the output should document:

- native Python runtime vs Docker web service decision
- backend root directory or Dockerfile path in monorepos
- build command
- start command
- pre-deploy/migration command when used
- required environment variables
- environment groups or secret handling
- `render.yaml` Blueprint if provider-native Render IaC is selected instead of Terraform for that service
- `sync: false` or `generateValue: true` for secrets in Blueprints
- health check path
- static file strategy
- CORS/API URL wiring from Vercel frontend to Render backend

Do not create a Render Postgres database when the project already uses Supabase Postgres unless explicitly requested.

## Non-Goals

- Do not rewrite frontend UI.
- Do not implement backend business logic.
- Do not invent missing product requirements.
- Do not commit real secrets.
- Do not claim production readiness unless validation was attempted and remaining gaps are documented.
