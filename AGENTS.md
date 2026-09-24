## Karya Repository

This repository contains independent Codex skills for direct MVP/prototype creation, opt-in market research/validation, opt-in commercial launch/validation, and opt-in project AI-harness design/execution/audit.

Karya is the umbrella system. A Factory is an independent workflow family inside Karya; a Skill is a specialized reusable capability. Preserve the names MVP Factory, Research Factory, Marketing Factory, and Project Harness Factory.

The installable `karya` skill is the optional conversational coordinator. It classifies the user's immediate objective, recommends the smallest suitable direct or Factory route, explains why, obtains approval, and then applies approved specialist skills internally while remaining the user-facing voice. It is not a fifth Factory or a mandatory prerequisite.

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
- Let users start with `$karya` when they do not know the catalog. Preserve direct specialist invocation when the required skill is already known.
- Require `$karya` to wait for route approval before applying specialist skills. Keep every cross-factory suggestion optional with `automatic_handoff: false`.
- Keep Karya as the conversational coordinator after approval; specialist skills work internally and retain their full contracts, prerequisites, validation, and authority boundaries.
- Never make Research or Marketing a prerequisite, hidden stage, or blocking gate for the MVP Factory.
- Invoke a cross-factory handoff only after explicit user request or approval; record `automatic_handoff: false` in machine-readable decisions.
- Use `project-harness-architect` only when the user explicitly asks to bootstrap or evolve how a project works with AI; it is not a prerequisite of any other Factory.
- Suggest a Spec when a change will require many steps or interactions across sessions; create one only if the user chooses that route. Handle bounded, sufficiently defined work directly. When a Spec is chosen, use `project-spec-architect` for its human-readable contract and resolved execution manifest; READY requires clean-thread executability without design-chat history.
- Use `project-skill-author` only for stable, specialized, recurring project procedures; keep truth in docs, decisions in ADRs, selected multi-step changes in Specs, and deterministic operations in scripts.
- Use `codex-runtime-router` only after runtime selection is materialized; the router validates and starts/resumes the declared Codex thread without another LLM choosing the runtime.
- Use `karya-execution-router` only as an optional economic route for a READY non-Django implementation with exact external confirmation, provider/model readiness, writable paths, mandatory prohibitions, snapshot, validations, and independent Codex review. OpenCode is never essential to Karya and Codex remains the fallback.
- Use `project-harness-auditor` to reconcile project truth, decisions, Specs, skills, runtime, threads, validation, and completion evidence without implementing corrections.
- Keep the project-pinned runtime policy at `.codex/references/runtime-policy.json`; do not silently validate a historical Spec against a newer Factory default.
- Keep only recoverable Spec/thread/run state under generated-project `.harness/runtime/`, gitignored and separate from durable project truth. Keep lifecycle, completion, review, and attempt evidence durably beside the Spec. Never store secrets, transcripts, conversation history, domain knowledge, ADRs, Specs, or persistent documentation in runtime state.
- Implement new Project Harness core scripts and deterministic tests in Python 3.12+; use the official Python Codex SDK directly for live routing. Preserve pre-existing Node mechanisms belonging to the other Factories.
- For an approved Spec route, prefer Design Thread -> durable Spec -> independent Implementation Thread. Do not use subagents as the normal specialization mechanism.
- Start from a PRD, product brief, client notes, or rough idea.
- Use `product-brief-architect` to create an executable product contract.
- Use `karya-frontend-builder` to implement the React frontend directly from product contracts.
- For the standard visible site flow, invoke external `@sites` together with `$karya-frontend-builder`; Sites owns preview/publication and the frontend skill owns implementation standards.
- Do not install Sites as an npm dependency merely to invoke the plugin.
- Use `django-backend-service-architect` only after enough product/frontend/API context exists; it plans, enriches backend project context, and audits but does not implement.
- Use `karya-backend-router` after backend contract approval to choose OpenCode Go when ready or Codex as the automatic fallback.
- Use `django-backend-code-executor` only after the backend implementation contract is explicitly approved.
- Use `karya-infra-orchestrator` only after a frontend/backend project shape exists.
- Preserve MVP validation speed over premature platform complexity.
- Validate every changed skill with `quick_validate.py`.

## Factory Routing

