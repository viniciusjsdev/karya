---
name: karya-backend-router
description: Route an explicitly approved Django backend implementation to OpenCode Go when the CLI, OpenCode Go authentication, and configured coding model are available, otherwise continue with Codex using the same executor-neutral contract. Use when Codex is orchestrating Karya backend code generation, needs a low-cost heavy-code executor, must wait passively for one final completion/error signal, or needs to diagnose OpenCode installation and routing readiness. Do not use for backend planning, contract approval, frontend work, backend audit, or infrastructure implementation.
---

# Karya Backend Router

## Purpose

Keep Codex responsible for orchestration and contract audit while delegating heavy Django code writing to OpenCode when it is ready. Keep all OpenCode configuration at the Karya level; never copy credentials or executor configuration into the generated project's `.codex/`.

## Required Gate

Require all six human-readable backend contracts, approved frontmatter in `docs/architecture/backend-implementation-contract.md`, and an approved matching `docs/architecture/backend-contract-manifest.json` with no unresolved template values:

```yaml
---
status: approved
contract_version: 1
approved_at: YYYY-MM-DD
---
```

Do not route or implement when the gate fails.

## Routing Workflow

1. Read `references/execution-protocol.md`.
2. Run the doctor when readiness is unknown:

   ```bash
   node <skill>/scripts/opencode-doctor.mjs
   ```

3. Start one passive routing call:

   ```bash
   node <skill>/scripts/route-backend-execution.mjs --project-root <project-root>
   ```

4. Do not poll OpenCode, summarize intermediate output, or spend model turns monitoring it. The router suppresses the event stream, waits on the child process, and returns once with a completion or error event.
5. Handle the returned route:
   - `opencode-completed`: send completion evidence and the deterministic scan to `django-backend-service-architect` in audit mode.
   - `opencode-reported-blocked` or `opencode-error`: inspect only the final artifacts, then decide whether the approved contract needs correction or Codex should perform a bounded retry.
   - `codex-fallback-required`: use `django-backend-code-executor` directly in the current Codex task. Do not ask the user merely because OpenCode is unavailable.
   - `preflight-blocked`: return to backend planning/approval; do not write code.

OpenCode is optional. Explicit `--executor opencode` changes unavailability from fallback to a blocking error; default `auto` preserves Codex fallback.

## Execution Boundaries

- Load `django-backend-code-executor` and its references as runtime instructions without placing them in the target project's `.codex/`.
- Use the model in `KARYA_OPENCODE_MODEL`, falling back to `opencode-go/kimi-k2.7-code`.
- Apply the router's bundled `assets/opencode.backend.json` through inline runtime configuration so target-project settings cannot weaken the factory guardrails; keep it synchronized with the Karya root `opencode.json`.
- Auto-approve only within the default-deny shell policy and explicit denies for secrets, approved contracts, migration-file edits, destructive Git operations, external web access, and subagents. Permit generated migrations only through approved Django management commands.
- Never pass an API key in arguments, prompts, result files, `.env`, or committed configuration.
- Store execution artifacts in the operating system temporary directory and return their paths to Codex.
- Snapshot and compare protected contracts, project instructions/context, environment files, target OpenCode config, and pre-existing migrations across the run; any integrity change blocks completion.
- Run the deterministic Django boundary scanner after OpenCode exits.
- Treat process exit as the wake-up event; do not require an LLM-based watcher.

Read `references/security-and-credentials.md` before changing authentication, permissions, or configuration. Read `references/installation.md` when setup is missing.

## Completion

The router must return exactly one JSON summary on stdout. Preserve the OpenCode event stream, stderr, request, completion, deterministic scan, and route result in the run directory. The final architecture decision remains with `django-backend-service-architect`; neither the router nor OpenCode may self-approve the implementation.
