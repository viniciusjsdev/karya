---
name: karya-frontend-builder
description: Build complete frontend applications directly from a product contract, PRD, screen specification, client notes, or sufficiently defined product idea. Use when Codex must initialize and implement a React product, site, dashboard, SaaS, internal tool, MVP, or prototype with the Karya stack, feature architecture, visual system, mocks, local persistence, API boundaries, responsive behavior, tests, and local validation. When invoked together with the external Sites plugin, act as the mandatory stack and architecture contract while Sites owns preview and publication. Do not install or embed Sites as an npm dependency. Do not use only to generate prompts, build Django backends, or configure full-stack infrastructure.
---

# Karya Frontend Builder

## Purpose

Transform a product contract into a complete, navigable, visually resolved React frontend. Implement the product directly in code; do not generate instructions for another application builder.

Preserve every explicit product decision and materialize it through the Karya stack and architecture. Fill implementation gaps with reasonable assumptions, record consequential assumptions, and prioritize a convincing MVP over premature platform complexity.

## Authority Order

Resolve decisions in this order:

1. Follow the user's explicit request.
2. Follow explicit product-contract decisions.
3. Follow Karya standards in this skill.
4. Make the smallest reasonable implementation decision.

Do not let a vague preference override an explicit product requirement. Explain any necessary exception to the factory baseline.

## Required Context

Accept any of these inputs:

- product contract or product brief
- PRD or client notes with enough product detail
- screen and flow specification
- existing repository plus a request for a new product area
- sufficiently defined idea when reasonable assumptions can close small gaps

Before coding, identify the objective, users, MVP scope, routes, primary journey, most important screen, data entities, critical interactions, visual direction, responsive expectations, and non-goals.

Prefer contracts under `docs/product/`: either `product-brief.md`, or the modular set `prd.md`, `screen-map.md`, `business-rules.md`, `data-contract.md`, `visual-direction.md`, and `acceptance-criteria.md`. Preserve path mappings documented by `product-brief-architect` when an existing PRD lives elsewhere.

If the input is too ambiguous to determine the core user journey or primary screen, route product definition to `product-brief-architect` before implementation. Do not invent a materially different product.

## Load References

Read only the references needed for the task, but always read the stack and architecture references before initializing a new project:

- `references/stack-baseline.md` for required technologies, versions, configuration, and exceptions.
- `references/architecture-standard.md` for repository shape and dependency direction.
- `references/component-responsibilities.md` before implementing pages, components, hooks, and shared UI.
- `references/data-and-api-boundary.md` before implementing mocks, persistence, forms, TanStack Query, Axios, or API contracts.
- `references/visual-responsive-standard.md` before defining tokens, layouts, PrimeReact theming, tables, charts, or mobile behavior.
- `references/npm-supply-chain-security.md` before adding, installing, auditing, or updating npm packages.
- `references/project-context-standard.md` before initializing or updating `AGENTS.md`, `.codex/`, or repository-local domain skills.
- `references/sites-composition.md` when the Karya workflow invokes this skill together with the external Sites plugin.
- `references/validation-checklist.md` before claiming completion.

Use `assets/frontend-starter/` when creating a new frontend from scratch. Adapt its product-neutral example instead of preserving demo content.

Use `assets/project-context-starter/` at the generated project root. Initialize it with `scripts/init-project-context.mjs`; preserve existing project context and rules.

Run `scripts/scan-karya-frontend.mjs` from the consuming project root after implementation. Use `--strict` only when warnings should fail CI.

## Workflow

1. Read repository instructions and every applicable contract under `docs/product/`.
2. Inspect existing files when a repository already exists; preserve unrelated user work.
3. Run the product-contract validator when available, resolve blocking contradictions, and state a concise implementation plan covering routes, features, data boundaries, visual system, validation, and explicit exclusions.
4. Initialize or merge the project-root Codex context from `assets/project-context-starter/`.
5. Initialize `frontend/` from `assets/frontend-starter/` when no frontend exists, unless the target repository itself is the frontend root.
6. Inspect dependency changes, run the lockfile verifier, and use the secure npm policy before installing packages.
7. Establish environment examples, design tokens, global styles, providers, shell, router, error boundary, and route-level loading behavior.
8. Implement the most important screen first, then complete the primary journey before secondary screens.
9. Keep routes thin and move screen composition into feature pages.
10. Put orchestration and derived state in hooks or view models.
11. Put data access, persistence, DTO mapping, and mock/API switching behind services or repository adapters.
12. Implement real interactions. Do not leave buttons, filters, forms, dialogs, menus, or navigation visually present but inert.
13. Implement loading, error, empty, success, disabled, and destructive-confirmation states where applicable.
14. Validate mobile behavior beginning at 360px and expand layouts for larger viewports.
15. Add focused tests for critical behavior, data mapping, validation, and the primary user journey.
16. Create or update `docs/frontend-architecture.md`, `docs/api-contract.md`, and `docs/validation-report.md` when they improve the downstream handoff.
17. Run supply-chain verification, clean install, signature verification, vulnerability audit, typecheck, format check, lint, tests, build, architecture scan, and local browser validation.
18. When the invoking request also names the Sites plugin, let Sites own its preview, hosting metadata, packaging, private deployment, and opening of the deployed URL. Continue to enforce this skill's stack and architecture throughout construction.
19. Report implemented scope, assumptions, validation results, remaining gaps, and the backend/publication handoff.

