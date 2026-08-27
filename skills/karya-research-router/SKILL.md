---
name: karya-research-router
description: Route an approved market-research contract to Codex, AppStoreTracker, Apple, OpenAlex, optional Perplexity, or Manus according to evidence type, authentication needs, cost, and source quality. Use after research scope exists. This skill routes and records provenance; it does not perform validation or make product decisions.
---

# Karya Research Router

## Purpose

Select the cheapest capable research mechanism while preserving evidence lineage. Codex remains the default research and synthesis worker. AppStoreTracker handles app-market intelligence; OpenAlex handles scholarly discovery; Perplexity is optional for broad open-web discovery; Manus is reserved for platform-native or authenticated research.

## Invocation Boundary

- Run only after an explicit research request and a focused question or research contract.
- Never run as an implicit prerequisite of the MVP Factory or Marketing Factory.
- Do not validate the idea, rewrite the research question, modify product scope, or perform public platform actions.
- Treat providers as retrieval mechanisms, not independent evidence sources.

## Routing Table

| Evidence need | Primary route | Fallback | Notes |
|---|---|---|---|
| Focused open-web fact or source | Codex web research | Perplexity if explicitly allowed | Prefer primary sources |
| Broad discovery across many open-web sources | Perplexity if allowed | Codex with narrower batches | Codex audits the returned sources |
| iOS app, developer, family, cohort, revenue/download estimates | `$app-market-intelligence-analyst` with AppStoreTracker | Apple metadata plus reported limitation | Estimates remain directional |
| Scientific, technical, or problem evidence | OpenAlex discovery, then original papers | Targeted web search | Metadata is not the paper's evidence |
| Authenticated or platform-native discovery | `$manus-platform-researcher` | Human-assisted browser research | Read-only unless separately approved |
| Synthesis, contradiction handling, decision preparation | Codex | none | Validation belongs to the harness |

Read `references/provider-routing.md` for the decision rules and `references/source-lineage.md` before merging results.

## Workflow

### 1. Validate the request

Require a decision, evidence class, geography, freshness, depth, output fields, and provider permissions. If no formal contract exists, create only the smallest routing brief needed; do not expand the research objective.

### 2. Split by evidence class

Route mixed requests into bounded tasks. Do not send the whole market question to every provider. Each task must include a maximum result count, time/period filter, and fallback.

### 3. Inspect provider readiness

Run `node scripts/research-doctor.mjs` when external providers may be used. A missing optional provider must not block Codex research. A missing authenticated-platform route produces `manual_required`, not fabricated results.

### 4. Produce the route plan

Use `node scripts/route-research.mjs <request.json>` for deterministic routing. Review the plan before running live retrieval. The script does not call external providers.

### 5. Execute bounded retrieval

- Use the web search available to Codex for focused primary-source work.
- Use `scripts/search-apple-apps.mjs` for Apple entity resolution when useful.
- Use `scripts/search-openalex.py` for scholarly discovery; inspect original papers before making substantive claims.
- Use Perplexity only when the user/configuration permits its cost and breadth adds value.
- Hand platform-native research to `$manus-platform-researcher` with a read-only contract.

### 6. Normalize evidence

Every evidence item must contain claim, evidence class, original source, retrieval mechanism, URL or stable ID, publication/event date when known, retrieval time, geography/period, observed-versus-estimated status, and confidence. Follow `references/source-quality.md`.

### 7. Handoff

Return an evidence bundle and search-failure log to `$market-validation-harness`. Do not return a build recommendation as if routing itself validated the market.

## Cost Policy

- Prefer Codex and free/owned data paths first.
- Use paid Perplexity or Manus tasks only when explicitly allowed or already approved in the research contract.
- Bound query count, result count, and task scope.
- Never use "maximum research" or unbounded autonomous exploration by default.
- Record provider, task ID where available, and reported usage; do not promise a fixed credit cost unless the provider contract guarantees it.

## Resources

- `references/provider-routing.md`: detailed provider selection.
- `references/source-lineage.md`: evidence provenance and dependence.
- `references/source-quality.md`: quality and freshness rules.
- `references/openalex.md`: OpenAlex discovery guidance.
- `references/appstoretracker.md`: AppStoreTracker role and limitations.
- `assets/research-route.schema.json`: route-plan contract.
- `assets/evidence-bundle.schema.json`: normalized evidence contract.
- `scripts/test-router.mjs`: deterministic router tests.
