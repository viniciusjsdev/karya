# Validation Checklist

## Product Coverage

- [ ] Explicit product decisions and assumptions documented
- [ ] MVP scope and non-goals respected
- [ ] Promised routes implemented
- [ ] Primary journey works end to end
- [ ] Most important screen is visually complete
- [ ] Visible controls are functional or clearly unavailable
- [ ] Realistic mock data and relevant edge cases included

## Stack

- [ ] Node 24 baseline documented
- [ ] npm is used and `package-lock.json` is the only lockfile
- [ ] npm CLI version matches the pinned `packageManager`
- [ ] direct dependencies use exact versions
- [ ] lockfile registry sources and sha512 integrity pass verification
- [ ] dependency install scripts are reviewed and version-pinned in `allowScripts`
- [ ] `ignore-scripts=true`, `min-release-age=7`, and Git/remote/file/directory sources are blocked
- [ ] registry signatures/provenance verification attempted
- [ ] high and critical audit findings resolved or treated as blockers
- [ ] SBOM generated for release workflows when applicable
- [ ] React, TypeScript strict, Vite, React Router, PrimeReact, and PrimeIcons configured
- [ ] SCSS Modules and design tokens used consistently
- [ ] No CRA, CRACO, JavaScript-only source, Tailwind, shadcn, or Styled Components introduced without an explicit exception
- [ ] Client environment contains no secrets
- [ ] Sites remains an external plugin rather than an npm dependency
- [ ] Sites composition does not replace the Karya stack or architecture

## Architecture

- [ ] Routes are thin
- [ ] Feature pages own screen composition
- [ ] Hooks/view models own orchestration
- [ ] Services/repositories own data access and mapping
- [ ] UI does not directly import mocks or call Axios
- [ ] UI does not directly access localStorage or environment variables
- [ ] Shared code is domain-neutral
- [ ] App shell and providers are focused
- [ ] mock/API selection occurs behind the service/repository boundary
- [ ] browser storage is encapsulated in a versioned adapter
- [ ] error boundary, route loading, lazy feature entry, and 404 route exist

## UX and Accessibility

- [ ] Loading, error, empty, success, disabled, and confirmation states covered where relevant
- [ ] 360px layout has no accidental horizontal overflow
- [ ] Tables, charts, dialogs, forms, and navigation work on mobile
- [ ] Keyboard focus and accessible names checked
- [ ] Reduced motion and contrast considered

## Commands

Run and record:

```bash
npm run security:lockfile
npm ci
npm run security:scripts
npm run security:signatures
npm run security:audit
npm run security:sbom
npm run typecheck
npm run format:check
npm run lint
npm run test -- --run
npm run build
node <skill-path>/scripts/scan-karya-frontend.mjs
npm run dev
npm run preview
```

When browser tooling is available, open the local URL and test the primary journey at mobile and desktop widths. Check console errors and failed network calls.

Classify failures as introduced defect, pre-existing defect, dependency/install failure, missing environment, unsupported environment, unavailable external service, or intentionally unimplemented scope. Fix introduced defects before finishing.

Do not claim the project works locally unless the dev server started and the rendered application was checked.

When the invoking workflow includes `@sites`, report its preview/publication result separately from frontend validation. Do not add hosting dependencies merely to reference the plugin.
