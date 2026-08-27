# Skill Catalog

## Invocation model

The catalog is divided into four independent factories. Install or invoke only the skills needed for the current objective. Research, Marketing, and Project Harness are never implicit prerequisites of MVP construction or of one another.

## MVP Factory

### product-brief-architect

Creates or completes an executable product contract from ideas, PRDs, notes, problems, features, or screens. It does not write application code.

### app-factory-frontend-builder

Builds the complete React/TypeScript frontend from product contracts. In the visible-site workflow it is composed with external `@sites`, which owns preview/publication without becoming an npm dependency.

### django-backend-service-architect

Creates backend planning, security, validation, and implementation contracts plus the machine-readable service/invariant/endpoint/validation manifest, materializes project context/architecture skills, and audits completed code with ID-level traceability. It does not implement.

### app-factory-backend-router

Routes an approved matching backend contract/manifest version to OpenCode Go when ready or Codex as fallback and validates structured per-ID completion evidence. It does not define or approve backend architecture.

### django-backend-code-executor

Implements an approved Django contract/manifest with explicit Model/Configuration, DTO/Mapper, Controller, Service, Repository, migrations, exact invariant and endpoint tests, exact allowed migration-generation commands, required validations, and structured evidence.

### app-factory-infra-orchestrator

Prepares Docker, environment, Supabase, frontend hosting, backend container, and VPS paths after a project shape exists.

## Research Factory

### market-research-architect

Creates the research decision frame, hypotheses, falsifiers, source/evidence tasks, depth, budget, and completion criteria. It plans but does not retrieve or decide.

### app-factory-research-router

Routes evidence tasks across Codex, AppStoreTracker/Apple, OpenAlex, optional Perplexity, and Manus. It preserves source lineage and does not validate the idea.

### app-market-intelligence-analyst

Analyzes iOS apps, developers/families, and comparable cohorts using AppStoreTracker estimates plus Apple confirmation. It distinguishes observed, estimated, derived, and missing data.

### manus-platform-researcher

Runs bounded read-only research inside native/authenticated platforms. It can find creators, communities, competitors, and live signals but never contacts, follows, likes, publishes, or changes state.

### market-validation-harness

Applies adversarial methodology, devil/angel, arbitration, evidence audit, and experiment design to produce a traceable market decision. It does not start another factory.

## Marketing Factory

### commercial-launch-architect

Creates positioning, offer, channels, account setup kits, campaign phases, KPIs, attribution, experiments, and human gates for any existing product.

### marketing-creative-builder

Creates channel-ready copy, creative/video briefs and assets, variants, accessibility fields, UTM metadata, and a production manifest. It never publishes.

### app-factory-commercial-router

Routes commercial work to Codex, Manus, or human gates while minimizing Manus credits and requiring exact approval for external actions.

### manus-commercial-operator

Executes only an approved publish, schedule, one-to-one contact, metrics read, or CRM update through a connected platform and returns a verification receipt.

### commercial-validation-analyst

Reconciles launch contract, receipts, funnel metrics, costs, and feedback to recommend scale, iterate, pivot, pause, or stop.

## Project Harness Factory

### project-harness-architect

Audits any new or existing project, maps sources of truth, preserves existing documentation, and materializes only the minimum AGENTS/Codex/Spec/runtime/thread/validation infrastructure needed for durable AI work. It does not implement project scope.

### project-spec-architect

Creates or refines one bounded `SPEC.md` plus a resolved `SPEC.execution.json`, applies the clean-thread READY definition, and materializes classification, model, reasoning, thread, skills, references, validation, review, escalation, and completion evidence paths. It does not execute.

### project-skill-author

Creates a project-local `.agents/skills/` capability only for stable specialized recurring procedure. It routes truth to docs, decisions to ADRs, changes to Specs, deterministic work to scripts, and rejects entity/file/endpoint/temporary-task skill fragmentation.

### codex-runtime-router

Validates a resolved READY/review execution manifest against the project-pinned runtime policy and deterministically calls the official Python Codex SDK `thread_start` or `thread_resume`. It records actual thread ID and usage under ignored `.harness/runtime/`, preserves mappings across invalid output, validates implementation or review evidence, and never asks another LLM to select the runtime.

### project-harness-auditor

Reconciles project truth, decisions, AGENTS routing, Specs, local skills, runtime policy, thread state, validation, completion/review evidence, actual changed files/artifacts, and specialized audits. It reports semantic/unobservable checks as unassessed rather than silently passing them.

## General rule

Every skill reports missing/contradictory inputs. No skill silently invokes another factory, creates an account, handles credentials, authorizes spend, or changes a product contract outside its responsibility.
