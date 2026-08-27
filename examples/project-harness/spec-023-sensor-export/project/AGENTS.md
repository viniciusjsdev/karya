# Sensor export project guidance

- Treat `docs/project/overview.md` and accepted ADRs as project truth.
- Execute bounded changes only from a validated Spec and resolved execution manifest.
- Use `$normalize-sensor-samples` when importing or comparing raw sensor samples.
- Preserve raw input order and never invent tie-breaking behavior.
- Return `needs_design` for a consequential absent decision.
- Keep `.codex/runtime/` temporary and resume the recorded implementation thread after design resolution.
- Do not use subagents as the normal specialization path.
