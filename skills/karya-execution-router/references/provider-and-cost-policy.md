# Provider and cost policy

Cost changes the recommendation, not the safety contract.

| Phase | Default owner | Economic route |
| --- | --- | --- |
| Planning, architecture, consequential decisions | Codex Sol/high | Do not delegate |
| Normal implementation from a READY Spec | Codex Terra/medium | OpenCode may be recommended after readiness and approval |
| Mechanical, low-risk change with deterministic validation | Codex Luna/low | Prefer the smallest proven OpenCode or local model when approved |
| Critical review, credentials, security, irreversible or external action | Codex Sol/high | Do not downshift while the risk trigger remains |

Provider options are consultative:

- OpenCode Go may suit predictable subscription-based economy, but never assume subscription, remaining access, or model availability.
- OpenCode Zen may suit curated pay-per-use access, but never assume billing, credits, price, or retention terms.
- A user's own provider API may reuse an existing account, but billing, privacy, regional processing, rate limits, and model quality belong to that provider.
- A local model can remove per-token provider billing but may require installation, capable hardware, more time, and a stronger deterministic quality gate.
- Codex remains the safe fallback when no external route is approved or ready.

Do not hardcode absolute prices. At recommendation time, report the available billing mode, known limit, uncertainty, expected validation burden, and the condition that returns execution to Codex. Provider choice never authorizes installation, authentication, billing, credit use, or execution.
