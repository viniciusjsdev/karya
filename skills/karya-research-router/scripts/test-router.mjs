import assert from "node:assert/strict";
import { buildRoute } from "./route-research.mjs";

const base = { request_id: "MR-TEST-01", depth: "rapid" };

const app = buildRoute({ ...base, intent: "app_market" }, {});
assert.equal(app.tasks[0].primary[0], "app-market-intelligence-analyst");
assert.equal(app.tasks[0].status, "ready");

const broadFallback = buildRoute({ ...base, intent: "broad_web", permissions: { perplexity_allowed: true } }, {});
assert.equal(broadFallback.tasks[0].primary[0], "codex_batched");
assert.equal(broadFallback.tasks[0].status, "limited");

const broadPaid = buildRoute({ ...base, intent: "broad_web", permissions: { perplexity_allowed: true } }, { PERPLEXITY_API_KEY: "configured" });
assert.equal(broadPaid.tasks[0].primary[0], "perplexity");

const platform = buildRoute({ ...base, intent: "platform_native", permissions: { manus_allowed: false } }, {});
assert.equal(platform.tasks[0].status, "manual_required");

const mixed = buildRoute({
  ...base,
  intent: "mixed",
  tasks: [
    { task_id: "TASK-A", intent: "scientific", evidence_class: "problem evidence" },
    { task_id: "TASK-B", intent: "targeted_web", evidence_class: "pricing" },
  ],
}, { OPENALEX_API_KEY: "configured" });
assert.equal(mixed.tasks.length, 2);
assert.equal(mixed.tasks[0].status, "ready");

assert.throws(() => buildRoute({ ...base, intent: "unknown" }, {}));
process.stdout.write("research router tests passed\n");
