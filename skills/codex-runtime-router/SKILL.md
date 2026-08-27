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

Use Python 3.12+. For a live SDK call, create an isolated environment and install the pinned official SDK with `python -m pip install -r requirements.txt`, then run `python scripts/codex_runtime_doctor.py`. Mock tests and manifest validation do not make a model call, but the router tests import the pinned SDK surface.

Preview the deterministic action:

```bash
python scripts/route_codex_runtime.py --project-root <root> --spec <SPEC.md> --manifest <SPEC.execution.json> --dry-run
```

Run only after the preview is correct:

```bash
python scripts/route_codex_runtime.py --project-root <root> --spec <SPEC.md> --manifest <SPEC.execution.json>
```

The script validates against the project-pinned `.codex/references/runtime-policy.json`, checks the clean-thread gate, and directly uses the official Python SDK. It calls `Codex.thread_start(...)` or `Codex.thread_resume(...)` with the exact model, `cwd`, sandbox, approval mode, and `config={"model_reasoning_effort": ...}` from the manifest. It passes the completion JSON Schema to `Thread.run(..., output_schema=...)`, records the actual thread ID and usage, validates evidence, and writes ephemeral state under ignored `.harness/runtime/`.

## Safety and state

- `automatic_handoff` remains false; invocation is explicit.
- A `new` manifest is rejected when the same Spec/purpose already has a recorded thread, preventing accidental duplicate execution.
- A `resume` manifest must name the recorded thread ID.
- Once the SDK exposes an ID, the mapping is preserved even if output validation fails; retry by resume instead of creating a duplicate thread.
- Same-working-tree execution is sequential by default.
- Runtime state and receipts under `.harness/runtime/` are not durable project truth. They may contain thread mappings, implementation/review state, temporary execution receipts, usage, and status only. Never put secrets, transcripts, conversation history, domain knowledge, ADRs, Specs, or persistent documentation there.
- `needs_design` returns structured evidence; do not retry blindly. Resolve in the design thread, revalidate, then resume the existing thread.
- The SDK package is optional until live routing. Deterministic validation and mock tests do not require a paid/model call.

Return one JSON route result. Do not claim implementation or review success when completion evidence fails reconciliation.
