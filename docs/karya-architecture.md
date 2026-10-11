# Karya Architecture

## Purpose

Karya is the umbrella system for four independent, explicitly invoked Factories:

1. **MVP Factory** turns product intent into a hosted, testable MVP.
2. **Research Factory** investigates and challenges a market hypothesis.
3. **Marketing Factory** prepares and operates a commercial launch, then evaluates results.
4. **Project Harness Factory** structures durable project knowledge, executable Specs, local Skills, isolated Threads, runtime policy, evidence, and audit.

Every Factory is optional. None is a prerequisite, hidden stage, or blocking gate for another.

```txt
Karya
├── optional $karya coordination layer
│     └── classify -> recommend -> explain -> approve -> coordinate
├── MVP Factory
├── Research Factory
├── Marketing Factory
└── Project Harness Factory
```

Artifacts may move between Factories only through an explicit, approved handoff. A compatible output never means automatic invocation.

The living navigation map records six source-backed areas: optional Karya coordination, the four independent Factories, and shared resources. Karya as a complete project is the root context; these areas are peers, not execution stages or concentric levels of authority. Shared resources include the public site and brand, repository-wide documentation/catalogs, installation, examples and the local operating kit used by Karya itself. The distributed Harness capabilities and their tests belong to Project Harness; applying that kit to this repository is local shared support. Area membership does not propagate automatically through directory containment. The viewer uses areas as color families, actual folder paths as related tones, and filters that preserve positions. The initial atomic/spherical composition brings connected records closer within content bands, and every node can be repositioned freely in the page session. Recorded `depends_on` direction, depth and cycles are shown in details; screen height and orbit membership do not impose a dependency hierarchy. Nodes without dependency evidence remain explicitly identified within the same map. Source-backed imports and resource reads enrich the map without turning optional Factory workflows into runtime dependencies. Content types remain a separate filter; neither area membership nor type determines an authority hierarchy.

## Karya coordination layer

`$karya` is the optional conversational front door for users who do not already know which Factory or skill fits their immediate objective. It reads a compact routing model and skill map, inspects relevant project context, recommends the smallest suitable route, explains why, and waits for approval.

After approval, Karya remains the user-facing coordinator while specialist skills are applied internally. It does not create another architectural stage, weaken specialist contracts, or make cross-factory continuation automatic. Direct skill invocation remains valid for users who already know the route.

See [Karya routing and coordination](karya-routing.md).

## Brand and architecture terminology

| Term | Meaning |
| --- | --- |
| Karya | Framework, system, and umbrella project |
| Karya coordination | Optional conversational classification, recommendation, approval, and specialist coordination layer |
| Factory | Independent workflow family inside Karya |
| Skill | Specialized reusable capability |
| Spec | Bounded executable unit of change |
| Thread | Temporary design, implementation, worker, or review context |
| Harness | AI operating structure of a target project |
| Docs and ADRs | Durable project truth and decisions |
| Runtime state | Ephemeral operational state, isolated from persistent context |

Threads communicate through durable artifacts, not chat history. Persistent Codex-facing context belongs under `.codex/`; ephemeral Harness state belongs under gitignored `.harness/runtime/`.

## MVP Factory

```txt
Idea or PRD
  -> executable product contract
  -> @sites + Karya React implementation
  -> Django planning and contract approval
  -> optional OpenCode/Codex backend routing
  -> executor-neutral Django implementation
  -> Django contract audit
  -> infrastructure and publication
  -> MVP validation
```

Its existing stages and rules remain unchanged.

## Research Factory

```txt
Idea, PRD, existing product, app, or market question
  -> market-research-architect
  -> karya-research-router
       -> Codex / focused web and synthesis
       -> app-market-intelligence-analyst / AppStoreTracker + Apple
       -> OpenAlex / scholarly discovery
       -> Perplexity / optional broad web discovery
       -> manus-platform-researcher / read-only native platform research
  -> market-validation-harness
  -> proceed | experiment | revise | pause | reject
```

The Research Factory produces evidence and a validation decision. It does not change a PRD or start construction/marketing automatically.

## Marketing Factory

