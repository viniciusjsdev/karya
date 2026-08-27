#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { validateSpecPair } from "../../project-spec-architect/scripts/_spec-core.mjs";
import { validateCompletion } from "../../codex-runtime-router/scripts/_runtime-core.mjs";

const args = process.argv.slice(2);
const option = (name) => { const index = args.indexOf(name); return index >= 0 ? args[index + 1] : null; };
const rootArg = option("--project-root");
if (!rootArg) {
  process.stderr.write("Usage: node audit-project-harness.mjs --project-root <root> [--skills-root <installed-skills>]\n");
  process.exit(2);
}
const root = path.resolve(rootArg);
const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const fallbackPolicy = path.resolve(scriptDir, "../../project-spec-architect/assets/runtime-policy.json");
const projectPolicy = path.join(root, ".codex", "references", "runtime-policy.json");
const skillsRoot = option("--skills-root") ?? (process.env.CODEX_HOME ? path.join(process.env.CODEX_HOME, "skills") : null);
const findings = [];
let sequence = 0;
function add(severity, category, message, evidence = []) {
  sequence += 1;
  findings.push({ id: `HARNESS-${String(sequence).padStart(3, "0")}`, severity, category, message, evidence });
}
function walk(directory, predicate, output = []) {
  if (!fs.existsSync(directory)) return output;
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    if ([".git", "node_modules", ".venv", "venv", "__pycache__"].includes(entry.name)) continue;
    const target = path.join(directory, entry.name);
    if (entry.isDirectory()) walk(target, predicate, output); else if (entry.isFile() && predicate(target)) output.push(target);
  }
  return output;
}
function rel(file) { return path.relative(root, file).replaceAll("\\", "/"); }

if (!fs.existsSync(path.join(root, "AGENTS.md"))) add("high", "agents", "AGENTS.md is missing.", ["AGENTS.md"]);
if (!fs.existsSync(path.join(root, ".codex", "references", "project-harness.md"))) add("medium", "navigation", "Project Harness navigation reference is missing.", [".codex/references/project-harness.md"]);
if (!fs.existsSync(projectPolicy)) add("medium", "runtime", "Project runtime policy copy is missing; audit used the Factory fallback.", [".codex/references/runtime-policy.json"]);
let policy;
try { policy = JSON.parse(fs.readFileSync(fs.existsSync(projectPolicy) ? projectPolicy : fallbackPolicy, "utf8")); }
catch (error) { add("high", "runtime", `Runtime policy is invalid JSON: ${error.message}`, [rel(projectPolicy)]); policy = JSON.parse(fs.readFileSync(fallbackPolicy, "utf8")); }
const gitignore = path.join(root, ".gitignore");
if (fs.existsSync(path.join(root, ".codex", "runtime")) && (!fs.existsSync(gitignore) || !fs.readFileSync(gitignore, "utf8").split(/\r?\n/).includes(".codex/runtime/"))) add("medium", "runtime_state", "Temporary .codex/runtime state is not ignored by version control.", [".codex/runtime/", ".gitignore"]);

