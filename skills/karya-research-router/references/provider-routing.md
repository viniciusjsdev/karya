# Provider routing policy

## Default order

1. Codex for focused research, primary-source inspection, normalization, and synthesis.
2. Free or already-owned source paths appropriate to the evidence class.
3. AppStoreTracker for iOS market estimates and cohorts.
4. OpenAlex for scholarly discovery, followed by inspection of original works.
5. Perplexity for broad open-web discovery when explicitly permitted.
6. Manus for authenticated or platform-native discovery that materially benefits from its integrations.

This is a cost and capability order, not a source-quality ranking.

## Route by need

### Codex

Use for bounded web questions, official documentation, primary-source reading, cross-source comparison, calculations, and final synthesis. Narrow an overly broad request before retrieval.

### AppStoreTracker plus Apple

Use for a specific iOS app, developer portfolio, family, category, or comparable cohort. AppStoreTracker supplies directional quantitative intelligence; Apple confirms listing identity and first-party metadata.

### OpenAlex

Use to discover scholarly works, authors, venues, concepts, citations, and related literature. Treat its metadata and reconstructed abstracts as discovery aids. Cite and inspect the original paper for substantive claims.

### Perplexity

Use for broad, multi-source open-web discovery when its breadth saves meaningful time and the user or contract allows paid usage. Codex must inspect the original cited pages before relying on important claims.

### Manus

Use for signed-in or platform-native search, such as identifying relevant creators within Instagram/TikTok/LinkedIn or inspecting live profile/content signals. Use `$manus-platform-researcher` and keep the task read-only.

## Fallbacks

- Missing Perplexity: use narrower Codex batches.
- Missing OpenAlex key: allow limited discovery if the service permits it and report the limitation; targeted primary-source web research remains available.
- Missing AppStoreTracker access: return Apple metadata and a quantitative coverage gap; do not manufacture revenue/download estimates.
- Missing Manus/authentication: return `manual_required` for platform-native evidence.

## Never route

- passwords, recovery codes, tokens, or session cookies through a prompt or artifact;
- account creation or identity verification as research;
- public posting, messaging, following, liking, or paid spend through the research router;
- an unbounded task to multiple paid providers merely to create artificial consensus.
