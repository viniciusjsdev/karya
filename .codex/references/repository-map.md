# Repository Map

## Source of Truth

- `skills/`: installable Codex skills.
- `docs/`: factory method and architecture documentation.
- `specs/`: durable handoff contracts between stages.
- `.codex/`: persistent Codex-facing workflows, references, goals, checklists, decisions, schemas, and templates.
- `templates/`: starter material for generated projects.
- `examples/`: sample outputs and project shapes.

The repository contains one optional coordination skill and four independent Factory catalogs:

- Karya coordination: `karya` classifies the immediate objective, recommends and explains the smallest route, obtains approval, and coordinates approved specialist skills without becoming a Factory.

- MVP Factory: product, frontend, backend architecture/routing/execution, and infrastructure skills.
- Research Factory: `market-research-architect`, `karya-research-router`, `app-market-intelligence-analyst`, `manus-platform-researcher`, and `market-validation-harness`.
- Marketing Factory: `commercial-launch-architect`, `marketing-creative-builder`, `karya-commercial-router`, `manus-commercial-operator`, and `commercial-validation-analyst`.
- Project Harness Factory: `project-harness-architect`, `project-spec-architect`, `project-skill-author`, `codex-runtime-router`, `karya-execution-router`, and `project-harness-auditor`.

Backend planning/audit lives in `skills/django-backend-service-architect/`. Optional OpenCode/Codex selection lives in `skills/karya-backend-router/`. Approved backend code execution lives in the independent, executor-neutral `skills/django-backend-code-executor/` skill. Research and Marketing workflows live in `.codex/workflows/` but do not alter the MVP sequence. Karya's compact routing model lives inside `skills/karya/` so installed users do not need the source repository to select a route.

Project Harness owns generic project-context audit/bootstrap, bounded Specs, structural baselines, generic local-skill policy, project-pinned runtime resolution, deterministic Python Codex SDK start/resume/review routing, optional economic OpenCode implementation routing, durable lifecycle and structured implementation/review evidence, and cross-project audit. Generated projects keep only recoverable operational state under ignored `.harness/runtime/`; done audits use durable Spec evidence. Provider configuration, credentials, external requests, and raw OpenCode logs remain outside project repositories.

## Do Not Confuse

- `.codex/` is not the install location for skills.
- Generated app projects receive a compact backend architecture kit and product-specific domain capabilities under `.agents/skills/`; this source repository keeps installable factory skills in `skills/` and the generated kit as an architect-skill asset.
- `opencode.json` and `.env.example` configure only this Karya repository. Do not copy them into generated projects.
- `karya-execution-router` builds its generic deny-by-default OpenCode configuration at runtime. Do not copy provider configuration or its external request into generated projects.
- Provider keys and authenticated platform state remain outside generated projects and must never appear in research, creative, or execution artifacts.
