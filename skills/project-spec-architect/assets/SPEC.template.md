---
id: SPEC-001
title: Replace with a bounded change title
status: draft
contract_version: 1
---

# SPEC-001: Replace with a bounded change title

## Goal

Describe the observable outcome.

## Context

Record only durable context needed by a clean thread.

## Scope

- Included work.

## Non-scope

- Explicitly excluded work.

## Requirements

- REQ-001: Testable requirement.

## Business or domain rules

- BR-001: Applicable invariant, or state that no additional domain rule applies.

## Decisions already made

- Decision and durable source.

## Constraints

- Technical, operational, legal, time, or evidence constraint.

## Acceptance criteria

- AC-001: Observable acceptance evidence.

## Affected areas

- Paths, processes, datasets, people, or systems affected.

## References

- Durable source path and why it is needed.

## Skills

- Required skill and why it applies, or state that no specialized skill is required.

## Validation requirements

- VAL-001: Exact command or observable verification.

When the project has `.codex/references/project-map.json`, add a VAL command for `python scripts/harness/project_map.py check --project-root .` with `kind: test` and `required: true`. Reconcile documentation and map impact, then explicitly record the executor's map review before this check. Never auto-review merely to clear pending fingerprints.

## Review requirements

State self-validation or independent review and the risk basis.

## Execution and runtime

Point to `SPEC.execution.json`; do not duplicate its resolved machine-readable fields.
