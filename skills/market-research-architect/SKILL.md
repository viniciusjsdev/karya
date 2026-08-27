---
name: market-research-architect
description: Turn a product idea, PRD, app concept, market question, or existing product into an executable market-research contract. Use when Codex must define hypotheses, audience, geography, evidence requirements, source routing, falsification criteria, research depth, and decision gates before collecting market evidence. This skill is optional and must never be invoked merely because an MVP is being built.
---

# Market Research Architect

## Purpose

Create the research contract that tells downstream researchers what must be learned, which claims must be challenged, and what evidence is sufficient for a decision. Keep this workflow independent from product construction and commercial launch.

## Invocation Boundary

- Run only when the user explicitly asks for market research, validation, opportunity analysis, competitive analysis, or a research contract.
- Accept a rough idea, PRD, product brief, live product, or focused market question.
- Do not block, start, or modify the MVP Factory.
- Do not silently hand findings to `product-brief-architect`; offer that handoff only after a research decision and explicit approval.
- Do not collect evidence or decide whether the idea should proceed. Define the work for the research router and validation harness.

## Workflow

### 1. Frame the decision

Record the decision the research must support, the decision owner, the deadline, and the allowed outcomes. Prefer a decision such as "run a paid-intent test" over a vague goal such as "understand the market".

### 2. Define the market frame

Specify:

- problem and proposed value;
- initial customer profile and excluded audiences;
- buyer, user, and beneficiary when they differ;
- geography, language, platform, and time horizon;
- business model and expected alternative behaviors;
- known constraints, regulated areas, and sensitive assumptions.

Read `references/research-dimensions.md` when selecting the dimensions that matter for the decision.

### 3. Turn beliefs into hypotheses

Give each hypothesis an identifier such as `HYP-001`. For every hypothesis, state:

- claim;
- why it matters;
- evidence that would support it;
- evidence that would weaken or falsify it;
- minimum acceptable confidence;
- intended decision if supported or rejected.

Do not encode the founder's preferred answer as the acceptance criterion.

### 4. Select research depth

Use one of these modes:

- `rapid`: one narrow decision, a few hours, directional evidence, explicit uncertainty;
- `standard`: multiple evidence classes and competitor/cohort comparison;
- `deep`: high-cost or high-risk decision, broader triangulation, methodology review, and stronger falsification.

Depth controls effort, not certainty. Never promise exhaustive coverage.

### 5. Design the evidence plan

Define tasks by evidence class rather than by provider. Typical classes are:

- demand and problem evidence;
- competitive and substitute evidence;
- app economics and cohort performance;
- scientific or technical evidence;
- platform-native evidence;
- pricing, distribution, and channel evidence;
- direct validation experiments.

For each task, record preferred and fallback sources, freshness needs, inclusion/exclusion rules, required fields, and maximum effort or provider budget. Let `$karya-research-router` resolve the provider.

### 6. Define completion and failure

Specify minimum source diversity, freshness, sample boundaries, missing-data handling, and stopping conditions. Search failures and unavailable sources are evidence about coverage and must be reported.

### 7. Produce the contract

Use `assets/market-research-contract.template.md`. Follow `references/contract-authoring.md` for identifiers and required sections.

## Required Output

Return:

1. executive research question;
2. market frame and exclusions;
3. numbered hypotheses;
4. research tasks with evidence class, source policy, and budget;
5. falsification and completion criteria;
6. risk and open-question register;
7. expected handoff to `$karya-research-router` and then `$market-validation-harness`;
8. a statement that no product or marketing workflow is started automatically.

## Quality Gate

Before handoff, confirm that:

- the decision is concrete;
- every critical claim has a falsifier;
- source mechanisms are not mistaken for independent evidence;
- app estimates are not treated as audited financials;
- authenticated-platform work is explicitly scoped as read-only research;
- research depth and paid-provider permissions are stated;
- missing permissions, compliance, billing, or sensitive-data questions remain open rather than silently decided.
