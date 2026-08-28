<img src="./assets/brand/banners/karya-readme-hero.png" alt="Karya — The structure behind AI-native development." width="100%" />

<p align="center">
  <a href="https://viniciusjsdev.github.io/karya/"><img src="https://img.shields.io/badge/Website-Open-C45A3C?style=flat-square&amp;labelColor=171310" alt="Karya Website"></a>
  <a href="./docs/karya-architecture.md"><img src="https://img.shields.io/badge/Documentation-Read-C45A3C?style=flat-square&amp;labelColor=171310" alt="Karya Documentation"></a>
  <a href="#quick-start"><img src="https://img.shields.io/badge/Get_Started-Quick_Start-C45A3C?style=flat-square&amp;labelColor=171310" alt="Get Started with Karya"></a>
  <a href="./CONTRIBUTING.md"><img src="https://img.shields.io/badge/Contributing-Guide-C45A3C?style=flat-square&amp;labelColor=171310" alt="Karya Contributing Guide"></a>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/License-MIT-C45A3C?style=flat-square&amp;labelColor=171310" alt="Karya MIT License"></a>
</p>

Karya is an open-source development system for Codex built around durable project knowledge, executable Specs, reusable Skills, isolated Threads, deterministic routing, validation, and evidence. Its four independent Factories cover product creation, market research, commercial launch, and durable AI project operations.

<p align="center"><strong>Durable Knowledge · Specs · Skills · Threads · Routing · Evidence</strong></p>

## How Karya works

```txt
Objective
   ↓
Karya classification
   ↓
Route + runtime recommendation
   ↓
Explicit approval
   ↓
Approved specialist capabilities
   ↓
Execution + evidence
```

Karya recommends; you approve; approved capabilities execute. Routing selects and explains a path—it is not authorization or execution, and Karya is not a fifth Factory.

## Quick start

### 1. Clone Karya

```bash
git clone https://github.com/viniciusjsdev/karya.git
cd karya
```

### 2. Install the skills

Windows / PowerShell:

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }
$skillsHome = Join-Path $codexHome "skills"
New-Item -ItemType Directory -Force $skillsHome | Out-Null

Get-ChildItem .\skills -Directory | ForEach-Object {
  Copy-Item -Recurse -Force $_.FullName (Join-Path $skillsHome $_.Name)
}
```

Linux / macOS:

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
mkdir -p "$CODEX_HOME/skills"
cp -R skills/. "$CODEX_HOME/skills/"
```

### 3. Start your first flow

In Codex, describe the outcome once:

```txt
Use $karya to analyze this objective and project, recommend the smallest suitable route with reasons, and wait for my approval before applying specialist skills internally: <your objective>
```

Review the recommendation and approve or revise its exact scope. Karya then coordinates the approved specialist capabilities while remaining the user-facing voice.

If you already know the route, invoke its entry skill directly—for example, `$product-brief-architect`, `$market-research-architect`, `$commercial-launch-architect`, or `$project-harness-architect`. See the [complete skill catalog](./specs/skill-catalog.md).

## Why Karya?

AI-assisted development becomes fragile when decisions and operating knowledge live only in conversations. Karya moves that context into durable, reviewable artifacts so projects can continue without reconstructing their history.

- **Durable knowledge** preserves project truth beyond a single conversation.
- **Explicit Specs and contracts** make bounded work executable and testable.
- **Reusable Skills** encode stable specialist procedures without proliferating agents.
- **Deterministic routing** materializes model, reasoning, thread, and validation policy when a Project Harness Spec requires it.
- **Evidence and independent review** keep completion claims tied to artifacts, commands, and results.

## Four independent Factories

Every Factory is opt-in. None is a hidden prerequisite for another, and cross-factory handoffs require an explicit request or approval.

### MVP Factory

Turns an idea, PRD, or existing product context into explicit product contracts, a testable implementation, backend and infrastructure boundaries, and validation. [Read the MVP method →](./docs/karya-method.md)

### Research Factory

Defines research hypotheses, routes evidence collection by source and provider, and challenges the result before recommending the next experiment or decision. [Read the research workflow →](./docs/research-workflow.md)

### Marketing Factory

Plans positioning and launch, prepares channel-ready creative, routes bounded external operations, and evaluates commercial results. [Read the marketing workflow →](./docs/marketing-workflow.md)

### Project Harness Factory

Makes project knowledge and AI execution durable through documentation, Specs, local Skills, runtime policy, isolated Threads, evidence, audit, and optional economic OpenCode implementation with Codex fallback and final review. [Read the Project Harness architecture →](./docs/project-harness-factory.md)

## Architecture

Karya separates persistent project truth from temporary execution state:

- **Knowledge** — Docs and ADRs preserve domain truth and decisions.
- **Specs** — bounded changes pair human intent with resolved execution policy.
- **Skills** — independently installable specialist capabilities package instructions, references, scripts, schemas, and assets.
- **Threads** — temporary design, implementation, worker, or review contexts communicate through durable artifacts, not chat history.
- **Runtime** — model, reasoning, working directory, thread mode, validation, and review requirements are materialized before Harness execution.
- **Routing** — `$karya` optionally recommends the smallest suitable direct or Factory route and waits for approval.
- **Evidence** — tests, artifacts, completion records, and independent reviews make results auditable.

