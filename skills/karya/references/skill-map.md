# Karya Skill Map

This is a compact routing index. After approval, load the selected skill's full `SKILL.md` and relevant references before using it.

## Karya coordination

| Skill | Responsibility | Boundary |
| --- | --- | --- |
| `karya` | Classifies the immediate objective, recommends the smallest route, explains why, obtains approval, and remains the conversational coordinator | It is not a Factory and does not replace specialist contracts |

## MVP Factory

| Skill | Responsibility | Required state |
| --- | --- | --- |
| `product-brief-architect` | Creates or completes an executable product contract | Idea, PRD, notes, problem, feature, or existing partial product context |
| `karya-frontend-builder` | Implements a React/TypeScript frontend and its validation contract | Sufficient product/frontend definition |
| `django-backend-service-architect` | Plans and audits API-first Django architecture and contracts | Product, frontend, or API context sufficient for backend decisions |
| `karya-backend-router` | Selects OpenCode when ready or Codex fallback for approved backend implementation | Explicitly approved matching backend contract and manifest |
| `django-backend-code-executor` | Implements the approved Django contract and returns evidence | Approved contract, manifest, writable scope, and executor selection |
| `karya-infra-orchestrator` | Creates or normalizes local and deployment infrastructure | Frontend/backend project shape exists |

## Research Factory

| Skill | Responsibility | Required state |
| --- | --- | --- |
| `market-research-architect` | Defines hypotheses, falsifiers, evidence tasks, depth, permissions, and completion rules | Market question, hypothesis, product, or research need |
| `karya-research-router` | Routes approved evidence tasks across suitable providers | Approved research contract |
| `app-market-intelligence-analyst` | Analyzes iOS apps, developers, families, and cohorts using modeled estimates plus Apple confirmation | Bounded iOS question and normalized scope |
| `manus-platform-researcher` | Performs bounded read-only research in authenticated/native platforms | Exact read-only research brief and available platform access |
| `market-validation-harness` | Produces an adversarial evidence-based market decision | Normalized evidence bundle |

## Marketing Factory

| Skill | Responsibility | Required state |
| --- | --- | --- |
| `commercial-launch-architect` | Defines audience, positioning, offer, channels, setup kits, KPIs, experiments, and gates | Existing product, service, launch brief, or accepted decision |
| `marketing-creative-builder` | Produces channel-ready creative packs and manifests | Approved launch contract and product/brand evidence |
| `karya-commercial-router` | Routes bounded commercial work to Codex, human gates, or Manus | Approved launch contract or exact bounded operation |
| `manus-commercial-operator` | Executes an exact approved native-platform action and returns a receipt | Exact account, artifact, target, timing, limits, and confirmation |
| `commercial-validation-analyst` | Reconciles plan, receipts, metrics, costs, and feedback | Sufficient commercial execution and measurement evidence |

## Project Harness Factory

| Skill | Responsibility | Required state |
| --- | --- | --- |
| `project-harness-architect` | Audits and materializes the minimum durable AI operating structure | Explicit request to bootstrap or evolve how a project works with AI |
| `project-spec-architect` | Creates one bounded `SPEC.md` and resolved `SPEC.execution.json` | A concrete change needing clean-thread execution |
| `project-skill-author` | Creates a project-local skill for a stable specialized recurring procedure | Durable truth exists and recurrence justifies a skill |
| `codex-runtime-router` | Validates and starts/resumes an exact READY implementation or review thread | Resolved valid execution manifest and project-pinned runtime policy |
| `project-harness-auditor` | Reconciles project truth, Specs, runtime, threads, validation, and evidence | Existing Harness artifacts and observable project state |

## Direct execution

Recommend direct Codex execution when the request is concrete, bounded, authorized, and does not require one of the specialist contracts above. Examples include a small bug fix, a focused explanation, a mechanical rename, or a review of supplied code.

Direct execution is a first-class Karya route, not a failure to select a Factory.
