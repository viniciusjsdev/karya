# Frontend Development Workflow

1. Read every applicable contract under `docs/product/` and relevant `.codex/references/` files.
2. Inspect the repository and preserve unrelated work.
3. Verify scope, primary journey, routes, business rules, data contracts, visual direction, acceptance criteria, and explicit non-goals.
4. If the request also invokes `@sites`, keep Sites responsible for preview/publication and this skill responsible for all implementation decisions.
5. Implement design tokens, providers, app shell, router, error boundary, loading, and 404 behavior.
6. Implement the most important screen and primary journey first.
7. Add services, repositories, mocks, storage, and future API adapters behind typed boundaries.
8. Implement responsive, accessible, loading, empty, error, success, and permission states.
9. Add focused tests and update architecture/API documentation.
10. Run `.codex/workflows/frontend-validation.md`.
11. Record remaining gaps and downstream Django/publication handoff.
