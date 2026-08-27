#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadPlan, validateHarnessPlan } from "./_harness-plan-core.mjs";

const args = process.argv.slice(2);
const option = (name) => { const index = args.indexOf(name); return index >= 0 ? args[index + 1] : null; };
const projectRoot = path.resolve(option("--project-root") ?? "");
const planPath = path.resolve(option("--plan") ?? "");
const dryRun = args.includes("--dry-run");
if (!option("--project-root") || !option("--plan")) {
  process.stderr.write("Usage: node bootstrap-project-harness.mjs --project-root <root> --plan <harness-plan.json> [--dry-run]\n");
  process.exit(2);
}

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const skillRoot = path.resolve(scriptDir, "..");
const starterRoot = path.resolve(skillRoot, "assets/project-harness-starter");
const specAssets = path.resolve(skillRoot, "../project-spec-architect/assets");
const plan = loadPlan(planPath);
const errors = validateHarnessPlan(plan, { requireAccepted: true });
if (errors.length) {
  process.stdout.write(`${JSON.stringify({ status: "blocked", errors }, null, 2)}\n`);
  process.exit(1);
}
for (const required of [starterRoot, specAssets]) if (!fs.existsSync(required)) throw new Error(`Required sibling Factory resource not found: ${required}`);
for (const source of [starterRoot, specAssets]) {
  const relative = path.relative(source, projectRoot);
  if (relative === "" || (!relative.startsWith("..") && !path.isAbsolute(relative))) throw new Error("Project root must not be a bundled skill asset or descendant.");
}
if (fs.existsSync(projectRoot) && !fs.statSync(projectRoot).isDirectory()) throw new Error(`Project root is not a directory: ${projectRoot}`);

const created = [];
const preserved = [];
function copyMissing(source, target) {
  if (fs.existsSync(target)) { preserved.push(path.relative(projectRoot, target)); return; }
  created.push(path.relative(projectRoot, target));
  if (dryRun) return;
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.copyFileSync(source, target, fs.constants.COPYFILE_EXCL);
}
function walk(sourceDir, targetDir) {
  for (const entry of fs.readdirSync(sourceDir, { withFileTypes: true })) {
    const source = path.join(sourceDir, entry.name);
    const target = path.join(targetDir, entry.name);
    if (entry.isDirectory()) walk(source, target); else if (entry.isFile()) copyMissing(source, target);
  }
}

walk(starterRoot, projectRoot);
for (const [sourceName, targetRelative] of [
  ["runtime-policy.json", ".codex/references/runtime-policy.json"],
  ["spec-execution.schema.json", ".codex/schemas/project-spec-execution.schema.json"],
  ["completion.schema.json", ".codex/schemas/project-spec-completion.schema.json"],
  ["review-evidence.schema.json", ".codex/schemas/project-spec-review.schema.json"],
  ["SPEC.template.md", ".codex/templates/project-spec.md"],
  ["SPEC.execution.template.json", ".codex/templates/project-spec.execution.json"],
]) copyMissing(path.join(specAssets, sourceName), path.join(projectRoot, targetRelative));

const decisionTarget = path.join(projectRoot, ".codex/decisions/project-harness-bootstrap.json");
if (fs.existsSync(decisionTarget)) preserved.push(path.relative(projectRoot, decisionTarget));
else {
  created.push(path.relative(projectRoot, decisionTarget));
  if (!dryRun) {
    fs.mkdirSync(path.dirname(decisionTarget), { recursive: true });
    fs.copyFileSync(planPath, decisionTarget, fs.constants.COPYFILE_EXCL);
  }
}

const gitignorePath = path.join(projectRoot, ".gitignore");
const warnings = [];
if (fs.existsSync(gitignorePath) && !fs.readFileSync(gitignorePath, "utf8").split(/\r?\n/).includes(".codex/runtime/")) warnings.push("Existing .gitignore was preserved; add .codex/runtime/ after review.");
process.stdout.write(`${JSON.stringify({ status: dryRun ? "preview" : "initialized", project_root: projectRoot, created, preserved, warnings }, null, 2)}\n`);
