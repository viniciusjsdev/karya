# Karya Method

This document describes only the MVP Factory. It remains independently runnable: the Research Factory, Marketing Factory, and Project Harness Factory are optional workflows. Users who do not know the appropriate entry point may first invoke `$karya` for an explained recommendation and approval; direct invocation of `product-brief-architect` remains valid.

1. Capture the idea, existing PRD, client notes, or product constraints.
2. Use `product-brief-architect` to create or complete executable product contracts.
3. Invoke external `@sites` together with `$karya-frontend-builder`: Sites shows and publishes the result, while the frontend skill governs the React implementation.
4. Validate the primary journey, responsive behavior, mocks/persistence, and API boundary.
5. Use `django-backend-service-architect` to create backend planning specs and the strict machine-readable contract manifest (including exact URLs, tests, migration-generation commands, and validations), enrich backend project context, materialize the project-local architecture skill kit, summarize decisions, and obtain matching explicit approval.
6. Use `karya-backend-router` to delegate heavy writing to OpenCode Go when ready or select Codex automatically when it is not.
7. Use `django-backend-code-executor` as the mandatory implementation contract for the selected engine, composing the matching project-local layer skills for scalable packages, explicit mappers, repository-only persistence, DTO-based Controllers, business Services, configured CamelCase Models, meaningful opening docstrings, Django-generated migrations, and layered tests.
8. Use `django-backend-service-architect` in audit mode to compare each manifest contract ID with code, environment/route wiring, migrations, exact tests, commands, and execution evidence.
9. Use `karya-infra-orchestrator` to prepare local and selected deployment paths.
10. Publish when requested and validate the MVP with explicit remaining gaps.

Do not ask a later skill to reconstruct missing decisions that an earlier contract should own. Preserve product intent, keep handoffs traceable, and prefer a complete MVP journey over premature platform complexity.

Do not add market research or commercial launch work to this sequence unless the user explicitly invokes the corresponding independent factory.
