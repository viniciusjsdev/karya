import fs from "node:fs";

function isObject(value) { return Boolean(value) && typeof value === "object" && !Array.isArray(value); }
function requireKeys(errors, value, label, keys) {
  if (!isObject(value)) { errors.push(`${label} must be an object`); return false; }
  for (const key of keys) if (!Object.hasOwn(value, key)) errors.push(`${label} is missing ${key}`);
  return true;
}
function placeholder(value) { return /(?:\breplace[_ -]?me\b|\bTBD\b|\bTODO\b|\{\{|<[^>]+>)/i.test(String(value)); }

export function validateHarnessPlan(plan, { requireAccepted = false } = {}) {
  const errors = [];
  const required = ["schema_version", "status", "project", "sources_of_truth", "documentation", "decisions", "workflows", "local_skill_candidates", "spec_strategy", "validation", "runtime_policy", "thread_policy", "automatic_handoff"];
  if (!requireKeys(errors, plan, "harness plan", required)) return errors;
  if (plan.schema_version !== "1.0") errors.push("schema_version must be 1.0");
  if (!["proposed", "accepted"].includes(plan.status)) errors.push("status must be proposed or accepted");
  if (requireAccepted && plan.status !== "accepted") errors.push("materialization requires an accepted plan");
  if (plan.automatic_handoff !== false) errors.push("automatic_handoff must be false");
  requireKeys(errors, plan.project, "project", ["name", "domain", "project_type", "objective"]);
  if (!Array.isArray(plan.sources_of_truth) || plan.sources_of_truth.length === 0) errors.push("sources_of_truth must contain at least one item");
  else for (const [index, source] of plan.sources_of_truth.entries()) {
    if (!requireKeys(errors, source, `sources_of_truth[${index}]`, ["path", "kind", "authority", "action"])) continue;
    if (!["preserve", "map", "create"].includes(source.action)) errors.push(`sources_of_truth[${index}].action is invalid`);
  }
  requireKeys(errors, plan.documentation, "documentation", ["preserve", "create", "path_mappings"]);
  requireKeys(errors, plan.decisions, "decisions", ["durable_path", "open"]);
  requireKeys(errors, plan.spec_strategy, "spec_strategy", ["root", "active_pattern", "markdown_name", "execution_name"]);
  requireKeys(errors, plan.runtime_policy, "runtime_policy", ["policy_version", "project_path"]);
  requireKeys(errors, plan.thread_policy, "thread_policy", ["design", "implementation", "needs_design", "parallel_writes", "subagents"]);
  if (!Array.isArray(plan.workflows) || !Array.isArray(plan.local_skill_candidates) || !Array.isArray(plan.validation)) errors.push("workflows, local_skill_candidates, and validation must be arrays");
  if (requireAccepted && placeholder(JSON.stringify(plan))) errors.push("accepted plan contains unresolved placeholder text");
  return errors;
}

export function loadPlan(file) { return JSON.parse(fs.readFileSync(file, "utf8")); }
