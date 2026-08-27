import assert from "node:assert/strict";
import { buildCommercialRoute } from "./route-commercial-operation.mjs";

const base = { operation_id: "COM-TEST-01" };

assert.equal(buildCommercialRoute({ ...base, operation_type: "content_creation" }, {}).owner, "codex");
assert.equal(buildCommercialRoute({ ...base, operation_type: "account_creation" }, {}).owner, "human");
assert.equal(buildCommercialRoute({ ...base, operation_type: "platform_research" }, {}).owner, "research_factory");

const unapproved = buildCommercialRoute({ ...base, operation_type: "platform_publish", manus_allowed: true }, { MANUS_API_KEY: "configured" });
assert.equal(unapproved.status, "approval_required");

const approved = buildCommercialRoute({ ...base, operation_type: "platform_publish", manus_allowed: true, confirmation: { status: "approved" } }, { MANUS_API_KEY: "configured" });
assert.equal(approved.owner, "manus");
assert.equal(approved.status, "ready");

const spend = buildCommercialRoute({ ...base, operation_type: "paid_spend" }, {});
assert.equal(spend.status, "blocked");

assert.throws(() => buildCommercialRoute({ ...base, operation_type: "content_creation", token: "secret" }, {}));
process.stdout.write("commercial router tests passed\n");
