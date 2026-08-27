#!/usr/bin/env node

import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const specAssets = path.resolve(scriptDir, "../../project-spec-architect/assets");
const root = fs.mkdtempSync(path.join(os.tmpdir(), "runtime-router-test-"));
try {
  fs.mkdirSync(path.join(root, "specs", "active", "SPEC-023"), { recursive: true });
  fs.mkdirSync(path.join(root, "docs"), { recursive: true });
  fs.mkdirSync(path.join(root, "src"), { recursive: true });
  fs.mkdirSync(path.join(root, ".codex", "schemas"), { recursive: true });
  fs.mkdirSync(path.join(root, ".codex", "references"), { recursive: true });
  fs.writeFileSync(path.join(root, "AGENTS.md"), "# Project rules\n", "utf8");
  fs.writeFileSync(path.join(root, "docs", "truth.md"), "# Durable truth\n", "utf8");
  fs.writeFileSync(path.join(root, "src", "export.mjs"), "export default {};\n", "utf8");
  fs.copyFileSync(path.join(specAssets, "completion.schema.json"), path.join(root, ".codex", "schemas", "project-spec-completion.schema.json"));
  fs.copyFileSync(path.join(specAssets, "review-evidence.schema.json"), path.join(root, ".codex", "schemas", "project-spec-review.schema.json"));
  fs.copyFileSync(path.join(specAssets, "runtime-policy.json"), path.join(root, ".codex", "references", "runtime-policy.json"));
  const specPath = path.join(root, "specs", "active", "SPEC-023", "SPEC.md");
  const manifestPath = path.join(root, "specs", "active", "SPEC-023", "SPEC.execution.json");
  fs.writeFileSync(specPath, `---\nid: SPEC-023\ntitle: Deterministic export\nstatus: ready\ncontract_version: 1\n---\n\n# SPEC-023\n\n## Goal\nProduce a stable export.\n## Context\nDurable context is in the repository.\n## Scope\n- Export records.\n## Non-scope\n- No new storage.\n## Requirements\n- REQ-001: Stable order.\n## Business or domain rules\n- BR-001: Preserve ties.\n## Decisions already made\n- Use JSON.\n## Constraints\n- Work offline.\n## Acceptance criteria\n- AC-001: Export fixture passes.\n## Affected areas\n- Export module.\n## References\n- docs/truth.md.\n## Skills\n- No specialized skill.\n## Validation requirements\n- VAL-001: Run tests.\n## Review requirements\nSelf-validation is sufficient.\n## Execution and runtime\nUse SPEC.execution.json.\n`, "utf8");
  const manifest = {
    schema_version: "1.0", spec_id: "SPEC-023", contract_version: 1, status: "ready", automatic_handoff: false,
    execution: { classification: "normal_implementation", role: "developer", model: "gpt-5.6-terra", reasoning: "medium", routing_rationale: "Architecture and acceptance criteria are already resolved.", runtime_override: null, working_directory: ".", sandbox_mode: "workspace-write", approval_policy: "on-request", thread: { mode: "new", purpose: "implementation", thread_id: null }, handoff_prompt: "Execute the bounded export change and return needs_design for consequential ambiguity." },
    skills: [], references: [{ path: "docs/truth.md", purpose: "durable domain truth", required: true }],
    validation: [{ id: "VAL-001", kind: "test", command: "node tests/export.test.mjs", required: true }],
    review: { required: false, independence: "self", model: null, reasoning: null, rationale: "Bounded low-risk change." },
    escalation: { policy_version: "1.0", allowed: ["terra_high", "needs_design"] },
    completion: { schema_path: ".codex/schemas/project-spec-completion.schema.json", output_path: ".codex/runtime/completions/SPEC-023.json" },
  };
  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2), "utf8");
  const mockPath = path.join(root, "mock-sdk.mjs");
  fs.writeFileSync(mockPath, `class MockThread {
  constructor(id) { this._id = id; }
  get id() { return this._id; }
  async run(input) {
    if (input.includes("SPEC-024")) return { finalResponse: "not-json", usage: null };
    if (input.includes("SPEC-025")) return { finalResponse: JSON.stringify({ spec_id: "SPEC-025", contract_version: 1, status: "approved", thread_id: null, runtime: { classification: "critical_review", model: "gpt-5.6-sol", reasoning: "high" }, review_input: ["SPEC.md", "git diff and artifacts", "completion evidence"], findings: [], evidence: ["independent review passed"], usage: null }), usage: { input_tokens: 8, cached_input_tokens: 1, cache_write_input_tokens: 0, output_tokens: 4, reasoning_output_tokens: 2 } };
    return { finalResponse: JSON.stringify({ spec_id: "SPEC-023", contract_version: 1, status: "completed", thread_id: null, runtime: { classification: "normal_implementation", model: "gpt-5.6-terra", reasoning: "medium" }, changed_files: ["src/export.mjs"], artifacts: [], acceptance_evidence: { "AC-001": { result: "passed", evidence: ["fixture checksum"], notes: [] } }, validation_evidence: { "VAL-001": { command: "node tests/export.test.mjs", result: "passed", exit_code: 0, evidence: ["1 test passed"], notes: [] } }, deviations: [], unresolved_items: [], needs_design: null, usage: null }), usage: { input_tokens: 10, cached_input_tokens: 2, cache_write_input_tokens: 0, output_tokens: 5, reasoning_output_tokens: 1 } };
  }
}
export class Codex {
  startThread(options) {
    if (options.model === "gpt-5.6-sol" && options.modelReasoningEffort === "high") return new MockThread("thread-review-025");
    if (options.model === "gpt-5.6-terra" && options.modelReasoningEffort === "medium") return new MockThread("thread-start-023");
    throw new Error("wrong runtime");
  }
  resumeThread(id, options) {
    if (id !== "thread-start-023" || options.model !== "gpt-5.6-terra") throw new Error("wrong resume");
    return new MockThread(id);
  }
}
`, "utf8");
  const router = path.join(scriptDir, "route-codex-runtime.mjs");
  const common = [router, "--project-root", root, "--spec", "specs/active/SPEC-023/SPEC.md", "--manifest", "specs/active/SPEC-023/SPEC.execution.json", "--sdk-module", mockPath];
  const preview = spawnSync(process.execPath, [...common, "--dry-run"], { encoding: "utf8" });
  assert.equal(preview.status, 0, preview.stdout || preview.stderr);
  assert.equal(JSON.parse(preview.stdout).action, "start");
  const start = spawnSync(process.execPath, common, { encoding: "utf8" });
  assert.equal(start.status, 0, start.stdout || start.stderr);
  const started = JSON.parse(start.stdout);
  assert.equal(started.thread_id, "thread-start-023");
  const completion = JSON.parse(fs.readFileSync(path.join(root, ".codex", "runtime", "completions", "SPEC-023.json"), "utf8"));
  assert.equal(completion.thread_id, "thread-start-023");
  assert.equal(completion.usage.input_tokens, 10);
  const duplicate = spawnSync(process.execPath, [...common, "--dry-run"], { encoding: "utf8" });
  assert.equal(duplicate.status, 1);
  assert.ok(JSON.parse(duplicate.stdout).errors.some((item) => item.includes("already recorded")));
  manifest.execution.thread = { mode: "resume", purpose: "implementation", thread_id: "thread-start-023" };
  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2), "utf8");
  const resume = spawnSync(process.execPath, common, { encoding: "utf8" });
  assert.equal(resume.status, 0, resume.stdout || resume.stderr);
  assert.equal(JSON.parse(resume.stdout).action, "resume");
  const badSpecDir = path.join(root, "specs", "active", "SPEC-024");
  fs.mkdirSync(badSpecDir, { recursive: true });
  fs.writeFileSync(path.join(badSpecDir, "SPEC.md"), fs.readFileSync(specPath, "utf8").replaceAll("SPEC-023", "SPEC-024"), "utf8");
  const badManifest = structuredClone(manifest);
  badManifest.spec_id = "SPEC-024";
  badManifest.execution.thread = { mode: "new", purpose: "implementation", thread_id: null };
  badManifest.completion.output_path = ".codex/runtime/completions/SPEC-024.json";
  fs.writeFileSync(path.join(badSpecDir, "SPEC.execution.json"), JSON.stringify(badManifest, null, 2), "utf8");
  const invalid = spawnSync(process.execPath, [router, "--project-root", root, "--spec", "specs/active/SPEC-024/SPEC.md", "--manifest", "specs/active/SPEC-024/SPEC.execution.json", "--sdk-module", mockPath], { encoding: "utf8" });
  assert.equal(invalid.status, 1, invalid.stdout || invalid.stderr);
  assert.equal(JSON.parse(invalid.stdout).thread_id, "thread-start-023");
  const failedState = JSON.parse(fs.readFileSync(path.join(root, ".codex", "runtime", "spec-threads.json"), "utf8"));
  assert.equal(failedState.specs["SPEC-024"].implementation_thread_id, "thread-start-023");
  assert.equal(failedState.specs["SPEC-024"].last_status, "failed");
  const reviewSpecDir = path.join(root, "specs", "active", "SPEC-025");
  fs.mkdirSync(reviewSpecDir, { recursive: true });
  fs.writeFileSync(path.join(reviewSpecDir, "SPEC.md"), fs.readFileSync(specPath, "utf8").replaceAll("SPEC-023", "SPEC-025").replace("status: ready", "status: review"), "utf8");
  const reviewManifest = structuredClone(manifest);
  reviewManifest.spec_id = "SPEC-025";
  reviewManifest.status = "review";
  reviewManifest.execution = { classification: "critical_review", role: "reviewer", model: "gpt-5.6-sol", reasoning: "high", routing_rationale: "The public contract requires an independent critical review.", runtime_override: null, working_directory: ".", sandbox_mode: "read-only", approval_policy: "never", thread: { mode: "new", purpose: "review", thread_id: null }, handoff_prompt: "Review SPEC-025 independently using its contract, diff and artifacts, tests, and completion evidence." };
  reviewManifest.review = { required: true, independence: "independent", model: "gpt-5.6-sol", reasoning: "high", rationale: "Public contract review is required." };
  reviewManifest.escalation.allowed = ["sol_xhigh"];
  reviewManifest.completion = { schema_path: ".codex/schemas/project-spec-review.schema.json", output_path: ".codex/runtime/reviews/SPEC-025.json" };
  fs.writeFileSync(path.join(reviewSpecDir, "SPEC.execution.json"), JSON.stringify(reviewManifest, null, 2), "utf8");
  const reviewRun = spawnSync(process.execPath, [router, "--project-root", root, "--spec", "specs/active/SPEC-025/SPEC.md", "--manifest", "specs/active/SPEC-025/SPEC.execution.json", "--sdk-module", mockPath], { encoding: "utf8" });
  assert.equal(reviewRun.status, 0, reviewRun.stdout || reviewRun.stderr);
  assert.equal(JSON.parse(reviewRun.stdout).route, "approved");
  const reviewState = JSON.parse(fs.readFileSync(path.join(root, ".codex", "runtime", "spec-threads.json"), "utf8"));
  assert.equal(reviewState.specs["SPEC-025"].review_thread_id, "thread-review-025");
  for (const file of ["thread-state.schema.json", "router-result.schema.json"]) JSON.parse(fs.readFileSync(path.resolve(scriptDir, "../assets", file), "utf8"));
  process.stdout.write("runtime router tests passed\n");
} finally {
  fs.rmSync(root, { recursive: true, force: true });
}
