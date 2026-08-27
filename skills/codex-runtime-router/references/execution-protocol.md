# Codex runtime execution protocol

```txt
READY Spec + resolved execution manifest
  -> project-pinned runtime policy, schema, and clean-thread validation
  -> duplicate-thread and resume-state validation
  -> startThread(options) or resumeThread(id, options)
  -> run(clean handoff, { outputSchema })
  -> inject actual thread ID and usage
  -> implementation completion or independent review evidence validation
  -> temporary state/receipt
```

The handoff contains only the Spec, manifest, AGENTS routing, declared references and skills, and the instruction to discover directly relevant repository files. It never contains the full design conversation.

For `needs_design`, completion includes the question, reason, impact, affected areas, and alternatives. The runtime state retains the implementation thread ID. A design thread updates project truth and the Spec, then the implementation manifest uses `resume` with that ID.

Thread purposes map independently: implementation/worker IDs use `implementation_thread_id`; review uses `review_thread_id`. Review receives Spec, manifest, diff or artifacts, test evidence, and completion evidence.

Implementation/worker runs use `project-spec-completion.schema.json`. Review runs use `project-spec-review.schema.json` and return `approved`, `changes_requested`, `blocked`, or `failed`; the router records the review thread independently and never converts a non-approved result into success.

The router never changes the Spec lifecycle status automatically. The architect/auditor reconciles source-of-truth state after evidence is inspected.

The default policy path is `.codex/references/runtime-policy.json`. A missing project policy blocks execution; the router does not silently substitute a newer Factory policy. As soon as the SDK exposes a thread ID, the router preserves the mapping even if structured output or evidence validation fails, preventing an accidental duplicate `new` thread on retry.
