# Architecture Standard

## Dependency Direction

Enforce:

```txt
Route -> Feature Page -> Hook/View Model -> Service -> Mock Repository or API Adapter
```

Allow dependencies to point inward toward stable boundaries:

```txt
app -> routes -> features -> shared
features -> services/shared
services -> shared infrastructure
mocks -> feature/shared types
```

Never allow `shared/` to import from `features/`.

## Project Shape

Create only folders required by the product, using this target:

```txt
project/
  AGENTS.md
  .agents/
    skills/
  .codex/
    references/
    workflows/
    checklists/
    decisions/
    goals/
    templates/
frontend/
  src/
    app/
      providers/
      router/
      config/
      styles/
    routes/
    features/
      feature-name/
        pages/
        components/
        hooks/
        services/
        schemas/
        mocks/
        types/
        index.ts
    shared/
      components/
      hooks/
      lib/
      types/
      utils/
    services/
      api-client.ts
      storage/
        storage.adapter.ts
    mocks/
      data/
      repositories/
      factories/
    test/
  docs/
    frontend-architecture.md
    api-contract.md
    validation-report.md
```

Keep `.codex/` and `.agents/skills/` at the project root, not inside `frontend/`, when the frontend is part of a multi-service project. If the repository itself is frontend-only, the repository root is also the frontend root.

Use feature-local mocks when only one feature owns them. Use root mocks for cross-feature entities and infrastructure.

## App Layer

Use `src/app/` for providers, router assembly, environment parsing, global styles, error boundaries, and app-wide composition. Do not put product business rules or feature-specific queries in the app layer.

Centralize providers in a clear order. Typical composition:

```txt
Error Boundary
  -> PrimeReact Provider
  -> Query Client Provider
  -> Session/Theme Providers
  -> Router
```

Provide an application error boundary, route-level loading fallback, wildcard/404 route, and lazy loading for feature entry points. Keep feature-internal splitting proportional to bundle size and navigation value.

## Routes

Keep route modules thin. Permit path declarations, lazy loading, route guards, params/search parsing, metadata, and rendering one feature page.

Do not put large JSX trees, API calls, mocks, persistence, business calculations, or form orchestration in routes.

## Features

Let features own product-specific screens, components, hooks, types, schemas, services, and adapters. Export a small public surface from `index.ts`. Avoid deep imports across features.

Cross-feature communication should use shared contracts, route state, or an intentional app-level coordinator. Do not import another feature's internal component or mock.

## Shared Code

Keep `shared/` domain-neutral. Suitable shared code includes design-system wrappers, generic layout primitives, generic hooks, formatting utilities, base errors, and reusable types.

Do not place product entities, domain validation, feature API calls, or feature copy in shared code merely to avoid deciding ownership.

## File Size and Cohesion

Review files over roughly 250 lines. Split when a file mixes data access, state, UI, business rules, and several meaningful subcomponents. Do not split concise code into meaningless wrappers.

Prefer one principal component or hook per file. Co-locate tiny private helpers when they improve readability.

## Documentation

Document:

- provider and routing structure
- feature boundaries
- service and repository contracts
- mock-to-API switching
- environment variables
- future backend endpoints
- validation status and known gaps

Keep documentation aligned with the code actually delivered.
