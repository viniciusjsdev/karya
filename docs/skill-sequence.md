# Skill Sequences

There is no mandatory global sequence. When the correct route is unclear, `$karya` classifies the immediate objective, recommends one primary route, explains why, and waits for approval. It then remains the conversational coordinator while approved specialist skills work internally. Users may still invoke any specialist directly when the route is already known.

```txt
User objective
  -> optional $karya classification
  -> recommendation and approval
  -> direct execution or one Factory sequence
  -> unified result through Karya
```

Cross-factory handoffs remain optional and require explicit approval.

## MVP Factory

```txt
Idea or PRD
  -> product-brief-architect
  -> @sites + karya-frontend-builder
  -> django-backend-service-architect
  -> karya-backend-router
  -> OpenCode Go or Codex + django-backend-code-executor
  -> django-backend-service-architect audit
  -> karya-infra-orchestrator
  -> publication and MVP validation
```

This sequence is self-contained. Do not insert market research or marketing as a prerequisite.

## Research Factory

```txt
Market question
  -> market-research-architect
  -> karya-research-router
  -> specialized retrieval/analysis tasks
  -> market-validation-harness
  -> decision and next experiment
```

- Use `app-market-intelligence-analyst` for iOS app/developer/family/cohort economics through AppStoreTracker plus Apple confirmation.
- Use OpenAlex for scholarly discovery and inspect original papers for substantive claims.
- Use Perplexity only as an optional broad-web discovery mechanism.
- Use `manus-platform-researcher` for bounded read-only research inside native/authenticated platforms.
- Codex owns normalization, synthesis, and the final adversarial review.

## Marketing Factory

```txt
Product or launch input
  -> commercial-launch-architect
  -> marketing-creative-builder
  -> karya-commercial-router
  -> Codex, human, or manus-commercial-operator
  -> commercial-validation-analyst
```

- Codex owns launch strategy, account information, copy, creative preparation, and analysis.
- The human owns account creation, credentials, verification, 2FA, connector authorization, and final external-action approval.
- Manus owns only bounded native actions and measurement after approval.
- Platform-native discovery belongs to the Research Factory, not the action task.

## Optional handoffs

- Accepted research may be supplied to `product-brief-architect` or `commercial-launch-architect`.
- An existing MVP may be supplied to `commercial-launch-architect` without prior research.
- Commercial results may motivate a new research request or product change, but neither starts automatically.
- Every optional handoff preserves the producer artifact and records user approval.
