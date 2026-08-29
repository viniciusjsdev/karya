# Project Harness navigation

This repository is the source of the Karya Project Harness Factory. Durable workflow and routing truth is split by responsibility:

- `AGENTS.md` defines repository-wide boundaries and invariants.
- `specs/project-harness-contract.md` defines the cross-skill contract.
- `.codex/workflows/project-harness-factory.md` defines the Factory workflow.
- `.codex/references/runtime-policy.json` pins this repository's runtime policy.
- `skills/project-harness-architect/` owns bootstrap and materialization.
- `skills/project-spec-architect/` owns bounded Specs, manifests, baselines, and output schemas.
- `skills/codex-runtime-router/` owns deterministic SDK routing, lifecycle state, validation replay, and evidence retention.
- `skills/project-harness-auditor/` owns independent deterministic reconciliation.

Ephemeral thread and run state belongs under `.harness/runtime/` and is never a durable source of truth. Completion, review, lifecycle, and baseline evidence required for later audit belongs beside its Spec.
