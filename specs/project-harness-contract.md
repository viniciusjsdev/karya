# Project Harness Factory contract

## Input

An idea, empty or existing project, product, software system, research program, data/AI project, automation, infrastructure, commercial project, or other bounded project.

## Durable outputs

- accepted harness plan and source-of-truth map;
- domain-appropriate documentation additions only where missing;
- accurate `AGENTS.md` routing and concise `.codex/` context;
- project-local skills only for stable specialized recurring procedures;
- one human-readable `SPEC.md` and machine-readable `SPEC.execution.json` per bounded change;
- versioned runtime policy plus resolved historical runtime in each manifest;
- temporary Spec-to-implementation/review thread mapping;
- structured acceptance/validation completion evidence with existing changed-file/artifact paths;
- structured independent review evidence when review is required;
- independent audit findings.

## Invariants

- READY means a clean thread can execute without design-chat history.
- Architect decides, executor implements, auditor verifies.
- A router validates a materialized decision and does not ask another model to choose the runtime.
- The router uses the project-pinned policy and preserves exposed thread IDs across output/evidence failures.
- The smallest capable runtime is preferred; size is not complexity.
- Subagents are not the default specialization mechanism.
- Project truth, decisions, Specs, skills, scripts, policy, and temporary runtime state remain distinct.
- Existing richer domain contracts are preserved.
- Cross-factory handoff is explicit and records `automatic_handoff: false`.

## Machine-readable contracts

Canonical schemas and templates live under `skills/project-spec-architect/assets/`, including separate implementation completion and independent review evidence schemas. Temporary thread state and route results are defined under `skills/codex-runtime-router/assets/`. Harness bootstrap and audit schemas live in their owning skills.

## Completion

The Factory is not complete because files exist. Completion requires successful structural validation, honest semantic gaps, usable start/resume flow, evidence reconciliation, accurate root documentation/catalog routing, and no critical project knowledge left only in the design conversation.
