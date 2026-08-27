import fs from "node:fs";
import path from "node:path";

export const STATUSES = new Set(["draft", "design", "ready", "in_progress", "needs_design", "implemented", "review", "done"]);
export const CLASSIFICATIONS = new Set(["design", "normal_implementation", "mechanical", "critical_review"]);
export const MODELS = new Set(["gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna"]);
export const REASONING = new Set(["low", "medium", "high", "xhigh", "max"]);
const REQUIRED_SECTIONS = [
  "Goal", "Context", "Scope", "Non-scope", "Requirements", "Business or domain rules",
  "Decisions already made", "Constraints", "Acceptance criteria", "Affected areas", "References",
  "Skills", "Validation requirements", "Review requirements", "Execution and runtime",
];

export function parseFrontmatter(text) {
  const match = text.replace(/^\uFEFF/, "").match(/^---\s*\r?\n([\s\S]*?)\r?\n---(?:\s*\r?\n|$)/);
  if (!match) return {};
  const result = {};
  for (const line of match[1].split(/\r?\n/)) {
    const item = line.match(/^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*?)\s*$/);
    if (item) result[item[1]] = item[2].replace(/^("|')|("|')$/g, "");
  }
  return result;
}

function isObject(value) { return Boolean(value) && typeof value === "object" && !Array.isArray(value); }
function requireKeys(errors, value, label, keys) {
  if (!isObject(value)) { errors.push(`${label} must be an object`); return false; }
  for (const key of keys) if (!Object.hasOwn(value, key)) errors.push(`${label} is missing ${key}`);
  return true;
}
function hasPlaceholder(value) { return /(?:\bTBD\b|\bTODO\b|replace[_ -]?me|\{\{|<[^>]+>)/i.test(String(value)); }
function unsafeCommand(command) { return /[;&|><`\r\n]|\$\(/.test(command); }

export function validateRuntimePolicy(policy) {
  const errors = [];
  if (!requireKeys(errors, policy, "runtime policy", ["policy_version", "models", "reasoning_levels", "defaults", "escalations"])) return errors;
  for (const classification of CLASSIFICATIONS) {
    const item = policy.defaults?.[classification];
    if (!item) errors.push(`runtime policy is missing default ${classification}`);
    else if (!MODELS.has(item.model) || !REASONING.has(item.reasoning) || !item.role) errors.push(`runtime policy default ${classification} is invalid`);
  }
  return errors;
}

export function validateExecutionManifest(manifest, policy) {
  const errors = [];
  const rootKeys = ["schema_version", "spec_id", "contract_version", "status", "automatic_handoff", "execution", "skills", "references", "validation", "review", "escalation", "completion"];
  if (!requireKeys(errors, manifest, "execution manifest", rootKeys)) return errors;
  if (manifest.schema_version !== "1.0") errors.push("schema_version must be 1.0");
  if (!/^SPEC-[0-9]{3,}$/.test(manifest.spec_id ?? "")) errors.push("spec_id must match SPEC-NNN");
  if (!Number.isInteger(manifest.contract_version) || manifest.contract_version < 1) errors.push("contract_version must be a positive integer");
  if (!STATUSES.has(manifest.status)) errors.push("status is invalid");
  if (manifest.automatic_handoff !== false) errors.push("automatic_handoff must be false");

  const execution = manifest.execution;
  if (requireKeys(errors, execution, "execution", ["classification", "role", "model", "reasoning", "routing_rationale", "runtime_override", "working_directory", "sandbox_mode", "approval_policy", "thread", "handoff_prompt"])) {
    if (!CLASSIFICATIONS.has(execution.classification)) errors.push("execution.classification is invalid");
    if (!MODELS.has(execution.model)) errors.push("execution.model is invalid");
    if (!REASONING.has(execution.reasoning)) errors.push("execution.reasoning is invalid");
    if (!["architect", "developer", "worker", "reviewer"].includes(execution.role)) errors.push("execution.role is invalid");
    if (String(execution.routing_rationale ?? "").length < 20) errors.push("execution.routing_rationale is too short");
    if (String(execution.handoff_prompt ?? "").length < 40) errors.push("execution.handoff_prompt is too short");
    if (!["read-only", "workspace-write", "danger-full-access"].includes(execution.sandbox_mode)) errors.push("execution.sandbox_mode is invalid");
    if (!["never", "on-request", "on-failure", "untrusted"].includes(execution.approval_policy)) errors.push("execution.approval_policy is invalid");
    if (requireKeys(errors, execution.thread, "execution.thread", ["mode", "purpose", "thread_id"])) {
      if (!["new", "resume"].includes(execution.thread.mode)) errors.push("execution.thread.mode is invalid");
      if (!["design", "implementation", "worker", "review"].includes(execution.thread.purpose)) errors.push("execution.thread.purpose is invalid");
      if (execution.thread.mode === "resume" && !execution.thread.thread_id) errors.push("resume mode requires execution.thread.thread_id");
      if (execution.thread.mode === "new" && execution.thread.thread_id !== null) errors.push("new mode requires a null execution.thread.thread_id");
    }
    const defaults = policy?.defaults?.[execution.classification];
    if (defaults) {
      const differs = defaults.model !== execution.model || defaults.reasoning !== execution.reasoning || defaults.role !== execution.role;
      if (differs && (!isObject(execution.runtime_override) || String(execution.runtime_override.reason ?? "").length < 20)) errors.push("runtime differing from policy defaults requires runtime_override.reason");
      if (differs && isObject(execution.runtime_override) && (execution.runtime_override.default_model !== defaults.model || execution.runtime_override.default_reasoning !== defaults.reasoning)) errors.push("runtime_override defaults do not match the runtime policy");
      if (!differs && execution.runtime_override !== null) errors.push("runtime_override must be null when policy defaults are used");
    }
  }

  if (!Array.isArray(manifest.skills)) errors.push("skills must be an array");
  else for (const [index, skill] of manifest.skills.entries()) {
    if (!requireKeys(errors, skill, `skills[${index}]`, ["name", "source", "path", "required"])) continue;
    if (!/^[a-z0-9-]+$/.test(skill.name ?? "")) errors.push(`skills[${index}].name is invalid`);
    if (!["project", "installed"].includes(skill.source)) errors.push(`skills[${index}].source is invalid`);
    if (skill.source === "project" && !skill.path) errors.push(`skills[${index}] project source requires path`);
    if (skill.source === "installed" && skill.path !== null) errors.push(`skills[${index}] installed source requires null path`);
  }
  if (!Array.isArray(manifest.references)) errors.push("references must be an array");
  else for (const [index, ref] of manifest.references.entries()) requireKeys(errors, ref, `references[${index}]`, ["path", "purpose", "required"]);
  if (!Array.isArray(manifest.validation) || manifest.validation.length === 0) errors.push("validation must contain at least one item");
  else {
    const ids = new Set();
    for (const [index, item] of manifest.validation.entries()) {
      if (!requireKeys(errors, item, `validation[${index}]`, ["id", "kind", "command", "required"])) continue;
      if (!/^VAL-[0-9]{3}$/.test(item.id ?? "")) errors.push(`validation[${index}].id is invalid`);
      if (ids.has(item.id)) errors.push(`duplicate validation id ${item.id}`); else ids.add(item.id);
      if (unsafeCommand(item.command)) errors.push(`validation ${item.id} contains shell control operators`);
    }
  }
  if (requireKeys(errors, manifest.review, "review", ["required", "independence", "model", "reasoning", "rationale"])) {
    if (manifest.review.required && (!MODELS.has(manifest.review.model) || !REASONING.has(manifest.review.reasoning))) errors.push("required review needs a supported model and reasoning");
    if (!manifest.review.required && (manifest.review.model !== null || manifest.review.reasoning !== null)) errors.push("non-required review must use null model and reasoning");
    if (execution?.classification === "critical_review" && (!manifest.review.required || manifest.review.model !== "gpt-5.6-sol" || manifest.review.reasoning !== "high" || manifest.review.independence !== "independent")) errors.push("critical_review requires independent Sol/high review");
  }
  if (requireKeys(errors, manifest.escalation, "escalation", ["policy_version", "allowed"]) && manifest.escalation.policy_version !== policy?.policy_version) errors.push("escalation.policy_version does not match the runtime policy");
  requireKeys(errors, manifest.completion, "completion", ["schema_path", "output_path"]);
  if (hasPlaceholder(JSON.stringify(manifest))) errors.push("execution manifest contains unresolved placeholder text");
  return errors;
}

function sectionBody(markdown, heading) {
  const escaped = heading.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const match = markdown.match(new RegExp(`^## ${escaped}\\s*\\r?\\n([\\s\\S]*?)(?=^## |\\s*$)`, "im"));
  return match?.[1]?.trim() ?? "";
}

export function validateSpecPair(markdown, manifest, policy, { projectRoot = null, skillsRoot = null, requireReady = false } = {}) {
  const errors = [...validateRuntimePolicy(policy), ...validateExecutionManifest(manifest, policy)];
  const fm = parseFrontmatter(markdown);
  for (const key of ["id", "title", "status", "contract_version"]) if (!fm[key]) errors.push(`SPEC.md frontmatter is missing ${key}`);
  if (fm.id && fm.id !== manifest.spec_id) errors.push("Spec ID differs between Markdown and manifest");
  if (fm.status && fm.status !== manifest.status) errors.push("Spec status differs between Markdown and manifest");
  if (fm.contract_version && Number(fm.contract_version) !== manifest.contract_version) errors.push("contract_version differs between Markdown and manifest");
  if (requireReady && manifest.status !== "ready") errors.push("--require-ready requires status ready");
  if (manifest.status === "ready" || manifest.status === "review" || requireReady) {
    for (const heading of REQUIRED_SECTIONS) {
      const body = sectionBody(markdown, heading);
      if (!body) errors.push(`READY Spec section is empty or missing: ${heading}`);
      else if (hasPlaceholder(body)) errors.push(`READY Spec section contains placeholder text: ${heading}`);
    }
    if (!/\bAC-[0-9]{3}\b/.test(sectionBody(markdown, "Acceptance criteria"))) errors.push("READY Spec needs at least one AC-NNN acceptance criterion");
    if (hasPlaceholder(markdown)) errors.push("READY Spec contains unresolved placeholder text");
    if (projectRoot) {
      for (const ref of manifest.references ?? []) if (ref.required && !fs.existsSync(path.resolve(projectRoot, ref.path))) errors.push(`required reference does not exist: ${ref.path}`);
      for (const skill of manifest.skills ?? []) {
        if (!skill.required) continue;
        const resolved = skill.source === "project" ? path.resolve(projectRoot, skill.path) : skillsRoot ? path.resolve(skillsRoot, skill.name, "SKILL.md") : null;
        if (resolved && !fs.existsSync(resolved)) errors.push(`required skill does not exist: ${skill.name}`);
      }
    }
  }
  return errors;
}

export function loadJson(file) { return JSON.parse(fs.readFileSync(file, "utf8")); }
