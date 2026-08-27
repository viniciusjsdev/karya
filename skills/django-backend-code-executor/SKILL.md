---
name: django-backend-code-executor
description: Implement an approved Django backend contract using scalable per-domain Model, Configuration, DTO, explicit Mapper, Controller, Service, and Repository packages. Use when an Karya project has approved backend architecture, API, security, validation, and implementation contracts and Codex, OpenCode, or another executor must write Django code, generate command-only migrations, add layered tests, validate boundaries, and return completion evidence. Do not use for planning, product decisions, contract approval, frontend, infrastructure, or implementation without approved contracts.
---

# Django Backend Code Executor

## Purpose

Implement approved backend contracts without changing product or architecture decisions. This skill is executor-neutral: Codex, OpenCode, or another coding agent may use it.

## Mandatory Preflight

Require:

```txt
docs/architecture/backend-plan.md
docs/architecture/domain-model.md
docs/architecture/api-contract.md
docs/architecture/security-contract.md
docs/architecture/backend-validation-plan.md
docs/architecture/backend-implementation-contract.md
docs/architecture/backend-contract-manifest.json
```

Verify `backend-implementation-contract.md` and `backend-contract-manifest.json` both have `status: approved`, the same positive contract version, no unresolved template values, and no unresolved implementation blocker. Inspect `AGENTS.md`, relevant `.codex/references/`, and the required project-local layer skills under `.agents/skills/`.

If the gate fails, do not create or modify backend code. Return a missing-contract or approval report.

## Non-negotiable Architecture

```txt
HTTP -> Controller -> Request DTO -> Explicit Mapper -> Service Input -> Service
Service -> Repository contract -> Django Repository -> ORM Model
Service Result -> Explicit Mapper -> Response DTO -> Controller -> HTTP
```

Enforce:

- one CamelCase ORM entity per snake_case module under `models/`;
- models declare entities only and are explicitly exported from `models/__init__.py`;
- matching modules under `configurations/` define model specifications;
- DTOs live in use-case modules under `dtos/`;
- explicit, testable mappers translate representations without AutoMapper-style reflection;
- repositories exclusively perform ORM reads and writes;
- controllers contain endpoint transport only;
- DTOs define every payload used by controllers;
- services own business rules without endpoint or direct database access;
- every authored backend Python module starts with a meaningful module docstring that explains what the file does, its responsibility and layer boundary, and relevant contract or `BR-###` references when applicable;
- Django-generated migration modules are exempt from the docstring rule and must not be edited to add documentation;
- migrations are generated only through Django management commands and never handwritten or patched.

Read `references/architecture-standard.md` and `references/module-documentation-rules.md` before editing code.

## Implementation Workflow

1. Read the approved contracts and project context.
2. Build a contract traceability plan from manifest service bindings, invariant IDs/tests, endpoint mappings/tests, allowed execution commands, and required validations.
3. Inspect the existing backend, package manager, settings, environment examples, URL wiring, tests, and migration state.
4. Produce a concise implementation plan mapped to the approved contract.
5. Select and follow the smallest matching project-local architecture skill set for the layers being changed.
6. Add the required opening module docstring while creating or changing each authored Python file.
7. Create or update per-entity model configuration modules.
8. Declare one CamelCase ORM entity per model module, export it explicitly, and use configuration values.
9. Implement repository contracts and Django ORM repositories.
10. Implement services against repository/Unit of Work contracts.
11. Implement DTO modules and explicit mappers by use case.
12. Implement the exact thin Controller class and HTTP methods declared by the manifest and wire that class in URL configuration. Prefer one use-case Controller; allow a shared resource Controller only when same-path Django routing requires it and every method is explicit in the manifest.
13. Wire dependencies in composition modules.
14. Add tests by layer, including every exact invariant and endpoint test named in the manifest and mapper tests.
15. Run only the manifest's exact allowed Django command to generate migrations, then its required migration validations.
16. Run every required manifest validation plus `scripts/scan-django-boundaries.py`.
17. Produce completion evidence matching `assets/completion.schema.json`, including contract evidence for every invariant/endpoint ID and validation evidence for every required validation ID.

