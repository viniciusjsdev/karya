import fs from "node:fs";
import { pathToFileURL } from "node:url";

const TYPES = new Set([
  "strategy_analysis",
  "content_creation",
  "account_setup_guide",
  "account_creation",
  "platform_research",
  "platform_publish",
  "platform_schedule",
  "approved_contact",
  "metrics_read",
  "crm_update",
  "paid_spend",
]);

const WRITE_TYPES = new Set(["platform_publish", "platform_schedule", "approved_contact", "crm_update"]);

export function buildCommercialRoute(operation, env = process.env) {
  if (!operation || typeof operation !== "object") throw new Error("Operation must be a JSON object.");
  if (!operation.operation_id) throw new Error("operation_id is required.");
  if (!TYPES.has(operation.operation_type)) throw new Error(`Unsupported operation_type: ${operation.operation_type}`);
  if (operation.credentials || operation.password || operation.token || operation.recovery_code) {
    throw new Error("Secrets are prohibited in commercial operations.");
  }

  const base = {
    schema_version: "1.0",
    operation_id: operation.operation_id,
    operation_type: operation.operation_type,
    limits: operation.limits ?? {},
    warnings: [],
    external_state_changed: false,
  };

  if (["strategy_analysis", "content_creation", "account_setup_guide"].includes(operation.operation_type)) {
    return { ...base, owner: "codex", status: "ready", confirmation_gate: "none_required", reason: "Codex owns reasoning, documents, and creative preparation.", fallback: "none" };
  }
  if (operation.operation_type === "account_creation") {
    return { ...base, owner: "human", status: "human_required", confirmation_gate: "human_step", reason: "Account ownership, credentials, verification, and 2FA remain human-controlled.", fallback: "Codex can provide an account setup kit." };
  }
  if (operation.operation_type === "platform_research") {
    return { ...base, owner: "research_factory", status: "ready", confirmation_gate: "none_required", reason: "Platform discovery belongs to the independent Research Factory.", fallback: "Use a human-assisted read-only browser session." };
  }
  if (operation.operation_type === "paid_spend") {
    const exact = operation.paid_spend?.enabled === true && Number(operation.paid_spend?.cap) > 0 && operation.paid_spend?.currency && operation.target_account;
    const confirmed = operation.confirmation?.status === "approved";
    if (!exact || !confirmed) {
      return { ...base, owner: "human", status: "blocked", confirmation_gate: "explicit_action_confirmation", reason: "Paid spend requires an exact account, positive cap, currency, and post-preview confirmation.", fallback: "Prepare the campaign and request exact human approval without activating spend." };
    }
    return { ...base, owner: "human", status: "human_required", confirmation_gate: "explicit_action_confirmation", reason: "Paid activation remains human-controlled by default even after preparation.", fallback: "No automatic paid activation." };
  }

  const manusReady = Boolean(env.MANUS_API_KEY) && operation.manus_allowed === true;
  const confirmed = operation.confirmation?.status === "approved";
  if (WRITE_TYPES.has(operation.operation_type) && !confirmed) {
    return { ...base, owner: manusReady ? "manus" : "human", status: "approval_required", confirmation_gate: "explicit_action_confirmation", reason: "The exact external write has not been explicitly confirmed.", fallback: "Return a final preview and confirmation request." };
  }
  if (!manusReady) {
    return { ...base, owner: "human", status: "provider_unavailable", confirmation_gate: WRITE_TYPES.has(operation.operation_type) ? "explicit_action_confirmation" : "none_required", reason: "Manus is unavailable or not allowed for this operation.", fallback: "Generate a human-execution package and require a receipt." };
  }
  return { ...base, owner: "manus", status: "ready", confirmation_gate: WRITE_TYPES.has(operation.operation_type) ? "explicit_action_confirmation" : "none_required", reason: "The task is bounded, the required confirmation is present, and Manus is configured.", fallback: "Human execution with the same operation contract." };
}

function main() {
  const path = process.argv[2];
  if (!path) throw new Error("Usage: node route-commercial-operation.mjs <operation.json>");
  const operation = JSON.parse(fs.readFileSync(path, "utf8"));
  process.stdout.write(`${JSON.stringify(buildCommercialRoute(operation), null, 2)}\n`);
}

if (process.argv[1] && pathToFileURL(process.argv[1]).href === import.meta.url) {
  try { main(); } catch (error) { process.stderr.write(`${error.message}\n`); process.exitCode = 1; }
}
