# Supabase Standard

Use Supabase as managed Postgres/Auth/Storage/Realtime when the product needs those managed services.

## Local Development

Prefer Supabase CLI when using Supabase-specific features:

- `supabase init`
- `supabase start`
- `supabase migration new`
- `supabase db reset`
- `supabase db diff`
- `supabase db push`
- `supabase status`

Keep generated `supabase/config.toml`, migrations and seed files versioned when appropriate. The `supabase` folder created by `supabase init` is safe to commit when it does not contain secrets.

The CLI local stack uses Docker. Do not duplicate it blindly inside the app's own Compose file unless there is a clear reason.

On untrusted public networks, document binding the local Supabase stack to localhost through a dedicated Docker network. Never expose the local Supabase stack publicly.

## Schema Ownership

For Django-backed products:

- Django migrations own backend domain tables by default.
- Supabase migrations can own Auth/Storage/RLS-specific SQL.
- Supabase can become the source of truth for other SQL schema only after an explicit approved ownership decision.

Do not mix schema ownership silently.

Terraform may manage the Supabase project, supported project settings and branches, but it must not own Django domain tables, run ORM migrations or apply application DDL. Do not introduce a PostgreSQL Terraform provider, SQL resources or shell provisioners for backend domain schema unless the approved schema-ownership contract explicitly changes.

## Terraform

When Terraform is selected:

- use the official `supabase/supabase` provider and pin a reviewed compatible version
- import an existing project before managing it
- reproduce current organization, region, plan/instance and supported settings before proposing changes
- protect production resources from accidental destruction where supported
- treat region, replacement and billing changes as explicit approval gates
- keep database passwords, connection strings, service-role keys and access tokens out of committed HCL and example files
- remember that sensitive provider inputs can remain in Terraform state
- use Terraform branches only when the selected Supabase plan and environment strategy support them

## Production Readiness

Document a Supabase production checklist:

- Security Advisor reviewed
- RLS enabled with policies on sensitive tables
- SSL enforcement
- database network restrictions
- MFA for Supabase accounts and organization when appropriate
- access roles reviewed
- service role key kept server-side only
- anon key exposed to frontend only with correct RLS/policies
- indexes reviewed for common query patterns
- Performance Advisor/Security Advisor reviewed
- load testing considered for expected launch traffic
- backups/PITR considered for production data
- Auth email/SMTP and rate limits reviewed when using Auth
- Auth CAPTCHA/abuse prevention reviewed for public sign-up/sign-in flows

Supabase is shared responsibility. Document which controls are handled by Supabase and which remain project responsibilities: schema design, RLS policies, API key handling, access management, application architecture, query performance and third-party integrations.
