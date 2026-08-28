# Optional Economic Execution Routing

## Outcome

Karya can recommend OpenCode when a user explicitly wants to economize Codex limits or execution cost. OpenCode is only an implementation executor. Codex remains the architect, coordinator, fallback, independent validator, and final auditor.

OpenCode is not required to use Karya, the MVP Factory, Research Factory, Marketing Factory, or Project Harness Factory.

## Eligibility

An external implementation is eligible only when:

- the project has a matching READY `SPEC.md` and `SPEC.execution.json`;
- architecture and consequential decisions are resolved;
- required validations are exact and safe to run without a shell;
- the Spec requires independent review;
- writable paths and mandatory prohibited actions are exact;
- a full pre-run snapshot will be captured;
- the chosen OpenCode provider and exact model are available;
- the human confirms the exact action-time request.

Use `karya-backend-router` instead for Django backend contracts. Planning, security architecture, credentials, external actions, critical review, and hard-to-reverse work remain with Codex by default.

## Provider options

Karya may explain these options without assuming access:

- **OpenCode Go:** a low-cost subscription route with a changing curated model catalog;
- **OpenCode Zen:** curated pay-per-use models and credits;
- **own provider API:** billing, limits, privacy, and data processing belong to that provider;
- **local model:** no provider token billing, with hardware, setup, latency, and capability tradeoffs;
- **Codex fallback:** normal Karya execution when no external route is approved or ready.

Consult the current [OpenCode Go](https://opencode.ai/docs/go/), [OpenCode Zen](https://opencode.ai/docs/zen/), and [provider](https://opencode.ai/docs/providers/) documentation before recommending a live option. Do not hardcode prices or assume subscription, credit, authentication, authorization, or model availability.

## Configuration boundary

OpenCode installation, authentication, credentials, provider configuration, and the exact execution request stay outside target project repositories. They never belong in project documentation, Specs, persisted prompts, `.codex`, `AGENTS.md`, or project `.env` files.

The external request records only the exact action being authorized: task and Spec identity/version, executor, provider/model identity, billing mode, timeout, writable paths, prohibited actions, baseline mode, validation IDs, and matching confirmation. It must not contain a credential.

## Operational flow

1. Codex designs or validates the project contract.
2. Karya identifies cost preference and explains whether OpenCode is eligible.
3. The human separately approves any installation, authentication, subscription, billing, or provider setup.
4. Karya verifies the exact model with the OpenCode CLI.
5. The human confirms the exact external execution request.
6. `karya-execution-router` snapshots the project and starts one non-interactive OpenCode child process.
7. OpenCode writes structured completion or blockage evidence and exits once; Codex does not poll it.
8. The router compares snapshots, rejects protected/out-of-scope changes, and reruns the exact validations independently.
9. Codex reviews the Spec, diff/snapshots, sanitized executor evidence, and validation results.
10. `project-harness-auditor` or a richer domain auditor makes the final reconciliation. OpenCode never approves itself.

## Failure and fallback

Optional OpenCode unavailability returns `codex-fallback-required`. Explicitly required OpenCode unavailability returns `opencode-unavailable`. A failed, timed-out, out-of-scope, or invalid-evidence run returns `opencode-error`; do not retry blindly. A reported consequential gap returns `opencode-reported-blocked` and goes back to Codex design before any resumed execution.
