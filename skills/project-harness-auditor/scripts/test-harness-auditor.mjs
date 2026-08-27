#!/usr/bin/env node

import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const root = fs.mkdtempSync(path.join(os.tmpdir(), "harness-auditor-test-"));
try {
  const run = spawnSync(process.execPath, [path.join(scriptDir, "audit-project-harness.mjs"), "--project-root", root], { encoding: "utf8" });
  assert.equal(run.status, 1);
  const report = JSON.parse(run.stdout);
  assert.equal(report.status, "blocked");
  assert.ok(report.findings.some((item) => item.message.includes("AGENTS.md")));
  assert.ok(report.unassessed.some((item) => item.includes("Chat-only")));
  const exampleSource = path.resolve(scriptDir, "../../../examples/project-harness/spec-023-sensor-export/project");
  const exampleCopy = path.join(root, "example");
  fs.cpSync(exampleSource, exampleCopy, { recursive: true });
  fs.rmSync(path.join(exampleCopy, "specs", "active", "SPEC-023", "evidence", "review.json"));
  const missingReview = spawnSync(process.execPath, [path.join(scriptDir, "audit-project-harness.mjs"), "--project-root", exampleCopy, "--skills-root", path.join(exampleCopy, ".agents", "skills")], { encoding: "utf8" });
  assert.equal(missingReview.status, 1);
  assert.ok(JSON.parse(missingReview.stdout).findings.some((item) => item.category === "review" && item.severity === "high"));
  JSON.parse(fs.readFileSync(path.resolve(scriptDir, "../assets/harness-audit.schema.json"), "utf8"));
  process.stdout.write("harness auditor tests passed\n");
} finally {
  fs.rmSync(root, { recursive: true, force: true });
}