```txt
Existing product, app, service, launch brief, or accepted market decision
  -> commercial-launch-architect
  -> marketing-creative-builder
  -> karya-commercial-router
       -> Codex / thinking and artifacts
       -> Human / account, identity, security, approval, spend
       -> manus-commercial-operator / exact native execution
  -> commercial-validation-analyst
  -> scale | iterate | pivot | pause | stop
```

Account setup information is produced by Codex. Account creation, credentials, verification, and 2FA remain human-controlled. Manus is reserved for bounded research or execution where platform integration adds value.

## Project Harness Factory

```txt
Design Thread
  -> durable SPEC and resolved runtime manifest
  -> Codex Runtime Router
       or optional Economic Execution Router -> OpenCode implementation
  -> isolated implementation execution
  -> tests and structured evidence
  -> independent Codex review
  -> harness audit
```

When execution encounters a consequential unresolved decision, it returns `needs_design`. The design context updates durable Docs, ADRs, or the Spec, and the router uses `thread_resume` rather than creating a duplicate implementation thread.

## Shared architecture rules

- Each folder under `skills/` is independently installable.
- Root `specs/` define optional cross-skill handoffs; skill folders contain executable instructions, references, scripts, and local schemas/templates.
- Providers are mechanisms, not evidence sources. Preserve original-source lineage.
- External writes require an exact operation and explicit confirmation.
- OpenCode is an optional economic implementation executor, never a Karya prerequisite or auditor. Provider configuration and credentials remain outside project repositories; Codex owns architecture, fallback, validation, and final audit.
- No Factory silently invokes another Factory. Karya may coordinate only an explicitly approved route and keeps cross-factory handoffs optional.
- Missing research does not block an MVP; missing marketing does not block publication of a technical preview.
- Secrets and authenticated session material stay outside the repository and generated projects.

## Document context in existing workflows

Karya uses available search, reading, and format-specific tools to inspect relevant source material progressively. Specialists preserve the context of tables and figures, attach source locations to material conclusions, and distinguish source statements from interpretation and access gaps. Required contract and audit reads still apply. Product source notes, research evidence bundles, Specs, and creative claim/proof registers carry this traceability without introducing a mandatory new artifact.

Model and reasoning recommendations address interpretation difficulty through the existing runtime policy. Indexing or RAG is an optional proposal for a demonstrated recurring retrieval bottleneck or an explicitly requested product feature, evaluated against ordinary search and reading. It is not a prerequisite for using Karya or any Factory.

New Project Harness bootstraps materialize `.codex/references/project-map.json` as the operational navigation graph, with explicit source/contract relations and a standalone maintenance tool. Project/map changes require source reconciliation and an explicit review record; new Specs include the freshness check and Harness audit verifies it. An optional offline HTML visualizes the JSON on request. Original docs and accepted bootstrap history remain authoritative in their own roles; legacy Markdown maps are preserved until explicit migration. See the [navigation map contract](../specs/project-navigation-map-contract.md).

## Repository shape

Karya also consumes its own navigation mechanism: `.codex/references/project-map.json` maps the whole repository, with local maintenance tools under `scripts/harness/`. Its scope includes all four Factories and the coordinator, installable packages, source contracts, examples/starters, distribution, brand and website. The website remains a separate product surface; generating a local map view does not publish it. Adoption by this repository does not make Harness a prerequisite for another Factory.

```txt
skills/
  # Optional Karya coordination
  karya/

  # MVP Factory
  product-brief-architect/
  karya-frontend-builder/
  django-backend-service-architect/
  karya-backend-router/
  django-backend-code-executor/
  karya-infra-orchestrator/

  # Research Factory
  market-research-architect/
  karya-research-router/
  app-market-intelligence-analyst/
  manus-platform-researcher/
  market-validation-harness/

  # Marketing Factory
  commercial-launch-architect/
  marketing-creative-builder/
  karya-commercial-router/
  manus-commercial-operator/
  commercial-validation-analyst/

  # Project Harness Factory
  project-harness-architect/
  project-spec-architect/
  project-skill-author/
  codex-runtime-router/
  karya-execution-router/
  project-harness-auditor/
```

Generated product projects continue to keep product truth in `docs/product/`, durable architecture in `docs/architecture/`, concise backend-operational context in project-root `.codex/`, and focused backend workflows in `.agents/skills/`. Research/marketing artifacts enter a generated project only when the user deliberately chooses that project as their durable location.
