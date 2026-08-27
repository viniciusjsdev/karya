# Project knowledge taxonomy

| Material | Durable home | Test |
| --- | --- | --- |
| persistent knowledge or truth | domain-appropriate docs or reference | future work must rely on it |
| durable architectural decision | ADR or `.codex/decisions/` | alternatives and consequence matter |
| bounded implementable change | Spec | one execution/review lifecycle |
| specialized recurring procedure | `.agents/skills/<name>/` | coherent capability with repeated triggers |
| deterministic repeated operation | script | inputs and outputs can be checked mechanically |
| one-time task | task/Spec only when needed | recurrence does not justify a skill |
| execution policy | versioned runtime policy | supplies defaults and escalation rules |
| resolved runtime for one change | `SPEC.execution.json` | historical execution must not drift with policy |
| temporary run/thread state | `.codex/runtime/` or external state store | not project truth; normally ignored by VCS |

Link to authoritative material rather than copying it into AGENTS, skills, Specs, and references. Promote important chat discoveries into the appropriate durable home before ending the design thread.
