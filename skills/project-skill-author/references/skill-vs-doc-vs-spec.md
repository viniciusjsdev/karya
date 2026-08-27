# Skill selection and design policy

## Classification

| Question | Artifact |
| --- | --- |
| Is this persistent truth? | docs or authoritative reference |
| Is this a durable consequential decision? | ADR or decision record |
| Is this one bounded change? | Spec |
| Is this deterministic and repeated? | script |
| Is this a specialized recurring procedure requiring judgment? | Skill |
| Is this a one-time task? | perform it; do not create a Skill automatically |

## A good local skill

It owns one coherent capability; has clear trigger and non-trigger requests; names required context; links to authoritative truth; defines a reusable workflow, invariants, boundaries, failure behavior, and validation; and includes scripts only where determinism improves reliability.

The skill must not become a hidden source of product, research, legal, operational, or architectural truth. Link to those sources. Avoid README files, changelogs, installation guides, duplicate summaries, and reference folders with no actual reader.

## Forward checks

Test at least:

- one request that should invoke the skill;
- one adjacent request that should not;
- one missing-context case that must stop or return a bounded gap;
- any deterministic script with representative inputs and observable output.