## Required Stack

Use the baseline defined in `references/stack-baseline.md`:

- Node.js 24 LTS and npm
- React 19 and TypeScript strict
- Vite
- React Router
- PrimeReact and PrimeIcons
- SCSS Modules plus controlled global styles and design tokens
- React Hook Form and Zod for non-trivial forms
- TanStack Query for asynchronous/server state
- React Context for small, truly global app state
- Axios behind a shared API client
- Vitest, Testing Library, and Playwright
- ESLint and Prettier

Pin direct dependency versions exactly, commit `package-lock.json`, restrict registry sources, require a seven-day release age, and disable dependency install scripts by default. Do not install an unreviewed package merely because generated code imports it.

Do not introduce CRA, CRACO, JavaScript-only source, Tailwind, shadcn/ui, Styled Components, Redux, or Zustand by default. Add a non-baseline library only when the product requires it and document why.

## Architecture Rule

Enforce this direction:

```txt
Route -> Feature Page -> Hook/View Model -> Service -> Mock Repository or API Adapter
```

Components must not directly access Axios, mock files, `localStorage`, environment variables, or backend endpoints. Shared code must remain domain-neutral. Feature code may depend on shared code; shared code must not depend on features.

## Visual Implementation Rule

Create a deliberate visual system before expanding screens:

- define colors, typography, spacing, radius, elevation, motion, and breakpoints as tokens
- configure PrimeReact consistently
- use product-specific copy and realistic mock data
- avoid generic dashboard filler and identical card grids
- make the primary screen visually strongest
- keep responsive behavior functional at 360px without horizontal page overflow
- provide accessible labels, focus states, keyboard behavior, contrast, and reduced-motion handling

Use image generation only when the product genuinely needs original raster imagery. Do not use it to replace ordinary interface implementation.

## MVP and Integration Boundaries

Default to mocked data and local persistence when a backend is not available. Prepare the same service contract for a later API adapter.

Do not implement Django, database migrations, authentication infrastructure, payments, external APIs, OCR, or AI inference unless explicitly included in the current task. Represent unavailable integrations honestly through mocks and document the future API requirement.

This skill does not install, vendor, or emulate the Sites plugin. In the Karya site workflow, the invoking command must reference both `@sites` and `$karya-frontend-builder`. Sites owns preview and publication mechanics; this skill owns stack, code architecture, quality, security, data boundaries, and validation expectations.

## Validation Commands

Run the available equivalents of:

```bash
npm run security:lockfile
npm ci
npm run security:scripts
npm run security:signatures
npm run security:audit
npm run typecheck
npm run format:check
npm run lint
npm run test -- --run
npm run build
node <skill-path>/scripts/scan-karya-frontend.mjs
npm run dev
npm run preview
```

Open the local application when browser tooling is available. Check the primary journey, console errors, responsive layouts, navigation, forms, dialogs, empty states, and failure feedback. Do not claim local readiness from a successful build alone.

## Definition of Done

Finish only when these conditions pass or are explicitly reported as blocked:

- product scope and assumptions are documented
- product contracts pass their validator, or warnings and blockers are reported
- all promised routes and primary flows are implemented
- the most important screen is complete and visually resolved
- interactions are functional rather than decorative
- routes, feature pages, hooks, services, mocks, and shared code have clear boundaries
- direct mock, API, storage, and environment access is absent from UI components
- loading, error, empty, success, and responsive states are implemented where relevant
- accessibility basics are checked
- API and architecture handoff documentation reflects the implementation
- direct dependencies, lockfile sources, integrity hashes, and install-script approvals pass supply-chain checks
- signature verification and vulnerability audit were attempted and blocking findings were investigated
- typecheck, formatting, lint, tests, build, scanner, dev server, and browser smoke checks were attempted
- when composed with Sites, Sites preview/publication results are reported without changing the Karya stack or architecture silently
- failures and unimplemented integrations are reported honestly
