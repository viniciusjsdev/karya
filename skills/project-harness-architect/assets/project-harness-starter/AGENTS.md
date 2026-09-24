# Project agent guidance

- Read the relevant durable project sources before changing behavior or truth.
- Use `.codex/references/project-map.json` to locate sources, decisions, workflows, Specs, and validation. The map is navigation; original documents remain authoritative.
- Before changes, run `python scripts/harness/project_map.py check --project-root .`, query relevant nodes and read their sources. If stale, reconcile before relying on the map; do not refresh blindly.
- Before completion, review changed code and documents, update affected paths/responsibilities/relations, and run `python scripts/harness/project_map.py review --project-root . --note "Describe the source/map reconciliation"`, then `check` again. No map edit is required when the review establishes that navigation remains accurate. Fingerprints do not prove semantic correctness.
- Suggest a Spec when a change needs many steps or interactions across sessions; create one only if the user chooses that route. Execute bounded, sufficiently defined work directly.
- If a Spec is chosen, include `python scripts/harness/project_map.py check --project-root .` in its required validation.
- To show the map on request, run `python scripts/harness/project_map.py render --project-root .` and show `.harness/views/project-map.html`. It is a dated snapshot; regenerate it after changes.
- For a chosen Spec, treat `SPEC.md` as human intent and `SPEC.execution.json` as the resolved runtime contract.
- Do not execute a Spec marked `ready` if a clean thread still needs design-conversation history.
- Return `needs_design` instead of inventing a consequential missing decision.
- Keep project-local recurring capabilities under `.agents/skills/`; do not create a skill for a one-time task, file, entity, or endpoint.
- Keep temporary thread IDs, runs, usage, and completion staging under `.harness/runtime/`, outside durable `.codex/` context and project truth.
- Use sequential writes in one working tree unless isolation, ownership, merge, and conflict rules are explicit.
- Preserve unrelated changes and report validation limitations honestly.
