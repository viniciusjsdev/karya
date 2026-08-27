---
name: project-skill-author
description: Create or update a project-local skill from a stable, specialized, recurring capability with clear triggers, context, invariants, references, workflow, and validation. Use when durable project truth already defines the capability and future tasks will repeatedly need the procedure. Do not use for one-time tasks, unresolved decisions, generic documentation, individual files, classes, endpoints, entities, or deterministic operations better expressed as scripts.
---

# Project Skill Author

Generalize the project-local skill policy without duplicating project truth or framework-specific skill kits.

## Selection gate

Read [references/skill-vs-doc-vs-spec.md](references/skill-vs-doc-vs-spec.md) and complete `assets/project-skill-spec.template.md` before creating a skill.

- Knowledge belongs in docs or an authoritative reference.
- A durable consequential decision belongs in an ADR/decision.
- A bounded change belongs in a Spec.
- A deterministic repeated operation belongs in a script.
- A specialized recurring procedure may become a skill.

Do not create one skill per endpoint, class, file, entity, CRUD operation, or temporary task. Stop when rules, ownership, permissions, sensitive data, state transitions, inputs, outputs, or failure behavior are unresolved.

## Workflow

1. Read `AGENTS.md`, the accepted harness map, authoritative domain sources, applicable decisions, and existing local skills.
2. Name one coherent capability in lowercase hyphen-case, preferably action-oriented and under 64 characters.
3. Create `.agents/skills/<name>/SKILL.md` and `agents/openai.yaml`. Add references, scripts, or assets only for a concrete execution need.
4. Put discriminating triggers and non-triggers in the frontmatter description. Keep detailed context, workflow, invariants, boundaries, references, and validation in the body.
5. Link to project truth instead of copying it. Stable rules remain owned by their source documents.
6. Add deterministic scripts only when repeated reliability warrants them and test every added script.
7. Validate with the available `quick_validate.py` and `node scripts/validate-project-skill.mjs <skill-dir> --project-root <root>`.
8. Add the capability to the relevant `AGENTS.md` routing inventory without turning AGENTS into a duplicate manual.

## Boundaries

Do not invent or approve domain behavior. Do not store credentials, secrets, cookies, verification material, executor configuration, thread IDs, temporary prompts, completion receipts, or runtime state in a skill. Preserve framework-specific local kits, such as the Django layer skills, when they are richer than this generic policy.

Finish only when the capability is cohesive, repeated, traceable to durable truth, discoverable from its description, narrow enough to avoid unrelated routing, and validated against at least one realistic trigger and one non-trigger.
