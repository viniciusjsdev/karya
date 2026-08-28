# Runtime, routing, review, and escalation policy

`assets/runtime-policy.json` is the machine-readable policy. This reference explains how to apply it.

## Classification before selection

| Classification | Nature of reasoning | Default runtime |
| --- | --- | --- |
| `design` | new architecture, ambiguity, trade-offs, deep project understanding | `gpt-5.6-sol` / `high` |
| `normal_implementation` | resolved architecture, non-trivial implementation, tests, moderate debugging | `gpt-5.6-terra` / `medium` |
| `mechanical` | repetitive, low-risk, minimally interpretive, easily validated | `gpt-5.6-luna` / `low` |
| `critical_review` | security, auth, payments, concurrency, complex migration, public contract, critical infra or irreversible data | `gpt-5.6-sol` / `high` |

Choose the smallest runtime capable of acceptable reliability. File count does not determine complexity. Prices change; do not distribute absolute prices through skills or manifests.

## Reasoning

- `low`: mechanical, low ambiguity, low risk.
- `medium`: normal implementation default.
- `high`: architecture, trade-offs, hard debugging, complex implementation, critical review.
- `xhigh` or `max`: only after high is demonstrably insufficient or exceptional risk justifies it.

## Routing tree

```txt
Consequential design remains? -> Sol/high
Otherwise mechanical?         -> Luna/low
Otherwise requirements clear? -> Terra/medium
Otherwise                     -> needs_design or Sol/high design
```

Luna escalates to Terra when work stops being mechanical. Terra may move to high while the Spec remains clear. Terra returns `needs_design` when architecture or consequential behavior is absent. Sol moves above high only with a recorded reason.

## Threads and context

A conversation, Codex thread, turn, execution/run, and subagent are distinct. Default to a Sol/high design thread and an independent Terra/medium implementation thread connected by durable artifacts. Resume the implementation thread after `needs_design`. Use a Luna worker thread only for a genuinely independent mechanical unit. Subagents are not the normal specialization mechanism.

Load progressively: Spec, declared skills, declared references, then relevant repository files discovered during execution. Do not pass the full design conversation.

Same-working-tree writes are sequential by default. Parallel writers require isolated branches/worktrees, explicit ownership, merge and conflict policy, and completion reconciliation.

## Optional economic executor

The model/reasoning in `SPEC.execution.json` remains the resolved Codex implementation fallback or review runtime. When the user explicitly prioritizes economy and the Spec is READY, `karya-execution-router` may resolve an OpenCode provider/model at action time through an external request outside the repository.

- `normal_implementation` and `mechanical` may be eligible.
- `design`, `critical_review`, unresolved decisions, credentials, external actions, and hard-to-reverse work are ineligible by default.
- OpenCode availability never changes the Spec's requirements, validation, review, or escalation policy.
- A live external run requires exact human confirmation and independent Codex review.
- No provider, subscription, credit, authentication, or local-model readiness is assumed.

## Review

Simple work may use executor self-validation. Medium work may use an independent Terra review when independence adds value. Critical categories require independent Sol/high review. Review receives the Spec, manifest, diff/artifacts, tests, and completion evidence, not the implementation conversation.
