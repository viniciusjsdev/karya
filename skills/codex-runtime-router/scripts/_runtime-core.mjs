import fs from "node:fs";
import path from "node:path";
import { validateSpecPair } from "../../project-spec-architect/scripts/_spec-core.mjs";

function isObject(value) { return Boolean(value) && typeof value === "object" && !Array.isArray(value); }
function requireKeys(errors, value, label, keys) {
  if (!isObject(value)) { errors.push(`${label} must be an object`); return false; }
  for (const key of keys) if (!Object.hasOwn(value, key)) errors.push(`${label} is missing ${key}`);
  return true;
}

export function resolveInside(root, value, label) {
  const resolvedRoot = path.resolve(root);
  const resolved = path.resolve(resolvedRoot, value);
  const relative = path.relative(resolvedRoot, resolved);
  if (relative.startsWith("..") || path.isAbsolute(relative)) throw new Error(`${label} must remain inside project root: ${value}`);
  return resolved;
}

export function acceptanceIds(markdown) {
  return [...new Set([...markdown.matchAll(/\bAC-[0-9]{3}\b/g)].map((match) => match[0]))];
}

export function validateCompletion(completion, manifest, markdown, threadId, { projectRoot = null } = {}) {
  const errors = [];
  const keys = ["spec_id", "contract_version", "status", "thread_id", "runtime", "changed_files", "artifacts", "acceptance_evidence", "validation_evidence", "deviations", "unresolved_items", "needs_design", "usage"];
  if (!requireKeys(errors, completion, "completion", keys)) return errors;
  for (const key of Object.keys(completion)) if (!keys.includes(key)) errors.push(`completion has unsupported property ${key}`);
  if (completion.spec_id !== manifest.spec_id) errors.push("completion spec_id does not match manifest");
  if (completion.contract_version !== manifest.contract_version) errors.push("completion contract_version does not match manifest");
  if (!["completed", "needs_design", "blocked", "failed"].includes(completion.status)) errors.push("completion status is invalid");
  if (completion.thread_id !== threadId) errors.push("completion thread_id does not match actual SDK thread");
  if (requireKeys(errors, completion.runtime, "completion.runtime", ["classification", "model", "reasoning"])) {
    for (const key of ["classification", "model", "reasoning"]) if (completion.runtime[key] !== manifest.execution[key]) errors.push(`completion runtime ${key} does not match manifest`);
  }
  for (const key of ["changed_files", "artifacts", "deviations", "unresolved_items"]) if (!Array.isArray(completion[key])) errors.push(`completion ${key} must be an array`);
  if (projectRoot) {
    for (const key of ["changed_files", "artifacts"]) {
      if (!Array.isArray(completion[key])) continue;
      for (const value of completion[key]) {
        try {
          const resolved = resolveInside(projectRoot, value, `completion ${key} path`);
          if (!fs.existsSync(resolved)) errors.push(`completion ${key} path does not exist: ${value}`);
          else if (key === "changed_files" && !fs.statSync(resolved).isFile()) errors.push(`completion changed_files path is not a file: ${value}`);
        } catch (error) { errors.push(error.message); }
      }
    }
  }
  if (!isObject(completion.acceptance_evidence)) errors.push("acceptance_evidence must be an object");
  if (!isObject(completion.validation_evidence)) errors.push("validation_evidence must be an object");
  if (completion.status === "completed") {
    if (completion.needs_design !== null) errors.push("completed evidence requires needs_design null");
    for (const id of acceptanceIds(markdown)) {
      const evidence = completion.acceptance_evidence?.[id];
      if (!evidence || evidence.result !== "passed" || !Array.isArray(evidence.evidence) || evidence.evidence.length === 0) errors.push(`completed evidence is missing passing acceptance evidence for ${id}`);
    }
    for (const validation of manifest.validation.filter((item) => item.required)) {
      const evidence = completion.validation_evidence?.[validation.id];
      if (!evidence) errors.push(`completed evidence is missing ${validation.id}`);
      else {
        if (evidence.command !== validation.command) errors.push(`${validation.id} command differs from manifest`);
        if (evidence.result !== "passed" || evidence.exit_code !== 0) errors.push(`${validation.id} did not pass with exit code zero`);
      }
    }
  }
  if (completion.status === "needs_design") {
    if (!requireKeys(errors, completion.needs_design, "needs_design", ["question", "reason", "impact", "affected_areas", "alternatives"])) errors.push("needs_design status requires a structured needs_design payload");
  } else if (completion.status !== "completed" && completion.needs_design !== null) {
    errors.push(`${completion.status} evidence requires needs_design null`);
  }
  return errors;
}

