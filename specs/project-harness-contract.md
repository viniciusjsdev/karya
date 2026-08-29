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
- optional external economic execution requests outside the project repository, with exact confirmation, provider/model readiness, bounded writable paths, mandatory prohibitions, snapshot, validations, and Codex fallback;
- durable Spec lifecycle with one implementation thread ID, one review thread ID when required, and append-only attempts;
- recoverable operational mapping under gitignored `.harness/runtime/`;
- structured acceptance/validation arrays with every declared ID exactly once;
- changed-file evidence that distinguishes added, modified, and deleted files and reconciles against a pre-run Git snapshot;
- structural behavior baselines covering tests, CLI, JSON, persistence, schemas/idempotency, protected paths, and pre-Spec decisions;
- structured independent review evidence when review is required;
- independent audit findings.

## Invariants

- READY means a clean thread can execute without design-chat history.
- Architect decides, executor implements, auditor verifies.
- A router validates a materialized decision and does not ask another model to choose the runtime.
- OpenCode is an optional implementation executor, never a Harness prerequisite, architect, external-action authority, or auditor.
- The router uses the project-pinned policy, rejects incompatible Structured Outputs schemas before SDK access, and preserves exposed thread IDs across output/evidence failures.
- The implementation runtime remains historical; review runtime is derived from `review` without manual manifest rewrites.
- The smallest capable runtime is preferred; size is not complexity.
- Subagents are not the default specialization mechanism.
- Project truth, decisions, Specs, skills, scripts, and policy remain persistent; ephemeral runtime state remains isolated under `.harness/runtime/` and contains no secrets, transcripts, chat history, domain truth, ADRs, Specs, or documentation.
- New Project Harness core code uses Python 3.12+ and the official Python Codex SDK directly; pre-existing Node mechanisms in other Factories are preserved.
- Existing richer domain contracts are preserved.
- Django backend execution remains under `karya-backend-router`; the generic economic router must not reinterpret it.
- Cross-factory handoff is explicit and records `automatic_handoff: false`.

## Machine-readable contracts

Canonical schemas and templates live under `skills/project-spec-architect/assets/`, including separate implementation completion, independent review, and structural baseline schemas. Durable lifecycle evidence is defined under `skills/codex-runtime-router/assets/` and materialized beside Spec evidence; `.harness/runtime/` retains only recoverable operational state. External economic execution requests, snapshots, raw logs, and route results are defined by `skills/karya-execution-router/` and stay in operating-system temporary storage outside the project repository.

## Completion

The Factory is not complete because files exist. Completion requires successful structural validation, honest semantic gaps, usable start/resume flow, evidence reconciliation, accurate root documentation/catalog routing, and no critical project knowledge left only in the design conversation.
