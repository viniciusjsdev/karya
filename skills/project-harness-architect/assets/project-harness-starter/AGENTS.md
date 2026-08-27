# Project agent guidance

- Read the relevant durable project sources before changing behavior or truth.
- Use `.codex/references/project-harness.md` to locate sources, decisions, workflows, Specs, and validation.
- Treat `SPEC.md` as human intent and `SPEC.execution.json` as the resolved runtime contract for a bounded change.
- Do not execute a Spec marked `ready` if a clean thread still needs design-conversation history.
- Return `needs_design` instead of inventing a consequential missing decision.
- Keep project-local recurring capabilities under `.agents/skills/`; do not create a skill for a one-time task, file, entity, or endpoint.
- Keep temporary thread IDs, runs, and completion staging under `.codex/runtime/`, outside durable project truth.
- Use sequential writes in one working tree unless isolation, ownership, merge, and conflict rules are explicit.
- Preserve unrelated changes and report validation limitations honestly.
