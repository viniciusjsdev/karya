# Thread lifecycle

- Design thread: understand domain, make consequential decisions, update truth/ADRs, and prepare Specs. Default Sol/high.
- Implementation thread: starts clean from a READY Spec and resolved manifest. Default Terra/medium for normal implementation.
- Worker thread: optional independent mechanical unit. Default Luna/low; not a routine child of implementation.
- Review thread: receives Spec, manifest, diff/artifacts, tests, and completion evidence. Critical review uses independent Sol/high.

Conversation, thread, turn, run, and subagent are different. Resume an existing implementation thread after `needs_design`. Do not use subagents as the normal specialization mechanism.
