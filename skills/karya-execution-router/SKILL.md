---
name: karya-execution-router
description: Route an explicitly approved, READY, executor-neutral project implementation to OpenCode as an optional economic executor or return Codex fallback, while preserving project contracts, blocked actions, one final signal, independent validation, and Codex audit. Use for Python, automations, frontend, and other non-Django implementation work when cost or Codex limits matter. Do not use for planning, critical decisions, Django backend routing, external actions, or self-approval.
---

# Karya Execution Router

Use OpenCode only as an optional implementation executor. Codex remains the architect, coordinator, fallback, validator, and final auditor. OpenCode never changes the Spec, approves its own result, authorizes external actions, or becomes a prerequisite for Karya.

## Required gate

Require all of the following before a live run:

- a matching `SPEC.md` and `SPEC.execution.json` with status `ready`;
- resolved acceptance criteria and exact required validation commands;
- an external execution request containing exact writable paths and mandatory prohibited actions;
- a snapshot baseline selected in the request;
- an exact provider/model confirmed available by the OpenCode CLI;
- explicit human approval matching the task, Spec version, executor, provider, model, writable paths, and validation IDs.

Provider configuration and credentials belong to OpenCode's user-level stores. Never place them in the target repository, its `.env`, `.codex`, Specs, durable documentation, or persisted prompts.

## Workflow

1. Read [references/execution-protocol.md](references/execution-protocol.md).
2. Read [references/provider-and-cost-policy.md](references/provider-and-cost-policy.md) when recommending an economic option.
3. Read [references/security-and-credentials.md](references/security-and-credentials.md) before changing permissions, readiness, or execution configuration.
4. Diagnose a proposed external request without starting implementation:

   ```bash
   python <skill>/scripts/opencode_doctor.py --request <external-request.json>
   ```

5. Preview the exact route:

   ```bash
   python <skill>/scripts/route_economic_execution.py --request <external-request.json> --dry-run
   ```

6. Start one live run only after the action-time confirmation in the external request matches exactly:

   ```bash
   python <skill>/scripts/route_economic_execution.py --request <external-request.json>
   ```

7. Do not poll or summarize intermediate events. Process exit yields exactly one route result.
8. On `opencode-completed`, Codex independently inspects the baseline diff, completion evidence, and router-run validation results before applying the required project or specialized audit.
9. On `codex-fallback-required`, Codex may implement the same approved Spec; the router itself does not start Codex or weaken the contract.

## Boundaries

- Use `karya-backend-router` for approved Django backend implementation. This generic router must not reinterpret Django contracts, migrations, or boundary scans.
- Planning, unresolved decisions, security architecture, credentials, external writes, destructive operations, and critical review stay with Codex.
- A critical or hard-to-reverse implementation is ineligible by default. Record and approve a narrower exception before routing it externally.
- Shell commands are denied by default. Only exact manifest validation commands and a small read-only Git set may run.
- Web access, subagents, questions, Git mutation, Spec changes, `.env`, `.codex`, `.agents`, `AGENTS.md`, provider configuration, credentials, and external-directory writes are blocked.
- A project with the living JSON navigation map uses Codex fallback before any provider command: source changes require explicit map review, and the economic executor cannot write protected `.codex` state. An explicitly forced OpenCode request returns unavailable. Preserve the same Spec and required validations; do not relax protection or auto-review to allow delegation.
- Run artifacts belong to the operating-system temporary directory. The router never intentionally writes credentials or provider configuration secrets and sanitizes common credential forms from executor evidence as defense in depth.

## Completion

Return exactly one JSON object on stdout. Preserve the request fingerprint, pre/post snapshot, changed-file reconciliation, OpenCode event log, stderr, completion evidence, independent validation results, and route result in the temporary run directory. OpenCode completion is evidence for Codex review, never approval.
