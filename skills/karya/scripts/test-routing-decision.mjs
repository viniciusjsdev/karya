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

process.stdout.write("Karya routing decision tests passed\n");
