# Research Factory Workflow

## Goal

Produce an auditable market decision from a bounded question and traceable evidence. The workflow is optional and independent from product construction and marketing.

## Sequence

1. `market-research-architect` creates the decision frame, hypotheses, falsifiers, evidence tasks, depth, budget, and completion criteria.
2. `karya-research-router` splits tasks by evidence class and selects the cheapest capable mechanism.
3. Specialized work runs only where needed:
   - Codex for focused web research, original-source reading, normalization, and synthesis;
   - `app-market-intelligence-analyst` for AppStoreTracker/Apple iOS analysis;
   - OpenAlex for scholarly discovery;
   - optional Perplexity for broad open-web discovery;
   - `manus-platform-researcher` for read-only native platform search.
4. Results are normalized into an evidence bundle with original-source lineage, retrieval mechanism, estimates, transformations, dependence groups, and failures.
5. `market-validation-harness` applies the methodology/devil/angel/arbiter/auditor/experiment lenses and returns one explicit outcome.

The adaptation from the separate `research-harness` repository is recorded in `research-harness-adoption.md`; the method was reused without coupling this repository to that runtime.

## App-market path

For a concrete app idea, start from a seed app or explicit cohort definition. Analyze:

- the app itself;
- its developer and related app family;
- a comparable cohort/category;
- matched periods, storefronts, currencies, and metric definitions;
- distribution and concentration, not only winners;
- directional downloads/revenue, rankings, ratings, reviews, and momentum;
- conservative/base/upside scenarios with visible assumptions.

AppStoreTracker estimates are not audited actuals. Apple metadata confirms identity but may be dependent on the same underlying data.

## Decisions

The validation outcome is one of `proceed_to_product_brief`, `experiment_first`, `revise_search`, `revise_hypothesis`, `pause`, or `reject`. Even `proceed_to_product_brief` does not start the MVP Factory automatically.

## Configuration

Optional environment variables:

- `OPENALEX_API_KEY` for reliable scholarly discovery;
- `PERPLEXITY_API_KEY` for approved broad-web tasks;
- `MANUS_API_KEY` for approved Manus integration.

AppStoreTracker access and signed-in platform sessions are confirmed outside repository files. Never store credentials or session material in contracts.
