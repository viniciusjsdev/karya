# SPEC-023 sensor export: complete thread handoff example

This example shows one software project, but every Harness artifact is domain-neutral. It demonstrates where threads end, which durable artifacts cross the boundary, and why no subagent is needed.

## Timeline

1. **Harness bootstrap — Design Thread `design-sol-001`, Sol/high.** `project-harness-architect` maps `docs/project/overview.md` as truth, creates minimal root context, and identifies sample normalization as a recurring procedure.
2. **Local capability — same Design Thread.** `project-skill-author` creates `.agents/skills/normalize-sensor-samples/`. The skill links to project truth; it does not copy the methodology.
3. **Feature design — same Design Thread.** `project-spec-architect` creates SPEC-023 and the first READY snapshot in `history/01-ready.execution-snapshot.json`. The Design Thread ends after durable artifacts are validated.
4. **Implementation starts — new thread `impl-terra-023`, Terra/medium.** `codex-runtime-router` receives only AGENTS, Spec, manifest, declared references/skill, and repository. No design-chat history or subagent crosses the boundary.
5. **Missing decision — Implementation Thread ends its turn with `needs_design`.** `history/02-needs-design.completion.json` asks how equal timestamps are ordered and preserves `impl-terra-023`.
6. **Design resumes — `design-sol-001`, Sol/high.** The decision becomes `docs/decisions/ADR-004-equal-timestamp-order.md`; SPEC-023 is updated and revalidated.
7. **Implementation resumes — same `impl-terra-023`, Terra/medium.** `history/03-resume-ready.execution-snapshot.json` uses thread mode `resume`, not a new implementation thread.
8. **Implementation completes.** `evidence/completion.json` maps AC/VAL IDs to files and command results.
9. **Critical review — new `review-sol-023`, Sol/high.** The matching `history/04-review.SPEC-snapshot.md` and `history/04-review.execution-snapshot.json` materialize the clean review handoff. The reviewer receives Spec, manifest, diff/artifacts, tests, and completion evidence; `evidence/review.json` records the schema-valid independent result.
10. **DONE.** `evidence/thread-state.json` maps SPEC-023 to both thread IDs. `project-harness-auditor` reconciles the durable chain.

```txt
Design Thread Sol/high
  -> SPEC + resolved manifest
  -> new Implementation Thread Terra/medium
  -> needs_design
  -> ADR + Spec update in Design Thread
  -> resume same Implementation Thread
  -> completion evidence
  -> independent Review Thread Sol/high
  -> DONE
```

No worker thread or subagent appears because the mechanical work belongs to the bounded implementation and has no independent ownership benefit.

Run `node tests/sensor-export.test.mjs` from `project/` to reproduce the two passing acceptance tests cited by the completion evidence. The Harness auditor also verifies that every declared changed file and local artifact exists before approving the example.
