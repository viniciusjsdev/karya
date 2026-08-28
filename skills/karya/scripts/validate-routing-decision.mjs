import fs from "node:fs";
import { pathToFileURL } from "node:url";

const intents = new Set([
  "direct_execution",
  "product_work",
  "market_research",
  "commercial_work",
  "project_harness",
  "mixed",
  "unclear"
]);
const confidenceLevels = new Set(["low", "medium", "high"]);
const costPreferences = new Set(["unspecified", "economize_codex", "lowest_safe_cost", "codex_preferred"]);
const routeModes = new Set(["direct", "factory"]);
const factories = new Set(["MVP Factory", "Research Factory", "Marketing Factory", "Project Harness Factory"]);
const approvalStatuses = new Set(["pending", "approved", "rejected", "revised"]);
const runtimeStatuses = new Set(["advisory", "materialized"]);
const runtimePhases = new Set(["bootstrap_design", "resolved_implementation", "mechanical_change", "critical_risk_or_review"]);
const runtimeProfiles = Object.freeze({
  bootstrap_design: Object.freeze({ model: "gpt-5.6-sol", reasoning: Object.freeze(["high"]) }),
  resolved_implementation: Object.freeze({ model: "gpt-5.6-terra", reasoning: Object.freeze(["medium", "high"]) }),
  mechanical_change: Object.freeze({ model: "gpt-5.6-luna", reasoning: Object.freeze(["low"]) }),
  critical_risk_or_review: Object.freeze({ model: "gpt-5.6-sol", reasoning: Object.freeze(["high"]) })
});
export const factorySkills = Object.freeze({
  "MVP Factory": Object.freeze([
    "product-brief-architect",
    "karya-frontend-builder",
    "django-backend-service-architect",
    "karya-backend-router",
    "django-backend-code-executor",
    "karya-infra-orchestrator"
  ]),
  "Research Factory": Object.freeze([
    "market-research-architect",
    "karya-research-router",
    "app-market-intelligence-analyst",
    "manus-platform-researcher",
    "market-validation-harness"
  ]),
  "Marketing Factory": Object.freeze([
    "commercial-launch-architect",
    "marketing-creative-builder",
    "karya-commercial-router",
    "manus-commercial-operator",
    "commercial-validation-analyst"
  ]),
  "Project Harness Factory": Object.freeze([
    "project-harness-architect",
    "project-spec-architect",
    "project-skill-author",
    "codex-runtime-router",
    "karya-execution-router",
    "project-harness-auditor"
  ])
});
export const knownSkillNames = Object.freeze(Object.values(factorySkills).flat());
const knownSkills = new Set(knownSkillNames);

function skillBelongsToFactory(skill, factory) {
  return factorySkills[factory]?.includes(skill) === true;
}

function fail(message) {
  throw new Error(message);
}

function requireObject(value, name) {
  if (!value || typeof value !== "object" || Array.isArray(value)) fail(`${name} must be an object.`);
}

function requireString(value, name) {
  if (typeof value !== "string" || !value.trim()) fail(`${name} must be a non-empty string.`);
}

function requireStringArray(value, name, { minItems = 0 } = {}) {
  if (!Array.isArray(value) || value.length < minItems) fail(`${name} must contain at least ${minItems} item(s).`);
  value.forEach((item, index) => requireString(item, `${name}[${index}]`));
}

