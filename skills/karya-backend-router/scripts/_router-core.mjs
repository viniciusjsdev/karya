import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { delimiter, extname, isAbsolute, resolve } from "node:path";

export const REQUIRED_CONTRACTS = [
  "docs/architecture/backend-plan.md",
  "docs/architecture/domain-model.md",
  "docs/architecture/api-contract.md",
  "docs/architecture/security-contract.md",
  "docs/architecture/backend-validation-plan.md",
  "docs/architecture/backend-implementation-contract.md",
  "docs/architecture/backend-contract-manifest.json",
];

export function commandName(name) {
  if (process.platform !== "win32" || name !== "opencode") return name;
  const candidates = [];
  if (process.env.APPDATA) candidates.push(resolve(process.env.APPDATA, "npm", "node_modules", "opencode-ai", "bin", "opencode.exe"));
  for (const directory of String(process.env.PATH ?? "").split(delimiter)) {
    if (directory) candidates.push(resolve(directory, "opencode.exe"));
  }
  return candidates.find((candidate) => existsSync(candidate)) ?? "opencode.exe";
}

export function resolveExecutable(command) {
  if (process.platform !== "win32") return command;
  if (!command || command === "opencode" || command === "opencode.cmd") return commandName("opencode");
  if (isAbsolute(command) && extname(command).toLowerCase() === ".cmd") {
    const nativeCandidate = resolve(command, "..", "node_modules", "opencode-ai", "bin", "opencode.exe");
    if (existsSync(nativeCandidate)) return nativeCandidate;
  }
  return command;
}

export function stripAnsi(value) {
  return value.replace(/\u001B\[[0-?]*[ -/]*[@-~]/g, "");
}

export function toPortablePath(value) {
  return resolve(value).replaceAll("\\", "/");
}

export function loadEnvFile(path) {
  if (!existsSync(path)) return;
  for (const rawLine of readFileSync(path, "utf8").split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) continue;
    const separator = line.indexOf("=");
    if (separator < 1) continue;
    const key = line.slice(0, separator).trim();
    let value = line.slice(separator + 1).trim();
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    if (!(key in process.env)) process.env[key] = value;
  }
}

export function parseFrontmatter(text) {
  const normalized = text.replace(/^\uFEFF/, "");
  const match = normalized.match(/^---\s*\r?\n([\s\S]*?)\r?\n---(?:\s*\r?\n|$)/);
  if (!match) return {};
  const result = {};
  for (const line of match[1].split(/\r?\n/)) {
    const item = line.match(/^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*?)\s*$/);
    if (!item) continue;
    result[item[1]] = item[2].replace(/^("|')|("|')$/g, "");
  }
  return result;
}

const SNAPSHOT_IGNORED_DIRECTORIES = new Set([".git", ".venv", "venv", "node_modules", "__pycache__"]);

function fileDigest(path) {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}

export function snapshotProtectedProjectState(projectRoot) {
  const root = resolve(projectRoot);
  const immutable = {};
  const existingMigrations = {};

  function walk(directory) {
    if (!existsSync(directory)) return;
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      if (entry.isSymbolicLink()) continue;
      if (entry.isDirectory() && SNAPSHOT_IGNORED_DIRECTORIES.has(entry.name)) continue;
      const path = resolve(directory, entry.name);
      if (entry.isDirectory()) {
        walk(path);
        continue;
      }
      if (!entry.isFile()) continue;
      const relative = toPortablePath(path).slice(toPortablePath(root).length + 1);
      const parts = relative.split("/");
      const name = parts.at(-1);
      const inImmutableDirectory = parts.includes(".codex") || parts.includes(".agents") || relative.startsWith("docs/architecture/");
      const immutableName = name === "AGENTS.md" || name === "opencode.json" || name === ".env" || name?.startsWith(".env.");
      if (inImmutableDirectory || immutableName) immutable[relative] = fileDigest(path);
      if (parts.includes("migrations") && name?.endsWith(".py")) existingMigrations[relative] = fileDigest(path);
    }
  }

  walk(root);
  return { immutable, existingMigrations };
}

