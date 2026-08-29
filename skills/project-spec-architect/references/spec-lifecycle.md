# Project Spec lifecycle

## States

```txt
draft -> design -> ready -> implementation -> implemented -> review -> done
                           ^                         |
                           |                         v
                           +--- changes_requested ---+
                           |
                           +--- needs_design
```

- `draft`: the change is recorded but incomplete.
- `design`: consequential requirements or decisions are being resolved.
- `ready`: a clean implementation thread has all durable inputs it needs.
- `in_progress`: the resolved implementation thread is working.
- `needs_design`: execution found a consequential missing or contradictory decision.
- `implemented`: implementation and required executor validation are reported complete.
- `review`: required review is underway.
- `changes_requested`: review found bounded corrections; resume the existing implementation thread, then the existing review thread.
- `done`: acceptance, validation, completion evidence, and required review are reconciled.

`needs_design` returns to the design thread. Update durable docs or an ADR when the answer changes project truth, update the Spec and execution manifest, validate `ready` again, then resume the existing implementation thread whenever possible.

## READY test

The validator enforces the material parts of this test:

- matching Spec ID, version, and status in Markdown and JSON;
- no unresolved placeholders;
- non-empty goal, scope, requirements, decisions, acceptance, validation, review, and execution sections;
- at least one stable acceptance ID;
- resolved model, reasoning, thread mode, skills, references, validations, review, escalation, and completion paths;
- every required project reference and project-local skill path exists;
- runtime deviations from policy include a reason.

Human review must still ask: could a clean thread execute without asking what the design conversation decided? Passing syntax checks is necessary, not sufficient.

## NEEDS_DESIGN payload

Return structured completion evidence with status `needs_design` and the missing question, why it is consequential, impact, affected areas, alternatives when useful, and the current implementation thread ID.

Do not discard validated work. The design thread resolves and persists the decision; version 2 routing resumes the recorded implementation thread without rewriting the implementation runtime.
