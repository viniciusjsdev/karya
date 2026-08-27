#!/usr/bin/env node

import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { validateHarnessPlan } from "./_harness-plan-core.mjs";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const root = fs.mkdtempSync(path.join(os.tmpdir(), "harness-bootstrap-test-"));
try {
  const project = path.join(root, "project");
  fs.mkdirSync(project);
  fs.writeFileSync(path.join(project, "AGENTS.md"), "# Existing\n", "utf8");
  const plan = {
    schema_version: "1.0", status: "accepted", project: { name: "sample", domain: "laboratory", project_type: "research", objective: "Keep a reproducible experiment record." },
    sources_of_truth: [{ path: "notebooks", kind: "methodology", authority: "primary", action: "preserve" }],
    documentation: { preserve: ["notebooks"], create: [], path_mappings: [] }, decisions: { durable_path: ".codex/decisions", open: [] }, workflows: [], local_skill_candidates: [],
    spec_strategy: { root: "specs", active_pattern: "specs/active/SPEC-NNN", markdown_name: "SPEC.md", execution_name: "SPEC.execution.json" }, validation: [],
    runtime_policy: { policy_version: "1.0", project_path: ".codex/references/runtime-policy.json" },
    thread_policy: { design: "new_or_existing_design_thread", implementation: "new_clean_thread", needs_design: "resume_implementation_after_design_resolution", parallel_writes: "sequential_by_default", subagents: "not_default" }, automatic_handoff: false,
  };
  assert.deepEqual(validateHarnessPlan(plan, { requireAccepted: true }), []);
  const planPath = path.join(root, "plan.json");
  fs.writeFileSync(planPath, JSON.stringify(plan, null, 2), "utf8");
  const run = spawnSync(process.execPath, [path.join(scriptDir, "bootstrap-project-harness.mjs"), "--project-root", project, "--plan", planPath], { encoding: "utf8" });
  assert.equal(run.status, 0, run.stderr || run.stdout);
  assert.equal(fs.readFileSync(path.join(project, "AGENTS.md"), "utf8"), "# Existing\n");
  assert.ok(fs.existsSync(path.join(project, ".codex/references/runtime-policy.json")));
  assert.ok(fs.existsSync(path.join(project, ".codex/schemas/project-spec-execution.schema.json")));
  assert.ok(fs.existsSync(path.join(project, ".codex/schemas/project-spec-completion.schema.json")));
  assert.ok(fs.existsSync(path.join(project, ".codex/schemas/project-spec-review.schema.json")));
  const executionTemplate = JSON.parse(fs.readFileSync(path.join(project, ".codex/templates/project-spec.execution.json"), "utf8"));
  assert.equal(path.resolve(project, "specs/active/SPEC-001", executionTemplate.$schema), path.join(project, ".codex/schemas/project-spec-execution.schema.json"));
  assert.ok(fs.existsSync(path.join(project, ".codex/decisions/project-harness-bootstrap.json")));
  const rerun = spawnSync(process.execPath, [path.join(scriptDir, "bootstrap-project-harness.mjs"), "--project-root", project, "--plan", planPath], { encoding: "utf8" });
  assert.equal(rerun.status, 0, rerun.stderr || rerun.stdout);
  assert.ok(JSON.parse(rerun.stdout).preserved.includes("AGENTS.md"));
  process.stdout.write("harness bootstrap tests passed\n");
} finally {
  fs.rmSync(root, { recursive: true, force: true });
}