export function compareProtectedProjectState(before, after) {
  const errors = [];
  const immutablePaths = new Set([...Object.keys(before.immutable), ...Object.keys(after.immutable)]);
  for (const path of immutablePaths) {
    if (!Object.hasOwn(before.immutable, path)) errors.push(`protected file was created during execution: ${path}`);
    else if (!Object.hasOwn(after.immutable, path)) errors.push(`protected file was removed during execution: ${path}`);
    else if (before.immutable[path] !== after.immutable[path]) errors.push(`protected file was modified during execution: ${path}`);
  }
  for (const [path, digest] of Object.entries(before.existingMigrations)) {
    if (!Object.hasOwn(after.existingMigrations, path)) errors.push(`existing migration was removed during execution: ${path}`);
    else if (after.existingMigrations[path] !== digest) errors.push(`existing migration was modified during execution: ${path}`);
  }
  return errors;
}

function isPlainObject(value) {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function checkObjectShape(errors, value, label, required, allowed = required) {
  if (!isPlainObject(value)) {
    errors.push(`${label} must be an object`);
    return false;
  }
  for (const key of required) {
    if (!Object.hasOwn(value, key)) errors.push(`${label} is missing required property ${key}`);
  }
  for (const key of Object.keys(value)) {
    if (!allowed.includes(key)) errors.push(`${label} has unsupported property ${key}`);
  }
  return true;
}

function fencedCommands(text) {
  return [...text.matchAll(/```(?:bash|powershell)\s*\r?\n([\s\S]*?)```/gi)]
    .flatMap((match) => match[1].split(/\r?\n/))
    .map((line) => line.trim())
    .filter((line) => line && !line.startsWith("#"));
}

function hasShellControl(value) {
  return /[;&|><`\r\n]|\$\(/.test(value);
}

export function validateBackendContractManifest(manifest, { requireApproved = true } = {}) {
  const errors = [];
  const contractIds = [];
  const contractRequiredTests = {};
  const validationCommands = {};
  const allValidationCommands = {};
  const allowedExecutionCommands = [];
  if (!checkObjectShape(
    errors,
    manifest,
    "backend contract manifest",
    ["contract_version", "status", "services", "environment_bindings", "invariants", "endpoints", "allowed_execution_commands", "required_validations"],
    ["$schema", "contract_version", "status", "services", "environment_bindings", "invariants", "endpoints", "allowed_execution_commands", "required_validations"],
  )) return { errors, contractIds, contractRequiredTests, validationCommands, allValidationCommands, allowedExecutionCommands };

  if (Object.hasOwn(manifest, "$schema") && typeof manifest.$schema !== "string") errors.push("backend contract manifest $schema must be a string");
  if (!Number.isInteger(manifest.contract_version) || manifest.contract_version < 1) errors.push("backend contract manifest has no positive integer contract_version");
  if (!["pending-approval", "approved"].includes(manifest.status)) errors.push("backend contract manifest status is invalid");
  if (requireApproved && manifest.status !== "approved") errors.push("backend contract manifest status is not approved");

  const arrays = ["services", "environment_bindings", "invariants", "endpoints", "allowed_execution_commands", "required_validations"];
  for (const field of arrays) {
    if (!Array.isArray(manifest[field])) errors.push(`backend contract manifest ${field} must be an array`);
  }
  for (const field of ["services", "invariants", "endpoints", "required_validations"]) {
    if (Array.isArray(manifest[field]) && manifest[field].length === 0) errors.push(`backend contract manifest ${field} must be a non-empty array`);
  }

  const serviceIds = new Set();
  for (const service of Array.isArray(manifest.services) ? manifest.services : []) {
    if (!checkObjectShape(errors, service, "backend contract manifest service", ["id", "runtime", "local_port", "root_urlconf"])) continue;
    if (typeof service.id !== "string" || !/^[a-z][a-z0-9_-]*$/.test(service.id)) errors.push("backend contract manifest service has an invalid id");
    else if (serviceIds.has(service.id)) errors.push(`backend contract manifest contains duplicate service id ${service.id}`);
    else serviceIds.add(service.id);
    if (typeof service.runtime !== "string" || !service.runtime.trim()) errors.push(`backend contract manifest service ${service.id ?? "<missing>"} needs a runtime`);
    if (typeof service.runtime === "string" && service.runtime.toLowerCase().includes("django")) {
      if (typeof service.root_urlconf !== "string" || !/^[a-zA-Z_][a-zA-Z0-9_.]*\.urls$/.test(service.root_urlconf)) errors.push(`backend contract manifest Django service ${service.id ?? "<missing>"} requires root_urlconf`);
    } else if (service.root_urlconf !== null) errors.push(`backend contract manifest non-Django service ${service.id ?? "<missing>"} must use root_urlconf null`);
    if (service.local_port !== null && (!Number.isInteger(service.local_port) || service.local_port < 1 || service.local_port > 65535)) {
      errors.push(`backend contract manifest service ${service.id ?? "<missing>"} has invalid local_port`);
    }
  }

  const bindingVariables = new Set();
  for (const binding of Array.isArray(manifest.environment_bindings) ? manifest.environment_bindings : []) {
    if (!checkObjectShape(errors, binding, "backend contract manifest environment binding", ["variable", "target_service", "url_role", "expected_url", "env_files"])) continue;
    if (typeof binding.variable !== "string" || !/^[A-Z][A-Z0-9_]*$/.test(binding.variable)) errors.push("backend contract manifest environment binding has an invalid variable");
    else if (bindingVariables.has(binding.variable)) errors.push(`backend contract manifest contains duplicate environment binding ${binding.variable}`);
    else bindingVariables.add(binding.variable);
    if (!serviceIds.has(binding.target_service)) errors.push(`backend contract manifest environment binding ${binding.variable ?? "<missing>"} targets an unknown service`);
    if (!["base_url", "callback_url", "public_url", "internal_url"].includes(binding.url_role)) errors.push(`backend contract manifest environment binding ${binding.variable ?? "<missing>"} has invalid url_role`);
    if (typeof binding.expected_url !== "string" || !/^https?:\/\//.test(binding.expected_url)) errors.push(`backend contract manifest environment binding ${binding.variable ?? "<missing>"} has invalid expected_url`);
    if (!Array.isArray(binding.env_files) || !binding.env_files.length || binding.env_files.some((value) => typeof value !== "string" || !value)) errors.push(`backend contract manifest environment binding ${binding.variable ?? "<missing>"} requires env_files`);
  }

  const seenContractIds = new Set();
  for (const invariant of Array.isArray(manifest.invariants) ? manifest.invariants : []) {
    if (!checkObjectShape(errors, invariant, "backend contract manifest invariant", ["id", "statement", "enforcement", "required_tests"])) continue;
    const id = invariant.id;
    if (typeof id !== "string" || !/^[A-Z][A-Z0-9_-]*-[0-9]{3}$/.test(id)) errors.push("backend contract manifest invariant has an invalid ID");
    else if (seenContractIds.has(id)) errors.push(`backend contract manifest contains duplicate contract ID ${id}`);
    else {
      seenContractIds.add(id);
      contractIds.push(id);
    }
    if (typeof invariant.statement !== "string" || invariant.statement.length < 12) errors.push(`backend contract manifest invariant ${id ?? "<missing>"} needs a meaningful statement`);
    if (!Array.isArray(invariant.enforcement) || !invariant.enforcement.length || invariant.enforcement.some((value) => typeof value !== "string" || !value)) errors.push(`backend contract manifest invariant ${id ?? "<missing>"} requires enforcement paths`);
    if (!Array.isArray(invariant.required_tests) || !invariant.required_tests.length || invariant.required_tests.some((value) => typeof value !== "string" || !/^test_[a-z0-9_]+$/.test(value))) errors.push(`backend contract manifest invariant ${id ?? "<missing>"} requires exact test_* names`);
    else if (typeof id === "string") contractRequiredTests[id] = [...invariant.required_tests];
  }

  for (const endpoint of Array.isArray(manifest.endpoints) ? manifest.endpoints : []) {
    if (!checkObjectShape(errors, endpoint, "backend contract manifest endpoint", ["id", "method", "path", "controller", "request_dto", "response_dto", "mapper", "service", "repositories", "required_tests"])) continue;
    const id = endpoint.id;
    if (typeof id !== "string" || !/^API-[0-9]{3}$/.test(id)) errors.push("backend contract manifest endpoint has an invalid ID");
    else if (seenContractIds.has(id)) errors.push(`backend contract manifest contains duplicate contract ID ${id}`);
    else {
      seenContractIds.add(id);
      contractIds.push(id);
    }
    if (!["GET", "POST", "PUT", "PATCH", "DELETE"].includes(endpoint.method)) errors.push(`backend contract manifest endpoint ${id ?? "<missing>"} has an invalid method`);
    if (typeof endpoint.path !== "string" || !endpoint.path.startsWith("/")) errors.push(`backend contract manifest endpoint ${id ?? "<missing>"} has an invalid path`);
    for (const field of ["controller", "service"]) {
      if (typeof endpoint[field] !== "string" || !endpoint[field].includes(".")) errors.push(`backend contract manifest endpoint ${id ?? "<missing>"}.${field} needs a dotted path`);
    }
    for (const field of ["request_dto", "response_dto", "mapper"]) {
      if (endpoint[field] !== null && (typeof endpoint[field] !== "string" || !endpoint[field].includes("."))) errors.push(`backend contract manifest endpoint ${id ?? "<missing>"}.${field} must be null or a dotted path`);
    }
    if (!Array.isArray(endpoint.repositories) || endpoint.repositories.some((value) => typeof value !== "string" || !value)) errors.push(`backend contract manifest endpoint ${id ?? "<missing>"}.repositories must be an array of dotted paths`);
    if (!Array.isArray(endpoint.required_tests) || !endpoint.required_tests.length || endpoint.required_tests.some((value) => typeof value !== "string" || !/^test_[a-z0-9_]+$/.test(value))) errors.push(`backend contract manifest endpoint ${id ?? "<missing>"} requires exact test_* names`);
    else if (typeof id === "string") contractRequiredTests[id] = [...endpoint.required_tests];
  }

  for (const command of Array.isArray(manifest.allowed_execution_commands) ? manifest.allowed_execution_commands : []) {
    if (typeof command !== "string" || !/^(?:python3?|py) manage\.py makemigrations(?: [A-Za-z0-9_.=:/-]+)+$/.test(command) || hasShellControl(command)) {
      errors.push("backend contract manifest allowed_execution_commands may contain only exact, non-compound Django makemigrations commands");
    } else {
      allowedExecutionCommands.push(command);
    }
  }

  const validationIds = new Set();
  for (const validation of Array.isArray(manifest.required_validations) ? manifest.required_validations : []) {
    if (!checkObjectShape(errors, validation, "backend contract manifest validation", ["id", "kind", "command", "required"])) continue;
    const id = validation.id;
    if (typeof id !== "string" || !/^VAL-[0-9]{3}$/.test(id)) errors.push("backend contract manifest validation has an invalid ID");
    else if (validationIds.has(id)) errors.push(`backend contract manifest contains duplicate validation ID ${id}`);
    else validationIds.add(id);
    if (!["check", "test", "scan", "migration", "integration", "browser"].includes(validation.kind)) errors.push(`backend contract manifest validation ${id ?? "<missing>"} has invalid kind`);
    if (typeof validation.command !== "string" || !validation.command.trim()) errors.push(`backend contract manifest validation ${id ?? "<missing>"} requires a command`);
    else if (hasShellControl(validation.command)) errors.push(`backend contract manifest validation ${id ?? "<missing>"} command contains shell control operators`);
    if (typeof validation.required !== "boolean") errors.push(`backend contract manifest validation ${id ?? "<missing>"} requires a boolean required flag`);
    if (typeof id === "string" && typeof validation.command === "string" && validation.command) allValidationCommands[id] = validation.command;
    if (validation.required === true && typeof id === "string" && typeof validation.command === "string") validationCommands[id] = validation.command;
  }

  return { errors, contractIds, contractRequiredTests, validationCommands, allValidationCommands, allowedExecutionCommands };
}

export function checkContractPreflight(projectRoot) {
  const root = resolve(projectRoot);
  const missing = REQUIRED_CONTRACTS.filter((relativePath) => !existsSync(resolve(root, relativePath)));
  const implementationPath = resolve(root, "docs/architecture/backend-implementation-contract.md");
  const manifestPath = resolve(root, "docs/architecture/backend-contract-manifest.json");
  const errors = missing.map((path) => `missing required contract: ${path}`);
  let contractVersion = null;
  let contractIds = [];
  let contractRequiredTests = {};
  let validationCommands = {};
  let allValidationCommands = {};
  let allowedExecutionCommands = [];

  if (existsSync(implementationPath)) {
    const metadata = parseFrontmatter(readFileSync(implementationPath, "utf8"));
    if (String(metadata.status ?? "").toLowerCase() !== "approved") {
      errors.push("backend implementation contract status is not approved");
    }
    contractVersion = Number(metadata.contract_version);
    if (!Number.isInteger(contractVersion) || contractVersion < 1) {
      errors.push("backend implementation contract has no positive integer contract_version");
      contractVersion = null;
    }
    if (!/^\d{4}-\d{2}-\d{2}/.test(String(metadata.approved_at ?? ""))) {
      errors.push("backend implementation contract has no approved_at date");
    }
  }

  for (const relativePath of REQUIRED_CONTRACTS.filter((value) => value.endsWith(".md"))) {
    const contractPath = resolve(root, relativePath);
    if (!existsSync(contractPath)) continue;
    if (/\{\{|replace[_-]me/i.test(readFileSync(contractPath, "utf8"))) {
      errors.push(`${relativePath} contains unresolved template values`);
    }
  }

  if (existsSync(manifestPath)) {
    try {
      const rawManifest = readFileSync(manifestPath, "utf8");
      const manifest = JSON.parse(rawManifest);
      const manifestValidation = validateBackendContractManifest(manifest);
      errors.push(...manifestValidation.errors);
      if (Number.isInteger(manifest.contract_version) && contractVersion && manifest.contract_version !== contractVersion) {
        errors.push("backend contract manifest version does not match implementation contract");
      }
      contractIds = manifestValidation.contractIds;
      contractRequiredTests = manifestValidation.contractRequiredTests;
      validationCommands = manifestValidation.validationCommands;
      allValidationCommands = manifestValidation.allValidationCommands;
      allowedExecutionCommands = manifestValidation.allowedExecutionCommands;
      const validationPlanPath = resolve(root, "docs/architecture/backend-validation-plan.md");
      if (existsSync(validationPlanPath)) {
        const plannedCommands = new Set(fencedCommands(readFileSync(validationPlanPath, "utf8")));
        const manifestCommands = new Set(
          (Array.isArray(manifest.required_validations) ? manifest.required_validations : [])
            .map((item) => item?.command)
            .filter((command) => typeof command === "string" && command),
        );
        for (const command of manifestCommands) {
          if (!plannedCommands.has(command)) errors.push(`backend-validation-plan.md is missing manifest command: ${command}`);
        }
        for (const command of plannedCommands) {
          if (!manifestCommands.has(command)) errors.push(`backend-validation-plan.md has a command absent from the manifest: ${command}`);
        }
      }
      if (/\{\{|replace[_-]me/i.test(rawManifest)) {
        errors.push("backend contract manifest contains unresolved template values");
      }
    } catch (error) {
      errors.push(`backend contract manifest is invalid JSON: ${error.message}`);
    }
  }

  return { ok: errors.length === 0, errors, contractVersion, contractIds, contractRequiredTests, validationCommands, allValidationCommands, allowedExecutionCommands };
}

export function runCapture(command, args, options = {}) {
  const timeoutMs = options.timeoutMs ?? 15_000;
  return new Promise((resolvePromise) => {
    let stdout = "";
    let stderr = "";
    let timedOut = false;
    let settled = false;
    let child;
    try {
      child = spawn(command, args, {
        cwd: options.cwd,
        env: options.env ?? process.env,
        windowsHide: true,
        shell: false,
      });
    } catch (error) {
      resolvePromise({ code: null, stdout, stderr: `${stderr}${error.message}`, timedOut: false });
      return;
    }
    const timer = setTimeout(() => {
      timedOut = true;
      child.kill();
    }, timeoutMs);
    child.stdout?.on("data", (chunk) => { stdout += chunk.toString(); });
    child.stderr?.on("data", (chunk) => { stderr += chunk.toString(); });
    child.on("error", (error) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      resolvePromise({ code: null, stdout, stderr: `${stderr}${error.message}`, timedOut });
    });
    child.on("close", (code) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      resolvePromise({ code, stdout, stderr, timedOut });
    });
  });
}

export async function inspectOpenCode({ command, model }) {
  const executable = resolveExecutable(command || "opencode");
  const version = await runCapture(executable, ["--version"]);
  if (version.code !== 0) {
    return {
      ready: false,
      installed: false,
      authenticated: false,
      modelAvailable: false,
      version: null,
      command: executable,
      reasons: ["OpenCode CLI is not installed or not executable"],
    };
  }

  const auth = await runCapture(executable, ["auth", "list"]);
  const authText = stripAnsi(`${auth.stdout}\n${auth.stderr}`);
  const authenticated = auth.code === 0 && /opencode(?:[ -]?go)/i.test(authText) && !/0 credentials/i.test(authText);
  const models = await runCapture(executable, ["models", "opencode-go"], { timeoutMs: 30_000 });
  const modelsText = stripAnsi(`${models.stdout}\n${models.stderr}`);
  const modelAvailable = models.code === 0 && modelsText.split(/\r?\n/).some((line) => line.trim() === model);
  const reasons = [];
  if (!authenticated) reasons.push("OpenCode Go is not authenticated in the current operating environment");
  if (!modelAvailable) reasons.push(`configured model is unavailable: ${model}`);

  return {
    ready: authenticated && modelAvailable,
    installed: true,
    authenticated,
    modelAvailable,
    version: stripAnsi(version.stdout).trim(),
    command: executable,
    reasons,
  };
}

export async function resolvePythonCommand(preferred = process.env.KARYA_PYTHON_COMMAND) {
  const candidates = [...new Set([
    preferred,
    ...(process.platform === "win32" ? ["python", "py"] : ["python3", "python"]),
  ].filter(Boolean))];
  for (const candidate of candidates) {
    const result = await runCapture(candidate, ["--version"]);
    if (result.code === 0) return candidate;
  }
  return candidates[0] ?? "python";
}

export function validateCompletion(
  value,
  expectedContractVersion,
  expectedContractIds = [],
  expectedValidationCommands = {},
  expectedContractRequiredTests = {},
  expectedTaskId = null,
  expectedAllowedValidationCommands = expectedValidationCommands,
  expectedAllowedExecutionCommands = [],
) {
  const errors = [];
  if (!value || typeof value !== "object" || Array.isArray(value)) return ["completion must be a JSON object"];
  checkObjectShape(
    errors,
    value,
    "completion",
    ["task_id", "contract_version", "status", "changed_files", "commands", "generated_migrations", "tests", "architecture_scan", "contract_evidence", "validation_evidence", "contract_deviations", "unresolved_items", "validation_limitations"],
  );
  const stringFields = ["task_id", "status"];
  for (const field of stringFields) if (typeof value[field] !== "string" || !value[field]) errors.push(`${field} must be a non-empty string`);
  if (expectedTaskId && value.task_id !== expectedTaskId) errors.push("completion task_id does not match the active run");
  if (!Number.isInteger(value.contract_version) || value.contract_version < 1) errors.push("contract_version must be a positive integer");
  if (expectedContractVersion && value.contract_version !== expectedContractVersion) errors.push("completion contract_version does not match approved contract");
  if (!["completed", "blocked", "failed", "contract-review-required"].includes(value.status)) errors.push("status is invalid");
  for (const field of ["changed_files", "commands", "generated_migrations", "tests", "contract_deviations", "unresolved_items", "validation_limitations"]) {
    if (!Array.isArray(value[field])) errors.push(`${field} must be an array`);
  }
  if (Array.isArray(value.commands)) {
    const allowedCommands = new Set([
      ...Object.values(expectedAllowedValidationCommands),
      ...expectedAllowedExecutionCommands,
    ]);
    const commandResults = new Map();
    for (const evidence of value.commands) {
      if (!checkObjectShape(errors, evidence, "command evidence", ["command", "result", "exit_code", "notes"])) continue;
      if (typeof evidence.command !== "string" || !evidence.command) errors.push("command evidence.command must be a non-empty string");
      else {
        if (allowedCommands.size && !allowedCommands.has(evidence.command)) errors.push(`command evidence contains unapproved command: ${evidence.command}`);
        commandResults.set(evidence.command, evidence);
      }
      if (!["passed", "failed", "not-run"].includes(evidence.result)) errors.push("command evidence.result is invalid");
      if (!Number.isInteger(evidence.exit_code) && evidence.exit_code !== null) errors.push("command evidence.exit_code must be an integer or null");
      if (!Array.isArray(evidence.notes)) errors.push("command evidence.notes must be an array");
      if (evidence.result === "passed" && evidence.exit_code !== 0) errors.push(`passing command evidence requires exit_code 0: ${evidence.command}`);
    }
    if (value.status === "completed") {
      for (const command of Object.values(expectedValidationCommands)) {
        const evidence = commandResults.get(command);
        if (!evidence || evidence.result !== "passed" || evidence.exit_code !== 0) {
          errors.push(`completed status requires passing command evidence for: ${command}`);
        }
      }
    }
  }
  if (!value.architecture_scan || typeof value.architecture_scan !== "object" || Array.isArray(value.architecture_scan)) {
    errors.push("architecture_scan must be an object");
  }
  if (!value.contract_evidence || typeof value.contract_evidence !== "object" || Array.isArray(value.contract_evidence)) {
    errors.push("contract_evidence must be an object");
  } else {
    const expectedIds = new Set(expectedContractIds);
    for (const id of value.status === "completed" ? expectedContractIds : []) {
      if (!value.contract_evidence[id] || typeof value.contract_evidence[id] !== "object") {
        errors.push(`contract_evidence is missing ${id}`);
      }
    }
    for (const [id, evidence] of Object.entries(value.contract_evidence)) {
      if (expectedIds.size && !expectedIds.has(id)) errors.push(`contract_evidence contains unknown contract ID ${id}`);
      if (!checkObjectShape(errors, evidence, `contract_evidence ${id}`, ["implementation", "tests", "result", "notes"])) continue;
      for (const field of ["implementation", "tests", "notes"]) {
        if (!Array.isArray(evidence[field])) errors.push(`contract_evidence ${id}.${field} must be an array`);
      }
      if (!["passed", "failed", "not-run", "not-applicable"].includes(evidence.result)) {
        errors.push(`contract_evidence ${id}.result is invalid`);
      }
      if (evidence.result === "passed" && (!evidence.implementation?.length || !evidence.tests?.length)) {
        errors.push(`passing contract_evidence for ${id} requires implementation and tests`);
      }
      for (const requiredTest of expectedContractRequiredTests[id] ?? []) {
        if (evidence.result === "passed" && !evidence.tests?.includes(requiredTest)) {
          errors.push(`passing contract_evidence for ${id} is missing required test ${requiredTest}`);
        }
      }
      if (value.status === "completed" && evidence.result !== "passed") {
        errors.push(`completed status requires passing contract_evidence for ${id}`);
      }
    }
  }
  if (!value.validation_evidence || typeof value.validation_evidence !== "object" || Array.isArray(value.validation_evidence)) {
    errors.push("validation_evidence must be an object");
  } else {
    for (const id of Object.keys(value.status === "completed" ? expectedValidationCommands : {})) {
      const evidence = value.validation_evidence[id];
      if (!evidence || typeof evidence !== "object" || Array.isArray(evidence)) {
        errors.push(`validation_evidence is missing ${id}`);
      }
    }
    for (const [id, evidence] of Object.entries(value.validation_evidence)) {
      if (!Object.hasOwn(expectedAllowedValidationCommands, id) && Object.keys(expectedAllowedValidationCommands).length) {
        errors.push(`validation_evidence contains unknown validation ID ${id}`);
      }
      if (!checkObjectShape(errors, evidence, `validation_evidence ${id}`, ["command", "result", "exit_code", "notes"])) continue;
      const command = expectedAllowedValidationCommands[id];
      if (evidence.command !== command) errors.push(`validation_evidence ${id}.command does not match manifest`);
      if (!["passed", "failed", "not-run"].includes(evidence.result)) {
        errors.push(`validation_evidence ${id}.result is invalid`);
      }
      if (!Number.isInteger(evidence.exit_code) && evidence.exit_code !== null) {
        errors.push(`validation_evidence ${id}.exit_code must be an integer or null`);
      }
      if (!Array.isArray(evidence.notes)) errors.push(`validation_evidence ${id}.notes must be an array`);
      if (evidence.result === "passed" && evidence.exit_code !== 0) {
        errors.push(`passing validation_evidence for ${id} requires exit_code 0`);
      }
      if (value.status === "completed" && evidence.result !== "passed") {
        errors.push(`completed status requires passing validation_evidence for ${id}`);
      }
    }
  }
  return errors;
}
