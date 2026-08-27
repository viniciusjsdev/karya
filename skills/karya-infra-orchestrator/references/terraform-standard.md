# Terraform Standard

Use Terraform as an optional cross-provider control plane for Render, Vercel and Supabase. Keep Docker Compose responsible for local orchestration and keep database schema changes in their approved migration system.

## Contents

- [Selection Gate](#selection-gate)
- [Target Layout](#target-layout)
- [Providers](#providers)
- [Ownership and Adoption](#ownership-and-adoption)
- [Render Boundary](#render-boundary)
- [Vercel Boundary](#vercel-boundary)
- [Supabase Boundary](#supabase-boundary)
- [Cross-Provider Wiring](#cross-provider-wiring)
- [State and Repository Hygiene](#state-and-repository-hygiene)
- [Validation and Apply Gate](#validation-and-apply-gate)

## Selection Gate

Select Terraform only when the user requests it or the infrastructure decision explicitly approves declarative cloud management. Do not add it merely because more than one cloud provider exists.

Before generating files, record:

- target environments
- Render owner and service decision
- Vercel account/team, project and Git integration decision
- Supabase organization/project and existing-vs-new decision
- state backend and access model
- create or import for every resource
- resource owner: Terraform, provider-native manifest, provider dashboard, Django migrations or Supabase CLI migrations
- settings deliberately left outside Terraform

Record `automatic_handoff: false` for any optional cross-factory handoff. Terraform selection is an MVP Factory infrastructure decision and does not authorize Research or Marketing work.

## Target Layout

Create only files required by the selected providers:

```txt
infra/terraform/
  versions.tf
  providers.tf
  variables.tf
  locals.tf
  render.tf
  vercel.tf
  supabase.tf
  imports.tf
  outputs.tf
  .terraform.lock.hcl
```

Use separate roots or a documented workspace strategy when environments need independent state. Prefer simple per-environment roots for MVPs when they reduce accidental cross-environment changes. Do not create premature module hierarchies.

## Providers

Use these provider sources:

| Platform | Provider source | Authentication environment |
| --- | --- | --- |
| Render | `render-oss/render` | `RENDER_API_KEY`, `RENDER_OWNER_ID` |
| Vercel | `vercel/vercel` | `VERCEL_API_TOKEN` |
| Supabase | `supabase/supabase` | provider access token from an approved secret source |

Verify each provider's current official registry documentation and resource schema at generation time. Pin Terraform and every provider to a compatible version range that excludes unreviewed major upgrades; do not use an unbounded `>=` constraint. Run `terraform init` and commit `.terraform.lock.hcl`.

Do not put provider tokens in HCL, committed `.tfvars`, example files, command history, logs or plan artifacts. Prefer provider-supported environment variables or the approved CI secret store. Document team/owner/organization identifiers as non-secret inputs where appropriate.

## Ownership and Adoption

Maintain a resource ownership matrix in `docs/architecture/infra-architecture.md` with at least:

| Resource | Environment | Existing? | Declared owner | Terraform address/import ID | Destructive risk |
| --- | --- | --- | --- | --- | --- |

Apply these rules:

- Assign exactly one declared owner to each resource.
- Do not manage one Render service through both Terraform and `render.yaml`.
- Do not mix Terraform-managed and inline/dashboard-managed variants of the same Vercel project environment variable.
- Import existing Render, Vercel and Supabase resources before planning changes.
- Reconcile imported configuration to the current remote settings before proposing intentional drift.
- Add `prevent_destroy` to production projects/services when supported and appropriate.
- Treat provider attributes that force replacement, region changes, plan changes and billed resources as human approval gates.
- Never use `terraform state rm`, `mv`, `import`, `apply` or `destroy` against live state without explicit approval and a recorded target address.

If a provider cannot manage a required setting safely, leave that setting dashboard-managed and document the exception instead of adding brittle API calls or `local-exec` workarounds.

## Render Boundary

Terraform may manage the Django web service, Docker or native runtime source, root/Dockerfile path, build/start/pre-deploy commands, health check, custom domains and environment variables supported by the pinned provider.

Prefer the production backend Dockerfile when reproducibility is important. Use the native runtime only when that remains the approved deployment path.

Do not create Render Postgres when Supabase Postgres is already selected. Keep migration execution as a controlled Render pre-deploy command or release procedure; Terraform defines that command but does not execute Django migration logic itself.

If `render.yaml` remains for other services, document the split and verify that no Terraform address targets those services.

## Vercel Boundary

Terraform may manage the frontend project, Git repository link, `frontend` root directory, framework/build settings, domains and environment variables supported by the pinned provider.

The human owner must authorize/install the Vercel GitHub integration before Terraform can link a GitHub repository. Terraform must not attempt account creation, credential setup, CAPTCHA, 2FA or connector authorization.

Use one environment-variable resource style consistently. Mark secret variables sensitive, but remember that sensitive values can still be stored in Terraform state. Keep browser-exposed `VITE_*` values non-secret and scope values explicitly to Development, Preview and Production.

Prefer Git-triggered deployments. Do not make every application build a Terraform-managed deployment resource unless that behavior is explicitly requested.

## Supabase Boundary

For an existing Supabase project, import the project before managing it. Reproduce current organization, name, region, plan/instance settings and relevant platform configuration in HCL before changing them. Use lifecycle protection for production and review provider plans for replacement or billing effects.

Terraform may manage the project, supported settings and branches. Confirm provider support at the pinned version rather than assuming every dashboard setting is available.

For Django-backed products:

- Keep backend domain tables under Django migrations by default.
- Keep ORM schema operations out of Terraform.
- Do not add a PostgreSQL provider, SQL resources, shell provisioners or `local-exec` to create/alter application tables.
- Use Supabase migrations only for explicitly assigned Supabase-owned SQL such as Auth, Storage or RLS resources.
- Preserve the schema-ownership decision in infra architecture docs.

Database passwords, connection strings, service-role keys and access tokens are secrets. Do not expose them as non-sensitive outputs or Vercel frontend variables.

## Cross-Provider Wiring

Wire only values with clear ownership and safe state handling:

- Render backend public URL to the Vercel frontend API base URL
- approved Vercel production/preview origins to backend CORS configuration
- non-secret project IDs, domains and service URLs through outputs

Avoid circular dependencies. Keep sensitive outputs marked `sensitive = true`; this only redacts normal CLI display and does not remove the value from state. If a secret must enter Terraform-managed provider configuration, require encrypted, access-controlled remote state. Otherwise keep it in provider dashboards or an approved secret manager and document the manual binding.

## State and Repository Hygiene

For shared or production environments, require remote state with encryption, locking where supported, least-privilege access, backup/recovery ownership and a documented bootstrap procedure. Do not commit local state.

Add at least these patterns to `.gitignore`:

```gitignore
.terraform/
*.tfstate
*.tfstate.*
*.tfplan
crash.log
crash.*.log
*.auto.tfvars
terraform.tfvars
```

Commit `.terraform.lock.hcl`. Commit only sanitized `*.tfvars.example` files when examples add value.

Treat state, saved plans and provider debug logs as sensitive because provider APIs can store secrets in them even when variables are marked sensitive.

## Validation and Apply Gate

Run from the target project:

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

Use authenticated remote initialization and planning only after the state decision and credentials exist. A detailed plan exit code of `0` means no changes, `2` means changes are present and `1` means failure.

Before any apply:

- list every create, update, replacement and destroy
- explain billed changes and provider limitations
- verify imported resources will not be recreated
- verify no domain table ownership moved out of Django migrations
- verify secrets are absent from committed files and captured artifacts
- obtain explicit approval for the exact plan and environment

Do not claim Terraform readiness when only formatting succeeded. Report skipped initialization, provider authentication gaps, missing imports, unsafe state, plan failures and unreviewed destructive actions.