- When `$karya` is explicitly invoked, classify the immediate desired outcome and current artifact state before selecting a route. Project type alone is insufficient; an automation may require direct execution, MVP, Research, Marketing, or Project Harness depending on the requested outcome.
- Recommend one primary route, explain the reason, name the internal skills covered by the proposed scope, and wait for explicit approval. Do not require the user to invoke each approved specialist manually.
- Include the recommended model, reasoning, rationale, downshift condition, and required audit in every `$karya` recommendation. Treat it as advisory until a Project Harness `SPEC.execution.json` materializes the runtime; never claim the active conversation changed models silently.
- Treat cost or Codex-limit pressure as an explicit recommendation signal. Distinguish Codex-owned planning/critical decisions/audit, normal READY implementation, and mechanical low-risk work. Provider options remain consultative and assume no installation, authentication, subscription, credit, billing, authorization, or model access.
- Use direct Codex execution for bounded, sufficiently defined work when no Factory contract is needed.
- For product definition, construction, backend, infrastructure, hosting, or technical MVP validation, use the standalone MVP Factory.
- For market investigation, app-market intelligence, evidence collection, or hypothesis validation, use the standalone Research Factory.
- For positioning, account setup information, launch planning, creative production, platform execution, or commercial-result validation, use the standalone Marketing Factory.
- For project knowledge architecture, AGENTS/Codex context, local skill policy, Spec-driven execution, deterministic model/reasoning/thread routing, or harness audit, use the standalone Project Harness Factory.
- Accept existing products and artifacts from outside Karya; no factory must have produced the input for another factory to use it.
- Preserve producer artifacts and use optional handoff contracts instead of silently changing another factory's source of truth.
- For a new project or one without durable AI structure, recommend Sol/high for Harness diagnosis and source/documentation/decision design; use it for a first Spec only when the user chooses that route. Recommend Terra/medium for the first resolved implementation, Luna/low for later mechanical corrections, and Sol/high for security, credentials, consequential external actions, hard-to-reverse changes, or critical review. Require an independent Harness audit after bootstrap materialization.

## Project Harness Factory

- Audit before materializing; classify mechanisms as exists, generalize, keep specific, or create new.
- Do not impose a fixed docs tree or create empty directories. Adapt to the project's domain and preserve coherent existing paths.
- Keep human intent in `SPEC.md` and resolved runtime in `SPEC.execution.json`.
- Central runtime defaults are Sol/high for design, Terra/medium for normal implementation, Luna/low for mechanical work, and Sol/high for critical review; deviations require reasons.
- Treat complexity as the nature of reasoning, not the number of files.
- On an absent consequential decision, return `needs_design`, persist the resolution in docs/ADR/Spec, and resume the existing implementation thread when possible.
- Reject incompatible Structured Outputs schemas before SDK access. Preserve a thread ID as soon as the SDK exposes it, including failed schema/evidence runs; retry through `resume`, not a duplicate `new` thread. Preserve one implementation ID and one review ID through correction cycles.
- Keep OpenCode provider configuration, credentials, and exact execution requests outside project repositories, documentation, Specs, persisted prompts, and project `.env` files. A live external run requires separate action-time confirmation after the exact executor, provider, model, writable paths, validation IDs, and cost mode are known.
- Route generic OpenCode execution through one passive non-interactive child process and one final completion/error result. Do not spend Codex turns polling it. Reconcile snapshot diff, completion evidence, router-run validations, and independent Codex review before approval.
- Preserve `karya-backend-router` as the richer Django-specific route. Never send its backend contracts or migration rules through `karya-execution-router`.
- Use the implementation completion schema for implementation/worker runs and the independent review evidence schema for review runs. A required review must receive the Spec, resolved manifest, diff/artifacts, tests, and completion evidence.
- Audit added, modified, and deleted files against the pre-run Git snapshot and structural baseline. Reexecute required automatable validation commands canonically; structured prose claiming a command passed is not sufficient when its files, IDs, paths, or required review do not reconcile.
- Keep same-working-tree writes sequential by default. Parallel writers require isolated worktrees/branches, ownership, merge, conflict, and completion policy.
- Preserve frontend/backend context starters and specialized Django contracts/audits; generic Harness artifacts may reference but must not downgrade them.

## Research and Market Validation

- Use `market-research-architect` to create the research decision, hypotheses, falsifiers, evidence tasks, depth, provider permissions, and completion rules.
- Use `karya-research-router` after a research question/contract exists; Codex is the default researcher and synthesizer.
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
- Use `karya-commercial-router` for bounded external operations. Keep strategy, synthesis, and creative preparation in Codex to minimize Manus credits.
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

- Build directly with the Karya React/TypeScript stack.
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

<!-- karya-project-map:start -->
## Project navigation map

Use `.codex/references/project-map.json` as the current navigation index. Existing Markdown navigation remains a preserved source, not a competing generated map.
Before changes, run `python scripts/harness/project_map.py check --project-root .`, query relevant nodes, and read their original sources and applicable contracts. A pending check calls for reconciliation, not blind refresh; source reading and required tests remain mandatory.
Before completion, inspect changed code and docs, update affected sources, paths and explicit relations, then run `python scripts/harness/project_map.py review --project-root . --note "Explain source/map reconciliation and any unchanged-map decision"`. Run `check` again. For an approved Spec, include the check in its required validation. Never run review automatically just to make a check pass.
Use `query --project-root . --text "topic"` for bounded navigation. When the user wants to see the map, run `render --project-root .` and show `.harness/views/project-map.html`; regenerate after changes. HTML is a read-only snapshot, not an editor or source of truth.
<!-- karya-project-map:end -->
