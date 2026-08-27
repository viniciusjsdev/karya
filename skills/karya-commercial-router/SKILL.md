---
name: karya-commercial-router
description: Route an approved commercial task between Codex, Manus, and mandatory human gates while minimizing paid Manus credits. Use after a launch contract or bounded operation exists. Codex owns strategy, writing, synthesis, and creative preparation; Manus is reserved for approved platform-native execution or measurement. The router never creates accounts or bypasses confirmation.
---

# Karya Commercial Router

## Purpose

Keep commercial orchestration inexpensive, auditable, and safe. Route thinking and artifact production to Codex, platform-native execution to Manus when it adds unique value, and identity/security steps to the human owner.

## Invocation Boundary

- Run only for an explicit commercial request.
- Require a bounded operation or launch contract before any external write.
- Do not assume approval because a launch plan or creative pack exists.
- Do not route market research through this skill; use the independent Research Factory.

## Routing Policy

| Operation | Owner | Why |
|---|---|---|
| Strategy, positioning, channel plan, account information kit | Codex | Reasoning and document production |
| Copy, scripts, creative briefs, image/video preparation | Codex | Artifact creation and QA |
| Account creation, credentials, CAPTCHA, email/SMS verification, 2FA, identity verification | Human | Identity, security, and platform ownership |
| Platform-native read-only discovery | Research Factory / Manus researcher | Separate evidence workflow |
| Approved publish or schedule action | Manus when connected, otherwise human | Native integration and execution receipt |
| Approved one-to-one contact | Manus when connected, otherwise human | Requires recipient scope and confirmation |
| Metrics retrieval from connected platforms | Manus when connected | Native access; Codex analyzes results |
| KPI analysis and next experiment | Codex | Evidence interpretation |

Read `references/routing-policy.md` and `references/approval-policy.md`.

## Workflow

### 1. Classify the operation

Use one of:

- `strategy_analysis`;
- `content_creation`;
- `account_setup_guide`;
- `account_creation`;
- `platform_research`;
- `platform_publish`;
- `platform_schedule`;
- `approved_contact`;
- `metrics_read`;
- `crm_update`;
- `paid_spend`.

### 2. Check prerequisites and risk

Confirm target platform/account, artifact version, action scope, affected audience, approval owner, confirmation status, spend cap, schedule/time zone, rollback or correction path, and prohibited data. Never accept secrets embedded in the operation.

### 3. Build a deterministic route

Run:

```powershell
node scripts/route-commercial-operation.mjs path\to\operation.json
```

Review the output. A route is a plan, not permission to execute.

### 4. Check provider readiness

Run `node scripts/commercial-doctor.mjs`. A missing Manus key or connected platform falls back to a human-execution package; it does not block planning and creative work.

### 5. Apply confirmation gates

Public writes, direct contact, CRM mutation, and paid spend require explicit action confirmation after the exact content, target, timing, and cost are known. Account creation is always human. Follow `references/approval-policy.md`.

### 6. Minimize Manus usage

Follow `references/credit-policy.md`:

- send final artifacts and exact actions, not open-ended strategy tasks;
- batch only homogeneous, approved actions;
- cap items, retries, and time;
- keep discovery out of the execution task;
- use Codex for analysis before and after execution;
- record provider task IDs and reported usage without promising an unverifiable maximum.

### 7. Execute and verify

Invoke `$manus-commercial-operator` only for an approved Manus route. Require an execution receipt and validate it with `scripts/validate-manus-receipt.mjs`. Never infer success from task submission alone.

## Output

Return route owner, readiness, required human gate, exact next artifact/operation, fallback, cost controls, and a statement of whether external execution occurred. Planning-only runs must state `external_state_changed: false`.
