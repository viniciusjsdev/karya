# Stack Baseline

## Baseline Snapshot

Use this baseline for new Karya frontends. Pin exact versions in `package-lock.json` and upgrade intentionally rather than silently changing major versions.

| Area                 | Baseline                                   |
| -------------------- | ------------------------------------------ |
| Runtime              | Node.js 24 LTS                             |
| Package manager      | npm 11.18.x                                |
| UI framework         | React 19                                   |
| Language             | TypeScript 6 with `strict: true`           |
| Build                | Vite 8                                     |
| Routing              | React Router 7                             |
| Component library    | PrimeReact 10.9.x                          |
| Icons                | PrimeIcons 7                               |
| Styling              | Sass, SCSS Modules, controlled global SCSS |
| Forms                | React Hook Form 7                          |
| Validation           | Zod 4                                      |
| Server state         | TanStack Query 5                           |
| HTTP                 | Axios 1                                    |
| Unit/component tests | Vitest 4 and Testing Library               |
| Browser tests        | Playwright                                 |
| Code quality         | ESLint flat config and Prettier            |

Use the latest compatible patch within these stable major lines when initializing a project. Validate before changing a major baseline.

## Required Configuration

Configure:

- `package.json` with Node 24 engine, npm scripts, and no competing package-manager field
- exact direct dependency versions and a pinned `packageManager`
- `package-lock.json` as the only lockfile
- `.npmrc` with registry, engine, peer-dependency, audit, seven-day release age, source restrictions, and disabled install scripts
- TypeScript strict mode with `noEmit`
- `@/*` alias mapped to `src/*`
- Vite React plugin and Vitest jsdom environment
- ESLint flat config for TypeScript, React hooks, and React refresh
- Prettier formatting
- `.env.example` using `VITE_` variables only for client-safe configuration
- development, build, preview, typecheck, lint, formatting, unit test, and end-to-end test scripts
- lockfile, install-script, signature, vulnerability, and SBOM security scripts

Read `npm-supply-chain-security.md` before adding or updating packages. Never weaken install-script policy or use forced audit remediation without documenting and reviewing the risk.

Never expose secrets through Vite environment variables. Every `VITE_` value is public in the browser bundle.

## UI and Styling

Use PrimeReact in styled mode by default. Import one approved theme and PrimeIcons at the app entry point. Wrap PrimeReact primitives when a shared product convention adds behavior or styling; do not create pointless one-line wrappers.

Use:

- SCSS Modules for feature and component styles
- global SCSS only for reset, tokens, typography, theme, and app-shell primitives
- CSS custom properties as the stable design-token interface
- responsive CSS using mobile-first media queries

Do not use Tailwind, shadcn/ui, CSS-in-JS, or Styled Components by default.

## State Selection

Use the narrowest state tool that fits:

- component state: `useState` or `useReducer`
- screen orchestration: feature hooks/view models
- URL state: React Router search params
- async/server state: TanStack Query
- app-wide session/theme/permissions: React Context
- durable mock state: repository adapter backed by `localStorage`

Do not add Redux or Zustand without a concrete cross-feature state problem that Context and Query cannot handle cleanly.

## Conditional Libraries

Add libraries only when required:

- ApexCharts for product dashboards and analytical visualizations
- date-fns for non-trivial date handling
- MSW for network-level mocks and integration tests
- Sentry for error monitoring
- PostHog for product analytics
- React PDF, jsPDF, XLSX, PapaParse, JSZip, or Quill for document-heavy products

Configure Sentry, PostHog, and every external service through environment variables. Never hardcode service credentials or environment-specific endpoints.

## Explicit Non-Baseline Choices

Do not initialize new projects with:

- Create React App or CRACO
- JavaScript or JSX-only source
- Tailwind or shadcn/ui
- Styled Components
- Redux or Zustand
- multiple chart libraries
- multiple date libraries
- multiple lockfiles

Treat an explicit user request or an existing repository constraint as an exception. Document the reason and keep the exception internally consistent.
