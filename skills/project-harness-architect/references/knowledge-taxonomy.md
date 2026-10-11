# Project knowledge taxonomy

| Material | Durable home | Test |
| --- | --- | --- |
| persistent knowledge or truth | domain-appropriate docs or reference | future work must rely on it |
| durable architectural decision | ADR or `.codex/decisions/` | alternatives and consequence matter |
| many-step change when the user chooses a Spec | Spec | one execution/review lifecycle |
| specialized recurring procedure | `.agents/skills/<name>/` | coherent capability with repeated triggers |
| deterministic repeated operation | script | inputs and outputs can be checked mechanically |
| one-time task | task/Spec only when needed | recurrence does not justify a skill |
| execution policy | versioned runtime policy | supplies defaults and escalation rules |
| resolved runtime for one change | `SPEC.execution.json` | historical execution must not drift with policy |
| temporary run/thread state | `.harness/runtime/` or external state store | not project truth or `.codex` context; ignored by VCS |

Link to authoritative material rather than copying it into AGENTS, skills, Specs, and references. Promote important chat discoveries into the appropriate durable home before ending the design thread.

## Make knowledge discoverable with existing tools

Use a compact source map in an existing project reference when navigation needs one: topic, authoritative path, and relevant heading or identifier. Prefer targeted search and reading, expanding to definitions, exceptions, and referenced tables or figures. Preserve their units, captions, and qualifications. Required audit and contract reads remain mandatory.

For newly bootstrapped Harness projects, the operational map is `.codex/references/project-map.json`. Maintain explicit documentary/contractual relations with the change workflow in [project-map.md](project-map.md). Existing Markdown maps remain supported until migration. Keep the accepted bootstrap plan historical and any rendered HTML derived; the JSON does not duplicate the full documents.

Tie material conclusions to source locations and distinguish source statements from interpretation. Document inaccessible or partially inspected sources that limit the audit. Summaries and search results do not replace Docs, ADRs, or approved contracts.

Do not create a document ingestion pipeline, vector store, or knowledge graph merely because the project has many files. Propose such infrastructure only for an observed recurring retrieval bottleneck, with an approved scope and a comparison against ordinary search and reading. If approved later, keep any index reconstructible from authorized sources, separate from durable truth and Harness run state.