Persistent Codex-facing context belongs under `.codex/`; gitignored operational state belongs under `.harness/runtime/`. [Read the architecture →](./docs/karya-architecture.md)

## Project Harness

Project Harness is the Factory that most directly expresses Karya's durable operating model:

```txt
Design Thread
  → durable Spec + resolved runtime manifest
  → isolated Implementation Thread
  → tests + structured evidence
  → independent review
  → Harness audit
```

If implementation encounters a consequential unresolved decision, it returns `needs_design`; the durable Spec, ADR, or documentation is updated before the mapped thread resumes. Secrets, transcripts, conversation history, domain truth, ADRs, Specs, and persistent documentation never belong in `.harness/runtime/`.

See the [Project Harness architecture](./docs/project-harness-factory.md), [durable contract](./specs/project-harness-contract.md), and [executable SPEC-023 example](./examples/project-harness/spec-023-sensor-export/).

## Core principles and boundaries

- **Artifacts over chat history.** Important knowledge must survive the conversation that created it.
- **Architect ≠ Executor ≠ Auditor.** Contract definition, implementation, and approval retain separate authority.
- **Smallest capable runtime.** Use the least expensive model and reasoning level that can complete the work reliably.
- **Deterministic operations belong in code.** Scripts validate and route what should not be guessed by another model.
- **Progressive context disclosure.** Threads receive the smallest useful context and load more only when required.
- **Explicit boundaries.** Recommendation is not approval; routing is not execution; approval does not authorize unlisted scope.
- **Independent Factories.** Research, Marketing, MVP, and Project Harness never hand work to one another automatically.
- **Human-controlled external actions.** Credentials, account creation, publication, communication, spending, and other consequential writes remain explicitly controlled.

## Requirements and installation details

Core requirements:

- [OpenAI Codex](https://developers.openai.com/codex/);
- Git.

Live Project Harness routing additionally requires Python 3.12+ and the pinned official Python Codex SDK. Existing MVP, Research, and Marketing mechanisms may use Node.js 24+, npm, or provider-specific tools documented by their owning skill.

Each folder under `skills/` is independently installable. To install only one capability, copy only its folder into `$CODEX_HOME/skills/`.

For live Project Harness routing, create an isolated Python environment and run:

```bash
python -m pip install -r skills/codex-runtime-router/requirements.txt
python skills/codex-runtime-router/scripts/codex_runtime_doctor.py
```

### Validation

Validate every skill definition:

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }
$quickValidate = Join-Path $codexHome "skills\.system\skill-creator\scripts\quick_validate.py"

Get-ChildItem .\skills -Directory | ForEach-Object {
  python $quickValidate $_.FullName
}
```

Run the Project Harness deterministic suite:

```bash
python -m pip install -r skills/codex-runtime-router/requirements-dev.txt
python -m pytest \
  skills/project-harness-architect/scripts/test_harness_bootstrap.py \
  skills/project-spec-architect/scripts/test_spec_validator.py \
  skills/project-skill-author/scripts/test_project_skill_validator.py \
  skills/codex-runtime-router/scripts/test_runtime_router.py \
  skills/karya-execution-router/scripts/test_execution_router.py \
  skills/project-harness-auditor/scripts/test_harness_auditor.py \
  examples/project-harness/spec-023-sensor-export/project/tests/test_sensor_export.py -q
```

Factory-specific validators remain inside their owning skill folders. Contributors should also follow the [implementation and validation workflow](./CONTRIBUTING.md#3-implement-and-validate).

## Documentation

- [Architecture](./docs/karya-architecture.md)
- [Karya method](./docs/karya-method.md)
- [Routing and coordination](./docs/karya-routing.md)
- [Factory workflow map](./docs/factory-workflow-map.md)
- [Project Harness](./docs/project-harness-factory.md)
- [Research workflow](./docs/research-workflow.md)
- [Marketing workflow](./docs/marketing-workflow.md)
- [Product workflow](./docs/product-workflow.md)
- [Complete skill catalog](./specs/skill-catalog.md)

[Explore the interactive Karya architecture and workflow →](https://viniciusjsdev.github.io/karya/)

## Why the name Karya?

Karya is a brand adaptation inspired by the Caryatids: female figures used as structural supports in classical architecture. The Caryatid is not decoration; she is structure—a metaphor for the durable layer that helps humans and AI build, validate, and evolve projects consistently.

Read the [Karya brand principles and official asset policy](./docs/branding.md).

## Contributing

Contributions to skills, deterministic tooling, tests, examples, documentation, and cross-platform support are welcome. Read [CONTRIBUTING.md](./CONTRIBUTING.md) for the package format, runtime conventions, validation requirements, and pull-request checklist.

## License

Karya is available under the [MIT License](./LICENSE).
