---
id: SPEC-023
title: Export normalized sensor samples as deterministic JSON
status: done
contract_version: 2
---

# SPEC-023: Export normalized sensor samples as deterministic JSON

## Goal

Produce a stable public JSON export of normalized sensor samples.

## Context

The project preserves raw provenance and uses the local normalization capability. During implementation, equal-timestamp ordering was resolved in ADR-004.

## Scope

- Normalize approved samples and export the contracted JSON fields.
- Preserve deterministic ordering and validation evidence.

## Non-scope

- Changing raw samples, methodology, units, or storage.
- Adding a value-based tie-breaker.

## Requirements

- REQ-001: Emit normalized samples in timestamp order.
- REQ-002: Preserve original input order for equal timestamps.

## Business or domain rules

- BR-001: Raw provenance is immutable.
- BR-002: Equal timestamps follow ADR-004.

## Decisions already made

- ADR-004 preserves original input order for equal timestamps.
- JSON field names are a public contract.

## Constraints

- Work offline and preserve existing project context.

## Acceptance criteria

- AC-001: The fixture export matches the approved deterministic JSON.
- AC-002: Equal-timestamp fixtures preserve original input order.

## Affected areas

- Sensor normalization, export serialization, fixtures, and contract tests.

## References

- `docs/project/overview.md` for project truth.
- `docs/decisions/ADR-004-equal-timestamp-order.md` for ordering.

## Skills

- `.agents/skills/normalize-sensor-samples/SKILL.md` for the recurring normalization procedure.

## Validation requirements

- VAL-001: `node tests/sensor-export.test.mjs`.

## Review requirements

Independent Sol/high review is required because JSON ordering and field names form a public contract.

## Execution and runtime

`SPEC.execution.json` records the implementation runtime. Review evidence records the separate Sol/high review thread.
