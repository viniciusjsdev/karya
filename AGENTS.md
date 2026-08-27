## App Factory Skills Repository

This repository contains independent Codex skills for direct MVP/prototype creation, opt-in market research/validation, opt-in commercial launch/validation, and opt-in project AI-harness design/execution/audit.

Rules:

- Treat each folder under `skills/` as an independent skill.
- Keep installable skills in `skills/`, not `.codex/` or `.agents/skills/`.
- Keep product definition, frontend construction, backend work, and infrastructure work in separate skills.
- Keep root `docs/` and `specs/` focused on workflow, routing, and handoff contracts.
- Keep `.codex/` focused on persistent factory-level workflows, references, checklists, decisions, goals, templates, and schemas.
- Keep `templates/` focused on reusable generated-project starter material.
- Keep `examples/` focused on sample contracts and project structures.
- Keep executable instructions, scripts, and detailed references inside the relevant skill folder.
- Treat the MVP Factory, Research Factory, Marketing Factory, and Project Harness Factory as independent workflows.
- Never make Research or Marketing a prerequisite, hidden stage, or blocking gate for the MVP Factory.
- Invoke a cross-factory handoff only after explicit user request or approval; record `automatic_handoff: false` in machine-readable decisions.
- Use `project-harness-architect` only when the user explicitly asks to bootstrap or evolve how a project works with AI; it is not a prerequisite of any other Factory.
- Use `project-spec-architect` to create a bounded human-readable Spec plus resolved machine-readable execution manifest; READY requires clean-thread executability without design-chat history.
- Use `project-skill-author` only for stable, specialized, recurring project procedures; keep truth in docs, decisions in ADRs, changes in Specs, and deterministic operations in scripts.
- Use `codex-runtime-router` only after runtime selection is materialized; the router validates and starts/resumes the declared Codex thread without another LLM choosing the runtime.
- Use `project-harness-auditor` to reconcile project truth, decisions, Specs, skills, runtime, threads, validation, and completion evidence without implementing corrections.
- Keep the project-pinned runtime policy at `.codex/references/runtime-policy.json`; do not silently validate a historical Spec against a newer Factory default.
- Keep ephemeral Spec/thread/run state under generated-project `.harness/runtime/`, gitignored and separate from durable project truth. Never store secrets, transcripts, conversation history, domain knowledge, ADRs, Specs, or persistent documentation there.
- Implement new Project Harness core scripts and deterministic tests in Python 3.12+; use the official Python Codex SDK directly for live routing. Preserve pre-existing Node mechanisms belonging to the other Factories.
- Prefer Design Thread -> durable Spec -> independent Implementation Thread. Do not use subagents as the normal specialization mechanism.
- Start from a PRD, product brief, client notes, or rough idea.
- Use `product-brief-architect` to create an executable product contract.
- Use `app-factory-frontend-builder` to implement the React frontend directly from product contracts.
- For the standard visible site flow, invoke external `@sites` together with `$app-factory-frontend-builder`; Sites owns preview/publication and the frontend skill owns implementation standards.
- Do not install Sites as an npm dependency merely to invoke the plugin.
- Use `django-backend-service-architect` only after enough product/frontend/API context exists; it plans, enriches backend project context, and audits but does not implement.
- Use `app-factory-backend-router` after backend contract approval to choose OpenCode Go when ready or Codex as the automatic fallback.
- Use `django-backend-code-executor` only after the backend implementation contract is explicitly approved.
- Use `app-factory-infra-orchestrator` only after a frontend/backend project shape exists.
- Preserve MVP validation speed over premature platform complexity.
- Validate every changed skill with `quick_validate.py`.

## Factory Routing

- For product definition, construction, backend, infrastructure, hosting, or technical MVP validation, use the standalone MVP Factory.
- For market investigation, app-market intelligence, evidence collection, or hypothesis validation, use the standalone Research Factory.
- For positioning, account setup information, launch planning, creative production, platform execution, or commercial-result validation, use the standalone Marketing Factory.
- For project knowledge architecture, AGENTS/Codex context, local skill policy, Spec-driven execution, deterministic model/reasoning/thread routing, or harness audit, use the standalone Project Harness Factory.
- Accept existing products and artifacts from outside the App Factory; no factory must have produced the input for another factory to use it.
- Preserve producer artifacts and use optional handoff contracts instead of silently changing another factory's source of truth.

