# Project Harness Factory workflow

This workflow is independent and opt-in. Do not insert it into MVP, Research, or Marketing unless the user explicitly requests the handoff.

1. Audit the project and classify mechanisms as exists, generalize, keep specific, or create new.
2. Use `project-harness-architect` to produce and validate an accepted minimal harness plan.
3. Preview and materialize missing root context without overwriting existing files or creating empty domain directories.
4. Preserve richer producer contracts and record path mappings.
5. Use `project-skill-author` only for stable recurring specialized procedures.
6. Use `project-spec-architect` to create one bounded `SPEC.md` plus resolved `SPEC.execution.json`.
7. Require clean-thread READY validation.
8. Validate against the project-pinned `.codex/references/runtime-policy.json`, then either use the Python 3.12+ `codex-runtime-router` for the exact materialized Codex SDK runtime or, when the user explicitly prioritizes economy, evaluate a READY non-Django implementation with `karya-execution-router`.
9. For optional OpenCode execution, keep provider configuration and the exact request outside the project, require action-time confirmation, snapshot the project, restrict writes/commands, wait for one final child-process result, and preserve Codex fallback.
10. Before structural work, require a durable behavior baseline and capture the dirty/untracked Git snapshot before SDK access.
11. Preserve any SDK-exposed thread ID. On `needs_design`, invalid schema, invalid evidence, or `changes_requested`, resume the existing purpose-specific thread instead of creating a duplicate.
12. Reconcile AC/VAL arrays, canonical router-run validations, and added/modified/deleted files against the baseline. OpenCode output still requires independent Codex review using its diff/snapshots, completion evidence, and router-run validations.
13. Materialize completion, review attempts, and lifecycle beside the Spec; use `project-harness-auditor` without depending on `.harness/runtime/`.

Keep persistent operating knowledge under `.codex/`. Keep durable Spec lifecycle and evidence under the Spec; keep only recoverable mappings and operational status under gitignored `.harness/runtime/`. Do not put secrets, transcripts, chat history, domain truth, ADRs, Specs, or persistent documentation there.

Same-working-tree writes are sequential by default. Parallel writers require isolated worktrees/branches and explicit ownership, merge, conflict, and completion policy.
