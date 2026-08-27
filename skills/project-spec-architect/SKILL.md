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
5. Resolve the exact runtime, thread mode, skills, references, validation, review, escalation, and completion paths in `SPEC.execution.json` from `assets/SPEC.execution.template.json`.
6. Record `automatic_handoff: false`. This skill prepares the handoff; it does not start another Factory or execution thread.
7. Run `python scripts/validate_spec.py <SPEC.md> <SPEC.execution.json> --project-root <root> --require-ready` before marking the Spec `ready`.

## Lifecycle authority

- `draft`, `design`, and `needs_design`: the architect may change design content.
- `ready`: architecture, requirements, acceptance, runtime, and handoff context are resolved.
- `in_progress`, `implemented`, and `review`: execution/review evidence advances the state; consequential redesign returns to `needs_design`.
- `done`: required acceptance and review evidence is reconciled.

Do not mark implementation complete or review approved from this skill alone.

## Routing boundaries

- `design` and unresolved consequential decisions default to Sol/high.
- A `ready` normal implementation defaults to Terra/medium.
- Mechanical, low-risk, easily validated work defaults to Luna/low.
- Critical review defaults to Sol/high.
- Size is not complexity. Runtime deviations require an explicit override reason.
- An executor that finds an absent consequential decision returns `needs_design`; it does not invent the decision.

## Resources

- `references/spec-lifecycle.md`: states, transitions, readiness, and `needs_design`.
- `references/runtime-policy.md`: classification, model, reasoning, review, escalation, and context policy.
- `assets/runtime-policy.json`: centralized deterministic defaults.
- `assets/spec-execution.schema.json`: execution manifest JSON Schema.
- `assets/completion.schema.json`: structured completion evidence JSON Schema.
- `assets/review-evidence.schema.json`: structured independent review inputs, findings, result, runtime, thread, and usage.
- `scripts/validate_spec.py`: dependency-free Python 3.12+ Spec/readiness validator.