export function validateReviewEvidence(review, manifest, threadId) {
  const errors = [];
  const keys = ["spec_id", "contract_version", "status", "thread_id", "runtime", "review_input", "findings", "evidence", "usage"];
  if (!requireKeys(errors, review, "review evidence", keys)) return errors;
  for (const key of Object.keys(review)) if (!keys.includes(key)) errors.push(`review evidence has unsupported property ${key}`);
  if (review.spec_id !== manifest.spec_id) errors.push("review evidence spec_id does not match manifest");
  if (review.contract_version !== manifest.contract_version) errors.push("review evidence contract_version does not match manifest");
  if (!["approved", "changes_requested", "blocked", "failed"].includes(review.status)) errors.push("review evidence status is invalid");
  if (review.thread_id !== threadId) errors.push("review evidence thread_id does not match actual SDK thread");
  if (requireKeys(errors, review.runtime, "review evidence runtime", ["classification", "model", "reasoning"])) {
    for (const key of ["classification", "model", "reasoning"]) if (review.runtime[key] !== manifest.execution[key]) errors.push(`review evidence runtime ${key} does not match manifest execution`);
  }
  for (const key of ["review_input", "findings", "evidence"]) if (!Array.isArray(review[key])) errors.push(`review evidence ${key} must be an array`);
  if (Array.isArray(review.review_input) && (!review.review_input.some((item) => /completion/i.test(item)) || !review.review_input.some((item) => /diff|artifact/i.test(item)))) errors.push("review evidence input must include completion evidence and diff/artifacts");
  if (review.status === "approved" && Array.isArray(review.findings) && review.findings.length > 0) errors.push("approved review evidence must have no findings");
  return errors;
}

export function buildHandoffPrompt(manifest, specRelative, manifestRelative) {
  const references = manifest.references.map((item) => `- ${item.path}: ${item.purpose}`).join("\n") || "- No additional declared references.";
  const skills = manifest.skills.map((item) => `- ${item.name} (${item.source}${item.path ? `: ${item.path}` : ""})`).join("\n") || "- No specialized skill is required.";
  return [
    `Execute ${manifest.spec_id}.`, "", "Source of truth:", `- ${specRelative}`, `- ${manifestRelative}`, "- AGENTS.md", "", "Declared references:", references, "", "Applicable skills:", skills, "", manifest.execution.handoff_prompt, "", "Load only these durable inputs and directly relevant repository files. Do not use design-conversation history or create subagents by default.", "Return JSON conforming to the supplied completion schema. Set thread_id and usage to null; the router records actual SDK values.",
  ].join("\n");
}

export function validatePreflight({ markdown, manifest, policy, projectRoot, skillsRoot, state }) {
  const reviewRun = manifest.execution?.thread?.purpose === "review";
  const errors = validateSpecPair(markdown, manifest, policy, { projectRoot, skillsRoot, requireReady: !reviewRun });
  if (reviewRun && manifest.status !== "review") errors.push("review thread purpose requires Spec status review");
  if (!reviewRun && manifest.status !== "ready") errors.push("implementation or worker execution requires Spec status ready");
  const slot = reviewRun ? "review_thread_id" : "implementation_thread_id";
  const recorded = state.specs?.[manifest.spec_id]?.[slot] ?? null;
  if (manifest.execution?.thread?.mode === "new" && recorded) errors.push(`new thread rejected because ${slot} is already recorded; use resume`);
  if (manifest.execution?.thread?.mode === "resume" && recorded && recorded !== manifest.execution.thread.thread_id) errors.push(`resume thread_id does not match recorded ${slot}`);
  return errors;
}

export function readState(file) {
  if (!fs.existsSync(file)) return { schema_version: "1.0", specs: {} };
  const state = JSON.parse(fs.readFileSync(file, "utf8"));
  if (state.schema_version !== "1.0" || !isObject(state.specs)) throw new Error("thread state is invalid");
  return state;
}

export function updateState(state, manifest, threadId, status) {
  const current = state.specs[manifest.spec_id] ?? { contract_version: manifest.contract_version, implementation_thread_id: null, review_thread_id: null, last_status: status, updated_at: new Date().toISOString() };
  const slot = manifest.execution.thread.purpose === "review" ? "review_thread_id" : "implementation_thread_id";
  state.specs[manifest.spec_id] = { ...current, contract_version: manifest.contract_version, [slot]: threadId, last_status: status, updated_at: new Date().toISOString() };
  return state;
}

export function writeJsonAtomic(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const temp = `${file}.${process.pid}.tmp`;
  fs.writeFileSync(temp, `${JSON.stringify(value, null, 2)}\n`, "utf8");
  fs.renameSync(temp, file);
}
