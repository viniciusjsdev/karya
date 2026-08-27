#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { buildHandoffPrompt, readState, resolveInside, updateState, validateCompletion, validatePreflight, validateReviewEvidence, writeJsonAtomic } from "./_runtime-core.mjs";

const args = process.argv.slice(2);
const option = (name) => { const index = args.indexOf(name); return index >= 0 ? args[index + 1] : null; };
const projectRootArg = option("--project-root");
const specArg = option("--spec");
const manifestArg = option("--manifest");
if (!projectRootArg || !specArg || !manifestArg) {
  process.stderr.write("Usage: node route-codex-runtime.mjs --project-root <root> --spec <SPEC.md> --manifest <SPEC.execution.json> [--policy <runtime-policy.json>] [--skills-root <root>] [--state <path>] [--sdk-module <module>] [--dry-run]\n");
  process.exit(2);
}

const projectRoot = path.resolve(projectRootArg);
const specPath = resolveInside(projectRoot, specArg, "Spec path");
const manifestPath = resolveInside(projectRoot, manifestArg, "Manifest path");
const statePath = resolveInside(projectRoot, option("--state") ?? ".codex/runtime/spec-threads.json", "State path");
const policyPath = resolveInside(projectRoot, option("--policy") ?? ".codex/references/runtime-policy.json", "Runtime policy path");
const skillsRoot = option("--skills-root") ?? (process.env.CODEX_HOME ? path.join(process.env.CODEX_HOME, "skills") : path.join(process.env.USERPROFILE ?? process.env.HOME ?? "", ".codex", "skills"));
const baseResult = { route: "preflight_blocked", spec_id: null, action: "none", model: null, reasoning: null, thread_id: null, completion_status: null, artifacts: {}, errors: [] };
let recovery = null;

try {
  const markdown = fs.readFileSync(specPath, "utf8");
  const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  const reviewRun = manifest.execution?.thread?.purpose === "review";
  const policy = JSON.parse(fs.readFileSync(policyPath, "utf8"));
  const state = readState(statePath);
  recovery = { manifest, state, statePath, thread: null };
  baseResult.spec_id = manifest.spec_id ?? null;
  baseResult.model = manifest.execution?.model ?? null;
  baseResult.reasoning = manifest.execution?.reasoning ?? null;
  const errors = validatePreflight({ markdown, manifest, policy, projectRoot, skillsRoot, state });
  const declaredCompletionSchema = resolveInside(projectRoot, manifest.completion?.schema_path ?? "", "Completion schema path");
  if (!fs.existsSync(declaredCompletionSchema)) errors.push(`declared completion schema does not exist: ${manifest.completion?.schema_path}`);
  let completionSchema = null;
  if (fs.existsSync(declaredCompletionSchema)) {
    try { completionSchema = JSON.parse(fs.readFileSync(declaredCompletionSchema, "utf8")); } catch (error) { errors.push(`completion schema is invalid JSON: ${error.message}`); }
  }
  if (errors.length) {
    baseResult.errors = errors;
    process.stdout.write(`${JSON.stringify(baseResult, null, 2)}\n`);
    process.exit(1);
  }

  const action = manifest.execution.thread.mode === "new" ? "start" : "resume";
  const prompt = buildHandoffPrompt(manifest, path.relative(projectRoot, specPath).replaceAll("\\", "/"), path.relative(projectRoot, manifestPath).replaceAll("\\", "/"));
  if (args.includes("--dry-run")) {
    process.stdout.write(`${JSON.stringify({ ...baseResult, route: "preview", action, errors: [], artifacts: { state: path.relative(projectRoot, statePath).replaceAll("\\", "/"), completion: manifest.completion.output_path, prompt } }, null, 2)}\n`);
    process.exit(0);
  }

  const sdkModuleArg = option("--sdk-module");
  const sdkModule = sdkModuleArg ? await import(pathToFileURL(path.resolve(sdkModuleArg)).href) : await import("@openai/codex-sdk");
  if (typeof sdkModule.Codex !== "function") throw new Error("SDK module does not export Codex");
  const codex = new sdkModule.Codex();
  const workingDirectory = resolveInside(projectRoot, manifest.execution.working_directory, "Working directory");
  const threadOptions = { model: manifest.execution.model, modelReasoningEffort: manifest.execution.reasoning, workingDirectory, sandboxMode: manifest.execution.sandbox_mode, approvalPolicy: manifest.execution.approval_policy };
  const thread = action === "start" ? codex.startThread(threadOptions) : codex.resumeThread(manifest.execution.thread.thread_id, threadOptions);
  recovery.thread = thread;
  const run = await thread.run(prompt, { outputSchema: completionSchema });
  const threadId = thread.id;
  if (!threadId) throw new Error("SDK did not expose a thread ID after the turn");
  writeJsonAtomic(statePath, updateState(state, manifest, threadId, "failed"));
  let completion;
  try { completion = JSON.parse(run.finalResponse); } catch (error) { throw new Error(`SDK finalResponse is not valid completion JSON: ${error.message}`); }
  completion.thread_id = threadId;
  completion.usage = run.usage ?? null;
  const completionErrors = reviewRun ? validateReviewEvidence(completion, manifest, threadId) : validateCompletion(completion, manifest, markdown, threadId, { projectRoot });
  if (completionErrors.length) {
    baseResult.route = "failed";
    baseResult.action = action;
    baseResult.thread_id = threadId;
    baseResult.completion_status = completion.status ?? null;
    baseResult.errors = completionErrors;
    process.stdout.write(`${JSON.stringify(baseResult, null, 2)}\n`);
    process.exit(1);
  }
  const completionPath = resolveInside(projectRoot, manifest.completion.output_path, "Completion output path");
  writeJsonAtomic(completionPath, completion);
  writeJsonAtomic(statePath, updateState(state, manifest, threadId, completion.status));
  const route = completion.status;
  process.stdout.write(`${JSON.stringify({ ...baseResult, route, action, thread_id: threadId, completion_status: completion.status, artifacts: { state: path.relative(projectRoot, statePath).replaceAll("\\", "/"), completion: path.relative(projectRoot, completionPath).replaceAll("\\", "/") }, errors: [] }, null, 2)}\n`);
} catch (error) {
  const recoverableThreadId = recovery?.thread?.id ?? null;
  if (recoverableThreadId) {
    baseResult.thread_id = recoverableThreadId;
    baseResult.action = recovery.manifest.execution.thread.mode === "new" ? "start" : "resume";
    try { writeJsonAtomic(recovery.statePath, updateState(recovery.state, recovery.manifest, recoverableThreadId, "failed")); }
    catch (stateError) { baseResult.errors.push(`unable to preserve thread mapping: ${stateError.message}`); }
  }
  baseResult.route = "failed";
  baseResult.errors.push(error.message);
  process.stdout.write(`${JSON.stringify(baseResult, null, 2)}\n`);
  process.exitCode = 1;
}
