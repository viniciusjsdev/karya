# Contributing to Karya

Thanks for your interest in contributing. Karya welcomes new skills, improvements to existing ones, bug fixes, documentation, examples, tests, and cross-platform compatibility work.

## What this project is

This repository contains the optional Karya conversational coordinator plus independent Codex skill packages organized into four opt-in Factories: MVP, Research, Marketing, and Project Harness.

Each skill is a small, self-contained package centered on a `SKILL.md`, optionally backed by references, deterministic scripts, schemas, and assets. You are primarily defining an agent capability, not building an application feature. A skill may still include validators, routers, schemas, and utilities when code is the more reliable mechanism.

A good skill:

- has one clear responsibility and explicit trigger boundaries;
- says what to produce, what context is required, and what must not be guessed silently;
- preserves durable source-of-truth ownership;
- produces artifacts another stage or skill can consume;
- validates its output proportionally to risk;
- does not silently invoke another Factory.

The `karya` skill is the narrow coordination exception: it may recommend and apply only the specialist capabilities explicitly approved by the user, while keeping every cross-factory handoff optional and preserving each specialist's contract.

Read [AGENTS.md](AGENTS.md) before changing repository structure or Factory behavior. The complete catalog is in [specs/skill-catalog.md](specs/skill-catalog.md).

This repository uses the living [Karya navigation map](.codex/references/project-map.json) across all four Factories, coordination, packages, contracts, site and brand. Before changes, run `python scripts/harness/project_map.py check --project-root .` and read the relevant original sources. Before completion, reconcile documentation and map impact, record `review --note` with the reason for updates or unchanged navigation, and run `check` again. Generate the optional offline view with `python scripts/harness/project_map.py render --project-root .`. See [the maintenance guide](skills/project-harness-architect/references/project-map.md).

## Ways to contribute

### New skill

Good candidates cover a durable stage, workflow, framework, or domain that is not already represented. Before creating one, confirm that the capability is not better expressed as documentation, a deterministic script, a bounded Spec, or an improvement to an existing skill.

### Existing skill improvement

- correct outdated or inaccurate instructions;
- improve trigger and non-trigger clarity;
- add missing edge cases or safety gates;
- add or fix references, schemas, validators, and tests;
- improve evidence and handoff contracts.

### Cross-platform support

Improvements to installation, validation, path handling, and tests on Windows, Linux, and macOS are welcome. Preserve the owning skill's current runtime unless a migration is explicitly justified.

### Documentation and examples

- end-to-end examples with representative inputs and durable output artifacts;
- tutorials for specific project types;
- architecture and workflow clarification;
- README translations, while keeping English as the primary version.

## Skill structure

Every installable skill lives under `skills/<skill-name>/`:

```txt
skills/my-skill/
├── SKILL.md               # Required skill instructions and trigger metadata
├── agents/
│   └── openai.yaml        # Required Codex picker interface
├── references/            # Stable material loaded when relevant
├── scripts/               # Optional deterministic validators or utilities
└── assets/                # Optional schemas, templates, or supporting files
```

Do not install repository skills under root `.codex/` or `.agents/skills/`. Those paths have different responsibilities described in [AGENTS.md](AGENTS.md).

### `SKILL.md`

Start with YAML frontmatter containing:

```yaml
---
name: my-skill
description: Explain what the skill does, when to use it, and important non-triggers.
---
```

The body should define the context, required inputs, workflow, outputs, invariants, boundaries, references, and validation needed by that capability. Use numbered `BR-###` rules when product or domain behavior must be testable.

### `agents/openai.yaml`

Use the repository's actual picker interface:

```yaml
interface:
  display_name: "My Skill"
  short_description: "One concise description of the capability"
  default_prompt: "Use $my-skill to perform the bounded workflow described by the user."
```

Keep `default_prompt` aligned with the skill name and its real trigger.

## Development workflow

### 1. Fork and branch

```bash
git clone https://github.com/<your-username>/karya.git
cd karya
git checkout -b skill/my-skill-name
```

### 2. Inspect related skills and contracts

Preserve existing Factory boundaries and richer specialist contracts. For a new skill, follow the closest owning Factory without copying unrelated implementation detail.

### 3. Implement and validate

Validate every changed skill with Codex's `quick_validate.py`:

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
python "$CODEX_HOME/skills/.system/skill-creator/scripts/quick_validate.py" ./skills/my-skill
```

Run every deterministic test owned by the changed skill. If behavior crosses a Factory boundary, run the relevant compatibility tests as well.

### 4. Exercise a representative use case

Use realistic input and confirm the produced artifacts, validation evidence, and safety behavior. Do not include credentials, tokens, cookies, private customer data, or authenticated browser state in fixtures or PR evidence.

### 5. Open a pull request

Include:

- what changed and why;
- the skill's trigger and non-trigger behavior;
- produced or changed artifacts;
- representative input and output summary;
- exact validation commands and results;
- compatibility or migration notes;
- any intentionally unassessed behavior.

## Runtime and code conventions

- Skill instructions use clear, imperative English unless a skill has an established language-specific audience.
- Skill folder names use lowercase hyphen-case.
- New Project Harness core and deterministic Harness scripts use Python 3.12+ and pytest.
- Backend scripts prefer Python when consistent with the existing skill and its contracts.
- Frontend and mature Node-based Factory tooling preserve their current Node.js stack.
- Do not rewrite stable tooling merely for language uniformity.
- Keep deterministic logic in scripts when code is safer and more reproducible than another model decision.
- Pin direct runtime dependencies and test every added script.
- Never hardcode secrets, credentials, user-specific absolute paths, or authenticated state.

## What we will not merge

- skills that silently decide permissions, compliance, billing, sensitive-data handling, spend, or core scope;
- hidden or automatic cross-factory stages;
- one skill per file, entity, endpoint, class, or temporary task;
- duplicated capabilities without a clear responsibility boundary;
- scripts that place temporary execution state or secrets in persistent project context;
- aggregate success claims without required artifact and validation evidence;
- generated migrations that were handwritten or patched.

## Questions

Open a [GitHub Issue](https://github.com/viniciusjsdev/karya/issues) before investing in a large capability if its Factory placement or responsibility is unclear.
