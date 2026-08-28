# Karya Routing Model

Use this model to determine the smallest route for the user's immediate objective. Classification is semantic: project type alone is never sufficient.

## Primary intent classes

| Intent | Strong signals | Default route |
| --- | --- | --- |
| `direct_execution` | A bounded bug, edit, command, explanation, review, or mechanical change with sufficient context | Codex direct execution or one clearly matching specialist skill |
| `product_work` | Define, build, change, integrate, host, or validate a product, system, automation, API, frontend, or backend | MVP Factory at the earliest unmet prerequisite |
| `market_research` | Investigate demand, competitors, users, market size, evidence, falsifiers, or whether an idea is worth pursuing | Research Factory |
| `commercial_work` | Position, package, launch, publish, acquire users, operate campaigns, or evaluate commercial performance | Marketing Factory |
| `project_harness` | Make project knowledge durable for AI, define Specs/thread/runtime policy, create reusable project-local skills, or audit AI-operating readiness | Project Harness Factory |
| `mixed` | Two or more independent outcomes are explicitly requested | One primary route plus optional ordered routes; start only the approved first route |
| `unclear` | The desired outcome or artifact state is too ambiguous to select responsibly | Ask the smallest route-changing question |

## Choose the route by outcome

Ask: “What result would make this request complete now?”

- “Create an automation” usually means `product_work`.
- “Make this existing automation understandable and maintainable by new Codex threads” means `project_harness`.
- “Fix this automation's date parser” usually means `direct_execution`.
- “Determine whether companies will pay for this automation” means `market_research`.
- “Prepare and publish the launch of this automation” means `commercial_work`.

Do not route to Project Harness merely because the project is long-lived, contains automation, uses Codex, or has an `AGENTS.md`. The requested outcome must concern its AI operating structure.

## Recommend the runtime as well as the route

Every Karya recommendation names a runtime for the immediate phase, even when no Harness exists yet. The recommendation is advisory until Project Harness materializes it in `SPEC.execution.json`; it does not silently change the active conversation.

| Immediate phase | Recommended runtime | Downshift or escalation |
| --- | --- | --- |
| New project or missing AI structure: diagnose sources, documentation, decisions, and first Spec | `gpt-5.6-sol/high` | Downshift after the contract and READY Spec remove design uncertainty |
| First implementation from a resolved contract/Spec | `gpt-5.6-terra/medium` | Use Terra/high only when implementation is unusually complex but design remains resolved |
| Later bounded mechanical correction | `gpt-5.6-luna/low` | Escalate to Terra/medium when behavior or architecture is no longer mechanical |
| Security, credentials, consequential external action, hard-to-reverse change, or critical review | `gpt-5.6-sol/high` | Do not downshift while the risk trigger remains |

When Project Harness bootstrap is the route, plan `project-harness-architect` for diagnosis/materialization and a final independent `project-harness-auditor` pass in the same approved Factory scope. The first implementation is a later phase and uses a separately resolved Spec runtime, normally Terra/medium.

## Select the earliest unmet prerequisite

### MVP Factory

| Available state and objective | Entry skill |
| --- | --- |
| Idea, rough notes, incomplete PRD, unresolved product behavior | `product-brief-architect` |
| Sufficient product/frontend contract and a React UI must be built | `karya-frontend-builder` |
| Product/frontend/API context exists and Django architecture must be planned or audited | `django-backend-service-architect` |
| Matching backend contract and manifest are explicitly approved and implementation should begin | `karya-backend-router` |
| Executor is already selected and must implement the approved Django contract | `django-backend-code-executor` |
| Frontend/backend shape exists and local/deployment infrastructure is requested | `karya-infra-orchestrator` |

Do not skip a prerequisite because the user asked for a later stage. Explain what is missing and recommend the skill that establishes it.

### Research Factory

| Available state and objective | Entry skill |
| --- | --- |
| Question or hypothesis exists but scope, falsifiers, evidence, depth, or completion rules are unresolved | `market-research-architect` |
| Approved research contract exists and evidence tasks need providers | `karya-research-router` |
| A bounded iOS app/developer/cohort question is already defined | `app-market-intelligence-analyst` |
| A bounded read-only native-platform research brief is already defined | `manus-platform-researcher` |
| Normalized evidence exists and an adversarial decision is requested | `market-validation-harness` |

### Marketing Factory

| Available state and objective | Entry skill |
| --- | --- |
| Existing product or launch input needs audience, positioning, offer, channels, KPIs, experiments, or human gates | `commercial-launch-architect` |
| Approved launch contract needs copy, assets, variants, accessibility, UTM, or production manifest | `marketing-creative-builder` |
| Approved bounded commercial task needs Codex, human, or Manus routing | `karya-commercial-router` |
| Exact account, content, target, timing, limits, and confirmation exist for native execution | `manus-commercial-operator` |
| Contract, receipts, metrics, costs, and feedback exist for result evaluation | `commercial-validation-analyst` |

### Project Harness Factory

| Available state and objective | Entry skill |
| --- | --- |
| A new or existing project needs its minimum durable AI operating structure designed or evolved | `project-harness-architect` |
| One bounded change needs a clean-thread-executable Spec and resolved runtime manifest | `project-spec-architect` |
| A stable specialized recurring project procedure deserves a project-local skill | `project-skill-author` |
| A READY execution manifest must start or resume the exact Codex implementation/review thread | `codex-runtime-router` |
| Existing Harness artifacts and implementation evidence need independent reconciliation | `project-harness-auditor` |

## Mixed requests

Keep Factories independent even when the user mentions several outcomes.

1. Identify the immediate priority explicitly stated by the user.
2. Recommend that route as primary.
3. List later routes as optional with a concrete trigger and `automatic_handoff: false`.
4. If no priority can be inferred and order changes cost or scope, ask the user which outcome comes first.

Examples:

- “Build the MVP now and research competitors later” → MVP primary, Research optional later.
- “Validate demand before I spend time building” → Research primary, MVP optional after the decision.
- “Organize the repository for AI and then implement SPEC-004” → Project Harness primary; execution remains inside its approved Spec/runtime flow.
- “Fix the bug and redesign our AI workflow” → ask whether the immediate priority is the direct fix or Harness evolution if both cannot safely proceed together.

## Confidence

- `high`: intent and required artifact state are explicit.
- `medium`: the route is clear but relies on a reversible assumption.
- `low`: evidence is incomplete; present the likely route and a route-changing question.

Confidence never authorizes execution. Approval remains required.
