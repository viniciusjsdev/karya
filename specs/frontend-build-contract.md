# Frontend Build Contract

## Input

- executable product contract under `docs/product/` or equivalent mapped paths
- explicit primary journey and route/screen expectations
- data/mock contract and visual direction
- acceptance criteria and known open questions

## Output

- React/TypeScript application using the Karya stack
- feature architecture following `Route -> Feature Page -> Hook/View Model -> Service -> Repository Adapter`
- functional routes, interactions, feedback, and responsive states
- realistic mocks and versioned local persistence when backend is absent
- stable service/repository contract for later API replacement
- frontend architecture, API boundary, and validation documentation
- secure npm configuration, exact dependencies, committed lockfile, tests, and build
- when the external Sites plugin is invoked, a visible preview and private publication result without adding Sites to npm dependencies

The frontend must preserve explicit product semantics. Any implementation assumption or variance must be recorded for backend and product review.

The standard factory command names both `@sites` and `$karya-frontend-builder`. Sites owns preview and hosting mechanics. The frontend skill remains authoritative for the application stack and architecture.
