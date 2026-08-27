# Factory Workflow Map

## Selection rule

Route by the current objective:

| User objective | Factory | Starts with |
|---|---|---|
| Define/build/host a product | MVP | `product-brief-architect` |
| Investigate/validate a market | Research | `market-research-architect` |
| Prepare/operate/evaluate a launch | Marketing | `commercial-launch-architect` |
| Structure how a project works and scales with AI | Project Harness | `project-harness-architect` |

If the user asks for more than one, create separate contracts and state the handoff order. Do not merge their responsibilities into one skill.

## Independence guarantees

- The MVP Factory can start from an idea or PRD without research or marketing.
- The Research Factory can analyze an idea, competitor, app, or existing product without building it.
- The Marketing Factory can launch a product built anywhere and does not require research.
- The Project Harness Factory can start from an idea, empty project, existing project, or artifact produced anywhere; no other Factory requires it.
- A failure or unavailable provider in one factory does not disable the others.
- Cross-factory artifacts are copied/referenced deliberately; no workflow mutates another factory's source of truth silently.

## Provider responsibilities

| Actor/source | Responsibility |
|---|---|
| Codex | Orchestration, focused research, original-source inspection, strategy, synthesis, creative preparation, contracts, validation |
| AppStoreTracker | Directional iOS app/developer/family/cohort market estimates and history |
| Apple | First-party app identity and listing metadata |
| OpenAlex | Scholarly discovery; original works remain the evidence |
| Perplexity | Optional broad open-web discovery |
| Manus research | Read-only native/authenticated platform discovery |
| Manus commercial | Exact approved native execution and measurement |
| Human owner | Accounts, credentials, verification, 2FA, connector authorization, confirmation, paid activation |

Provider availability and pricing may change. The contracts route by capability and preserve fallbacks instead of making one paid provider a hard dependency.
