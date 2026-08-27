---
name: codex-runtime-router
description: Validate and execute an already resolved READY Project Harness Spec through the Codex SDK using its materialized model, reasoning, working directory, thread mode, skills, references, validation, review, and completion contract. Use to start or resume the exact implementation or review thread recorded by a valid SPEC.execution.json. Do not choose a runtime with another LLM, redesign the Spec, run non-READY work, or use subagents as the normal execution path.
---

# Codex Runtime Router

Execute a decision already made by `project-spec-architect`. The router validates; it does not deliberate about model selection.

## Required gate

Require `AGENTS.md`, a matching `SPEC.md` and `SPEC.execution.json` with status `ready`, the canonical runtime policy, every required reference and project-local skill, and a valid completion schema. Run the Spec validator before any SDK call.

Read [references/execution-protocol.md](references/execution-protocol.md) before live execution and [references/codex-sdk-capabilities.md](references/codex-sdk-capabilities.md) before changing the adapter.

## Execution

For a live SDK call, install the pinned package once inside this skill directory with `pnpm install --frozen-lockfile` (or an equivalent lockfile-respecting package manager command), then run `node scripts/codex-runtime-doctor.mjs`. Mock tests and manifest validation do not need the installed package.

Preview the deterministic action:

```bash
node scripts/route-codex-runtime.mjs --project-root <root> --spec <SPEC.md> --manifest <SPEC.execution.json> --dry-run
```

Run only after the preview is correct:

```bash
node scripts/route-codex-runtime.mjs --project-root <root> --spec <SPEC.md> --manifest <SPEC.execution.json>
```

The script validates against the project-pinned `.codex/references/runtime-policy.json`, checks the clean-thread gate, starts or resumes with the manifest's exact `model`, `modelReasoningEffort`, `workingDirectory`, sandbox, and approval policy, supplies the completion JSON Schema through `outputSchema`, records actual thread ID and usage, validates evidence, and writes temporary state under `.codex/runtime/`.

## Safety and state

- `automatic_handoff` remains false; invocation is explicit.
- A `new` manifest is rejected when the same Spec/purpose already has a recorded thread, preventing accidental duplicate execution.
- A `resume` manifest must name the recorded thread ID.
- Once the SDK exposes an ID, the mapping is preserved even if output validation fails; retry by resume instead of creating a duplicate thread.
- Same-working-tree execution is sequential by default.
- Runtime state and receipts are not durable project truth. Persist decisions in docs/ADRs/Specs.
- `needs_design` returns structured evidence; do not retry blindly. Resolve in the design thread, revalidate, then resume the existing thread.
- The SDK package is optional until live routing. Deterministic validation and mock tests do not require a paid/model call.

Return one JSON route result. Do not claim implementation or review success when completion evidence fails reconciliation.
