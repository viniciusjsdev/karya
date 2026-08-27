# Factory Handoff Contracts

## Independence and invocation

The MVP, Research, and Marketing factories are independent. The handoffs below describe compatible artifacts, not a mandatory global pipeline. A consumer runs only after explicit user invocation or approval; a producer must never trigger it silently.

## Product to frontend

Producer: `product-brief-architect`

Consumer: external `@sites` composed with `karya-frontend-builder`

Required output: product source of truth, scope/non-scope, primary journey, routes/screens/states/interactions, numbered business rules, data/DTO contract, visual direction, acceptance criteria, assumptions, and open questions.

Invocation rule: Sites owns preview/private publication; the frontend builder owns stack, architecture, security, code quality, and application validation. Do not install Sites merely to reference the plugin.

## Frontend to backend

Producer: `karya-frontend-builder`

Consumer: `django-backend-service-architect`

Required output: implemented frontend, architecture notes, repository/service contracts, mock DTOs, future API contract, environment expectations, validation report, and any variance from product contracts.

## Backend architecture to implementation

Producer: `django-backend-service-architect`

Consumer: `karya-backend-router`, then OpenCode Go or Codex using `django-backend-code-executor`

Required output: explicitly approved backend implementation contract, domain/API/security/validation contracts, matching approved `backend-contract-manifest.json`, resolved project-root `.codex` backend context, compact `.agents/skills/` architecture kit, scalable per-domain package/module map, service/active-URLconf/exact-environment topology, invariant-to-test map, exact endpoint/layer/test map, exact allowed migration-generation commands, explicit mapper responsibilities, authored-module documentation policy, writable scope, migration policy, and layered test expectations.

Routing rule: use OpenCode only when its CLI, OpenCode Go credential, and configured model are ready. Otherwise continue with Codex without changing the approved contract. OpenCode execution waits passively and emits one final completion/error result; no executor configuration enters the generated project's `.codex/`.

## Backend implementation to audit

Producer: `django-backend-code-executor`

Consumer: `django-backend-service-architect`

Required output: Django implementation with meaningful opening docstrings in every authored Python module, untouched Django-generated migrations, layered tests including mapper coverage, command results, architecture scan, changed-file manifest, contract evidence for every invariant/endpoint ID, validation evidence for every required validation ID, validation limitations, contract deviations, and unresolved items.

## Backend to infrastructure

Producer: audited output from `django-backend-service-architect`

Consumer: `karya-infra-orchestrator`

Required output: backend structure, environment example, database ownership, migrations and server commands, health endpoint, CORS/auth/rate-limit expectations, API contract, container compatibility, and validation status.

## Infrastructure to validation/publication

Producer: `karya-infra-orchestrator`

Consumer: user and selected deployment target

Required output: local orchestration, service Docker assets where applicable, environment contracts, deployment instructions/configuration, secrets boundaries, smoke-test commands, and honest validation status.

## Research architecture to routing

Producer: `market-research-architect`

Consumer: `karya-research-router`

Required output: research/decision ID, market frame, numbered hypotheses and falsifiers, evidence tasks, geography/platform/period/freshness, inclusion/exclusion rules, depth, provider permissions/budget, completion/stop conditions, and open questions.

## Research routing to specialized evidence work

Producer: `karya-research-router`

Consumers: Codex research, `app-market-intelligence-analyst`, OpenAlex discovery, optional Perplexity discovery, or `manus-platform-researcher`

Required output: bounded task IDs, evidence class, primary/fallback mechanism, query/filters, result cap, source fields, provenance requirements, cost limits, and status. Provider mechanisms must preserve original-source lineage.

## Evidence to market validation

Producer: research tasks and specialized analysts

Consumer: `market-validation-harness`

Required output: normalized evidence items, observed/estimated/derived status, original source, retrieval mechanism, scope/period, transformations, dependence groups, confidence, limitations, counterevidence, and search failures.

Optional next consumers: `product-brief-architect`, `commercial-launch-architect`, or a new research/experiment run. The market decision only recommends the handoff; it does not invoke it.

## Commercial architecture to creative production

Producer: `commercial-launch-architect`

Consumer: `marketing-creative-builder`

Required output: approved audience, positioning, offer, channel/placement, product truth and proof, prohibited claims, CTA/destination, brand/language/accessibility constraints, experiment metadata, and approval owner.

## Account setup kit to human owner

Producer: `commercial-launch-architect`

Consumer: human account owner

Required output: handle options, display/category/bio/link/contact fields, visual brief, professional settings, business/analytics connections, security/recovery checklist, and first content structure. Passwords, verification, 2FA, recovery codes, and live account creation are never included.

## Creative pack to commercial routing

Producer: `marketing-creative-builder`

Consumer: `karya-commercial-router`

Required output: immutable artifact/version references, final copy/assets, channel/placement, target account, CTA/URL/UTM, accessibility fields, claim proof, approval state, experiment ID, and expected metrics.

## Commercial routing to Manus execution

Producer: `karya-commercial-router`

Consumer: `manus-commercial-operator`

Required output: exact operation ID/mode/account, final artifact version, recipients or target objects, schedule/time zone, confirmation record, cost/item/retry/time limits, and expected receipt fields. Strategy, discovery, credentials, and account creation are prohibited.

## Execution to commercial validation

Producer: `manus-commercial-operator` or human executor

Consumer: `commercial-validation-analyst`

Required output: receipt with operation/provider task IDs, status, account/platform, timestamps, changed objects, native URLs/IDs/readback, errors, retries, reported usage, and external-state flag. The validator also consumes funnel/product/CRM metrics and complete known costs.

## Cross-factory handoff rule

When one factory's result suggests work in another, record `optional_handoff`, target skill, reason, required input, and `automatic_handoff: false`. The user chooses whether and when to continue.
