#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadJson, validateSpecPair } from "./_spec-core.mjs";

const args = process.argv.slice(2);
const option = (name) => { const index = args.indexOf(name); return index >= 0 ? args[index + 1] : null; };
const consumed = new Set(["--project-root", "--policy", "--skills-root"].flatMap((name) => { const index = args.indexOf(name); return index >= 0 ? [name, args[index + 1]] : []; }).concat("--require-ready"));
const positional = args.filter((item) => !consumed.has(item));
const specPath = positional[0];
const manifestPath = positional[1];
if (!specPath || !manifestPath) {
  process.stderr.write("Usage: node validate-spec.mjs <SPEC.md> <SPEC.execution.json> [--project-root <root>] [--policy <runtime-policy.json>] [--skills-root <root>] [--require-ready]\n");
  process.exit(2);
}

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const policyPath = option("--policy") ?? path.resolve(scriptDir, "../assets/runtime-policy.json");
const projectRoot = path.resolve(option("--project-root") ?? path.dirname(path.resolve(specPath)));
try {
  const errors = validateSpecPair(fs.readFileSync(path.resolve(specPath), "utf8"), loadJson(path.resolve(manifestPath)), loadJson(policyPath), { projectRoot, skillsRoot: option("--skills-root"), requireReady: args.includes("--require-ready") });
  process.stdout.write(`${JSON.stringify({ valid: errors.length === 0, spec: path.resolve(specPath), manifest: path.resolve(manifestPath), errors }, null, 2)}\n`);
  if (errors.length) process.exitCode = 1;
} catch (error) {
  process.stderr.write(`${error.message}\n`);
  process.exitCode = 1;
}
