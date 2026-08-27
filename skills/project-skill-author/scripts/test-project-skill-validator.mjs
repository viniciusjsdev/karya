#!/usr/bin/env node

import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const root = fs.mkdtempSync(path.join(os.tmpdir(), "project-skill-test-"));
try {
  const skillDir = path.join(root, ".agents", "skills", "normalize-samples");
  fs.mkdirSync(path.join(skillDir, "agents"), { recursive: true });
  fs.writeFileSync(path.join(skillDir, "SKILL.md"), `---\nname: normalize-samples\ndescription: Normalize approved sensor samples. Use when repeated laboratory imports need the documented normalization procedure. Do not use for methodology design or one-time data repair.\n---\n\n# Normalize Samples\n\n## Required Context\nRead the approved protocol.\n\n## Workflow\nApply the repeatable sequence.\n\n## Invariants\nPreserve raw data.\n\n## Validation\nCompare the fixture checksum.\n\n## Boundaries\nDo not alter methodology.\n`, "utf8");
  fs.writeFileSync(path.join(skillDir, "agents", "openai.yaml"), "interface:\n  display_name: Normalize Samples\n  short_description: Normalize samples\n", "utf8");
  const run = spawnSync(process.execPath, [path.join(scriptDir, "validate-project-skill.mjs"), skillDir, "--project-root", root], { encoding: "utf8" });
  assert.equal(run.status, 0, run.stdout || run.stderr);
  const bad = fs.readFileSync(path.join(skillDir, "SKILL.md"), "utf8").replace("## Invariants", "## TODO");
  fs.writeFileSync(path.join(skillDir, "SKILL.md"), bad, "utf8");
  const rejected = spawnSync(process.execPath, [path.join(scriptDir, "validate-project-skill.mjs"), skillDir, "--project-root", root], { encoding: "utf8" });
  assert.equal(rejected.status, 1);
  assert.ok(JSON.parse(rejected.stdout).errors.some((item) => item.includes("Invariants")));
  process.stdout.write("project skill validator tests passed\n");
} finally {
  fs.rmSync(root, { recursive: true, force: true });
}
