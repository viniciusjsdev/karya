# Security and Credentials

## Credential Boundary

- Authenticate through OpenCode's user-level credential store.
- Commit only non-secret routing defaults.
- Keep `.env` ignored and use it only for executor, model, timeout, or command selection.
- Never add an OpenCode key to a generated project, its `.codex/`, its `AGENTS.md`, a prompt, CLI argument, log, schema, or completion report.

## Runtime Guardrails

The factory runtime config must override target-project OpenCode settings and:

- deny edits to `.env*`, `.git`, `AGENTS.md`, `.codex`, approved architecture contracts, and migration Python files;
- deny subagents, questions, web fetch/search, and arbitrary external-directory access;
- deny Git state changes and destructive cleanup while allowing read-only Git inspection;
- allow only the unique temporary run directory as an external write location;
- pin the requested OpenCode Go model.

These permissions reduce risk but do not replace the backend architecture scan or Codex audit. Shell tools can create complex behavior, so the executor instructions remain mandatory and every migration must show Django-generated provenance.
