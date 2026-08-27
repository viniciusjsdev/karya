# Sites Composition

Sites is an external Codex plugin. It is not an npm dependency of this frontend.

When a request names both `@sites` and `$karya-frontend-builder`:

- Sites owns preview, hosting adaptation, private publication, and opening the deployed URL.
- The frontend builder owns stack, architecture, npm security, UI, data boundaries, tests, and validation.
- Preserve React Router, PrimeReact, SCSS Modules, feature architecture, services, repositories, and mocks unless the product contract explicitly changes them.
- Do not install Cloudflare, Wrangler, Vinext, Sites SDKs, or hosting packages merely to invoke the plugin.
- Report an incompatibility instead of silently replacing the Karya implementation contract.
