# Mock-to-API Workflow

1. Preserve the repository contract consumed by the service.
2. Document the endpoint, request, response DTO, permissions, and failures.
3. Implement the API repository with the shared Axios client.
4. Parse and map the response at the boundary.
5. Switch adapter selection through validated environment configuration.
6. Keep pages, components, and view models unchanged unless the product behavior changes.
7. Test both adapters against the same contract expectations.
8. Remove obsolete mock behavior only after API parity is validated.
