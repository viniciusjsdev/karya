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
├── MVP Factory
├── Research Factory
├── Marketing Factory
└── Project Harness Factory
```

Artifacts may move between Factories only through an explicit, approved handoff. A compatible output never means automatic invocation.

## Brand and architecture terminology

| Term | Meaning |
| --- | --- |
| Karya | Framework, system, and umbrella project |
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
  -> Python Codex Runtime Router
  -> isolated Implementation Thread
  -> tests and structured evidence
  -> independent review
  -> harness audit
```

When execution encounters a consequential unresolved decision, it returns `needs_design`. The design context updates durable Docs, ADRs, or the Spec, and the router uses `thread_resume` rather than creating a duplicate implementation thread.

## Shared architecture rules

- Each folder under `skills/` is independently installable.
- Root `specs/` define optional cross-skill handoffs; skill folders contain executable instructions, references, scripts, and local schemas/templates.
- Providers are mechanisms, not evidence sources. Preserve original-source lineage.
- External writes require an exact operation and explicit confirmation.
- No factory silently invokes another factory.
- Missing research does not block an MVP; missing marketing does not block publication of a technical preview.
- Secrets and authenticated session material stay outside the repository and generated projects.

## Repository shape

```txt
skills/
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
  project-harness-auditor/
```

Generated product projects continue to keep product truth in `docs/product/`, durable architecture in `docs/architecture/`, concise backend-operational context in project-root `.codex/`, and focused backend workflows in `.agents/skills/`. Research/marketing artifacts enter a generated project only when the user deliberately chooses that project as their durable location.