const manifests = walk(root, (file) => file.endsWith(".execution.json"));
for (const manifestPath of manifests) {
  const directory = path.dirname(manifestPath);
  const specPath = path.join(directory, "SPEC.md");
  if (!fs.existsSync(specPath)) { add("high", "spec", "Execution manifest has no sibling SPEC.md.", [rel(manifestPath)]); continue; }
  try {
    const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
    const markdown = fs.readFileSync(specPath, "utf8");
    const errors = validateSpecPair(markdown, manifest, policy, { projectRoot: root, skillsRoot, requireReady: manifest.status === "ready" });
    for (const error of errors) add(manifest.status === "ready" ? "high" : "medium", "spec", error, [rel(specPath), rel(manifestPath)]);
    if (["implemented", "review", "done"].includes(manifest.status)) {
      const completionPath = path.resolve(root, manifest.completion?.output_path ?? "");
      if (!fs.existsSync(completionPath)) add("high", "completion", `${manifest.status} Spec has no declared completion evidence.`, [rel(manifestPath), rel(completionPath)]);
      else {
        const completion = JSON.parse(fs.readFileSync(completionPath, "utf8"));
        const completionErrors = validateCompletion(completion, manifest, markdown, completion.thread_id, { projectRoot: root });
        for (const error of completionErrors) add("high", "completion", error, [rel(completionPath)]);
      }
    }
    if (manifest.status === "done" && manifest.review?.required) {
      const reviewPath = path.join(directory, "evidence", "review.json");
      if (!fs.existsSync(reviewPath)) add("high", "review", "DONE Spec requires the declared independent review evidence.", [rel(manifestPath), rel(reviewPath)]);
      else {
        const review = JSON.parse(fs.readFileSync(reviewPath, "utf8"));
        if (review.spec_id !== manifest.spec_id || review.contract_version !== manifest.contract_version) add("high", "review", "Review evidence does not match the Spec identity/version.", [rel(reviewPath)]);
        if (!review.thread_id) add("high", "review", "Review evidence has no thread ID.", [rel(reviewPath)]);
        if (review.runtime?.model !== manifest.review.model || review.runtime?.reasoning !== manifest.review.reasoning) add("high", "review", "Review evidence runtime differs from the manifest review policy.", [rel(reviewPath)]);
        if (review.status !== "approved") add("high", "review", "DONE Spec does not have an approved review result.", [rel(reviewPath)]);
        if (!Array.isArray(review.review_input) || !review.review_input.some((item) => /completion/i.test(item)) || !review.review_input.some((item) => /diff|artifact/i.test(item))) add("medium", "review", "Independent review input must include completion evidence and diff/artifacts.", [rel(reviewPath)]);
      }
    }
  } catch (error) { add("high", "spec", `Unable to parse or audit Spec: ${error.message}`, [rel(specPath), rel(manifestPath)]); }
}

const localSkillsRoot = path.join(root, ".agents", "skills");
const localSkillDirs = fs.existsSync(localSkillsRoot) ? fs.readdirSync(localSkillsRoot, { withFileTypes: true }).filter((entry) => entry.isDirectory()).map((entry) => path.join(localSkillsRoot, entry.name)) : [];
const seen = new Set();
for (const directory of localSkillDirs) {
  const name = path.basename(directory);
  if (seen.has(name)) add("medium", "skill", `Duplicate local skill name ${name}.`, [rel(directory)]); else seen.add(name);
  const skillPath = path.join(directory, "SKILL.md");
  if (!fs.existsSync(skillPath)) add("high", "skill", `Local skill ${name} has no SKILL.md.`, [rel(directory)]);
  else {
    const text = fs.readFileSync(skillPath, "utf8");
    if (/\b(?:TBD|TODO|replace[_ -]?me)\b/i.test(text)) add("medium", "skill", `Local skill ${name} contains unresolved placeholder text.`, [rel(skillPath)]);
    if (!/\bUse when\b/i.test(text) || !/\bDo not use\b/i.test(text)) add("medium", "skill", `Local skill ${name} lacks discriminating trigger/non-trigger wording.`, [rel(skillPath)]);
  }
}

const counts = { high: findings.filter((item) => item.severity === "high").length, medium: findings.filter((item) => item.severity === "medium").length, low: findings.filter((item) => item.severity === "low").length, specs: manifests.length, local_skills: localSkillDirs.length };
const status = counts.high ? "blocked" : counts.medium ? "corrections_required" : counts.low ? "approved_with_notes" : "approved";
const report = { status, project_root: root, findings, summary: counts, unassessed: ["Semantic docs-to-reality drift requires domain inspection.", "Chat-only knowledge cannot be detected unless relevant chat evidence is supplied.", "Runtime cost and latency suitability require observed usage/evaluation data.", "Parallel-write safety requires branch/worktree and execution evidence when parallelism was used."] };
process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
if (["blocked", "corrections_required"].includes(status)) process.exitCode = 1;
