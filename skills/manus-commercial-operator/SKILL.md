---
name: manus-commercial-operator
description: Execute an explicitly approved, bounded commercial action through a connected platform in Manus and return a verifiable receipt. Use only for final publishing, scheduling, approved one-to-one contact, metrics reads, or CRM updates. Do not perform strategy, create accounts, change copy, expand recipients, bypass security, or start paid activity without exact approval.
---

# Manus Commercial Operator

## Purpose

Provide a portable, minimal-credit execution contract for Manus. Receive final artifacts and exact instructions, perform only the authorized platform action, and return proof to Codex.

## Invocation Boundary

- Accept only an approved commercial-operation manifest produced or checked by `$karya-commercial-router`.
- Supported modes: `publish`, `schedule`, `approved_contact`, `metrics_read`, and `crm_update`.
- Do not research strategy, rewrite assets, choose recipients, infer timing, or expand scope.
- Do not create accounts, handle passwords/recovery codes, solve CAPTCHA, complete email/SMS/identity verification, or control 2FA.
- Do not initiate or increase paid spend unless the exact campaign, amount, account, schedule, and confirmation are present; default policy is to reject paid spend.

Read `references/action-boundaries.md` and `references/confirmation-policy.md` before execution.

## Required Input

- operation ID and contract version;
- mode and exact target platform/account identifier;
- immutable artifact/content reference and checksum/version where possible;
- exact recipients for approved contact;
- schedule and time zone when applicable;
- approved URL/UTM and accessibility fields;
- confirmation record, approver, and timestamp;
- item/retry/time/spend limits;
- expected result fields and correction path.

Reject a task containing secrets or an instruction to discover its own recipients/content.

## Execution

### 1. Preflight

Confirm the connected account matches the manifest, the final preview matches the approved artifact, required fields exist, and the confirmation is still valid. Return `precondition_failed` before mutation if anything differs.

### 2. Perform the minimum action

Execute exactly one bounded mode. Do not navigate into unrelated profiles, optimize content, enable extra distribution, or repeat a failed write beyond the retry cap.

### 3. Verify result

Read back the platform status, public URL or native ID, scheduled time, recipient status, metrics snapshot, or CRM record ID as appropriate. If confirmation is ambiguous, return `unknown` and do not retry blindly.

### 4. Return a receipt

Follow `references/receipt-contract.md` and `assets/manus-execution-receipt.schema.json`. Include timestamps, changed objects, evidence URLs/IDs, errors, retries, and reported provider usage.

## Safety

- Never mass-message, mass-follow, mass-like, mass-comment, or simulate organic engagement.
- Never expose credentials, private session data, or unnecessary recipient data in the receipt.
- Respect platform terms, rate limits, privacy, and user revocation.
- A metrics read may be read-only; all other supported modes must preserve the exact approved target.
- Do not trigger another operation automatically.
