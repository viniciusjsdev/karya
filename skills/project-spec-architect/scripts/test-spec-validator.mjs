#!/usr/bin/env node

import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadJson, validateSpecPair } from "./_spec-core.mjs";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const assets = path.resolve(scriptDir, "../assets");
const policy = loadJson(path.join(assets, "runtime-policy.json"));
for (const file of ["runtime-policy.schema.json", "spec-execution.schema.json", "completion.schema.json", "review-evidence.schema.json"]) JSON.parse(fs.readFileSync(path.join(assets, file), "utf8"));

const root = fs.mkdtempSync(path.join(os.tmpdir(), "project-spec-test-"));
try {
  fs.mkdirSync(path.join(root, "docs"), { recursive: true });
  fs.writeFileSync(path.join(root, "docs", "truth.md"), "# Truth\n", "utf8");
  const markdown = `---\nid: SPEC-023\ntitle: Add deterministic export\nstatus: ready\ncontract_version: 2\n---\n\n# SPEC-023\n\n## Goal\nProduce a deterministic export.\n## Context\nThe clean thread uses only durable inputs.\n## Scope\n- Export one format.\n## Non-scope\n- No new storage.\n## Requirements\n- REQ-001: Stable order.\n## Business or domain rules\n- BR-001: Preserve source order ties.\n## Decisions already made\n- JSON is the selected format.\n## Constraints\n- No network access.\n## Acceptance criteria\n- AC-001: Fixture output is stable.\n## Affected areas\n- Export module.\n## References\n- docs/truth.md.\n## Skills\n- No specialized skill is required.\n## Validation requirements\n- VAL-001: Run the test.\n## Review requirements\nSelf-validation is sufficient for this bounded change.\n## Execution and runtime\nUse SPEC.execution.json.\n`;
  const manifest = {
    schema_version: "1.0", spec_id: "SPEC-023", contract_version: 2, status: "ready", automatic_handoff: false,
    execution: { classification: "normal_implementation", role: "developer", model: "gpt-5.6-terra", reasoning: "medium", routing_rationale: "Architecture and acceptance criteria are already resolved.", runtime_override: null, working_directory: ".", sandbox_mode: "workspace-write", approval_policy: "on-request", thread: { mode: "new", purpose: "implementation", thread_id: null }, handoff_prompt: "Execute SPEC-023 from durable sources and return needs_design for consequential ambiguity." },
    skills: [], references: [{ path: "docs/truth.md", purpose: "source of truth", required: true }],
    validation: [{ id: "VAL-001", kind: "test", command: "node test-export.mjs", required: true }],
    review: { required: false, independence: "self", model: null, reasoning: null, rationale: "Bounded low-risk change." },
    escalation: { policy_version: "1.0", allowed: ["terra_high", "needs_design"] },
    completion: { schema_path: ".codex/schemas/project-spec-completion.schema.json", output_path: ".codex/runtime/completions/SPEC-023.json" },
  };
  assert.deepEqual(validateSpecPair(markdown, manifest, policy, { projectRoot: root, requireReady: true }), []);
  assert.ok(validateSpecPair(markdown.replace("The clean thread uses only durable inputs.", "TBD from the design chat."), manifest, policy, { projectRoot: root, requireReady: true }).some((item) => item.includes("placeholder")));
  const unreasonedOverride = structuredClone(manifest);
  unreasonedOverride.execution.model = "gpt-5.6-sol";
  assert.ok(validateSpecPair(markdown, unreasonedOverride, policy, { projectRoot: root, requireReady: true }).some((item) => item.includes("runtime_override")));
  const inaccurateOverride = structuredClone(unreasonedOverride);
  inaccurateOverride.execution.runtime_override = { default_model: "gpt-5.6-luna", default_reasoning: "low", reason: "The implementation has an exceptional documented constraint." };
  assert.ok(validateSpecPair(markdown, inaccurateOverride, policy, { projectRoot: root, requireReady: true }).some((item) => item.includes("do not match the runtime policy")));
  const stalePolicy = structuredClone(manifest);
  stalePolicy.escalation.policy_version = "0.9";
  assert.ok(validateSpecPair(markdown, stalePolicy, policy, { projectRoot: root, requireReady: true }).some((item) => item.includes("policy_version")));
  const unsafe = structuredClone(manifest);
  unsafe.validation[0].command = "node test-export.mjs; Remove-Item docs/truth.md";
  assert.ok(validateSpecPair(markdown, unsafe, policy, { projectRoot: root, requireReady: true }).some((item) => item.includes("shell control")));
  process.stdout.write("spec validator tests passed\n");
} finally {
  fs.rmSync(root, { recursive: true, force: true });
}
