# Data and API Boundary

## Contract

Hide the physical data source behind a typed interface:

```ts
export interface CaseRepository {
  list(input: ListCasesInput): Promise<CaseSummary[]>;
  getById(id: string): Promise<CaseDetails>;
  create(input: CreateCaseInput): Promise<CaseDetails>;
}
```

Select the adapter in infrastructure code:

```ts
export const caseRepository = env.useMocks
  ? new LocalCaseRepository(storage)
  : new ApiCaseRepository(apiClient);
```

The page and feature components must not know which adapter is active.

Keep one repository contract, one local/mock implementation, and one API implementation when the backend handoff is known. Instantiate the selected repository at the service boundary using validated environment configuration. Do not make the UI branch on mock mode.

## Mock-First MVP

Default to mocks when the backend is unavailable. Use realistic records, stable identifiers, meaningful dates, varied states, and edge cases. Avoid placeholder names such as Item 1 or User A when product language is known.

Persist user-created demo data through a storage adapter when persistence improves the prototype. Provide a documented reset mechanism when useful.

Never access `localStorage` directly from pages, components, or hooks. Wrap serialization, versioning, fallback, and parse errors in an adapter.

## TanStack Query

Use Query for asynchronous reads, caching, invalidation, and mutations even when the first repository is local/mock and returns promises. Keep query keys feature-owned and stable.

Do not mirror Query data into Context. Use Context only for app-wide concerns that are not server state.

## Axios

Create one shared Axios client with:

- base URL from validated environment configuration
- request timeout
- content-type defaults
- authentication hook when applicable
- normalized response/error handling
- no hardcoded production URL

Feature API repositories may depend on the shared client. Components and hooks must not call Axios directly.

## Forms

Use React Hook Form and Zod for non-trivial forms. Keep schemas in the owning feature. Infer form types from Zod when practical and map form values to service inputs explicitly.

Show field errors, submission progress, server failure, success feedback, and destructive confirmation. Prevent duplicate submission.

## Environment

Parse client environment once in `src/app/config/env.ts`. Expose typed, safe configuration. Remember that every `VITE_` value is public.

Recommended variables:

```env
VITE_APP_ENV=development
VITE_API_BASE_URL=http://localhost:8000/api
VITE_USE_MOCKS=true
```

Do not put secret keys, private credentials, service-role keys, or database URLs in frontend environment files.

## API Handoff

Document each future endpoint with:

- feature and screen
- method and path
- request/query shape
- response DTO
- frontend view-model mapping
- authentication and permission expectation
- loading, empty, validation, conflict, and failure behavior
- current mock repository method

Do not derive backend database models directly from component props. Treat the API contract as an explicit boundary.
