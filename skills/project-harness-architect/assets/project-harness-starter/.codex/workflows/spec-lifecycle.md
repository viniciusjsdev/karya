# Spec lifecycle workflow

1. Design durable project truth and decisions.
2. Create `SPEC.md` and `SPEC.execution.json` with `project-spec-architect`.
3. Validate clean-thread readiness.
4. Route the resolved manifest with `codex-runtime-router`; the router does not choose the runtime.
5. If completion is `needs_design`, resolve and persist the decision, revalidate, and resume the same implementation thread.
6. Reconcile acceptance and validation evidence.
7. Run the required review with only durable handoff artifacts.
8. Mark `done` only after evidence and review agree.
