# Project Harness audit method

## Evidence layers

1. Structural: required files, valid metadata, schemas, references, paths, state, and receipts.
2. Contractual: IDs, versions, lifecycle status, runtime, validations, and review agree.
3. Semantic: docs and decisions describe reality; Specs cover the requested outcome; Skills remain coherent and non-duplicative.
4. Operational: threads were started/resumed as declared, context remained bounded, writes were isolated when parallel, and completion is reproducible.

For version 2, added/modified files must exist as files, deleted files must be absent, and the declared set must reconcile with the pre-run Git snapshot. A `DONE` Spec must retain durable lifecycle, canonical completion, all attempts, and required review evidence with matching Spec/version, runtime, thread IDs, baseline inputs, and approval result. `.harness/runtime/` is never required to audit done work.

For optional economic execution, inspect the external router result and its temporary artifacts. Confirm that the request fingerprint is present, the result matches the Spec/version, snapshot changes equal reported changed files, every changed path was approved, and router-run validations passed. Require an approved independent Codex review receipt that explicitly names the route result, completion evidence, snapshot diff, and router validations as inputs. Provider readiness and OpenCode completion are execution evidence, not audit approval.

## Findings

Each finding names severity, category, statement, and evidence. `high` blocks approval; `medium` requires correction; `low` may produce approval with notes. Unassessed work is not a pass.

## Runtime audit questions

- Was classification based on reasoning nature rather than file count?
- Did the runtime use policy defaults, or is the override reason concrete?
- Did Luna remain mechanical?
- Did Terra return `needs_design` instead of inventing architecture?
- Was Sol reserved for design or critical review?
- Did reasoning above high have demonstrated justification?
- Did review independence match risk?

## Knowledge audit questions

If JSON navigation exists, the deterministic audit validates its structure, local targets and fingerprints; stale or unreviewed maps require correction even when a legacy Markdown map also exists. Check that AGENTS points to JSON. Then independently reconcile node responsibilities and relation rationales with sources and the actual change. An executor's `review --note` is not independent semantic evidence. Legacy Markdown-only projects retain their prior navigation contract; do not require migration just to audit them.

- What important fact or decision exists only in supplied chat history?
- Which docs are contradicted by code, data, procedures, or observed behavior?
- Which recurring procedure is repeatedly re-discovered and deserves a Skill or script?
- Which Skill duplicates truth, attracts unrelated work, or exists for a temporary task?

When chat history is not supplied, report chat-only knowledge detection as unassessed.
