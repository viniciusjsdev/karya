---
name: product-brief-architect
description: Transform a rough product idea, PRD, client notes, market problem, feature list, or screen list into an executable product contract for direct frontend and backend implementation. Use when Codex must define or refine MVP scope, routes, screens, journeys, business rules, entities, mock data, future API shapes, visual direction, non-functional requirements, success metrics, and testable acceptance criteria. Preserve an existing PRD and create only missing companion contracts. Do not generate prompts for external app builders or implement frontend, Django, or infrastructure code.
---

# Product Brief Architect

## Purpose

Turn product intent into an executable PRD that `karya-frontend-builder` and `django-backend-service-architect` can implement without reconstructing essential decisions from guesses.

Write product contracts inside the target project. Do not produce instructions for an external application builder, and do not implement application code.

## Authority Order

1. Preserve the user's explicit decisions.
2. Preserve an existing PRD as the product source of truth.
3. Reconcile supporting artifacts against the PRD.
4. Add the smallest reasonable assumptions needed for an implementable MVP.

Never silently convert an open question into a consequential business, authorization, compliance, billing, or sensitive-data rule. Record it under `Questões em aberto` and describe its implementation impact.

## Required Inputs

Accept one or more of:

- rough idea or market problem
- existing PRD or product brief
- client notes or discovery transcript
- feature, module, route, or screen list
- existing repository and partial product documentation

Before writing, inspect `AGENTS.md`, existing `docs/product/`, relevant architecture documents, and current frontend/backend contracts. Preserve useful existing content and unrelated user work.

## Choose Contract Granularity

Use one of two modes:

### Compact mode

Use `docs/product/product-brief.md` for a landing page, focused prototype, or small MVP whose screens, rules, data, and acceptance criteria remain understandable in one document.

Start from `assets/compact/product-brief.md`.

### Modular mode

Use this structure for platforms, multiple roles, multiple modules, sensitive workflows, substantial domain rules, or a non-trivial future API:

```txt
docs/product/
  prd.md
  screen-map.md
  business-rules.md
  data-contract.md
  visual-direction.md
  acceptance-criteria.md
```

Start from the matching files in `assets/modular/`.

If a project already has a PRD, preserve its path and content. Create only missing companion contracts and document any path mapping at the top of the companion file that depends on it.

Read `references/granularity-and-authority.md` when deciding between modes or resolving conflicting sources.

## Workflow

1. Inventory the supplied sources and existing project documents.
2. Extract explicit facts, constraints, decisions, uncertainties, and contradictions.
3. Identify objective, users, problem, value proposition, primary journey, MVP boundary, non-goals, and success signals.
4. Select compact or modular mode using product complexity rather than document length.
5. Draft the PRD or preserve the existing one.
6. Define every promised route and screen, including purpose, components, states, interactions, permissions, and responsive behavior.
7. Number testable domain rules as `BR-001`, `BR-002`, and so on. Link affected screens, data, and acceptance criteria back to these identifiers.
8. Define entities, fields, relationships, enums, ownership, sensitive-data classification, mock records, local persistence, and future API shapes.
9. Define a bounded visual direction with tokens, density, component patterns, accessibility, mobile guidance, and visual restrictions.
10. Write acceptance criteria by feature and primary journey. Use observable outcomes, including validation, failure, permissions, persistence, responsiveness, and feedback.
11. Record assumptions and open questions with impact and owner when known.
12. Check cross-document traceability and run `scripts/validate-product-contract.mjs <project-root>`.
13. Report created or preserved documents, assumptions, open blockers, validation output, and the frontend/backend handoff.

## Contract Requirements

### Product source of truth

The primary PRD must explain what the product is and why it will be built. Include summary, problem, objective, users, value proposition, MVP scope, non-scope, features, journeys, non-functional requirements, success metrics, assumptions, and open questions.

### Frontend contract

For each route or distinct stateful section, define:

- objective and user role
- content and relevant components
- loading, empty, error, populated, success, disabled, and confirmation states where applicable
- navigation and functional interactions
- authorization visibility and permitted actions
- mobile and desktop behavior

Read `references/screen-and-interaction-standard.md` before writing screen contracts.

### Domain and data contract

Make business rules numbered, unambiguous, and testable. Define ownership and permission rules explicitly. Do not hide domain behavior only inside prose examples.

Define data at a contract level, not as database implementation. Include entity semantics, typed fields, relationships, enums, validation, example records, persistence expectations, request/response shapes, and error semantics.

Read `references/domain-data-and-api-standard.md` when the product has domain entities, permissions, local persistence, sensitive data, or a future API.

### Visual contract

Describe recognizable product direction without specifying every pixel. Include brand personality, references supplied by the user, token direction, typography, density, patterns for tables/cards/forms, mobile constraints, accessibility expectations, and prohibited visual choices.

### Acceptance contract

Use checkboxes with observable, verifiable outcomes. Each important feature must cover its happy path and relevant validation, error, empty, permission, persistence, and responsive cases. Reference `BR-*` identifiers when a criterion verifies a business rule.

Read `references/quality-and-traceability.md` before validation.

## Handoff Rules

The frontend builder consumes the PRD, screen map, data contract, visual direction, and acceptance criteria. It may use mocks or local persistence while preserving the documented DTO shapes.

For the standard Karya site handoff, provide this next-step invocation:

```txt
Use @sites to build, show, and privately publish this product.
Follow $karya-frontend-builder as the mandatory implementation contract.
Read docs/product/ and preserve its stack, architecture, npm security,
data boundaries, responsive rules, tests, and validation.
```

`@sites` is an external Codex plugin. Do not add it or its hosting implementation as an npm dependency of the generated frontend.

The Django architect consumes the PRD, business rules, data contract, authorization expectations, sensitive-data decisions, and acceptance criteria. Backend planning may refine transport and persistence details but must not silently change product semantics.

When a blocking product decision is unresolved, mark the affected implementation area as blocked. Do not make the entire contract unusable when unaffected MVP work can proceed safely.

## Definition of Done

Finish only when:

- the product source of truth is explicit and preserved
- scope and non-scope are distinguishable
- the primary journey and most important screen are identifiable
- every promised route has screen behavior and relevant states
- business rules are numbered and testable
- roles, permissions, ownership, and sensitive-data assumptions are explicit
- entities and DTO examples support frontend mocks and backend planning
- visual direction is specific enough for coherent implementation
- acceptance criteria are observable and traceable
- assumptions and open questions are visible
- the contract validator passes, or every warning/blocker is reported honestly
