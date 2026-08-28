---
name: project-harness-auditor
description: Audit a project's durable AI operating harness by reconciling documentation, decisions, AGENTS.md, Specs, local skills, runtime policy, thread state, completion evidence, validation, and implementation reality. Use for periodic harness health checks or final independent review. Do not implement product changes, approve missing evidence, infer unseen chat knowledge, or replace richer domain-specific auditors.
---

# Project Harness Auditor

Verify that the project can continue without relying on the conversation that designed it.

## Audit modes

Read [references/audit-method.md](references/audit-method.md). Run deterministic structure and evidence checks first:

```bash
python scripts/audit_project_harness.py --project-root <root> [--skills-root <installed-skills>]
```

Then perform semantic reconciliation against actual project artifacts. Preserve specialized auditors: for example, a Django backend audit still owns its contract-ID-to-code-to-test traceability; this auditor verifies that the specialized result is correctly connected to the generic Spec and runtime lifecycle.

## Required comparisons

- docs and declared sources of truth against current project reality;
- decisions against architecture, methodology, or operations;
- Specs against implementation/artifacts and completion evidence;
- local skills against recurring workflows and authoritative sources;
- AGENTS routing against the actual project shape and skill inventory;
- runtime policy defaults against resolved historical execution;
- thread IDs/purposes and context boundaries against the manifest;
- validation claims against commands, exit codes, and evidence;
- parallel-writing claims against actual isolation and ownership.
- optional OpenCode route results against the external request fingerprint, Spec/version, snapshot diff, approved writable paths, router-run validations, and independent Codex review; OpenCode-authored completion is never approval.

Detect missing or obsolete truth, implicit decisions, chat-only knowledge when chat evidence is supplied, missing or redundant skills, skills for temporary tasks, oversized skills, unjustified Sol/Terra/Luna or reasoning choices, Specs that depend on history, missing evidence, and unsafe parallelism.

## Evidence and authority

Separate deterministic findings from semantic findings and unassessed areas. Never mark an unobservable check as passed. Do not convert aggregate green tests or executor-authored prose into approval without mapping acceptance/validation IDs to implementation or artifacts and command results.

Return `approved`, `approved_with_notes`, `corrections_required`, or `blocked`, with bounded findings and evidence paths. This skill audits; it does not silently repair the project.
