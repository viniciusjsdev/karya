# Sites Composition

Sites is an external Codex plugin, not an npm dependency and not a bundled part of this skill.

The Karya creation request should invoke both capabilities:

```txt
Use @sites to build, show, and privately publish this product.
Follow $karya-frontend-builder as the mandatory implementation contract.
Read docs/product/ and preserve the Karya stack, feature architecture,
npm security policy, data boundaries, responsive rules, tests, and validation.
```

## Responsibility boundary

`@sites` owns:

- the visible local preview
- Sites-specific project metadata and build adaptation
- packaging and hosting mechanics
- private publication by default
- opening and returning the deployed URL

`$karya-frontend-builder` owns:

- React/TypeScript stack decisions
- React Router, PrimeReact, SCSS Modules, and design tokens
- feature architecture and component responsibilities
- mocks, local persistence, services, and future API adapters
- npm supply-chain policy
- responsive behavior, accessibility, tests, and application validation

Do not add Cloudflare, Wrangler, Vinext, Sites SDKs, or hosting packages to the frontend merely to reference the plugin. Let Sites apply its own current hosting workflow externally.

If a Sites default conflicts with an explicit Karya product, stack, architecture, or security decision, preserve the Karya decision because the invoking request explicitly makes this skill the implementation contract. Report any hosting incompatibility instead of silently replacing the frontend stack.
