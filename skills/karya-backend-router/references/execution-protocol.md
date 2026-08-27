# Backend Routing Protocol

## Inputs

- target project root;
- six backend architecture contracts plus the approved matching `backend-contract-manifest.json`;
- approved implementation frontmatter;
- Karya executor instructions;
- optional executor/model/timeout overrides.

## Decision

```txt
approved contract?
  no  -> preflight-blocked
  yes -> executor=codex?
           yes -> codex-fallback-required
           no  -> OpenCode installed + authenticated + model available?
                    no + auto     -> codex-fallback-required
                    no + opencode -> opencode-unavailable
                    yes           -> one passive opencode run
```

## OpenCode Run

Run non-interactively with `opencode --pure run --format json --model <model> --agent karya-backend --auto --dir <project>`. Capture raw stdout and stderr to files. Do not stream progress to Codex. The runtime-defined primary agent prevents target or global agents/plugins from weakening the factory execution boundary.

The runtime prompt requires a structured `completion.json` with the exact manifest-listed tests in contract evidence for every invariant/endpoint ID and passing validation evidence for every required validation ID. Before each run, discard any prior completion file for the same task ID. After process exit, validate the fresh completion and run the executor's deterministic boundary scanner from the target project root.

The bundled OpenCode policy denies shell commands by default. A small exact read-only Git set, every exact manifest validation command, and every exact `allowed_execution_commands` migration-generation command are allowlisted at runtime. Shell control operators are rejected during preflight. Approved architecture files remain non-writable; migration Python is written only as a side effect of the approved Django migration command.

Snapshot approved contracts, `.codex/`, `.agents/`, `AGENTS.md`, environment files, target `opencode.json`, and every pre-existing migration before execution. Compare hashes after OpenCode exits. Any creation/removal/modification in immutable paths or any change/removal of an existing migration prevents `opencode-completed`; new migration files remain allowed only when the deterministic scanner confirms Django-generated provenance.

The router resolves `django-backend-code-executor` as a sibling installed skill and loads its bundled `assets/opencode.backend.json`. It must work both from this source repository and from `~/.codex/skills/` without relying on source-repository paths. Use `KARYA_ENV_FILE` only when installed execution needs non-default routing preferences.

## Wake-up Contract

One child-process exit produces exactly one route result. Success, reported blockage, timeout, invalid completion, and process failure all wake Codex once. No timer, recurring automation, or model polling is necessary.

## Fallback

Fallback means Codex loads `django-backend-code-executor` and continues from the same approved contract. It does not weaken architecture rules and it does not require new user approval unless the contract itself is incomplete or conflicting.