## Project Harness Factory

- Audit before materializing; classify mechanisms as exists, generalize, keep specific, or create new.
- Do not impose a fixed docs tree or create empty directories. Adapt to the project's domain and preserve coherent existing paths.
- Keep human intent in `SPEC.md` and resolved runtime in `SPEC.execution.json`.
- Central runtime defaults are Sol/high for design, Terra/medium for normal implementation, Luna/low for mechanical work, and Sol/high for critical review; deviations require reasons.
- Treat complexity as the nature of reasoning, not the number of files.
- On an absent consequential decision, return `needs_design`, persist the resolution in docs/ADR/Spec, and resume the existing implementation thread when possible.
- Preserve a thread ID as soon as the SDK exposes it, including failed structured-output/evidence runs; retry through `resume`, not a duplicate `new` thread.
- Use the implementation completion schema for implementation/worker runs and the independent review evidence schema for review runs. A required review must receive the Spec, resolved manifest, diff/artifacts, tests, and completion evidence.
- Audit declared changed files and local artifacts against the working tree. Structured prose claiming a command passed is not sufficient when its files, IDs, paths, or required review do not reconcile.
- Keep same-working-tree writes sequential by default. Parallel writers require isolated worktrees/branches, ownership, merge, conflict, and completion policy.
- Preserve frontend/backend context starters and specialized Django contracts/audits; generic Harness artifacts may reference but must not downgrade them.

## Research and Market Validation

- Use `market-research-architect` to create the research decision, hypotheses, falsifiers, evidence tasks, depth, provider permissions, and completion rules.
- Use `app-factory-research-router` after a research question/contract exists; Codex is the default researcher and synthesizer.
- Use `app-market-intelligence-analyst` for iOS apps, developers/app families, or comparable cohorts with AppStoreTracker plus Apple confirmation.
- Treat AppStoreTracker downloads/revenue as directional modeled estimates, never audited actuals; normalize storefronts, periods, currencies, cohorts, and metric definitions.
- Use OpenAlex for scholarly discovery and inspect original works for substantive evidence.
- Use Perplexity only as an optional broad open-web discovery mechanism when permitted.
- Use `manus-platform-researcher` only for bounded read-only research inside native/authenticated platforms; it must not contact, follow, like, publish, create accounts, or change state.
- Preserve original-source lineage separately from retrieval mechanism, transformations, dependence groups, limitations, counterevidence, and search failures.
- Use `market-validation-harness` after evidence exists; its adversarial lenses do not justify duplicate paid calls.
- Market validation may recommend product, marketing, experiment, revised research, pause, or rejection but must never invoke the next factory automatically.

## Commercial Launch and Validation

- Use `commercial-launch-architect` to define audience, positioning, offer, channels, account setup kits, campaign phases, KPIs, attribution, experiments, and human gates.
- Codex produces account information and instructions; the human owner creates the account and controls credentials, verification, CAPTCHA, recovery, 2FA, connector authorization, roles, billing, and paid activation.
- Never store passwords, tokens, cookies, verification codes, recovery codes, or authenticated browser state in the repository, generated projects, prompts, or receipts.
- Use `marketing-creative-builder` for channel-ready copy/assets, real experiment variants, accessibility fields, UTM metadata, claims QA, and the creative manifest; it must not publish.
- Use `app-factory-commercial-router` for bounded external operations. Keep strategy, synthesis, and creative preparation in Codex to minimize Manus credits.
- Route platform-native discovery to the Research Factory, not inside a write/execution task.
- Use `manus-commercial-operator` only after the exact account, content, target/recipients, timing, limits, and required human confirmation are present.
- Prohibit mass engagement, autonomous recipient expansion, account creation, credential handling, unapproved spend, and blind retries of ambiguous writes.
- Require a structured execution receipt and platform readback; task submission is not success.
- Use `commercial-validation-analyst` to reconcile plan, execution, data quality, funnel metrics, costs, and feedback before recommending scale, iterate, pivot, pause, or stop.

## Product Definition

