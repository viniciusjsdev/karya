# Security and credential boundary

## Outside the project repository

- OpenCode installation and user-level configuration;
- provider authentication and API keys;
- provider/model selection profiles;
- the exact action-time execution request;
- temporary prompts, raw events, stderr, snapshots, and router results.

The router may record provider/model identity and reported usage in a temporary receipt, but never a key, token, authorization header, cookie, credential value, or provider configuration object.

## Mandatory prohibitions

Every request must explicitly prohibit:

- `secrets_and_credentials`;
- `environment_files`;
- `external_actions`;
- `spec_changes`;
- `destructive_git`;
- `web_access`.

The runtime additionally protects `.git`, `.env*`, `AGENTS.md`, `.agents`, `.codex`, `specs`, the selected Spec/manifest, and every `opencode.json`. Those protections cannot be weakened by the request's writable paths.

## Runtime policy

- Edit is deny-by-default and then opened only for exact approved paths.
- Shell is deny-by-default and then opened only for read-only Git inspection and exact Spec validation commands.
- External directories, web fetch/search, subagents, extra skill loading, LSP, textual grep, and interactive questions are denied. Listing and direct reads remain available, subject to explicit `.env` and `.git` read denials.
- The router snapshots the project before and after execution. Created, removed, or modified files outside the approved scope fail the run.
- Validation commands reject shell control operators and known installation, network, destructive, external-write, and Git-mutation commands.
- Executor events, stderr, and validation output are sanitized for common credential forms before retention. This is defense in depth, not permission to expose a secret to the executor.

These controls reduce risk; they do not replace Codex review or a specialized auditor.
