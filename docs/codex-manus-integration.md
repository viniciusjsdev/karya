# Codex and Manus Integration

Official API behavior last verified: 2026-07-13.

## Operating model

Codex is the primary orchestrator. It creates contracts, strategy, queries, creative artifacts, schemas, validation, and bounded execution instructions. Manus is an optional edge executor for work that benefits from native platform integrations, signed-in search, connected actions, or platform metrics.

This division reduces Manus credit consumption and keeps product/commercial reasoning in the existing Codex stack.

## Coupling pattern

```txt
User approval
  -> Codex builds bounded contract + final artifacts + output schema
  -> Karya router selects Manus only when native access adds value
  -> Manus API v2 task.create
       - exact message
       - connector UUIDs
       - portable skill ID in enable_skills/force_skills
       - structured_output_schema
  -> webhook or bounded task.listMessages lifecycle
  -> human handles waiting/confirmation when required
  -> structured evidence bundle or execution receipt
  -> Codex audits, synthesizes, and decides next step
```

## Portable Manus skills

Two repository skills are intentionally self-contained for Manus:

- `manus-platform-researcher`: read-only creator, community, competitor, and content discovery;
- `manus-commercial-operator`: exact approved publish, schedule, contact, metrics, or CRM operation.

In Manus, add/bundle the skill, resolve its ID with `skill.list`, and pass it through `message.enable_skills` and preferably `message.force_skills` for the bounded task. Open Apps can bundle private skills. Codex still supplies the operation contract and validates the structured result.

## Connector and account setup

The human owner first creates and secures the platform account, then authorizes the connector in Manus/OAuth with minimum scopes. `connector.list` returns the UUID passed to `task.create`. Do not place passwords, access tokens, cookies, verification codes, or recovery codes in Karya files.

## Lifecycle and approval

Manus tasks are asynchronous. Prefer webhooks or bounded `task.listMessages` polling. A task can stop, fail, or wait for input/confirmation. For `waiting` events, inspect the returned `confirm_input_schema` and route sensitive/external actions to the human. A launch-plan approval does not authorize a platform write.

## Cost discipline

- Codex narrows the task and prepares final content before Manus runs.
- Use one operation type, exact account, bounded items, retries, time, and result schema.
- Do not ask Manus to research and publish in one task.
- Do not ask Manus to rewrite final assets or discover recipients during execution.
- Use reported usage from the task/receipt; do not promise fixed credits when the provider does not enforce them.
- Fall back to a human-execution package when a connector or Manus key is unavailable.

## Official Manus references

- API v2 introduction: <https://open.manus.ai/docs/v2/introduction>
- Task creation and skill/connector fields: <https://open.manus.ai/docs/v2/task.create>
- Task lifecycle and confirmation: <https://open.manus.ai/docs/v2/task-lifecycle>
- Connectors: <https://open.manus.ai/docs/v2/connectors>
- Open Apps, OAuth scopes, and bundled skills: <https://open.manus.ai/docs/v2/open-app>
- Webhooks: <https://open.manus.ai/docs/v2/webhooks-overview>
- Credit behavior: <https://help.manus.im/en/articles/11711097-what-are-the-rules-for-credits-consumption-and-how-can-i-obtain-them>
