# Project Harness Factory workflow

This workflow is independent and opt-in. Do not insert it into MVP, Research, or Marketing unless the user explicitly requests the handoff.

1. Audit the project and classify mechanisms as exists, generalize, keep specific, or create new.
2. Use `project-harness-architect` to produce and validate an accepted minimal harness plan.
3. Preview and materialize missing root context without overwriting existing files or creating empty domain directories.
4. Preserve richer producer contracts and record path mappings.
5. Use `project-skill-author` only for stable recurring specialized procedures.
6. Use `project-spec-architect` to create one bounded `SPEC.md` plus resolved `SPEC.execution.json`.
7. Require clean-thread READY validation.
8. Validate against the project-pinned `.codex/references/runtime-policy.json`, then use the Python 3.12+ `codex-runtime-router` to preview and call the exact materialized SDK runtime through `thread_start` or `thread_resume`.
9. Preserve any SDK-exposed thread ID. On `needs_design` or invalid output, do not create a duplicate thread; persist the design resolution when applicable, revalidate, and resume.
10. Reconcile completion IDs/commands with existing changed files and artifacts. When independent review is required, materialize a review Spec/manifest, use the review evidence schema, and require an approved result before `done`.
11. Use `project-harness-auditor` for the cross-project audit and report unassessed semantic areas honestly.

Keep persistent operating knowledge under `.codex/`. Keep Spec-to-thread mappings, implementation/review state, temporary receipts, usage, and operational status only under gitignored `.harness/runtime/`; do not put secrets, transcripts, chat history, domain truth, ADRs, Specs, or persistent documentation there.

Same-working-tree writes are sequential by default. Parallel writers require isolated worktrees/branches and explicit ownership, merge, conflict, and completion policy.
