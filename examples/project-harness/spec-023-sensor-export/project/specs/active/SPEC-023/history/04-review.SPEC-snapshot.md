---
id: SPEC-023
title: Export normalized sensor samples as deterministic JSON
status: review
contract_version: 2
---

# SPEC-023: Export normalized sensor samples as deterministic JSON

## Goal

Produce a stable public JSON export of normalized sensor samples.

## Context

The implementation is complete. The clean review thread receives the durable contract, ADR-004, diff/artifacts, tests, and completion evidence without implementation-chat history.

## Scope

- Review normalized export behavior, ordering, fields, tests, and evidence.

## Non-scope

- Redesigning the approved public contract or changing implementation.

## Requirements

- REQ-001: Independently reconcile the implementation with SPEC-023.

## Business or domain rules

- BR-001: Raw provenance is immutable.
- BR-002: Equal timestamps follow ADR-004.

## Decisions already made

- ADR-004 preserves original input order for equal timestamps.
- JSON field names are a public contract.

## Constraints

- Review is read-only and independent from the implementation conversation.

## Acceptance criteria

- AC-001: The fixture export matches the approved deterministic JSON.
- AC-002: Equal-timestamp fixtures preserve original input order.

## Affected areas

- Sensor export implementation, fixtures, contract tests, and completion evidence.

## References

- `docs/decisions/ADR-004-equal-timestamp-order.md`.
- `specs/active/SPEC-023/evidence/completion.json`.

## Skills

- No specialized procedure is required for independent review.

## Validation requirements

- VAL-001: `python -m pytest tests/test_sensor_export.py -q`.

## Review requirements

Use a new independent Sol/high review thread and emit the review evidence schema.

## Execution and runtime

`history/04-review.execution-snapshot.json` materializes the review run.
