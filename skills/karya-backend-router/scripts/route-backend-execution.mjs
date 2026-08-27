#!/usr/bin/env node
import { spawn } from "node:child_process";
import { closeSync, copyFileSync, existsSync, mkdirSync, openSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, isAbsolute, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import {
  checkContractPreflight,
  inspectOpenCode,
  loadEnvFile,
  resolvePythonCommand,
  runCapture,
  compareProtectedProjectState,
  snapshotProtectedProjectState,
  toPortablePath,
  validateCompletion,
} from "./_router-core.mjs";

function parseArgs(argv) {
  const result = { dryRun: false };
  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (value === "--dry-run") result.dryRun = true;
    else if (value.startsWith("--")) {
      const key = value.slice(2).replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());
      const next = argv[index + 1];
      if (!next || next.startsWith("--")) throw new Error(`missing value for ${value}`);
      result[key] = next;
      index += 1;
    } else throw new Error(`unexpected argument: ${value}`);
  }
  return result;
}

function safeTaskId(value) {
  const fallback = `backend-${new Date().toISOString().replace(/[:.]/g, "-")}`;
  const normalized = String(value || fallback).toLowerCase().replace(/[^a-z0-9_-]+/g, "-").replace(/^-+|-+$/g, "");
  if (!normalized) throw new Error("task id is empty after normalization");
  return normalized.slice(0, 96);
}

function writeResult(runDir, result) {
  if (runDir) {
    mkdirSync(runDir, { recursive: true });
    writeFileSync(resolve(runDir, "route-result.json"), `${JSON.stringify(result, null, 2)}\n`, "utf8");
  }
  process.stdout.write(`${JSON.stringify(result)}\n`);
}

async function runQuiet(command, args, { cwd, env, timeoutMs, stdoutPath, stderrPath }) {
  const stdoutFd = openSync(stdoutPath, "w");
  const stderrFd = openSync(stderrPath, "w");
  return await new Promise((resolvePromise) => {
    let settled = false;
    let timedOut = false;
    let child;
    try {
      child = spawn(command, args, {
        cwd,
        env,
        windowsHide: true,
        shell: false,
        stdio: ["ignore", stdoutFd, stderrFd],
      });
    } catch (error) {
      closeSync(stdoutFd);
      closeSync(stderrFd);
      resolvePromise({ code: null, signal: null, error: error.message, timedOut: false });
      return;
    }
    const timer = setTimeout(() => {
      timedOut = true;
      child.kill();
    }, timeoutMs);
    const finish = (value) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      closeSync(stdoutFd);
      closeSync(stderrFd);
      resolvePromise({ ...value, timedOut });
    };
    child.on("error", (error) => finish({ code: null, error: error.message }));
    child.on("close", (code, signal) => finish({ code, signal, error: null }));
  });
}

const scriptDir = dirname(fileURLToPath(import.meta.url));
const skillRoot = resolve(scriptDir, "..");
const sourceRepositoryRoot = resolve(skillRoot, "..", "..");
const executorSkillRoot = resolve(skillRoot, "..", "django-backend-code-executor");
const environmentFile = process.env.KARYA_ENV_FILE
  ? resolve(process.env.KARYA_ENV_FILE)
  : resolve(sourceRepositoryRoot, ".env");
loadEnvFile(environmentFile);

let args;
try {
  args = parseArgs(process.argv.slice(2));
} catch (error) {
  process.stderr.write(`${error.message}\n`);
  process.exit(64);
}

if (!args.projectRoot) {
  process.stderr.write("usage: route-backend-execution.mjs --project-root <path> [--task-id <id>] [--executor auto|opencode|codex] [--model <provider/model>] [--timeout-minutes <n>] [--dry-run]\n");
  process.exit(64);
}

const projectRoot = resolve(args.projectRoot);
const taskId = safeTaskId(args.taskId);
const executor = String(args.executor || process.env.KARYA_BACKEND_EXECUTOR || "auto").toLowerCase();
const model = args.model || process.env.KARYA_OPENCODE_MODEL || "opencode-go/kimi-k2.7-code";
const timeoutMinutes = Number(args.timeoutMinutes || process.env.KARYA_OPENCODE_TIMEOUT_MINUTES || "120");
const runDir = resolve(tmpdir(), "karya-backend-runs", taskId);
const baseResult = { task_id: taskId, model, project_root: projectRoot, reasons: [], artifacts: { run_dir: runDir } };

