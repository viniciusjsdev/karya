# Source lineage

## Three layers

Keep these distinct:

1. **Original source**: the page, paper, store listing, platform profile, dataset, interview, or experiment that supports the observation.
2. **Retrieval mechanism**: Codex web search, Perplexity, OpenAlex, AppStoreTracker, Manus, an API, or a browser.
3. **Analyst transformation**: filtering, normalization, calculation, classification, or inference performed after retrieval.

A retrieval mechanism is not automatically an independent source.

## Evidence item fields

Every material item should record:

- unique evidence ID;
- claim or observation;
- evidence class;
- original source name, URL/stable ID, and publisher/owner;
- publication/event date and retrieval time;
- retrieval mechanism and task/query ID where available;
- geography, platform, and measurement period;
- status: observed, modeled estimate, derived, or unknown;
- transformation/formula;
- dependence group;
- confidence and limitations.

## Dependence groups

Assign the same dependence group when multiple outputs originate from the same underlying data. Examples:

- AppStoreTracker metadata derived from Apple and the Apple listing;
- several articles repeating one press release;
- Perplexity and Codex both retrieving the same webpage;
- OpenAlex metadata and a citation export for the same paper.

Do not count repeated reporting as source diversity.
