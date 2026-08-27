import fs from "node:fs";

const modes = new Set(["publish", "schedule", "approved_contact", "metrics_read", "crm_update"]);
const statuses = new Set(["succeeded", "partial", "failed", "unknown", "precondition_failed"]);
const path = process.argv[2];

function fail(message) { throw new Error(message); }
if (!path) fail("Usage: node validate-manus-receipt.mjs <receipt.json>");
const value = JSON.parse(fs.readFileSync(path, "utf8"));
if (value.schema_version !== "1.0") fail("schema_version must be 1.0.");
for (const field of ["operation_id", "platform", "account_id", "started_at", "completed_at"]) {
  if (typeof value[field] !== "string" || !value[field]) fail(`${field} is required.`);
}
if (!modes.has(value.mode)) fail("mode is invalid.");
if (!statuses.has(value.status)) fail("status is invalid.");
for (const field of ["changed_objects", "evidence", "errors"]) if (!Array.isArray(value[field])) fail(`${field} must be an array.`);
if (!Number.isInteger(value.retries) || value.retries < 0) fail("retries must be a non-negative integer.");
if (value.mode === "metrics_read" && value.external_state_changed !== false) fail("metrics_read must not change external state.");
if (value.status === "succeeded" && value.evidence.length === 0) fail("A succeeded receipt requires verification evidence.");
process.stdout.write("Manus execution receipt is valid\n");
