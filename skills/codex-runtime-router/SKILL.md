---
name: codex-runtime-router
description: Validate and execute an already resolved Project Harness Spec through the Codex SDK using its materialized implementation runtime, derived review runtime, durable lifecycle, baseline, validation, and evidence contracts. Use to start or resume the exact implementation or review thread without manual manifest rewrites. Do not choose a runtime with another LLM, redesign the Spec, run unresolved work, or use subagents as the normal execution path.
---

# Codex Runtime Router

Execute a decision already made by `project-spec-architect`. The router validates; it does not deliberate about model selection.

## Required gate

Require `AGENTS.md`, a matching `SPEC.md` and `SPEC.execution.json` in an executable lifecycle status, the canonical runtime policy, every required reference and project-local skill, and the phase-appropriate valid output schema. A new implementation starts only from `ready`; v2 resumes implementation from `changes_requested` and starts or resumes review from `implemented`/`review`. Run the Spec validator before any SDK call.

Read [references/execution-protocol.md](references/execution-protocol.md) before live execution and [references/codex-sdk-capabilities.md](references/codex-sdk-capabilities.md) before changing the adapter.

## Execution

Use Python 3.12+. For a live SDK call, create an isolated environment and install the pinned official SDK with `python -m pip install -r requirements.txt`, then run `python scripts/codex_runtime_doctor.py`. Mock tests and manifest validation do not make a model call, but the router tests import the pinned SDK surface.

Preview the deterministic action:

```bash
python scripts/route_codex_runtime.py --project-root <root> --spec <SPEC.md> --manifest <SPEC.execution.json> --dry-run
```

Run only after the preview is correct:

```bash
python scripts/route_codex_runtime.py --project-root <root> --spec <SPEC.md> --manifest <SPEC.execution.json>
```

The script validates against the project-pinned `.codex/references/runtime-policy.json`, rejects incompatible Structured Outputs schemas locally, and directly uses the official Python SDK. For v2 it derives implementation or review from the durable status, starts each purpose once, resumes the recorded ID automatically, reruns required automatable VAL commands, and writes canonical completion, review, attempt history, and lifecycle evidence under the Spec. `.harness/runtime/` remains only a recoverable operational cache.

## Safety and state

- `automatic_handoff` remains false; invocation is explicit.
- Version 1 preserves the explicit `new`/`resume` contract and rejects duplicate starts or mismatched resume IDs.
- Version 2 derives `start`/`resume` from durable purpose-specific lifecycle evidence, using `.harness/runtime/` only as a cross-check/cache; the implementation runtime block is not rewritten.
- Once the SDK exposes an ID, the mapping is preserved even if output validation fails; retry by resume instead of creating a duplicate thread.
- Version 2 preserves one implementation thread and, when review is required, one review thread across `changes_requested`, correction, and re-review.
- `changed_files` records `added`, `modified`, or `deleted`; the router compares it with the pre-run Git snapshot and excludes unchanged user-owned dirt.
- Required non-manual validations are executed by the router from their manifest command. Model-reported commands cannot replace the canonical command.
- Same-working-tree execution is sequential by default.
- Runtime state and receipts under `.harness/runtime/` are not durable project truth. They may contain thread mappings, implementation/review state, temporary execution receipts, usage, and status only. Never put secrets, transcripts, conversation history, domain knowledge, ADRs, Specs, or persistent documentation there.
- `needs_design` returns structured evidence; do not retry blindly. Resolve in the design thread, revalidate, then resume the existing thread.
- The SDK package is optional until live routing. Deterministic validation and mock tests do not require a paid/model call.

Return one JSON route result. Do not claim implementation or review success when schema, baseline, Git, AC/VAL, command, lifecycle, or evidence reconciliation fails.
