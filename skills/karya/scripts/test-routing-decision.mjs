import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { knownSkillNames, validateRoutingDecision } from "./validate-routing-decision.mjs";

const currentDirectory = path.dirname(fileURLToPath(import.meta.url));
const validFactoryDecision = JSON.parse(
  fs.readFileSync(path.resolve(currentDirectory, "../assets/routing-decision.template.json"), "utf8")
);

const skillsRoot = path.resolve(currentDirectory, "../..");
const actualSpecialistSkills = fs
  .readdirSync(skillsRoot, { withFileTypes: true })
  .filter((entry) => entry.isDirectory() && entry.name !== "karya" && fs.existsSync(path.join(skillsRoot, entry.name, "SKILL.md")))
  .map((entry) => entry.name)
  .sort();
assert.deepEqual(actualSpecialistSkills, [...knownSkillNames].sort(), "Karya's routing map must cover every specialist skill exactly once.");

assert.equal(validateRoutingDecision(validFactoryDecision), true);

const directDecision = structuredClone(validFactoryDecision);
directDecision.classification.primary_intent = "direct_execution";
directDecision.recommended_route = {
  mode: "direct",
  factory: null,
  entry_skill: null,
  reason: "The requested change is bounded and already specified.",
  approved_scope: ["Apply the focused change and run its tests."],
  planned_skills: []
};
directDecision.supporting_routes = [];
directDecision.runtime_recommendation = {
  status: "advisory",
  phase: "mechanical_change",
  model: "gpt-5.6-luna",
  reasoning: "low",
  rationale: "The change is bounded, resolved, and mechanical.",
  downshift_condition: null,
  audit: { required: false, capability: null, when: null }
};
assert.equal(validateRoutingDecision(directDecision), true);

function expectFailure(mutator, pattern) {
  const candidate = structuredClone(validFactoryDecision);
  mutator(candidate);
  assert.throws(() => validateRoutingDecision(candidate), pattern);
}

expectFailure((value) => {
  value.automatic_handoff = true;
}, /automatic_handoff must be false/);

expectFailure((value) => {
  value.approval.required = false;
}, /approval.required must be true/);

expectFailure((value) => {
  value.recommended_route.entry_skill = "unknown-skill";
}, /entry_skill is unknown/);

expectFailure((value) => {
  value.recommended_route.planned_skills[0].skill = "karya-frontend-builder";
}, /first planned skill must match entry_skill/);

expectFailure((value) => {
  value.recommended_route.factory = "Research Factory";
}, /entry_skill does not belong to the selected factory/);

expectFailure((value) => {
  value.supporting_routes[0].requires_additional_approval = false;
}, /must require additional approval/);

expectFailure((value) => {
  value.coordination.user_facing_interface = "specialist";
}, /user_facing_interface must be karya/);

expectFailure((value) => {
  value.runtime_recommendation.model = "gpt-5.6-luna";
}, /must use gpt-5.6-sol\/high for bootstrap_design/);

const complexImplementation = structuredClone(validFactoryDecision);
complexImplementation.runtime_recommendation = {
  status: "advisory",
  phase: "resolved_implementation",
  model: "gpt-5.6-terra",
  reasoning: "high",
  rationale: "The Spec is resolved, but the implementation has unusual technical complexity.",
  downshift_condition: "Return to Terra/medium after the complex implementation boundary is complete.",
  audit: { required: false, capability: null, when: null }
};
assert.equal(validateRoutingDecision(complexImplementation), true);

expectFailure((value) => {
  value.runtime_recommendation.status = "materialized";
}, /only Project Harness Factory may materialize/);

const harnessBootstrap = structuredClone(validFactoryDecision);
harnessBootstrap.classification.primary_intent = "project_harness";
harnessBootstrap.recommended_route = {
  mode: "factory",
  factory: "Project Harness Factory",
  entry_skill: "project-harness-architect",
  reason: "The project needs durable AI operating structure.",
  approved_scope: ["Audit and bootstrap the Harness, then independently audit it."],
  planned_skills: [
    { skill: "project-harness-architect", purpose: "Audit and materialize the minimum Harness.", when: "After approval." },
    { skill: "project-harness-auditor", purpose: "Independently reconcile the resulting Harness.", when: "After materialization." }
  ]
};
harnessBootstrap.runtime_recommendation = {
  status: "advisory",
  phase: "bootstrap_design",
  model: "gpt-5.6-sol",
  reasoning: "high",
  rationale: "Bootstrap requires architecture and source-of-truth decisions.",
  downshift_condition: "Use Terra/medium after a READY Spec resolves the first implementation.",
  audit: { required: true, capability: "project-harness-auditor", when: "After bootstrap materialization." }
};
harnessBootstrap.supporting_routes = [];
assert.equal(validateRoutingDecision(harnessBootstrap), true);

const economicExecution = structuredClone(validFactoryDecision);
economicExecution.classification.primary_intent = "project_harness";
economicExecution.classification.project_state = "READY non-Django implementation contract";
economicExecution.classification.cost_preference = "economize_codex";
economicExecution.recommended_route = {
  mode: "factory",
  factory: "Project Harness Factory",
  entry_skill: "karya-execution-router",
  reason: "The user wants to economize Codex during a resolved implementation.",
  approved_scope: ["Route the approved implementation after a separate exact action confirmation."],
  planned_skills: [
    { skill: "karya-execution-router", purpose: "Check eligibility and route optional OpenCode execution.", when: "After exact action-time confirmation." },
    { skill: "project-harness-auditor", purpose: "Independently reconcile the result.", when: "After executor completion." }
  ]
};
economicExecution.runtime_recommendation = {
  status: "advisory",
  phase: "resolved_implementation",
  model: "gpt-5.6-terra",
  reasoning: "medium",
  rationale: "The implementation contract is resolved and Codex remains the fallback.",
  downshift_condition: "Use a mechanical model only after the work becomes repetitive and low risk.",
  audit: { required: true, capability: "project-harness-auditor", when: "After OpenCode returns one final result." }
};
economicExecution.economic_execution = {
  eligible: true,
  status: "advisory",
  recommended_executor: "opencode",
  reason: "A READY bounded implementation can use an economic external executor.",
  provider_options: ["OpenCode Go", "OpenCode Zen", "approved BYOK provider", "approved local model"],
  requires_action_confirmation: true,
  fallback: "codex",
  assumptions: "none"
};
economicExecution.supporting_routes = [];
assert.equal(validateRoutingDecision(economicExecution), true);

expectFailure((value) => {
  value.economic_execution.eligible = true;
  value.economic_execution.status = "advisory";
  value.economic_execution.recommended_executor = "opencode";
  value.economic_execution.provider_options = ["OpenCode Go"];
}, /resolved or mechanical implementation/);

const missingActionConfirmation = structuredClone(economicExecution);
missingActionConfirmation.economic_execution.requires_action_confirmation = false;
assert.throws(() => validateRoutingDecision(missingActionConfirmation), /action-time confirmation/);

expectFailure((value) => {
  value.classification.primary_intent = "project_harness";
  value.recommended_route = structuredClone(harnessBootstrap.recommended_route);
  value.runtime_recommendation.audit = { required: false, capability: null, when: null };
}, /Project Harness bootstrap requires/);

process.stdout.write("Karya routing decision tests passed\n");
