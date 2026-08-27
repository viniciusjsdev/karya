# Component Responsibilities

## Feature Pages

Use feature pages to compose complete screens. Let them call feature hooks, select view states, arrange sections, and pass typed data and callbacks to components.

Do not let pages import mocks, call Axios, manipulate storage, parse environment variables, or contain substantial business calculations.

## Feature Components

Use feature components for product-specific cards, tables, forms, filters, charts, dialogs, drawers, and sections. Keep visual-only local state inside the component when appropriate.

Require typed props. Keep backend DTOs out of rendering components; map them to frontend view models in services or hooks.

## Shared Components

Use shared components for domain-neutral layout, accessibility, feedback, and PrimeReact conventions. Shared components must not depend on feature modules, product entities, or mock data.

Create wrappers when they add a consistent behavior such as labels, validation feedback, accessibility, loading, or product theming. Avoid wrappers that only rename a PrimeReact prop.

## Hooks and View Models

Use hooks to orchestrate state, queries, mutations, derived data, filters, pagination, feedback, and user actions. Return serializable view data and callbacks, not JSX.

Use clear names such as:

```txt
useCaseList
useCaseFilters
useCaseForm
useCaseActions
useCaseViewModel
```

Do not name ordinary functions with a `use` prefix.

## Services and Repositories

Use services for product operations and DTO mapping. Use repositories/adapters for the physical data source: mock memory, localStorage, HTTP API, or another integration.

Services must not render UI, manipulate the DOM, choose layout, or emit PrimeReact components. Normalize technical failures into typed application errors; let the view model choose user feedback.

## App Shell

Split the app shell into focused pieces as needed:

```txt
AppShell
AppHeader
AppSidebar
MobileNavigation
PageHeader
GlobalFeedback
```

Keep feature-specific actions in the feature page or inject them through explicit slots. Do not turn the shell into a global dumping ground.

## Interaction Standard

Every visible action must do something meaningful or be explicitly presented as unavailable. Implement disabled, loading, success, error, empty, and confirmation states where relevant.

Do not ship decorative filters, fake navigation, inert buttons, forms that only close a dialog, or success toasts without a state change.
