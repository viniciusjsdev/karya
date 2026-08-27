# Karya End-to-End Workflow

This workflow is the standalone MVP Factory. Do not insert Research Factory or Marketing Factory stages unless the user explicitly asks to run them. Their absence is not a product-contract defect.

1. Inspect the idea, PRD, existing repository, and product documents.
2. Route missing or incomplete product contracts to `product-brief-architect`.
3. Validate `docs/product/` and resolve blocking product questions.
4. Invoke `@sites` together with `$karya-frontend-builder`: Sites owns preview/private publication, while the frontend skill is the mandatory stack, architecture, security, and quality contract.
5. Validate frontend behavior, architecture, npm supply chain, tests, and build without installing Sites as an application dependency.
6. Route backend planning, project-context enrichment, and local architecture-kit materialization to `django-backend-service-architect`.
7. Require matching explicit approval and contract version in `docs/architecture/backend-implementation-contract.md` and the strict `docs/architecture/backend-contract-manifest.json` (exact URLs, invariant/endpoint tests, allowed migration-generation commands, and validations), then run the manifest validator with `--require-approved`.
8. Invoke `karya-backend-router`; use OpenCode Go only when its CLI, credential, and configured model are ready, otherwise continue with Codex.
9. Require the selected engine to follow `django-backend-code-executor` and the matching generated-project layer skills. When OpenCode runs, wait passively for its single completion/error exit and do not poll or narrate progress.
10. Return implementation evidence and the deterministic boundary scan to `django-backend-service-architect` for independent ID-level contract audit.
11. Route only audited backend output to `karya-infra-orchestrator`.
12. Return the Sites preview/publication result when that plugin was invoked and report every validation gap honestly.

If an accepted research or commercial artifact is supplied, treat it as input evidence without transferring ownership of its decisions into this workflow. Cross-factory continuation remains explicit.
