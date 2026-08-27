# OpenCode for Backend Execution

## Responsibility

Codex remains the Karya orchestrator. It creates or validates the Goal, requires an approved backend contract, invokes the router once, waits passively, and resumes only when OpenCode exits successfully or with an error. OpenCode performs the heavy Django code-writing phase using `django-backend-code-executor`. Codex then sends the result to `django-backend-service-architect` for contract audit.

OpenCode is optional. When it is absent, unauthenticated, or missing the selected model, the default `auto` route returns `codex-fallback-required` and Codex implements the same approved contract directly.

## 1. Install OpenCode

Official documentation: [OpenCode installation](https://opencode.ai/docs/) and [Windows/WSL guidance](https://opencode.ai/docs/windows-wsl/).

Windows PowerShell can use one of:

```powershell
npm install -g opencode-ai
# or
choco install opencode
# or
scoop install opencode
```

OpenCode recommends WSL for the best Windows experience. Inside WSL:

```bash
curl -fsSL https://opencode.ai/install | bash
```

Choose one execution environment and keep installation, authentication, the Karya router, and target project in that environment. PowerShell and WSL use separate OpenCode credential stores.

Verify:

```powershell
opencode --version
```

This workstation currently uses the npm installation path. Do not add `opencode-ai` as a dependency of generated applications.

## 2. Subscribe and authenticate OpenCode Go

Official documentation: [OpenCode Go](https://opencode.ai/docs/go/) and [providers](https://opencode.ai/docs/providers/).

1. Subscribe to OpenCode Go and copy the API key from the OpenCode account.
2. Start the TUI:

   ```powershell
   opencode
   ```

3. Run `/connect`.
4. Select `OpenCode Go`.
5. Paste the key into the OpenCode prompt.
6. Run `/models` and confirm the intended coding model appears.

The equivalent credential-management entry point is:

```powershell
opencode auth login
```

Verify without revealing the key:

```powershell
opencode auth list
opencode models opencode-go
```

OpenCode stores provider credentials in its user-level credential store. Never place the API key in this repository, `.env`, `opencode.json`, a generated project, shell history, task prompt, or completion evidence.

## 3. Configure Karya routing

Create the ignored local file:

```powershell
Copy-Item .env.example .env
```

Available settings:

```dotenv
KARYA_BACKEND_EXECUTOR=auto
KARYA_OPENCODE_MODEL=opencode-go/kimi-k2.7-code
KARYA_OPENCODE_TIMEOUT_MINUTES=120
```

When invoking the installed router from outside this repository and using non-default preferences, set `KARYA_ENV_FILE` to this ignored `.env`. Credentials still remain in OpenCode's native store.

Executor values:

- `auto`: use OpenCode when ready, otherwise request Codex fallback;
- `opencode`: require OpenCode and report a blocking setup error when unavailable;
- `codex`: skip OpenCode explicitly.

The default heavy-code model is `opencode-go/kimi-k2.7-code`. `opencode-go/deepseek-v4-flash` is configured as the small model for cheap auxiliary work. The OpenCode Go catalog changes over time, so use `opencode models opencode-go` and the [current OpenCode Go list](https://opencode.ai/docs/go/) before changing model identifiers.

Run the doctor:

```powershell
node .\skills\karya-backend-router\scripts\opencode-doctor.mjs
```

Readiness is true only when the CLI runs, OpenCode Go is authenticated, and the exact configured model is available.

## 4. Route an approved backend

The target project must contain all six human-readable backend contracts, an approved matching `docs/architecture/backend-contract-manifest.json`, and this frontmatter in `docs/architecture/backend-implementation-contract.md`:

```yaml
---
status: approved
contract_version: 1
approved_at: 2026-07-13
---
```

Dry-run the decision:

```powershell
$projectRoot = (Resolve-Path ..\my-project).Path
node .\skills\karya-backend-router\scripts\route-backend-execution.mjs `
  --project-root $projectRoot `
  --dry-run
```

Execute:

```powershell
$projectRoot = (Resolve-Path ..\my-project).Path
node .\skills\karya-backend-router\scripts\route-backend-execution.mjs `
  --project-root $projectRoot `
  --task-id implementar-contrato-backend-v1
```

The router calls `opencode --pure run` non-interactively with the configured model, a runtime-defined Karya agent, the executor skill as mandatory instructions, restricted permissions, and `--auto`. It disables external plugins, redirects all raw events to a file, and performs no polling. The single child-process exit is the completion/error wake-up signal for Codex.

The manifest must have the same `contract_version`, `status: approved`, no template values, and non-empty services, invariants, endpoints, and required validations. Environment bindings include the exact approved example URL. Invariants and endpoints list exact required test function names. `allowed_execution_commands` lists exact project-specific `makemigrations` commands. Completion evidence must cite those exact tests for every invariant/endpoint ID and report passing evidence for every required validation ID before the router returns `opencode-completed`.

Validate before routing:

```powershell
node .\skills\django-backend-service-architect\scripts\validate-backend-contract-manifest.mjs `
  $projectRoot --require-approved
```

Artifacts are stored under the operating system temporary directory:

```txt
<temp>/karya-backend-runs/<task-id>/
  request.json
  opencode-events.ndjson
  opencode-stderr.log
  completion.json
  completion.schema.json
  architecture-scan.log
  route-result.json
```

## 5. Interpret the final route

- `opencode-completed`: Codex audits the code and evidence with `django-backend-service-architect`.
- `opencode-reported-blocked`: Codex reads final evidence and resolves a bounded implementation or contract issue.
- `opencode-error`: Codex reads final logs/evidence and decides on a bounded retry or fallback.
- `codex-fallback-required`: Codex immediately uses `django-backend-code-executor` itself.
- `preflight-blocked`: return to planning or explicit approval; no backend code may be written.
- `opencode-unavailable`: OpenCode was explicitly required, so fix setup rather than silently changing executors.

## Security model

The committed root `opencode.json` and the router's bundled `assets/opencode.backend.json` contain the same non-secret guardrails. At runtime the router applies its bundled configuration through OpenCode's highest-priority inline configuration and pins the selected provider/model. It denies edits to credentials, Git metadata, generated-project instructions/context, approved architecture contracts, and migration Python files. Shell commands are denied by default; the runtime permits a small exact read-only Git set, exact approved validation commands, and exact approved `makemigrations` commands. Compound shell operators are rejected in manifest commands. It also denies subagents, questions, web access, destructive Git operations, and broad external-directory access.

The router permits exactly one temporary run directory for completion evidence and removes any stale `completion.json` before reusing a task ID. It snapshots immutable contracts/instructions/environment files and every pre-existing migration, then rejects completion if their hashes change; only new scanner-verified Django-generated migrations may appear. OpenCode never writes executor configuration into the generated project's `.codex/`. Codex performs the final contract audit.

Playwright/full-stack validation remains Codex-supervised because it benefits from active visual and behavioral inspection; this backend router only owns the heavy backend writing phase.

## Troubleshooting

`OpenCode CLI is not installed`: install it in the same environment running Node and the router.

`OpenCode Go is not authenticated`: run `opencode auth login` or TUI `/connect`, then check `opencode auth list`.

`configured model is unavailable`: run `opencode models opencode-go` and update `KARYA_OPENCODE_MODEL` to an exact returned identifier.

PowerShell works but WSL does not, or the reverse: authenticate separately in the environment that runs the router.

`preflight-blocked`: do not bypass it. Complete the six human-readable contracts and approve the matching implementation contract/JSON manifest version first.

Projects generated before the contract-manifest gate must rerun `init-backend-project-context.mjs`, resolve the newly created manifest from their existing approved Markdown contracts, and obtain matching approval before routing again. The initializer preserves every existing contract and project file.
