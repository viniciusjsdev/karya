# Economic execution protocol

## Two-plane contract

The target repository contains durable project truth only: `AGENTS.md`, a READY Spec, resolved Codex fallback/review runtime, acceptance criteria, exact validation commands, and project documentation. The external execution request contains the action-time executor choice, provider/model, writable paths, baseline mode, and matching human confirmation. It must live outside the target repository.

```text
READY Spec + external approved request
  -> deterministic contract and safety validation
  -> OpenCode CLI/provider/model readiness
  -> pre-run whole-project snapshot
  -> one non-interactive OpenCode child process
  -> completion evidence + process exit
  -> post-run snapshot and allowed-path reconciliation
  -> router-run exact validations
  -> one final route result
  -> independent Codex review/audit
```

## Route outcomes

- `preflight-blocked`: the Spec, request, confirmation, paths, validations, or safety policy is incomplete or conflicting.
- `codex-fallback-required`: OpenCode is optional and unavailable, or Codex was selected.
- `opencode-unavailable`: OpenCode was explicitly required but its CLI, provider authentication, or exact model is unavailable.
- `opencode-ready`: dry-run gates and readiness passed; no implementation ran.
- `opencode-completed`: OpenCode reported completion, protected state stayed intact, changed files remained in scope, and router-run validations passed.
- `opencode-reported-blocked`: OpenCode returned `blocked` or `needs_design` evidence.
- `opencode-error`: timeout, process failure, missing/invalid evidence, out-of-scope change, protected mutation, or validation failure.

## One-signal rule

The router redirects OpenCode's event stream and stderr to files, waits on the child process without model polling, and emits one JSON route result after process exit. Timeout also terminates in one result. Do not add heartbeat automation or an LLM watcher.

## Audit handoff

Codex receives the Spec, execution manifest, external request fingerprint, pre/post snapshots, actual changed files, completion evidence, exact router-run validation results, and sanitized event/stderr logs. It reruns or inspects evidence in proportion to risk and records an independent review receipt before invoking the Harness or richer domain auditor. OpenCode never reviews or approves its own work.
