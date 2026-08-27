# Project Handoff Checklist

- Executable product contract exists and passes its validator.
- Scope, non-scope, primary journey, permissions, and open questions are explicit.
- Frontend code, architecture, API boundary, and validation report exist before backend work.
- Standard site creation invokes external `@sites` together with `$karya-frontend-builder` without adding Sites to npm dependencies.
- Backend preflight context, six human-readable architecture contracts, matching approved `backend-contract-manifest.json`, resolved project-root `.codex` context, and the validated `.agents/skills/` backend architecture kit exist before implementation.
- Backend implementation contract is explicitly approved before `django-backend-code-executor` runs.
- Backend routing records OpenCode readiness and uses Codex fallback automatically when `auto` is selected.
- No OpenCode credential, config, log, or run artifact is stored in the generated project's `.codex/`.
- Domain apps use scalable packages; ORM Models are CamelCase and explicitly exported; matching Configurations define specifications; explicit Mappers contain transformation only; database access is repository-only; Services are persistence-agnostic; Controllers use DTO payloads; and migrations are Django-generated.
- Backend audit traces every manifest invariant and endpoint ID to implementation, exact tests, and required command results; aggregate test counts alone do not approve the backend.
- Product-specific domain skills, when present, are contract-backed capabilities rather than generic layer duplication or one-skill-per-entity noise.
- Backend audit is approved before infrastructure work.
- Infrastructure validation was attempted before claiming readiness.
- Remaining gaps and contract variances are listed explicitly.