if (!existsSync(projectRoot) || !isAbsolute(projectRoot)) {
  writeResult(runDir, { ...baseResult, route: "preflight-blocked", executor: "none", reasons: ["project root does not exist"] });
  process.exit(2);
}
if (!new Set(["auto", "opencode", "codex"]).has(executor)) {
  process.stderr.write("executor must be auto, opencode, or codex\n");
  process.exit(64);
}
if (!Number.isFinite(timeoutMinutes) || timeoutMinutes <= 0) {
  process.stderr.write("timeout-minutes must be a positive number\n");
  process.exit(64);
}

const preflight = checkContractPreflight(projectRoot);
if (!preflight.ok) {
  writeResult(runDir, { ...baseResult, route: "preflight-blocked", executor: "none", reasons: preflight.errors });
  process.exit(2);
}

const routerConfigPath = resolve(skillRoot, "assets", "opencode.backend.json");
const requiredRouterResources = [
  resolve(executorSkillRoot, "SKILL.md"),
  resolve(executorSkillRoot, "assets", "completion.schema.json"),
  resolve(executorSkillRoot, "scripts", "scan-django-boundaries.py"),
  routerConfigPath,
];
const missingRouterResources = requiredRouterResources.filter((path) => !existsSync(path));
if (missingRouterResources.length > 0) {
  writeResult(runDir, {
    ...baseResult,
    route: "preflight-blocked",
    executor: "none",
    reasons: missingRouterResources.map((path) => `missing router resource: ${path}`),
  });
  process.exit(2);
}

if (executor === "codex") {
  writeResult(runDir, { ...baseResult, route: "codex-fallback-required", executor: "codex", reasons: ["Codex executor was selected explicitly"] });
  process.exit(0);
}

const readiness = await inspectOpenCode({ command: process.env.KARYA_OPENCODE_COMMAND, model });
if (!readiness.ready) {
  const route = executor === "opencode" ? "opencode-unavailable" : "codex-fallback-required";
  writeResult(runDir, { ...baseResult, route, executor: route === "opencode-unavailable" ? "none" : "codex", reasons: readiness.reasons, readiness });
  process.exit(route === "opencode-unavailable" ? 3 : 0);
}

if (args.dryRun) {
  writeResult(runDir, { ...baseResult, route: "opencode-ready", executor: "opencode", readiness });
  process.exit(0);
}

mkdirSync(runDir, { recursive: true });
const completionPath = resolve(runDir, "completion.json");
const completionSchemaPath = resolve(runDir, "completion.schema.json");
const eventsPath = resolve(runDir, "opencode-events.ndjson");
const stderrPath = resolve(runDir, "opencode-stderr.log");
const scanPath = resolve(runDir, "architecture-scan.log");
copyFileSync(resolve(executorSkillRoot, "assets", "completion.schema.json"), completionSchemaPath);
rmSync(completionPath, { force: true });

const baseConfig = JSON.parse(readFileSync(routerConfigPath, "utf8"));
const portableRunDir = toPortablePath(runDir);
const runtimePermission = {
  ...baseConfig.permission,
  edit: {
    ...baseConfig.permission.edit,
    [`${portableRunDir}/**`]: "allow",
  },
  external_directory: {
    "*": "deny",
    [`${portableRunDir}/**`]: "allow",
  },
  bash: {
    ...baseConfig.permission.bash,
    ...Object.fromEntries(
      [...Object.values(preflight.allValidationCommands), ...preflight.allowedExecutionCommands]
        .map((command) => [command, "allow"]),
    ),
  },
};
const runtimeConfig = {
  ...baseConfig,
  model,
  enabled_providers: [model.split("/")[0]],
  instructions: [
    toPortablePath(resolve(executorSkillRoot, "SKILL.md")),
    `${toPortablePath(resolve(executorSkillRoot, "references"))}/*.md`,
  ],
  permission: runtimePermission,
  agent: {
    "karya-backend": {
      description: "Implement only the approved Karya Django backend contract",
      mode: "primary",
      model,
      permission: runtimePermission,
    },
  },
};

