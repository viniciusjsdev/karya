# Frontend Validation Workflow

Run from the frontend root:

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
node <skill-path>/scripts/scan-karya-frontend.mjs --strict
npm run dev
npm run preview
npm run test:e2e
```

Open the application and test the primary journey on mobile and desktop. Check console errors, failed requests, keyboard behavior, responsive layouts, and failure feedback.

When the invoking request includes `@sites`, let the external plugin perform its own preview and publication workflow after this validation. Do not install hosting dependencies into the application just to invoke the plugin. Record results in `docs/validation-report.md`.
