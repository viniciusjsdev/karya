# Factory Workflow Map

## Selection rule

When the route is unknown, start with `$karya`. It classifies the current objective and artifact state, recommends the smallest route with reasons, and waits for approval before applying specialist skills internally. Direct specialist invocation remains valid when the route is already known.

Route by the current objective:

| User objective | Factory | Starts with |
|---|---|---|
| Complete a bounded, sufficiently defined task | No Factory required | Direct Codex execution |
| Define/build/host a product | MVP | `product-brief-architect` |
| Investigate/validate a market | Research | `market-research-architect` |
| Prepare/operate/evaluate a launch | Marketing | `commercial-launch-architect` |
| Structure how a project works and scales with AI | Project Harness | `project-harness-architect` |

If the user asks for more than one, Karya recommends one primary route and optional later routes with explicit approval boundaries. Create separate contracts and state the handoff order. Do not merge their responsibilities into one skill.

## Independence guarantees

- The MVP Factory can start from an idea or PRD without research or marketing.
- The Research Factory can analyze an idea, competitor, app, or existing product without building it.
- The Marketing Factory can launch a product built anywhere and does not require research.
- The Project Harness Factory can start from an idea, empty project, existing project, or artifact produced anywhere; no other Factory requires it.
- A failure or unavailable provider in one factory does not disable the others.
- Cross-factory artifacts are copied/referenced deliberately; no workflow mutates another factory's source of truth silently.
- Karya coordination never changes `automatic_handoff: false`; a new Factory requires a new recommendation and approval.

## Provider responsibilities

| Actor/source | Responsibility |
|---|---|
| Codex | Architecture, orchestration, fallback implementation, focused research, strategy, contracts, independent validation, and final audit |
| OpenCode | Optional economic implementation executor for an exact approved READY contract; never architecture, external-action authority, or self-approval |
| AppStoreTracker | Directional iOS app/developer/family/cohort market estimates and history |
| Apple | First-party app identity and listing metadata |
| OpenAlex | Scholarly discovery; original works remain the evidence |
| Perplexity | Optional broad open-web discovery |
| Manus research | Read-only native/authenticated platform discovery |
| Manus commercial | Exact approved native execution and measurement |
| Human owner | Accounts, credentials, verification, 2FA, provider setup, exact execution confirmation, billing, credits, and paid activation |

Provider availability and pricing may change. The contracts route by capability and preserve fallbacks instead of making one paid provider a hard dependency.