Do not alter approved contracts during implementation. If the code cannot satisfy them, stop with `contract-review-required` and describe the conflict.

## Layer Rules

Read as needed:

- Project `.agents/skills/<layer>/SKILL.md` for the exact local workflow and hard boundaries.
- `references/model-configuration-rules.md` before models or configurations.
- `references/mapping-rules.md` before DTO/service or ORM/record transformations.
- `references/module-documentation-rules.md` before creating or changing any Python module.
- `references/repository-rules.md` before persistence code.
- `references/service-rules.md` before business workflows.
- `references/dto-controller-rules.md` before payloads or endpoints.
- `references/migration-command-rules.md` before schema changes.
- `references/security-implementation-rules.md` before auth, permissions, sensitive data, CORS, throttling, or sessions.
- `references/testing-rules.md` before tests.
- `references/completion-protocol.md` before returning results.
- `references/validation-checklist.md` before finishing.

## Expected App Shape

Create only files required by the contract:

```txt
apps/<app_name>/
  configurations/
    __init__.py
    <entity>.py
  models/
    __init__.py
    <entity>.py
  dtos/
    __init__.py
    <use_case>.py
  mappers/
    __init__.py
    <use_case>.py
  composition.py
  repositories/
    __init__.py
    contracts.py
    records.py             optional
    mappers.py             when ORM/record conversion is required
    django_repository.py
    unit_of_work.py         optional
  services/
    __init__.py
    <use_case>.py
  api/
    __init__.py
    controllers/
      __init__.py
      <use_case>.py
    permissions.py
    urls.py
  tests/
    dtos/
    mappers/
    repositories/
    services/
    api/
  migrations/
    __init__.py
```

Every authored Python file in this shape, including tests and `__init__.py`, requires the opening module docstring. Files created by Django under `migrations/` are the only exception and must remain untouched.

Do not introduce `selectors/`. Repository methods own read behavior.

## Migration Workflow

Never use a file-editing tool on a migration Python file.

Use only the exact generation command in `backend-contract-manifest.json#allowed_execution_commands`, followed by the required manifest validation commands. A typical approved set is:

```bash
python manage.py makemigrations billing
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py showmigrations
```

If Django generates an incorrect migration, change the relevant model/configuration module and regenerate safely. Do not repair the generated file manually. Do not create handwritten data migrations; use an approved management-command backfill workflow.

## Validation

Run available equivalents of:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py test
python scripts/scan-django-boundaries.py
```

Use the repository's pytest, ruff, mypy, Docker, or task-runner commands only when they are listed exactly in the approved manifest validations. Do not hide a failure with `|| true`. Report unavailable dependencies or services exactly.

## Completion

Return one of:

- `completed`;
- `blocked`;
- `failed`;
- `contract-review-required`.

Completion evidence must list contract version, files changed, Django commands, generated migrations, tests, scanner result, deviations, unresolved items, validation limitations, `contract_evidence` for every invariant/endpoint ID, and `validation_evidence` for every required validation ID. Never self-approve architectural compliance; the architect/auditor performs final approval.

## Definition of Done

- approved contract gate passed;
- approved manifest matched the implementation contract and every ID was traced to code/test evidence;
- implementation stays inside allowed scope;
- all architecture invariants hold;
- domain apps use scalable packages and explicit mapper modules without an AutoMapper dependency;
- every authored backend Python module has a meaningful opening docstring and generated migrations remain untouched;
- required project-local architecture skills were followed without overriding approved contracts;
- migrations were generated by Django commands only;
- tests cover DTOs, services, repositories, APIs, and security requirements;
- validation commands were attempted and truthfully reported;
- completion evidence conforms to the schema;
- no contract, secret, frontend, infrastructure, or executor configuration was changed outside approved scope.
