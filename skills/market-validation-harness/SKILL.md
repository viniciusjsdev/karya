---
name: market-validation-harness
description: Challenge a market hypothesis with a provider-neutral, adversarial evidence review and produce an auditable proceed, experiment, revise, pause, or reject decision. Use after a research evidence bundle exists. This skill separates evidence, inference, assumptions, open questions, and search failures; it never starts product construction automatically.
---

# Market Validation Harness

## Purpose

Convert collected evidence into a defensible market decision. Apply opposing lenses, audit provenance and methodology, expose uncertainty, and design the cheapest next experiment. This adapts the useful reasoning structure from `research-harness` without coupling Karya to its runtime.

## Invocation Boundary

- Run only after an explicit validation request and an evidence bundle or declared evidence gap.
- Do not browse by default; request targeted follow-up through `$karya-research-router` when necessary.
- Do not modify the PRD, start an MVP, create a marketing plan, or trigger platform activity.
- Offer an optional handoff only after the decision is accepted by the user.

## Evidence Labels

Label every material statement as one of:

- `Evidence`: directly supported by a cited source or measured experiment;
- `Inference`: reasoned interpretation of evidence;
- `Assumption`: unverified premise used for planning;
- `Open question`: unresolved issue that can change the decision;
- `Search failure`: requested evidence that was unavailable or inaccessible.

Never let a provider-generated summary become `Evidence` without its original source.

## Review Depth

- `rapid`: lead, devil, arbiter, evidence audit, one next experiment;
- `standard`: full lens set and source-dependence audit;
- `deep`: full lens set, methodology/data-quality review, sensitivity analysis, and independent reproduction of key calculations.

## Adversarial Loop

Read `references/adversarial-loop.md` and apply these lenses in order:

1. **Research lead** reconstructs the hypothesis, decision, and evidence map.
2. **Methodology reviewer** checks definitions, samples, comparisons, modeled metrics, and calculation reproducibility.
3. **Devil** builds the strongest evidence-backed case against the opportunity.
4. **Angel** builds the strongest evidence-backed case for the opportunity without hiding risks.
5. **Arbiter** reconciles disagreements and identifies the claims that actually drive the decision.
6. **Evidence auditor** checks citations, independence, freshness, source lineage, and overclaiming.
7. **Experiment designer** proposes the lowest-cost test that resolves the highest-value uncertainty.
8. **Scribe** produces the final validation brief and decision record.

These are analytical lenses, not separate providers or autonomous personas. Do not multiply calls merely to simulate roles.

## Decision Policy

Choose exactly one outcome:

- `proceed_to_product_brief`: enough evidence for an MVP definition; building still requires explicit invocation;
- `experiment_first`: a bounded market experiment is cheaper than further desk research or MVP construction;
- `revise_search`: key evidence is missing but discoverable;
- `revise_hypothesis`: current framing is contradicted or too broad;
- `pause`: evidence is inadequate and the next useful step is not justified now;
- `reject`: critical falsification criteria were met or economics/risk make the hypothesis untenable.

Follow `references/decision-policy.md`. Do not turn weak or absent evidence into a positive decision.

## Required Output

Use `assets/market-validation-brief.template.md` and include:

- hypothesis and decision frame;
- evidence map with labels and lineage;
- strongest case for and against;
- methodology and data-quality findings;
- contradictions and source dependencies;
- sensitivity to critical assumptions;
- outcome, confidence, and decision rationale;
- cheapest next experiment with pass/fail criteria;
- unresolved questions and search failures;
- optional handoff target, explicitly not invoked.

Validate a machine-readable decision with:

```powershell
node scripts/validate-market-decision.mjs path\to\decision.json
```

## Quality Gate

Use `references/evidence-audit.md`. A decision is not ready when key claims lack original sources, modeled data is presented as observed, comparisons use incompatible periods, counterevidence was ignored, or the next action has no measurable stop condition.
