# Backend Project Context Standard

## Location

Use one project-root context shared by frontend, backend, and infrastructure:

```txt
project/
  AGENTS.md
  .agents/skills/
  .codex/
    references/
    workflows/
    checklists/
    decisions/
    templates/
  docs/
    architecture/
      backend-contract-manifest.json
  frontend/
  backend/
```

Never create `backend/.codex` inside a full-stack repository.

When `project-harness-architect` already owns the generic root context, preserve it and enrich only missing backend-specific references, workflows, checklists, contracts, and layer skills. Do not replace the generic Spec/runtime policy, and do not downgrade the richer backend contract manifest into a generic Spec manifest. The backend initializer remains valid when Project Harness was not requested.

## Responsibilities

- `docs/`: durable human-facing product and architecture truth.
- `.codex/references/`: concise resolved operational context.
- `.codex/workflows/`: repeatable project procedures.
- `.codex/checklists/`: verification gates.
- `.codex/decisions/`: accepted architecture decisions.
- `.agents/skills/`: compact project-local backend architecture kit plus project-specific domain capabilities.

Materialize the compact architecture kit for Models/Configurations, DTOs/Mappers, Repositories, Services, Controllers, migrations, testing, and domain-skill authoring. The local skills route execution and hard boundaries; `.codex/references/` and approved contracts remain the source of truth.

The mandatory kit is:

```txt
.agents/skills/
  django-model-configuration/
  django-dto-mapper/
  django-repository/
  django-service/
  django-controller/
  django-migration/
  django-backend-testing/
  backend-domain-skill-author/
```

Create additional domain skills only when the project has stable, repeated, product-specific behavior that benefits from invocation. Do not create one skill per entity, endpoint, or temporary task.

The generic `project-skill-author` policy may classify a candidate, but `backend-domain-skill-author` remains authoritative for backend product behavior because it requires approved product/backend contracts and `BR-###` traceability.

Backend context must resolve the domain-first package layout and explicit mapping policy, including Model/Configuration pairs, use-case DTO/Mapper/Controller modules, and any repository-local ORM/record mapper.

It must also include `.codex/references/module-documentation.md`, which requires a meaningful opening docstring in every authored backend Python module and records the Django-generated migration exception, plus `.codex/references/domain-skill-policy.md` for product-specific skill creation.

## Initialization

Run `scripts/init-backend-project-context.mjs`. The script creates missing context, local skills, and backend contract templates while preserving existing files. After initialization, replace placeholders only in files created by the current operation or deliberately update existing project context after inspection. Approve neither the Markdown implementation contract nor the JSON manifest while template values remain.

Do not place executor configuration, API keys, OpenCode prompts, callback state, or temporary run artifacts in `.codex`.