export function validateRoutingDecision(value) {
  requireObject(value, "decision");
  if (value.schema_version !== "1.2") fail("schema_version must be 1.2.");
  requireString(value.decision_id, "decision_id");
  requireString(value.request_summary, "request_summary");
  if (value.automatic_handoff !== false) fail("automatic_handoff must be false.");

  requireObject(value.classification, "classification");
  if (!intents.has(value.classification.primary_intent)) fail("classification.primary_intent is invalid.");
  requireString(value.classification.project_state, "classification.project_state");
  if (!costPreferences.has(value.classification.cost_preference)) fail("classification.cost_preference is invalid.");
  if (!confidenceLevels.has(value.classification.confidence)) fail("classification.confidence is invalid.");
  requireStringArray(value.classification.signals, "classification.signals");

  requireObject(value.recommended_route, "recommended_route");
  const route = value.recommended_route;
  if (!routeModes.has(route.mode)) fail("recommended_route.mode is invalid.");
  requireString(route.reason, "recommended_route.reason");
  requireStringArray(route.approved_scope, "recommended_route.approved_scope", { minItems: 1 });
  if (!Array.isArray(route.planned_skills)) fail("recommended_route.planned_skills must be an array.");

  if (route.mode === "direct") {
    if (route.factory !== null || route.entry_skill !== null || route.planned_skills.length !== 0) {
      fail("direct routes require null factory, null entry_skill, and no planned_skills.");
    }
  } else {
    if (!factories.has(route.factory)) fail("recommended_route.factory is invalid.");
    if (!knownSkills.has(route.entry_skill)) fail("recommended_route.entry_skill is unknown.");
    if (!skillBelongsToFactory(route.entry_skill, route.factory)) fail("recommended_route.entry_skill does not belong to the selected factory.");
    if (route.planned_skills.length === 0) fail("factory routes require at least one planned skill.");
    if (route.planned_skills[0]?.skill !== route.entry_skill) fail("the first planned skill must match entry_skill.");
  }

  const plannedNames = new Set();
  route.planned_skills.forEach((item, index) => {
    requireObject(item, `recommended_route.planned_skills[${index}]`);
    if (!knownSkills.has(item.skill)) fail(`planned skill is unknown: ${item.skill}`);
    if (!skillBelongsToFactory(item.skill, route.factory)) fail(`planned skill does not belong to the selected factory: ${item.skill}`);
    if (plannedNames.has(item.skill)) fail(`planned skill is duplicated: ${item.skill}`);
    plannedNames.add(item.skill);
    requireString(item.purpose, `recommended_route.planned_skills[${index}].purpose`);
    requireString(item.when, `recommended_route.planned_skills[${index}].when`);
  });

  requireObject(value.runtime_recommendation, "runtime_recommendation");
  const runtime = value.runtime_recommendation;
  if (!runtimeStatuses.has(runtime.status)) fail("runtime_recommendation.status is invalid.");
  if (!runtimePhases.has(runtime.phase)) fail("runtime_recommendation.phase is invalid.");
  const expectedRuntime = runtimeProfiles[runtime.phase];
  if (runtime.model !== expectedRuntime.model || !expectedRuntime.reasoning.includes(runtime.reasoning)) {
    fail(`runtime_recommendation must use ${expectedRuntime.model}/${expectedRuntime.reasoning.join("|")} for ${runtime.phase}.`);
  }
  requireString(runtime.rationale, "runtime_recommendation.rationale");
  if (runtime.downshift_condition !== null) requireString(runtime.downshift_condition, "runtime_recommendation.downshift_condition");
  requireObject(runtime.audit, "runtime_recommendation.audit");
  if (typeof runtime.audit.required !== "boolean") fail("runtime_recommendation.audit.required must be boolean.");
  if (runtime.audit.required) {
    requireString(runtime.audit.capability, "runtime_recommendation.audit.capability");
    requireString(runtime.audit.when, "runtime_recommendation.audit.when");
    if (runtime.audit.capability !== "project-harness-auditor") fail("required runtime audit must use project-harness-auditor.");
  } else if (runtime.audit.capability !== null || runtime.audit.when !== null) {
    fail("an optional runtime audit requires null capability and when.");
  }
  if (runtime.status === "materialized" && route.factory !== "Project Harness Factory") {
    fail("only Project Harness Factory may materialize a runtime recommendation.");
  }
  if (route.entry_skill === "project-harness-architect") {
    if (runtime.phase !== "bootstrap_design" || runtime.audit.required !== true) {
      fail("Project Harness bootstrap requires bootstrap_design runtime and an independent audit.");
    }
    if (!route.planned_skills.some((item) => item.skill === "project-harness-auditor")) {
      fail("Project Harness bootstrap must plan project-harness-auditor.");
    }
  }

  requireObject(value.economic_execution, "economic_execution");
  const economic = value.economic_execution;
  if (typeof economic.eligible !== "boolean") fail("economic_execution.eligible must be boolean.");
  requireString(economic.reason, "economic_execution.reason");
  if (!Array.isArray(economic.provider_options)) fail("economic_execution.provider_options must be an array.");
  economic.provider_options.forEach((option, index) => requireString(option, `economic_execution.provider_options[${index}]`));
  if (economic.requires_action_confirmation !== true) fail("economic execution must require action-time confirmation.");
  if (economic.fallback !== "codex") fail("economic execution fallback must be codex.");
  if (economic.assumptions !== "none") fail("economic execution must assume no provider, credit, subscription, or authorization.");
  if (economic.eligible) {
    if (economic.status !== "advisory" || economic.recommended_executor !== "opencode") fail("eligible economic execution must be an advisory OpenCode recommendation.");
    if (economic.provider_options.length === 0) fail("eligible economic execution must name at least one consultative provider option.");
    if (!["resolved_implementation", "mechanical_change"].includes(runtime.phase)) fail("OpenCode is eligible only for resolved or mechanical implementation.");
    if (!runtime.audit.required || runtime.audit.capability !== "project-harness-auditor") fail("OpenCode eligibility requires independent Project Harness audit.");
  } else if (economic.status !== "not_applicable" || economic.recommended_executor !== null || economic.provider_options.length !== 0) {
    fail("ineligible economic execution must be not_applicable with no executor or provider options.");
  }
  if (route.entry_skill === "karya-execution-router" && !economic.eligible) fail("karya-execution-router requires eligible economic execution.");

  requireObject(value.coordination, "coordination");
  if (value.coordination.coordinator !== "karya") fail("coordination.coordinator must be karya.");
  if (value.coordination.user_facing_interface !== "karya") fail("coordination.user_facing_interface must be karya.");
  if (value.coordination.execution_mode !== "same_thread_by_default") fail("coordination.execution_mode must be same_thread_by_default.");
  if (value.coordination.active_skill !== null && !knownSkills.has(value.coordination.active_skill)) {
    fail("coordination.active_skill is unknown.");
  }

  if (!Array.isArray(value.supporting_routes)) fail("supporting_routes must be an array.");
  value.supporting_routes.forEach((item, index) => {
    requireObject(item, `supporting_routes[${index}]`);
    if (!factories.has(item.factory)) fail(`supporting_routes[${index}].factory is invalid.`);
    if (!knownSkills.has(item.entry_skill)) fail(`supporting_routes[${index}].entry_skill is unknown.`);
    if (!skillBelongsToFactory(item.entry_skill, item.factory)) fail(`supporting_routes[${index}].entry_skill does not belong to its factory.`);
    requireString(item.reason, `supporting_routes[${index}].reason`);
    requireString(item.when, `supporting_routes[${index}].when`);
    if (item.requires_additional_approval !== true) fail(`supporting_routes[${index}] must require additional approval.`);
    if (item.automatic_handoff !== false) fail(`supporting_routes[${index}].automatic_handoff must be false.`);
  });

  if (value.not_recommended !== undefined) requireStringArray(value.not_recommended, "not_recommended");
  requireStringArray(value.open_questions, "open_questions");

  requireObject(value.approval, "approval");
  if (value.approval.required !== true) fail("approval.required must be true.");
  if (!approvalStatuses.has(value.approval.status)) fail("approval.status is invalid.");
  requireString(value.approval.question, "approval.question");

  return true;
}

export function validateRoutingDecisionFile(filePath) {
  if (!filePath) fail("Usage: node validate-routing-decision.mjs <decision.json>");
  const value = JSON.parse(fs.readFileSync(filePath, "utf8"));
  validateRoutingDecision(value);
  return value;
}

if (process.argv[1] && pathToFileURL(process.argv[1]).href === import.meta.url) {
  validateRoutingDecisionFile(process.argv[2]);
  process.stdout.write("Karya routing decision is valid\n");
}
