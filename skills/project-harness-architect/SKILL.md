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
6. Validate it with `python scripts/validate_harness_plan.py <plan>`.

## Materialization

Preview before writing:

```bash
python scripts/bootstrap_project_harness.py --project-root <root> --plan <harness-plan.json> --dry-run
python scripts/bootstrap_project_harness.py --project-root <root> --plan <harness-plan.json>
```

The initializer creates only missing operational files, copies the canonical Spec/runtime schemas from sibling `project-spec-architect`, records the accepted bootstrap decision, and preserves every existing file. It does not create domain documentation directories. Author only the domain documents listed in the accepted plan and only when no equivalent truth exists.

For new projects it generates `.codex/references/project-map.json` from the accepted plan and installs a standalone maintenance kit under `scripts/harness/`. Read [references/project-map.md](references/project-map.md) for the schema, source review, change detection, migration and optional Karya HTML viewer. Bootstrap never marks the initial map reviewed. The map is navigation, not domain truth or proof that a declared validation ran. `--dry-run` lists creation without writes, and existing maps/tools are preserved. Projects with only legacy `project-harness.md` remain supported until explicit migration. If the declared runtime policy path differs from the fixed bootstrap destination, resolve the reported mismatch before execution.

When the project's sources define useful areas, record source-backed memberships in the optional version 1.1 `navigation` block. Keep the complete project as its root and areas as peers. Do not infer ownership from a node's type, a reference edge, or directory containment alone. Preserve unassigned or multiple memberships explicitly; do not classify unknown elements as shared resources. New bootstrap maps remain valid version 1.0 without invented areas. Areas color and filter the same dependency map; folder paths provide related tones. Inspect imports and consumed resources before enriching `depends_on` relations, recording source evidence in each rationale. Do not treat reference links, optional handoffs or workflow ordering as runtime dependencies. The viewer defaults to the single atomic map with sphere, separated-band and 2D alternatives. Initial placement brings recorded connections closer within visual constraints; free node dragging changes only session-local display offsets. Dependency direction, cycles and recorded depth remain explicit in details, not imposed as screen rows. Never infer a dependency from manual position or orbit membership. Content-type filters remain independent of placement. Never impose Karya's Factory names on another project.

Merge relevant routing into an existing `AGENTS.md` after inspection; never overwrite it. Use `.codex/` for persistent agent-operational references, workflows, checklists, decisions, goals, templates, and schemas. Use ignored `.harness/runtime/` only for ephemeral Harness execution state and receipts. Use `.agents/skills/` for project-local capabilities. Keep human and stakeholder truth in domain-appropriate `docs/` or an existing equivalent.

## Factory and authority boundaries

This Factory is independent and opt-in. It may consume an idea, existing project, or output from MVP, Research, or Marketing, but it never invokes those factories automatically. Product, backend, frontend, research, commercial, and infrastructure specialists keep their richer contracts and authority.

Suggest `project-spec-architect` when a change needs many steps or interactions across sessions. Do not create a Spec automatically for every change; the user chooses whether to use that route. Use `project-skill-author` for approved recurring project procedures, `codex-runtime-router` for an already resolved READY execution manifest, and `project-harness-auditor` for reconciliation. Do not implement the project with this skill.

When the user explicitly wants an economic implementation route, map the project to `karya-execution-router` without making OpenCode part of the minimum Harness. Preserve the READY Spec and Codex fallback/review runtime, keep provider configuration and the exact execution request outside the project repository, and require a separate action-time confirmation. Use `karya-backend-router` instead when the implementation is governed by the richer Django backend contract.

## Completion

Report created, preserved, mapped, and intentionally omitted artifacts. A bootstrap is complete only when project truth is discoverable, AGENTS routing is accurate, Spec/runtime policy is usable, validation is named, temporary runtime state is excluded from durable truth, and no important decision exists only in the bootstrap conversation.
