# Product Workflow

## 1. Product definition

`product-brief-architect` accepts a rough idea, PRD, notes, market problem, feature list, or screen list. It preserves an existing PRD and creates the missing executable contracts.

Small products use `docs/product/product-brief.md`. Larger products use PRD, screen map, business rules, data contract, visual direction, and acceptance criteria under `docs/product/`.

## 2. Frontend construction

The standard command invokes external `@sites` together with `$karya-frontend-builder`. Sites owns the visible preview and publication. The frontend skill consumes product contracts and remains the mandatory contract for React stack, routes, feature pages, hooks/view models, services, repository adapters, realistic mocks, local persistence, responsive states, tests, and frontend/API handoff documents. Sites is not installed as an application dependency.

## 3. Django backend

`django-backend-service-architect` consumes product rules, data contracts, authorization expectations, frontend service contracts, and acceptance criteria. It creates and audits backend contracts, enriches project context, and materializes the local backend architecture skill kit. After explicit approval, `karya-backend-router` chooses OpenCode Go for one passive heavy-code run when ready or Codex as the automatic fallback. The selected engine follows `django-backend-code-executor` plus the matching local layer skills, using domain-first apps with `models/`, `configurations/`, `dtos/`, explicit `mappers/`, `repositories/`, `services/`, and `api/controllers/`; all ORM access stays in repositories and migrations remain Django-generated.

## 4. Infrastructure and publication

`karya-infra-orchestrator` consumes the validated frontend/backend shape, environment contract, database ownership, and deployment choice. It prepares local Docker and selected hosting paths without inventing missing application settings.
