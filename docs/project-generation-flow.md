# Project Generation Flow

This is the standalone MVP generation flow. Research and marketing may consume or contribute artifacts through explicit handoffs, but they are never implicit generation stages.

The process may start from a rough idea, PRD, client notes, screen list, or existing partial project.

1. Create or complete the executable product contract.
2. Invoke external `@sites` together with `$karya-frontend-builder` to build from that contract, show the result, and publish it privately without installing Sites in the application.
3. Validate product flows, responsive behavior, data boundaries, tests, and build.
4. Plan Django, create the strict machine-readable backend contract manifest with exact URLs/tests/commands, enrich root `.codex` backend context, materialize the `.agents/skills/` architecture kit, and approve the matching manifest/implementation contract version.
5. Route the approved backend to OpenCode Go when ready or Codex as fallback.
6. Implement Django through the executor-neutral backend skill and matching project-local layer skills, with one passive final/error handoff when OpenCode is selected.
7. Audit the backend against manifest IDs, contracts, environment and route wiring, generated migrations, exact tests, and validation evidence.
8. Prepare infrastructure for local and selected deployment paths.
9. Publish when requested and document validation gaps.

The result is an MVP project that can run locally and evolve from mocks to an API without changing product semantics silently.
