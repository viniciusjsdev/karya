---
name: project-spec-architect
description: Design or refine an executable project change Spec with a human-readable SPEC.md and a resolved machine-readable SPEC.execution.json. Use for features, bugs, refactors, architecture changes, experiments, research, infrastructure, automation, or other bounded work that must be executable by a clean Codex thread. Do not implement the change or silently resolve consequential product, domain, security, billing, or compliance decisions.
---

# Project Spec Architect

Create one durable unit of change that can cross from a design thread to an independent implementation thread.

## Core invariant

A Spec is `ready` only when a clean thread can execute it from `AGENTS.md`, the Spec, its execution manifest, declared references and skills, and the repository. If execution would need the design conversation, keep the Spec in `design` or `needs_design`.

## Workflow

1. Read `AGENTS.md`, existing project truth, applicable decisions, and [references/spec-lifecycle.md](references/spec-lifecycle.md).
2. Bound one change. Preserve domain-specific contracts that are richer than the generic Spec; reference them instead of flattening them.
3. Write `SPEC.md` from `assets/SPEC.template.md` and assign stable requirement, rule, acceptance, and validation IDs.
4. Classify the reasoning before selecting a runtime. Read [references/runtime-policy.md](references/runtime-policy.md) and use `assets/runtime-policy.json` as the machine-readable defaults.
5. Resolve the exact implementation runtime, skills, references, validation, review, baseline, lifecycle, and durable evidence paths in `SPEC.execution.json` from `assets/SPEC.execution.template.json`. Version 2 manifests keep the implementation runtime stable; the router derives review execution from `review`.
6. Record `automatic_handoff: false`. This skill prepares the handoff; it does not start another Factory or execution thread.
7. Run `python scripts/validate_spec.py <SPEC.md> <SPEC.execution.json> --project-root <root> --require-ready` before marking the Spec `ready`.

## Lifecycle authority

- `draft`, `design`, and `needs_design`: the architect may change design content.
- `ready`: architecture, requirements, acceptance, runtime, and handoff context are resolved.
- `in_progress`, `implemented`, `review`, and `changes_requested`: router evidence advances the durable lifecycle; consequential redesign returns to `needs_design`.
- `done`: required acceptance and review evidence is reconciled.

Do not mark implementation complete or review approved from this skill alone.

## Routing boundaries

- `design` and unresolved consequential decisions default to Sol/high.
- A `ready` normal implementation defaults to Terra/medium.
- Mechanical, low-risk, easily validated work defaults to Luna/low.
- Critical review defaults to Sol/high.
- A READY Spec may declare independent review and later be routed through `karya-execution-router` when the user explicitly wants an economic non-Django executor. Provider/model selection, credentials, writable paths, snapshot, and action-time confirmation stay in an external request outside the project repository; they do not become Spec fields.
- The resolved Codex runtime remains the fallback and review contract. OpenCode eligibility never makes the external executor mandatory.
- Size is not complexity. Runtime deviations require an explicit override reason.
- An executor that finds an absent consequential decision returns `needs_design`; it does not invent the decision.

## Resources

- `references/spec-lifecycle.md`: states, transitions, readiness, and `needs_design`.
- `references/runtime-policy.md`: classification, model, reasoning, review, escalation, and context policy.
- `assets/runtime-policy.json`: centralized deterministic defaults.
- `assets/spec-execution.schema.json`: execution manifest JSON Schema.
- `assets/completion.schema.json`: structured completion evidence JSON Schema.
- `assets/review-evidence.schema.json`: structured independent review inputs, findings, result, runtime, thread, and usage.
- `assets/structural-baseline.schema.json`: required behavior inventory for structural migration, promotion, or reorganization.
- `scripts/_structured_output_schema.py`: dependency-free validation of the strict Structured Outputs subset used before SDK access.
- `scripts/validate_spec.py`: dependency-free Python 3.12+ Spec/readiness validator.

For optional economic execution, the Spec must make affected areas, non-scope, exact validations, and independent review sufficiently precise for the external request to narrow writable paths without redesigning the change.
