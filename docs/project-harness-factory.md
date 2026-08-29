# Project Harness Factory

The Project Harness Factory is an independent, opt-in workflow for making any project operable and scalable with AI through durable knowledge, Specs, local skills, deterministic runtime materialization, Codex threads, validation, completion evidence, and audit.

It may be invoked directly or selected through an approved `$karya` recommendation. Karya remains the conversational coordinator, while Project Harness retains authority over its own planning, Spec, runtime, thread, evidence, and audit contracts.

## Audit result and reuse matrix

| Mechanism | Disposition | Project Harness treatment |
| --- | --- | --- |
| frontend `project-context-standard` and preserving starter | generalize | reuse the root `AGENTS.md` + `.codex/` + `.agents/skills/` concept; keep frontend files specific |
| backend `project-context-standard` and preserving initializer | generalize | reuse one root context, preservation, decisions, workflows, checklists, and local skills; keep backend kit/contracts specific |
| frontend `domain-skill-spec.md` | generalize | expand into the generic project skill selection/specification policy |
| backend `backend-domain-skill-author` and domain-skill policy | generalize and keep specific | generic selection becomes `project-skill-author`; the backend author remains the richer backend capability |
| backend Markdown implementation contract + JSON manifest | generalize and keep specific | use the human/machine split for generic Specs; never downgrade the backend manifest |
| backend completion schema and ID-level audit | generalize and keep specific | generic acceptance/validation evidence follows the pattern; backend keeps invariant/endpoint traceability |
| `karya-backend-router` | keep specific | continues OpenCode/Codex Django routing and security boundaries |
| Django OpenCode safety pattern | generalize | reuse approval, deny-by-default permissions, snapshots, one final signal, and independent audit without reusing Django contracts |
| `karya-research-router` | keep specific | continues provider/evidence routing; it does not execute Project Specs |
| `karya-commercial-router` | keep specific | continues approved external commercial operations |
| generic Spec lifecycle/readiness | create new | `project-spec-architect`, schemas, validator, templates |
| explicit GPT-5.6 runtime + reasoning materialization | create new | centralized runtime policy and per-Spec resolved execution manifest |
| Codex SDK start/resume router and thread mapping | create new | Python 3.12+ `codex-runtime-router`, official Python SDK, durable lifecycle plus recoverable ignored state, and mock-tested adapter |
| generic optional economic execution | create new | `karya-execution-router` consumes a READY non-Django Spec plus an external approved request and returns OpenCode evidence or Codex fallback |
| cross-project harness audit | create new | `project-harness-auditor` with deterministic and semantic layers |

## Minimal architecture

Six skills are retained because they have different authority and side effects:

1. `project-harness-architect` audits and bootstraps project context; it does not design a change or implement it.
2. `project-spec-architect` makes bounded change and runtime decisions; it does not execute.
3. `project-skill-author` authors reusable local procedure; it does not invent domain truth.
4. `codex-runtime-router` validates and executes a resolved manifest; it does not select a runtime.
5. `karya-execution-router` optionally executes a READY implementation through OpenCode after exact external confirmation; it does not plan, approve, or replace Codex.
6. `project-harness-auditor` independently reconciles contracts, reality, and evidence; it does not repair.

Combining these would let an executor redefine its contract or let an author self-approve its output. Shared runtime defaults and schemas remain centralized under `project-spec-architect`; bootstrap and routing consume those canonical resources.

## Workflow

```txt
Idea or existing project
  -> project-harness-architect audit and accepted harness plan
  -> minimal AGENTS/.codex/context plus domain truth mappings
  -> project-skill-author only for recurring specialized procedures
  -> project-spec-architect for one bounded change
  -> clean-thread READY validation and resolved runtime
  -> codex-runtime-router thread_start/thread_resume
       or explicitly approved karya-execution-router/OpenCode execution
  -> durable completion evidence or needs_design
  -> derived independent review -> changes_requested/correction/re-review when needed
  -> project-harness-auditor
```

The Factory never invokes MVP, Research, or Marketing automatically. Those factories may provide or consume artifacts only after explicit user request or approval, with `automatic_handoff: false`.

## Runtime and evidence guarantees

- Bootstrap copies a versioned runtime policy into `.codex/references/runtime-policy.json`; the router blocks a missing or version-incompatible policy instead of silently using a newer Factory default.
- Persistent operational knowledge remains under `.codex/`. Durable lifecycle, completion, review, and attempt evidence live beside the Spec. Gitignored `.harness/runtime/` contains only recoverable operational mapping; secrets, transcripts, conversation history, domain truth, ADRs, Specs, and persistent documentation are prohibited there.
- The new Harness core runs on Python 3.12+ and calls the official Python Codex SDK directly. Existing Node-based mechanisms from MVP, Research, and Marketing remain unchanged.
- Structured Outputs schemas are checked locally before SDK import; doctor and dry-run reject unsupported composition, dynamic maps, missing types, and incomplete `required` arrays without a paid call.
- Each purpose starts once. Once the SDK exposes an ID, invalid schema/evidence resumes that ID; `changes_requested` resumes the same implementation thread and then the same review thread.
- Implementation emits AC/VAL arrays with every declared ID exactly once. The router injects and executes canonical required commands. Changed files distinguish added, modified, and deleted paths and reconcile with the pre-run Git snapshot.
- Structural migrations require a baseline of tests, CLI, JSON fields, persistence methods, schemas/idempotency keys, protected paths, and decisions effective before the Spec. Review records a category-by-category assessment.
- Optional economic execution keeps provider configuration, credentials, and its exact action-time request outside the project repository; it snapshots the project, restricts writes, returns one process-exit signal, reruns exact validations, and requires independent Codex review.
- A `DONE` Spec with required independent review must have a durable done lifecycle and approved review receipt whose runtime, baseline inputs, and purpose-specific thread IDs reconcile without `.harness/runtime/`.

The executable [SPEC-023 sensor export example](../examples/project-harness/spec-023-sensor-export/) demonstrates bootstrap, local skill creation, clean-thread handoff, `needs_design`, ADR resolution, resume, real implementation tests, completion evidence, independent review, and final audit without subagents.

## Compatibility

Generic Specs may reference a specialized backend planning contract. A Django change can therefore flow from a generic project change into `django-backend-service-architect`, its approved manifest, `karya-backend-router`, `django-backend-code-executor`, and its specialized audit. The generic harness records the cross-artifact handoff without replacing the backend contract.

Frontend/backend context initializers remain valid when Project Harness is absent. When a Harness already exists, they enrich missing domain-specific context and preserve the generic root context.
