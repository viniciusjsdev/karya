# READY Spec checklist

- The Spec ID, version, and status match the execution manifest.
- Goal, scope, non-scope, requirements, decisions, constraints, acceptance, references, skills, validation, review, and execution are resolved.
- A clean thread does not need design-chat history.
- Required references and project-local skills exist.
- When JSON navigation is present, original sources and map relations have been reconciled, and the Spec declares `python scripts/harness/project_map.py check --project-root .` as a required validation. Review is explicit, never an automatic check repair.
- Classification precedes runtime selection; overrides have reasons.
- Thread mode and purpose are explicit.
- Completion schema/output and `needs_design` behavior are explicit.
- `automatic_handoff` is false.
