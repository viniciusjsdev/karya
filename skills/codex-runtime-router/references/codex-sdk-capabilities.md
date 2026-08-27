# Codex Python SDK capability snapshot

Verified 2026-08-26 against the official Codex SDK documentation and the published `openai-codex==0.147.0` Python package.

Official documentation: [Codex SDK](https://developers.openai.com/codex/codex-sdk) and [GPT-5.6 model guidance](https://developers.openai.com/api/docs/guides/latest-model).

The Python package exposes the direct runtime surface required by Project Harness:

- `from openai_codex import Codex`;
- `Codex.thread_start(...)` and `Codex.thread_resume(thread_id, ...)`;
- thread options including `model`, `cwd`, `sandbox`, `approval_mode`, and `config`;
- reasoning through `config={"model_reasoning_effort": "low|medium|high|xhigh|max"}`;
- `Thread.run(input, output_schema=schema)`;
- `TurnResult.final_response` and token `usage`;
- sandbox values `read_only`, `workspace_write`, and `full_access`;
- approval values `deny_all` and `auto_review`.

The repository policy requires Python 3.12+ even if a published SDK release supports an older interpreter. The Project Harness manifest uses stable JSON spellings such as `workspace-write`; the Python adapter maps them explicitly to SDK enum values. Policy support is not inferred merely from SDK type support.

The router imports the SDK directly. It does not use a Python-to-Node bridge, does not ask another model to select runtime policy, and does not promise remote/cloud thread control. Re-check official documentation and the installed package signatures before changing the pin.
