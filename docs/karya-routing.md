# Karya Routing and Coordination

## Purpose

`$karya` is the optional conversational front door to the Karya catalog. A user describes the desired outcome once; Karya inspects the prompt and relevant project state, recommends the smallest suitable route, explains the decision, obtains approval, and then applies specialist skills internally while remaining the user-facing coordinator.

The user does not need to read the repository or know every skill name before starting.

```txt
User objective
  -> Karya classification
  -> route plus runtime recommendation and rationale
  -> explicit approval
  -> approved specialist capabilities
  -> unified progress and result through Karya
```

Karya is not a fifth Factory, a mandatory gateway, or a replacement for direct skill invocation.

## What Karya classifies

Routing starts from the immediate desired outcome rather than the project type:

| Immediate objective | Primary route |
| --- | --- |
| Complete a bounded, sufficiently defined task | Direct Codex execution or one matching specialist |
| Define, build, integrate, host, or validate a product, system, or automation | MVP Factory |
| Investigate demand, competitors, users, evidence, or a market hypothesis | Research Factory |
| Position, launch, publish, operate, or evaluate commercial work | Marketing Factory |
| Make project knowledge and AI execution durable across Threads | Project Harness Factory |
| Achieve several independent outcomes | One primary route plus optional approved handoffs |

An automation is not automatically a Harness project. Creating it is usually MVP work; making an existing automation durable for clean AI Threads is Harness work; fixing one isolated defect may be direct execution.

## Conversation contract

Before execution, Karya reports:

- its understanding of the request;
- the observed project/artifact state;
- the user's cost preference, including whether economizing Codex limits is an explicit objective;
- the primary Factory or direct route;
- the entry skill;
- the evidence-based reason;
- the recommended model and reasoning for the immediate phase;
- the runtime rationale, downshift condition, and required audit;
- whether optional economic OpenCode execution is eligible, its prerequisites, and Codex fallback;
- the specialist skills expected inside the approved scope;
- relevant exclusions or alternatives;
- route-changing open questions;
- the exact scope awaiting approval.

The user can approve, reject, or revise the recommendation. Approval does not authorize unlisted scope, another Factory, external writes, publication, communication, spending, credentials, or other consequential actions.

The runtime recommendation is advisory when the project has no Project Harness manifest: Karya cannot claim to have changed the active conversation's model or reasoning. When Harness is approved, the exact runtime is materialized by `project-spec-architect` in `SPEC.execution.json` and executed by `codex-runtime-router`.

Default recommendations are Sol/high for new-project or missing-structure diagnosis and first-Spec design, Terra/medium for the first resolved implementation, Luna/low for later mechanical corrections, and Sol/high for security, credentials, consequential external action, hard-to-reverse work, or critical review. A Harness bootstrap includes an independent `project-harness-auditor` pass after materialization.

When the user explicitly needs to economize Codex limits or cost, Karya may recommend `karya-execution-router` for a READY normal or mechanical non-Django implementation. The recommendation is advisory: OpenCode is optional, Codex remains the fallback, and installation, authentication, provider/model choice, billing, credit use, writable scope, and execution each retain explicit human control. Django continues through `karya-backend-router`.

## Internal specialist use

After approval, Karya loads and follows the selected specialist's complete instructions. The specialist owns its domain contract, prerequisites, safety gates, validation, and completion definition. Karya owns the continuous user-facing explanation and unified result.

Skills normally operate inside the same Codex conversation; “internal” does not imply separate agents. Project Harness may start or resume isolated Codex Threads only when its independently approved Spec/runtime contracts require that behavior.

When responsibility changes inside the approved route, Karya states the active skill and why. A new Factory requires a new recommendation and approval, with `automatic_handoff: false`.

## Invocation

```txt
$karya <describe what you want to achieve>
```

Example:

```txt
$karya I have a Python automation that works, but every new Codex conversation must rediscover its architecture and business rules.
```

Expected route: Project Harness Factory through `project-harness-architect`, because the immediate outcome concerns durable AI operating structure rather than product construction.

Direct invocation remains available:

```txt
$product-brief-architect <already-known product-definition request>
```

## Machine-readable decisions

Substantial or auditable routing decisions may use `skills/karya/assets/routing-decision.schema.json`. The record captures classification, confidence, primary route, runtime recommendation, downshift condition, audit requirement, approved scope, planned skills, optional routes, approval status, and the invariant `automatic_handoff: false`.

Validate a materialized decision with:

```bash
node skills/karya/scripts/validate-routing-decision.mjs <decision.json>
```

Do not create a routing file merely to answer a conversational question. Persist it only when the project already has or explicitly approves a durable decision location.
