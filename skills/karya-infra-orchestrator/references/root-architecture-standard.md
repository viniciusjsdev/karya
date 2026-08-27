# Root Architecture Standard

Use this target shape for Karya monorepos:

```txt
/
  frontend/
  backend/
  supabase/
  infra/
    terraform/
  docs/
  .agents/skills/
  .codex/
  docker-compose.yml
  docker-compose.override.yml
  docker-compose.prod.yml
  Makefile
  .env.example
  AGENTS.md
  README.md
```

Create only what is useful for the current project. Do not invent a backend, Supabase or Vercel setup before the project reaches that stage.

## Modes

- Local/full Docker: run frontend, backend and optional local db together.
- Cloud split: Vercel for frontend, backend container on a compatible host, Supabase as managed services.
- Declarative cloud split: Terraform coordinates selected Render, Vercel and Supabase resources from `infra/terraform/` while Docker Compose remains local-only.
- VPS/full-stack: run frontend static server, backend and database/proxy as containers when the user chooses VPS deployment.

Document which mode is active. Create `infra/terraform/` only when Terraform is explicitly selected, and declare one owner for every cloud resource it manages.
