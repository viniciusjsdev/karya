# Data Boundaries

- Define a typed repository contract for each meaningful data capability.
- Keep local/mock and API implementations behind the same contract.
- Select adapters behind the service boundary using validated environment configuration.
- Use TanStack Query for async/server state; do not mirror query data into Context.
- Use React Context only for small app-wide concerns such as session, theme, and permissions.
- Encapsulate localStorage through a versioned adapter with parse fallback and namespace.
- Parse API responses at the boundary with Zod when runtime validation is valuable.
- Map backend DTOs to frontend view models before rendering.
- Document future endpoints in `docs/api-contract.md`.
