# Stack Reference

## Frontend Baseline

- Node.js 24 LTS
- npm 11.18.x with exact direct versions and lockfile v3
- React 19
- TypeScript 6 strict
- Vite 8
- React Router 7
- PrimeReact 10.9.x and PrimeIcons 7
- SCSS Modules and CSS custom-property design tokens
- React Hook Form and Zod
- TanStack Query and Axios
- Vitest, Testing Library, and Playwright
- ESLint flat config and Prettier

Add conditional libraries only when product requirements justify them. Record major stack exceptions in `.codex/decisions/`.

## Backend Handoff

Prepare typed frontend contracts for Django and Django REST Framework. Do not couple components to Django models or endpoint implementation details.
