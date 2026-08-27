# Vercel Standard

Use Vercel for frontend deployment from `/frontend`.

Typical settings:

```txt
Root Directory: frontend
Build Command: npm run build
Output Directory: dist or framework-specific output
```

## Monorepos

For a monorepo, configure the Vercel project Root Directory as `frontend`.

If using Vercel CLI, run linking/deploy commands from the monorepo root and select the intended project. Do not run the CLI from a subdirectory as the default workflow.

## Build Settings

Vercel can auto-detect install and build settings for supported frontend frameworks. Karya frontend projects should use npm by default. Override the install command, build command or output directory only when the detected settings are wrong or a documented package-manager exception exists.

Create `frontend/vercel.json` only when the project needs custom rewrites, headers, framework settings or other explicit Vercel project configuration.

## Terraform

When Terraform is selected, use the official `vercel/vercel` provider to manage only the approved project, Git repository link, `frontend` root, build settings, domains and environment variables.

- Pin a reviewed compatible provider version and commit the Terraform lockfile.
- Import an existing Vercel project before managing it.
- Require the human owner to authorize the Vercel GitHub integration before linking a GitHub repository.
- Prefer Git-triggered deployments; do not create a Terraform deployment for every application build unless explicitly requested.
- Use one environment-variable resource style consistently; do not manage the same variable both inline and through standalone Terraform resources.
- Scope variables to Development, Preview and Production and mark secrets sensitive, while recognizing they still exist in Terraform state.
- Keep `VERCEL_API_TOKEN` in the environment or an approved secret store, never in committed files.

## Backend Boundary

Do not deploy Django backend as if it were a Vercel frontend project.

Vercel supports Django through Vercel Functions, but this is an explicit alternative path. If chosen, document Vercel Functions limitations, bundle/runtime constraints, static file handling and migration strategy. The Karya default is a backend container on a container-friendly host.

For API calls:

- `VITE_API_BASE_URL` or equivalent must point to backend API
- Development, Preview and Production env vars must be documented separately
- frontend env vars such as `VITE_*` must not contain secrets
- backend/API secrets must stay server-side
- CORS must allow Vercel preview/prod domains
- avoid wildcard CORS with credentials