- Preserve an existing PRD as the source of truth.
- Use compact product documentation for small products and modular contracts for platforms.
- Define scope, non-scope, routes, screens, interactions, states, business rules, data, visual direction, and acceptance criteria.
- Number domain rules as `BR-###` and make them testable.
- Do not silently decide permissions, compliance, billing, sensitive-data, or core-scope questions.

## Frontend Construction

- Build directly with the App Factory React/TypeScript stack.
- Enforce `Route -> Feature Page -> Hook/View Model -> Service -> Repository Adapter`.
- Keep mocks, local persistence, API access, and environment variables outside UI components.
- Use secure npm defaults, exact direct dependency versions, and a committed lockfile.
- Validate typecheck, formatting, lint, tests, build, architecture, responsive behavior, and primary flows.
- Keep Sites plugin mechanics outside the application dependency graph.

## Django Backend Creation

- Build API-first Django backends.
- Preserve product and frontend API contracts.
- Use per-domain packages for CamelCase ORM Models, model Configurations, DTOs, explicit Mappers, Repositories, Services, thin Controllers, and layered tests.
- Keep every ORM query and persistence operation inside Repositories.
- Keep Services responsible for business rules without endpoints, HTTP types, ORM imports, QuerySets, or direct database access.
- Define Controller request and response payloads in DTOs and use those DTOs in Controllers.
- Keep Controllers limited to endpoint transport.
- Keep one ORM Model per snake_case module under `models/`, export it from `models/__init__.py`, and reference specifications from the matching module under `configurations/`.
- Keep DTOs and explicit Mappers in use-case modules under `dtos/` and `mappers/`. Prefer use-case Controllers under `api/controllers/`; when Django requires multiple methods on the same URL pattern, allow one thin shared resource Controller only when every assigned method and downstream use-case module is explicit in the approved manifest.
- Use explicit, testable mapping and never add AutoMapper-style reflection dependencies; keep ORM/record mappers inside `repositories/`.
- Start every authored backend Python file with a meaningful module docstring that answers what the file does. Include its responsibility, architectural boundary, and relevant contract or business-rule references when applicable; this includes tests and package `__init__.py` files.
- Do not add or patch docstrings in Django-generated migration files. Their generated provenance header is the only permitted exception to the authored-file documentation rule.
- Never handwrite or patch migration code; generate migrations only with Django management commands.
- Prefer PostgreSQL and environment-driven settings.
- Create and explicitly approve backend planning, security, validation, and implementation contracts before implementation.
- Materialize `docs/architecture/backend-contract-manifest.json` from the architect template; keep its version/status synchronized with the implementation contract and record service ports/active Django `ROOT_URLCONF`, exact environment URL bindings, invariant IDs with exact tests, endpoint-to-layer mappings with exact endpoint tests, exact allowed `makemigrations` commands, and required validations.
- Enrich the generated project's root `.codex/` with resolved backend context; do not put executor configuration there.
- Materialize the compact project-local backend architecture kit under generated-project `.agents/skills/`; keep its skills focused on layer workflows and make them defer to approved contracts and `.codex/references/`.
- Use additional generated-project domain skills only for stable, approved, reusable product behavior; never create one skill per entity, endpoint, or temporary task.
- Keep OpenCode credentials, routing configuration, logs, and temporary execution artifacts outside generated-project `.codex/` directories.
- Route OpenCode through one passive non-interactive run; wake Codex only on the final process completion or error event, then audit with `django-backend-service-architect`.
- Require the final backend audit to build independent `contract ID -> implementation -> test -> command result` traceability; passing aggregate tests or executor-authored audit prose is insufficient.

## Infrastructure Orchestration

- Support local full-stack Docker, frontend-native hosting, backend containers, and VPS paths when needed.
- Treat Supabase as managed Postgres/Auth/Storage only when configured.
- Document RLS, SSL, network restrictions, MFA, access control, indexes, performance, backups/PITR, and secrets when relevant.
- Never commit real secrets or hardcode service role keys.
- Run `docker compose config` and the infra scan before claiming readiness.

When adding a new skill, create it under `skills/<skill-name>/` with:

```txt
SKILL.md
agents/openai.yaml
references/
scripts/      optional
assets/       optional
```
