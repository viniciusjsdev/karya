# Karya official website

The official Karya website is a static, interactive explainer of the architecture and method documented in the repository. It is intentionally isolated under `site/`; deleting this folder does not affect Karya's Skills, Specs, Factories, routing, or runtime.

## Local development

Requirements: Node.js 24+ and npm 11+.

```bash
npm install
npm run dev
```

Production validation:

```bash
npm ci
npm run typecheck
npm run lint
npm run test
npm run build
npm run preview
```

Vite uses the `/karya/` base path in production. The expected GitHub Pages URL is `https://viniciusjsdev.github.io/karya/`.

## Architecture

- `src/content/karya.ts` is the single website content model for navigation, workflow steps, architecture nodes, routing examples, Factories, benefits, and documentation links.
- `src/App.tsx` composes the narrative page.
- `src/components/` contains focused interactive and structural UI.
- `ArchitectureDiagram.tsx` is lazy-loaded and uses `@xyflow/react`; other diagrams use semantic HTML so their information is available without canvas interaction.
- `src/styles.css` defines the Amphora/Papyrus brand tokens, shared diagram system, responsive layouts, focus states, and reduced-motion behavior.

This site uses Tailwind CSS as explicitly required by the website contract, with a controlled custom layer for the structural visual system. This is a documented exception to the normal Karya frontend baseline, which otherwise defaults to SCSS Modules and PrimeReact.

## Brand asset sync

`assets/brand/` at the repository root is the only source of truth. `scripts/sync-brand-assets.mjs` replaces `site/public/brand/` during `predev` and `prebuild`. Never edit generated files in `public/brand/` manually.

## Editing content and diagrams

1. Confirm terminology against the repository documentation.
2. Edit copy, nodes, edges, routes, and links in `src/content/karya.ts`.
3. Keep recommendation distinct from approval, Karya distinct from a Factory, and every cross-Factory handoff explicit.
4. Preserve text equivalents for every diagram.
5. Run typecheck, lint, tests, build, and a browser review at the documented breakpoints.

## GitHub Pages

`.github/workflows/pages.yml` builds only `site/dist` after a clean install, typecheck, lint, and production build. It runs on pushes to `main` that affect the website or brand assets and can also be dispatched manually.

After the first approved push, configure the repository Pages source as **GitHub Actions**.
