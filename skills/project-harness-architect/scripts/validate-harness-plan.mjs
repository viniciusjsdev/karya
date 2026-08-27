#!/usr/bin/env node

import path from "node:path";
import { loadPlan, validateHarnessPlan } from "./_harness-plan-core.mjs";

const args = process.argv.slice(2);
const planPath = args.find((item) => !item.startsWith("--"));
if (!planPath) {
  process.stderr.write("Usage: node validate-harness-plan.mjs <harness-plan.json> [--require-accepted]\n");
  process.exit(2);
}
try {
  const errors = validateHarnessPlan(loadPlan(path.resolve(planPath)), { requireAccepted: args.includes("--require-accepted") });
  process.stdout.write(`${JSON.stringify({ valid: errors.length === 0, plan: path.resolve(planPath), errors }, null, 2)}\n`);
  if (errors.length) process.exitCode = 1;
} catch (error) {
  process.stderr.write(`${error.message}\n`);
  process.exitCode = 1;
}
