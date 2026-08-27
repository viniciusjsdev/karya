# Stack Standard

## Frontend

- Node.js 24 LTS and npm
- React 19 and TypeScript strict
- Vite and React Router
- PrimeReact and PrimeIcons
- SCSS Modules and design tokens
- React Hook Form and Zod
- TanStack Query and Axios behind services/adapters
- Vitest, Testing Library, Playwright, ESLint, and Prettier

The complete version and supply-chain baseline lives in `skills/karya-frontend-builder/references/stack-baseline.md` and `npm-supply-chain-security.md`.

## Backend

- Python 3.12
- Django 5 and Django REST Framework
- PostgreSQL
- domain-first packages with one CamelCase ORM Model and matching Configuration per module, use-case DTOs, explicit Mappers, Repositories, Services, thin Controllers, and layered tests
- explicit mapping without AutoMapper-style reflection dependencies
- repository-only ORM access and Django-command-generated migrations
- meaningful opening module docstrings across authored backend Python files, excluding untouched Django-generated migrations
- project-local architecture skills for Model/Configuration, DTO/Mapper, Repository, Service, Controller, migration, and testing workflows
- environment-driven configuration and container compatibility

## Infrastructure

- Docker Compose for local full-stack development
- frontend-native hosting from `frontend/` when selected
- Django backend container
- Supabase as managed Postgres/Auth/Storage only when configured
- VPS or compatible full-stack container path when required

Do not force one deployment platform or introduce non-baseline frontend libraries without a product requirement and documented rationale.