const prompt = [
  "Implement the explicitly approved Django backend contract in the current project.",
  `Task ID: ${taskId}. Approved contract version: ${preflight.contractVersion}.`,
  "The Karya Django executor skill and all references are already loaded as mandatory runtime instructions.",
  "Work autonomously until completed, blocked, failed, or contract review is required. Do not ask questions and do not call Codex.",
  "Never edit approved contracts, AGENTS.md, .codex, .env files, Git metadata, or migration Python files.",
  "Generate migrations only with Django management commands. Do not commit, push, switch branches, or use subagents or web access.",
  "For completed work, contract evidence must cite every exact required_tests name from the manifest and validation evidence must use each exact required command.",
  `Write the final JSON completion evidence to ${toPortablePath(completionPath)} and conform to ${toPortablePath(completionSchemaPath)}.`,
  "Write completion.json before your final response. Your process exit is the only signal that wakes the Codex orchestrator.",
].join("\n");

writeFileSync(resolve(runDir, "request.json"), `${JSON.stringify({
  task_id: taskId,
  project_root: projectRoot,
  contract_version: preflight.contractVersion,
  executor: "opencode",
  model,
  started_at: new Date().toISOString(),
  timeout_minutes: timeoutMinutes,
}, null, 2)}\n`, "utf8");

const protectedStateBefore = snapshotProtectedProjectState(projectRoot);

const childEnv = {
  ...process.env,
  OPENCODE_CONFIG_CONTENT: JSON.stringify(runtimeConfig),
  OPENCODE_DISABLE_AUTOUPDATE: "true",
  OPENCODE_AUTO_SHARE: "false",
};
const run = await runQuiet(readiness.command, [
  "--pure",
  "run",
  "--format", "json",
  "--model", model,
  "--agent", "karya-backend",
  "--auto",
  "--dir", projectRoot,
  "--title", `Karya backend ${taskId}`,
  prompt,
], {
  cwd: projectRoot,
  env: childEnv,
  timeoutMs: timeoutMinutes * 60_000,
  stdoutPath: eventsPath,
  stderrPath,
});

const protectedStateAfter = snapshotProtectedProjectState(projectRoot);
const protectedIntegrityErrors = compareProtectedProjectState(protectedStateBefore, protectedStateAfter);

const scanner = resolve(executorSkillRoot, "scripts", "scan-django-boundaries.py");
const pythonCommand = await resolvePythonCommand();
const scan = await runCapture(pythonCommand, [scanner], { cwd: projectRoot, timeoutMs: 10 * 60_000 });
writeFileSync(scanPath, `${scan.stdout}${scan.stderr}`, "utf8");

let completion = null;
let completionErrors = [];
if (existsSync(completionPath)) {
  try {
    completion = JSON.parse(readFileSync(completionPath, "utf8"));
    completionErrors = validateCompletion(
      completion,
      preflight.contractVersion,
      preflight.contractIds,
      preflight.validationCommands,
      preflight.contractRequiredTests,
      taskId,
      preflight.allValidationCommands,
      preflight.allowedExecutionCommands,
    );
  } catch (error) {
    completionErrors = [`completion.json is invalid JSON: ${error.message}`];
  }
} else completionErrors = ["OpenCode did not write completion.json"];

const reasons = [];
if (run.timedOut) reasons.push(`OpenCode exceeded ${timeoutMinutes} minute(s)`);
if (run.error) reasons.push(run.error);
if (run.code !== 0) reasons.push(`OpenCode exited with code ${run.code ?? "unknown"}`);
if (scan.code !== 0) reasons.push("deterministic Django boundary scan failed");
reasons.push(...protectedIntegrityErrors);
reasons.push(...completionErrors);

let route = "opencode-error";
if (completion && completionErrors.length === 0 && completion.status === "completed" && run.code === 0 && scan.code === 0 && protectedIntegrityErrors.length === 0) {
  route = "opencode-completed";
} else if (completion && ["blocked", "contract-review-required"].includes(completion.status)) {
  route = "opencode-reported-blocked";
}

const result = {
  ...baseResult,
  route,
  executor: "opencode",
  reasons,
  readiness,
  process: run,
  completion_status: completion?.status ?? null,
  architecture_scan_exit_code: scan.code,
  protected_integrity: {
    ok: protectedIntegrityErrors.length === 0,
    errors: protectedIntegrityErrors,
  },
  artifacts: {
    run_dir: runDir,
    request: resolve(runDir, "request.json"),
    events: eventsPath,
    stderr: stderrPath,
    completion: completionPath,
    completion_schema: completionSchemaPath,
    architecture_scan: scanPath,
    route_result: resolve(runDir, "route-result.json"),
  },
};
writeResult(runDir, result);
process.exit(route === "opencode-completed" ? 0 : 3);
