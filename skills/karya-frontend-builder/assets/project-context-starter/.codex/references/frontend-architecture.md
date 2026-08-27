# Frontend Architecture

Use this dependency direction:

```txt
Route -> Feature Page -> Hook/View Model -> Service -> Repository
                                                    -> Local/Mock Adapter
                                                    -> API Adapter
```

## Ownership

- `src/app`: providers, router assembly, environment parsing, global styles, and composition.
- `src/routes`: thin route entries, lazy loading, guards, and params.
- `src/features`: product-specific screens, components, hooks, services, schemas, types, and repositories.
- `src/shared`: domain-neutral components, hooks, utilities, and types.
- `src/services`: shared infrastructure such as Axios and storage adapters.
- `src/mocks`: mock data, factories, and local repository implementations.

Shared code must not depend on features. UI files must not access Axios, mocks, storage, endpoints, or environment variables directly.
