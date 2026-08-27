# OpenCode Installation and Readiness

Use the root guide at `docs/opencode-backend-execution.md` for human-facing setup. Operationally, readiness requires all of the following:

1. `opencode --version` succeeds.
2. `opencode auth list` contains OpenCode Go credentials.
3. `opencode models opencode-go` contains the configured `provider/model` identifier.

Prefer native OpenCode authentication with `opencode auth login` or TUI `/connect`. Credentials belong to OpenCode's user-level credential store, outside Karya and target repositories.

On Windows, install and authenticate in the same environment that will run the router. PowerShell and WSL have different executables and credential stores.

Do not infer readiness from the presence of a `.env` variable alone. Do not request, print, copy, or validate the raw API key.
