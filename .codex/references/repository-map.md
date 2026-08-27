# Repository Map

## Source of Truth

- `skills/`: installable Codex skills.
- `docs/`: factory method and architecture documentation.
- `specs/`: durable handoff contracts between stages.
- `.codex/`: persistent Codex-facing workflows, references, goals, checklists, decisions, schemas, and templates.
- `templates/`: starter material for generated projects.
- `examples/`: sample outputs and project shapes.

The repository contains four independent catalogs:

- MVP Factory: product, frontend, backend architecture/routing/execution, and infrastructure skills.
- Research Factory: `market-research-architect`, `app-factory-research-router`, `app-market-intelligence-analyst`, `manus-platform-researcher`, and `market-validation-harness`.
- Marketing Factory: `commercial-launch-architect`, `marketing-creative-builder`, `app-factory-commercial-router`, `manus-commercial-operator`, and `commercial-validation-analyst`.
- Project Harness Factory: `project-harness-architect`, `project-spec-architect`, `project-skill-author`, `codex-runtime-router`, and `project-harness-auditor`.

Backend planning/audit lives in `skills/django-backend-service-architect/`. Optional OpenCode/Codex selection lives in `skills/app-factory-backend-router/`. Approved backend code execution lives in the independent, executor-neutral `skills/django-backend-code-executor/` skill. Research and Marketing workflows live in `.codex/workflows/` but do not alter the MVP sequence.

Project Harness owns generic project-context audit/bootstrap, bounded Specs, generic local-skill policy, project-pinned runtime resolution, deterministic Python Codex SDK start/resume/review routing, structured implementation/review evidence, and cross-project audit. Generated projects keep ephemeral Harness execution state under ignored `.harness/runtime/`, separate from persistent `.codex/` context. It references rather than replaces richer frontend/backend context, Django contracts, provider routing, or commercial execution contracts.

## Do Not Confuse

- `.codex/` is not the install location for skills.
- Generated app projects receive a compact backend architecture kit and product-specific domain capabilities under `.agents/skills/`; this source repository keeps installable factory skills in `skills/` and the generated kit as an architect-skill asset.
- `opencode.json` and `.env.example` configure only this App Factory repository. Do not copy them into generated projects.
- Provider keys and authenticated platform state remain outside generated projects and must never appear in research, creative, or execution artifacts.
