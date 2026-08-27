# Django Backend Contract

## Inputs

Consume product contracts, numbered business rules, data/DTO contracts, authorization and sensitive-data expectations, acceptance criteria, frontend architecture, and frontend service/API contracts.

## Architecture stage

Producer: `django-backend-service-architect`

Create:

- `docs/architecture/backend-plan.md`
- `docs/architecture/domain-model.md`
- `docs/architecture/api-contract.md`
- `docs/architecture/security-contract.md`
- `docs/architecture/backend-validation-plan.md`
- `docs/architecture/backend-implementation-contract.md`
- `docs/architecture/backend-contract-manifest.json`
- resolved backend context under project-root `.codex/`
- compact project-local backend architecture kit under `.agents/skills/`

Summarize entities, ownership, repositories, services, DTO/controller groups, auth/permissions, sensitive data, migrations, validation, and open assumptions. The JSON manifest records the matching service topology and active Django `ROOT_URLCONF`, exact environment URL bindings, invariants/tests, endpoints/layers/exact endpoint tests, exact allowed `makemigrations` commands, and required validations. Implementation requires matching explicit approval metadata and contract version in both the implementation contract and manifest.

## Implementation stage

Producer: `django-backend-code-executor`

Router: `karya-backend-router` selects OpenCode Go when ready or Codex as fallback. Executor selection does not change this contract.

Implement:

```txt
Controller -> Request DTO -> Explicit Mapper -> Service -> Repository contract
Django Repository -> ORM Model
Service Result -> Explicit Mapper -> Response DTO -> Controller
```

Required invariants:

- ORM entity class names use CamelCase.
- Each Model lives in a snake_case module under `models/`, is exported from `models/__init__.py`, and references the matching `configurations/` module.
- DTOs and explicit Mappers use per-use-case modules. Prefer per-use-case Controllers; same-path methods may share only an explicitly manifested thin resource Controller. AutoMapper-style reflection dependencies are forbidden.
- Application Mappers perform representation conversion only; ORM/record Mappers remain repository-local and never query or persist.
- Repositories exclusively own ORM queries and persistence.
- Controllers contain endpoint transport and use DTO-defined payloads.
- Services own business rules without endpoints, HTTP types, ORM imports, QuerySets, or direct database access.
- Every authored backend Python module, including tests and package `__init__.py` files, starts with a meaningful docstring explaining what it does, its responsibility and boundary, and relevant contract or `BR-###` references when applicable.
- Django-generated migration files are the sole docstring exception and must never be patched to add documentation.
- Project-local layer skills route focused implementation work but never override approved contracts or `.codex` references.
- Schema migrations are generated only through Django management commands and are never handwritten or patched.

Return code, generated migrations, layered DTO/Mapper/Service/Repository/API tests, command results, architecture scan, contract evidence for every invariant/endpoint ID, validation evidence for every required validation ID, validation limitations, and structured completion evidence.

## Audit stage

Producer: `django-backend-service-architect`

Compare approved contracts and manifest with code, environment examples, URL wiring, generated migrations, exact invariant tests, required command results, and execution evidence. Return approval or bounded correction findings without changing implementation code.
