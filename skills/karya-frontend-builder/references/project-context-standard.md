# Project Codex Context Standard

## Purpose

Initialize every generated project with concise Codex-operational context at the project root. Keep application source inside `frontend/` and repository-local domain skills inside `.agents/skills/`.

## Required Shape

```txt
project/
  AGENTS.md
  .agents/
    skills/
  .codex/
    references/
      sites-composition.md
    workflows/
    checklists/
    decisions/
    goals/
    templates/
  frontend/
  docs/
```

Codex discovers repository skills under `.agents/skills`, not `.codex`. Use `.codex` for project memory, implementation workflows, validation checklists, goals, architecture decisions, and templates.

## Initialization

Run from the skill location:

```bash
node scripts/init-project-context.mjs <project-root>
```

The script creates missing files and preserves every existing file. Run with `--dry-run` to preview. Never overwrite an existing `AGENTS.md`, project decision, goal, or reference automatically.

When `project-harness-architect` has already initialized the root context, do not create a competing generic starter. Preserve its `AGENTS.md`, Spec/runtime policy, thread lifecycle, decisions, and source-of-truth map; add only missing frontend-specific references, workflows, checklists, and routing. The frontend initializer remains valid for projects that did not request Project Harness.

## Evolution

Start with factory-neutral frontend references. As domain rules become stable and repeatable:

1. Write a domain-skill specification from `.codex/templates/domain-skill-spec.md`.
2. Create `.agents/skills/<skill-name>/SKILL.md` with a narrow trigger description.
3. Put detailed domain knowledge in the skill's `references/`.
4. Add deterministic scripts only when repeated reliability warrants them.
5. Validate and test the skill against realistic project requests.

Do not convert temporary notes, one-off decisions, or generic project documentation into skills.

Use the generic `project-skill-author` selection policy when available. The frontend domain-skill specification remains a compact compatible input, not a second source of truth.

## Source of Truth

- `AGENTS.md`: durable repository rules.
- `.codex/references`: concise agent-operational technical context.
- `.codex/workflows`: recurring project procedures.
- `.codex/checklists`: completion and validation gates.
- `.codex/decisions`: accepted architecture decisions.
- `.agents/skills`: invocable domain capabilities.
- `docs/`: durable documentation for developers and stakeholders.

Link across these surfaces instead of copying long content.
