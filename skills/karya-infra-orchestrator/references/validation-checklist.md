# Validation Checklist

Before finishing, check:

- [ ] root architecture documented
- [ ] `docker-compose.yml` exists when Docker orchestration is requested
- [ ] `docker-compose.prod.yml` exists when production/VPS containers are requested
- [ ] frontend Dockerfiles exist when frontend exists
- [ ] backend Dockerfiles exist when backend exists
- [ ] root `.env.example` exists
- [ ] frontend `.env.example` exists when frontend exists
- [ ] backend `.env.example` exists when backend exists
- [ ] no obvious secrets are committed
- [ ] Makefile exists
- [ ] infra docs exist
- [ ] Vercel guidance exists when frontend exists
- [ ] Vercel monorepo root directory and env environments are documented when frontend deploys to Vercel
- [ ] Render guidance exists when Render is chosen or requested for backend hosting
- [ ] Render env vars, build/start commands and migration/pre-deploy command are documented when Render is used
- [ ] Render secrets are not hardcoded in `render.yaml`, Dockerfiles or docs
- [ ] `infra/terraform/` exists when Terraform is selected
- [ ] Terraform and provider versions are bounded and `.terraform.lock.hcl` is committed
- [ ] every Terraform-managed resource has a documented owner and create/import decision
- [ ] existing Render, Vercel and Supabase resources are imported before reconciliation
- [ ] no Render service is managed by both Terraform and `render.yaml`
- [ ] shared/production Terraform state is remote, encrypted, access-controlled and recoverable
- [ ] state, plan files, `.terraform/` and secret `.tfvars` are ignored
- [ ] Terraform provider credentials are absent from HCL, examples and logs
- [ ] Vercel GitHub integration authorization is documented as a human prerequisite
- [ ] Django migrations remain the owner of backend domain tables
- [ ] Terraform does not use PostgreSQL/SQL resources or provisioners for Django domain schema
- [ ] `terraform fmt -check -recursive`, `init -backend=false`, `validate` and `providers` attempted
- [ ] an authenticated `terraform plan -detailed-exitcode` was attempted when safe state and credentials are available
- [ ] all create/update/replace/destroy actions are reviewed before apply approval
- [ ] Supabase folder exists when Supabase is part of the stack
- [ ] Supabase production checklist is documented when Supabase is used
- [ ] Supabase service role key is server-side only
- [ ] Supabase local stack is not exposed publicly
- [ ] `docker compose config` attempted
- [ ] build/up/test commands attempted when possible
- [ ] failures are reported honestly

Classify failures as:

- Docker unavailable
- missing frontend/backend stage
- missing environment variables
- missing dependencies
- port conflict
- Supabase CLI unavailable
- Terraform CLI unavailable
- Terraform provider authentication unavailable
- Terraform state backend unsafe or undecided
- Terraform import required
- Terraform plan contains unreviewed replacement or destroy
- production decision pending
