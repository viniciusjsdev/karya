# Codex runtime execution protocol

```txt
READY Spec + resolved execution manifest
  -> project-pinned runtime policy, schema, and clean-thread validation
  -> duplicate-thread and resume-state validation
  -> Codex.thread_start(...) or Codex.thread_resume(id, ...)
  -> Thread.run(clean handoff, output_schema=schema)
  -> inject actual thread ID and usage
  -> canonical validation execution and evidence reconciliation
  -> durable completion/review attempts and lifecycle under the Spec
  -> recoverable operational mapping under .harness/runtime/
```

The handoff contains only the Spec, manifest, AGENTS routing, declared references and skills, and the instruction to discover directly relevant repository files. It never contains the full design conversation.

For `needs_design`, completion includes the question, reason, impact, affected areas, and alternatives. The runtime state retains the implementation thread ID. A design thread updates project truth and the Spec, then the implementation manifest uses `resume` with that ID.

Thread purposes map independently: implementation/worker IDs use `implementation_thread_id`; review uses `review_thread_id`. Version 2 derives the phase from status and never rewrites the implementation runtime to review. `changes_requested` resumes the same implementation ID, then the same review ID.

Implementation/worker runs use `project-spec-completion.schema.json`. Review runs use `project-spec-review.schema.json` and return `approved`, `changes_requested`, `blocked`, or `failed`; the router records the review thread independently and never converts a non-approved result into success.

For version 2, the router advances matching Markdown/manifest status only after validated evidence and appends the transition to `evidence/lifecycle.json`. Completion and review attempts are retained; canonical `completion.json` and `review.json` point to the latest accepted attempt.

`.harness/runtime/` may hold recoverable Spec-to-thread mappings and operational status. A done audit uses durable evidence and does not depend on it. It is gitignored and must not hold secrets, transcripts, conversation history, domain truth, ADRs, Specs, or persistent documentation.

The default policy path is `.codex/references/runtime-policy.json`. A missing project policy blocks execution; the router does not silently substitute a newer Factory policy. As soon as the SDK exposes a thread ID, the router preserves the mapping even if structured output or evidence validation fails, preventing an accidental duplicate `new` thread on retry.
