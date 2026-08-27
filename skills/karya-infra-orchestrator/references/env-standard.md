# Environment Standard

Create:

```txt
.env.example
frontend/.env.example
backend/.env.example
```

Root `.env.example` should include common orchestration variables:

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

`SUPABASE_SERVICE_ROLE_KEY` is server-side only. Do not include it in `frontend/.env.example`, Vercel frontend environment variables or client-side code.

If the frontend talks directly to Supabase, use frontend-safe names such as:

```env
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
```

Only expose the anon key when RLS and policies are designed for client access.

Never commit real secrets.

Examples must use placeholders such as `change-me`, `example`, or empty values.

Secrets that must stay server-side:

- `DJANGO_SECRET_KEY`
- `DATABASE_URL` with production credentials
- `SUPABASE_SERVICE_ROLE_KEY`
- provider API keys

Terraform provider authentication must come from the operator environment or an approved CI secret store. Document names such as `RENDER_API_KEY`, `RENDER_OWNER_ID` and `VERCEL_API_TOKEN` without putting values in `.env.example`, HCL or committed `.tfvars`. Supply the Supabase provider access token through an approved secret source.

Terraform `sensitive` values are redacted from normal CLI output but still exist in state. Require encrypted, access-controlled remote state before Terraform manages provider environment variables that contain secrets; otherwise leave those bindings dashboard-managed and document them.

Vercel Development, Preview and Production environments should be documented separately. Pulling Vercel env vars locally can create `.env` files; these must remain ignored when they contain real values.

Render backend environments should document required service variables separately from frontend variables:

- `DATABASE_URL`
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`
- provider API keys used only by the backend

When using `render.yaml`, secrets should use `sync: false`, `generateValue: true`, environment groups or dashboard-managed values instead of committed values.
