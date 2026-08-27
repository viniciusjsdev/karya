---
name: project-harness-architect
description: Audit and prepare a new or existing project to work durably with AI through sources of truth, domain-appropriate documentation, AGENTS.md, Codex context, local skills, Specs, runtime policy, thread policy, validation, evidence, and audit. Use when explicitly asked to bootstrap or evolve a project's AI operating harness. Do not build the project's product, conduct market research, launch commercially, or replace richer domain-specific contracts.
---

# Project Harness Architect

Create the minimum cognitive and operational infrastructure that lets a project continue after its design conversation disappears.

## Audit before materialization

1. Inspect the project objective, domain, repository or artifact shape, existing instructions, documentation, decisions, workflows, validation, and recurring procedures.
2. Read [references/harness-audit-and-design.md](references/harness-audit-and-design.md) and classify each mechanism as `exists`, `generalize`, `keep_specific`, or `create_new`.
3. Preserve existing sources of truth and richer contracts. Record path mappings instead of moving or flattening them without explicit need.
4. Apply [references/knowledge-taxonomy.md](references/knowledge-taxonomy.md). Do not turn every fact, task, entity, or file into a skill.
5. Write an accepted `harness-plan.json` from `assets/harness-plan.template.json`. Keep `automatic_handoff: false`.
6. Validate it with `node scripts/validate-harness-plan.mjs <plan>`.

## Materialization

Preview before writing:

```bash
node scripts/bootstrap-project-harness.mjs --project-root <root> --plan <harness-plan.json> --dry-run
node scripts/bootstrap-project-harness.mjs --project-root <root> --plan <harness-plan.json>
```

The initializer creates only missing operational files, copies the canonical Spec/runtime schemas from sibling `project-spec-architect`, records the accepted bootstrap decision, and preserves every existing file. It does not create domain documentation directories. Author only the domain documents listed in the accepted plan and only when no equivalent truth exists.

Merge relevant routing into an existing `AGENTS.md` after inspection; never overwrite it. Use `.codex/` for agent-operational references, workflows, checklists, decisions, goals, templates, schemas, and ignored runtime state. Use `.agents/skills/` for project-local capabilities. Keep human and stakeholder truth in domain-appropriate `docs/` or an existing equivalent.

## Factory and authority boundaries

This Factory is independent and opt-in. It may consume an idea, existing project, or output from MVP, Research, or Marketing, but it never invokes those factories automatically. Product, backend, frontend, research, commercial, and infrastructure specialists keep their richer contracts and authority.

Use `project-spec-architect` for bounded change Specs, `project-skill-author` for approved recurring project procedures, `codex-runtime-router` for an already resolved READY execution manifest, and `project-harness-auditor` for reconciliation. Do not implement the project with this skill.

## Completion

Report created, preserved, mapped, and intentionally omitted artifacts. A bootstrap is complete only when project truth is discoverable, AGENTS routing is accurate, Spec/runtime policy is usable, validation is named, temporary runtime state is excluded from durable truth, and no important decision exists only in the bootstrap conversation.
