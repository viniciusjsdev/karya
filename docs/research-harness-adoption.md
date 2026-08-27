# Research Harness Adoption Record

## Source reviewed

The separate `research-harness` repository was reviewed as a methodological reference for Karya's Research Factory. Its strongest contribution is an adversarial validation loop that distinguishes sourced evidence from interpretation and deliberately constructs both rejection and opportunity cases.

## Adopted

- evidence labels: Evidence, Inference, Assumption, Open question, and Search failure;
- explicit Research Lead framing;
- Literature/Evidence Scout as a retrieval concern;
- Methodology and data-quality review;
- Devil and Angel cases held to the same evidence standard;
- Arbiter reconciliation instead of majority voting;
- Evidence Auditor for citation, dependence, freshness, and overclaiming;
- Experiment Designer for the cheapest discriminating test;
- Scribe for one durable, auditable decision record.

These are analytical lenses inside `market-validation-harness`, not a requirement to create separate agents or duplicate provider calls.

## Not adopted

- coupling to the source repository's runtime or folder layout;
- a monolithic research skill that owns question framing, retrieval, and decision;
- source-specific assumptions that prevent independent skill installation;
- additional paid calls merely to simulate debate;
- automatic handoff into product construction.

## Karya mapping

| Harness concern | Karya owner |
|---|---|
| Decision and hypotheses | `market-research-architect` |
| Retrieval routing | `karya-research-router` |
| App economics/cohorts | `app-market-intelligence-analyst` |
| Native platform discovery | `manus-platform-researcher` |
| Scholarly discovery | OpenAlex route |
| Adversarial review and experiment | `market-validation-harness` |

## Reason

Separating architecture, retrieval, specialized analysis, and validation keeps the Research Factory robust without making it a dependency of the MVP Factory. It also lets Codex reuse the reasoning method while choosing AppStoreTracker, OpenAlex, Perplexity, or Manus only when their evidence class warrants it.
