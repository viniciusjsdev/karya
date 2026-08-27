## Project Rules

This project is built and maintained with Codex-first workflows.

- Read the relevant files under `.codex/references/` before changing architecture, dependencies, data boundaries, or code conventions.
- Follow `.codex/workflows/` for recurring implementation and handoff procedures.
- Use `.codex/checklists/` before claiming work is complete.
- Keep durable human-facing documentation in `docs/`; keep concise agent-operational context in `.codex/`.
- Keep repository-local domain skills in `.agents/skills/<skill-name>/` with a valid `SKILL.md`.
- Create domain skills only for repeatable domain expertise or workflows, not for one-off project notes.
- Keep frontend routes thin and enforce `Route -> Feature Page -> Hook/View Model -> Service -> Repository`.
- Use the pinned npm version, exact dependency versions, the committed lockfile, and the npm security policy.
- Never commit secrets or expose private values through `VITE_` environment variables.
- When the request invokes `@sites`, treat `$karya-frontend-builder` as the mandatory stack and architecture contract while Sites owns preview and publication.
- Do not add Sites, Cloudflare, Wrangler, or hosting SDK packages merely to reference the external plugin.
- Preserve unrelated user changes and report blocked validations honestly.

Before completing frontend work, run the commands documented in `.codex/workflows/frontend-validation.md`.
