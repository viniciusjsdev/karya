# Harness audit and design

## Audit matrix

For every existing mechanism, record:

| Disposition | Meaning |
| --- | --- |
| `exists` | already satisfies the generic need; preserve and reference it |
| `generalize` | a reusable principle should become project-wide while the producer remains authoritative |
| `keep_specific` | a richer domain mechanism must not be replaced by the generic harness |
| `create_new` | no adequate mechanism exists and a concrete operational artifact is needed |

Inspect source-of-truth ownership, documentation navigation, AGENTS rules, Codex context, decisions, Specs/change requests, recurring procedures, scripts, validation commands, runtime selection, thread state, completion evidence, and audit.

## Minimal architecture test

Create an artifact only when it has an immediate reader or executor. Do not create empty directory trees, placeholder documents, duplicate summaries, or speculative skills. Use path mappings when an equivalent artifact already exists.

Domain shapes are discovered, not imposed. Software may need product/domain/architecture/engineering/decisions; research may need question/literature/methodology/experiments/datasets/findings; commercial work may need market/positioning/experiments/metrics. Existing conventions win when they remain coherent.

## Sources and authority

For every durable source record its path, kind, authority, owner when known, and conflicts. `AGENTS.md` routes behavior but is not a replacement for product, scientific, legal, operational, or architectural truth.

Do not silently decide permissions, compliance, billing, sensitive data, irreversible scope, or ownership. Record the open decision and keep dependent Specs out of `ready`.
