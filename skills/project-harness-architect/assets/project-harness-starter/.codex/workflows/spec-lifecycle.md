# Spec lifecycle workflow

1. Design durable project truth and decisions.
2. Create `SPEC.md` and `SPEC.execution.json` with `project-spec-architect`.
3. Validate clean-thread readiness.
4. Route the resolved manifest with `codex-runtime-router`; the router does not choose the runtime.
5. If completion is `needs_design`, resolve and persist the decision, revalidate, and resume the same implementation thread.
6. Reconcile changed code, documentation and navigation. When the JSON map exists, update paths/responsibilities/relations when needed, explicitly record the source review with `project_map.py review --note`, and run the required map check alongside the Spec's tests. Review is not automatic and the map does not replace source inspection.
7. Reconcile acceptance and validation evidence.
8. Run the required review with only durable handoff artifacts.
9. Mark `done` only after evidence and review agree.
