#!/usr/bin/env node

import assert from "node:assert/strict";
import { cpSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const skillRoot = resolve(scriptDir, "..");
const source = resolve(skillRoot, "assets", "backend-contracts");
const fixture = mkdtempSync(resolve(tmpdir(), "karya-contract-manifest-test-"));
const architecture = resolve(fixture, "docs", "architecture");

function run(...extra) {
  return spawnSync(process.execPath, [
    resolve(scriptDir, "validate-backend-contract-manifest.mjs"),
    fixture,
    ...extra,
  ], { encoding: "utf8", windowsHide: true });
}

try {
  cpSync(source, architecture, { recursive: true });
  const pending = run();
  assert.equal(pending.status, 1);
  assert.match(pending.stderr, /unresolved template values/);

  const exampleRoot = resolve(skillRoot, "..", "..", "examples", "backend-contracts", "django-case-analysis");
  for (const name of [
    "backend-contract-manifest.json",
    "backend-plan.md",
    "domain-model.md",
    "api-contract.md",
    "security-contract.md",
    "backend-validation-plan.md",
    "backend-implementation-contract.md",
  ]) {
    writeFileSync(resolve(architecture, name), readFileSync(resolve(exampleRoot, name)));
  }
  const approved = run("--require-approved");
  assert.equal(approved.status, 0, approved.stderr);

  const validationPlanPath = resolve(architecture, "backend-validation-plan.md");
  const validationPlan = readFileSync(validationPlanPath, "utf8");
  writeFileSync(validationPlanPath, validationPlan.replace(/python scripts\/smoke_django_fastapi\.py\r?\n/, ""), "utf8");
  const unsynchronizedPlan = run("--require-approved");
  assert.equal(unsynchronizedPlan.status, 1);
  assert.match(unsynchronizedPlan.stderr, /missing manifest command: python scripts\/smoke_django_fastapi.py/);
  writeFileSync(validationPlanPath, validationPlan, "utf8");

  const manifestPath = resolve(architecture, "backend-contract-manifest.json");
  const manifest = JSON.parse(readFileSync(manifestPath, "utf8"));
  const malformed = structuredClone(manifest);
  delete malformed.environment_bindings[0].url_role;
  delete malformed.endpoints[0].mapper;
  delete malformed.required_validations[0].kind;
  delete malformed.services[0].root_urlconf;
  malformed.services[0].unsupported = true;
  malformed.allowed_execution_commands = ["python manage.py makemigrations cases; Set-Content contract hacked"];
  writeFileSync(manifestPath, `${JSON.stringify(malformed, null, 2)}\n`, "utf8");
  const malformedResult = run("--require-approved");
  assert.equal(malformedResult.status, 1);
  assert.match(malformedResult.stderr, /missing required property url_role/);
  assert.match(malformedResult.stderr, /missing required property mapper/);
  assert.match(malformedResult.stderr, /missing required property kind/);
  assert.match(malformedResult.stderr, /missing required property root_urlconf/);
  assert.match(malformedResult.stderr, /unsupported property unsupported/);
  assert.match(malformedResult.stderr, /non-compound Django makemigrations/);

  manifest.contract_version = 2;
  writeFileSync(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`, "utf8");
  const mismatch = run("--require-approved");
  assert.equal(mismatch.status, 1);
  assert.match(mismatch.stderr, /versions do not match/);

  process.stdout.write("backend contract manifest tests passed\n");
} finally {
  rmSync(fixture, { recursive: true, force: true });
}
