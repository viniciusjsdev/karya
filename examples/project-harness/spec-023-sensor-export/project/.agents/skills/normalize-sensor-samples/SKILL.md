---
name: normalize-sensor-samples
description: Normalize sensor samples according to the approved project methodology while preserving raw provenance and input order. Use when repeated imports, comparisons, exports, or tests need normalized sample records. Do not use for methodology design, destructive raw-data cleanup, or one-time unrelated data repair.
---

# Normalize Sensor Samples

## Required Context

Read `docs/project/overview.md`, applicable ADRs, and the active Spec before normalizing.

## Workflow

Validate input provenance, apply documented unit normalization, preserve timestamp and original position, and emit normalization evidence for the caller.

## Invariants

- Raw values remain unchanged.
- Normalized records retain provenance.
- Equal timestamps retain original input order under ADR-004.

## Validation

Run the exact normalization/export validation declared by the active Spec and report the command result.

## Boundaries

Do not redefine methodology, infer missing units, remove samples, or approve a public export contract.
