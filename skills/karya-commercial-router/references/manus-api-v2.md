# Manus API v2 integration

Official source: <https://open.manus.ai/docs/v2/introduction>

Last verified: 2026-07-13.

API v2 is the current Manus API. API v1 is deprecated. The base URL is `https://api.manus.ai`, with direct API-key authentication through `x-manus-api-key` or OAuth for an Open App.

## Codex-to-Manus coupling

Codex owns the orchestration and produces:

- the bounded research or commercial-operation contract;
- the final prompt and final artifacts;
- the JSON `structured_output_schema` for the result/receipt;
- the portable Manus skill package;
- connector and skill IDs to enable/force;
- confirmation, retry, and cost limits.

Manus executes only the provider-specific edge task.

Create an asynchronous task with `POST /v2/task.create`. The request can pass:

- `message.content` for the bounded instruction;
- `message.connectors` with authorized connector UUIDs;
- `message.enable_skills` for available skill IDs;
- `message.force_skills` to require the portable research/operator skill;
- `structured_output_schema` for the evidence or receipt contract;
- `project_id` when shared Manus project instructions are deliberately in scope.

Use `skill.list` and `connector.list` to resolve IDs rather than hardcoding display names. Open Apps can bundle private skills; use the smallest necessary skill/connector set.

Official task reference: <https://open.manus.ai/docs/v2/task.create>

## Connector authorization

Authorize connectors through the Manus web app/OAuth flow before an API task, then pass their UUIDs. Connector access can be revoked; never assume a previously authorized connector is still available. Use minimum Open App scopes such as `create_task`, `use_connectors`, or `use_my_browsers` instead of `manage_all_tasks` unless broad access is genuinely required.

Official references:

- <https://open.manus.ai/docs/v2/connectors>
- <https://open.manus.ai/docs/v2/open-app>

## Lifecycle

Tasks run asynchronously. Prefer webhooks for `task_created` and `task_stopped`, or use bounded `task.listMessages` polling with backoff. Interpret terminal state and read the structured output/result; task submission is not execution proof.

When the task enters `waiting`, inspect `waiting_for_event_type` and its `confirm_input_schema`. Do not auto-confirm external writes, mail/contact, browser connection, authentication, or expanded access. Route those events to the human approval gate and call `task.confirmAction` only with the exact approved input.

Official references:

- <https://open.manus.ai/docs/v2/task-lifecycle>
- <https://open.manus.ai/docs/v2/webhooks-overview>

## Cost controls

Manus credits can reflect language-model work, virtual-machine/browser execution, and third-party APIs, with consumption varying by task complexity and duration. Therefore keep tasks narrow, final, structured, and bounded; record reported usage rather than guaranteeing a fixed cost.

Official credit policy: <https://help.manus.im/en/articles/11711097-what-are-the-rules-for-credits-consumption-and-how-can-i-obtain-them>

## Separation

Read-only discovery forces `$manus-platform-researcher`; write execution forces `$manus-commercial-operator`. Never enable both merely for convenience. Credentials, connector tokens, and authenticated browser state stay outside generated product repositories.
