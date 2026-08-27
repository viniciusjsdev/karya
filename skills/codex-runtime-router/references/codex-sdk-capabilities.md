# Codex SDK capability snapshot

Verified 2026-08-26 against official Codex SDK documentation and published `@openai/codex-sdk` package version `0.150.0`.

Official documentation: [Codex SDK](https://developers.openai.com/codex/codex-sdk) and [GPT-5.6 model guidance](https://developers.openai.com/api/docs/guides/latest-model).

The TypeScript SDK supports:

- `new Codex()`;
- `startThread(options)` and `resumeThread(id, options)`;
- `ThreadOptions.model`, `workingDirectory`, `modelReasoningEffort`, `sandboxMode`, `approvalPolicy`, network/search controls, and additional directories;
- `thread.id`, populated after the first turn starts;
- `run(input, { outputSchema })` and streamed execution;
- result `finalResponse`, items, and token usage;
- thread/turn failure and fatal error events.

The current published reasoning type also includes `minimal`, `ultra`, and other levels, but Project Harness policy intentionally materializes only `low`, `medium`, `high`, `xhigh`, and `max`. Policy support is not inferred from SDK type support.

The official Python SDK uses a different surface (`thread_start`) and app-server transport. This router implements the confirmed TypeScript surface. It does not invent a cross-language abstraction or promise remote/cloud thread control.

Re-check the official docs and published types before upgrading the pinned SDK. Prices and model availability are not encoded in routing logic.
