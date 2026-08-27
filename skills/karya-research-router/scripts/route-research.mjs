import fs from "node:fs";
import { pathToFileURL } from "node:url";

const INTENTS = new Set([
  "targeted_web",
  "broad_web",
  "app_market",
  "scientific",
  "platform_native",
  "mixed",
]);

function providerReady(provider, env) {
  if (provider === "perplexity") return Boolean(env.PERPLEXITY_API_KEY);
  if (provider === "manus") return Boolean(env.MANUS_API_KEY);
  return true;
}

function routeOne(intent, permissions, env) {
  const perplexityAllowed = permissions.perplexity_allowed === true;
  const manusAllowed = permissions.manus_allowed === true;

  if (intent === "targeted_web") {
    return { primary: ["codex"], fallback: [], status: "ready", reason: "Codex is the default for bounded primary-source web research." };
  }
  if (intent === "broad_web") {
    if (perplexityAllowed && providerReady("perplexity", env)) {
      return { primary: ["perplexity", "codex_audit"], fallback: ["codex_batched"], status: "ready", reason: "Perplexity is allowed for broad discovery; Codex audits original sources." };
    }
    return { primary: ["codex_batched"], fallback: [], status: "limited", reason: "Perplexity is unavailable or not approved; use narrower Codex batches." };
  }
  if (intent === "app_market") {
    return { primary: ["app-market-intelligence-analyst", "appstoretracker", "apple"], fallback: ["apple", "coverage_gap"], status: "ready", reason: "AppStoreTracker supplies directional iOS market estimates and Apple confirms identity." };
  }
  if (intent === "scientific") {
    return { primary: ["openalex", "original_papers", "codex"], fallback: ["codex_primary_source_search"], status: env.OPENALEX_API_KEY ? "ready" : "limited", reason: env.OPENALEX_API_KEY ? "OpenAlex is configured for scholarly discovery." : "OpenAlex key is missing; anonymous access may be limited." };
  }
  if (intent === "platform_native") {
    if (manusAllowed && providerReady("manus", env)) {
      return { primary: ["manus-platform-researcher"], fallback: ["human_assisted_browser"], status: "ready", reason: "Manus is approved and configured for read-only platform-native research." };
    }
    return { primary: ["human_assisted_browser"], fallback: [], status: "manual_required", reason: "Manus is unavailable or not approved; authenticated platform research needs a human-assisted session." };
  }
  throw new Error(`Unsupported task intent: ${intent}`);
}

export function buildRoute(request, env = process.env) {
  if (!request || typeof request !== "object") throw new Error("Request must be a JSON object.");
  if (!request.request_id) throw new Error("request_id is required.");
  if (!INTENTS.has(request.intent)) throw new Error(`intent must be one of: ${[...INTENTS].join(", ")}`);
  if (!["rapid", "standard", "deep"].includes(request.depth)) throw new Error("depth must be rapid, standard, or deep.");

  const permissions = request.permissions ?? {};
  const rawTasks = request.intent === "mixed" ? request.tasks : [{ task_id: "TASK-001", intent: request.intent, evidence_class: request.evidence_class ?? request.intent, limits: request.limits ?? {} }];
  if (!Array.isArray(rawTasks) || rawTasks.length === 0) throw new Error("mixed intent requires at least one task.");

  const tasks = rawTasks.map((task, index) => {
    if (!task.intent || task.intent === "mixed") throw new Error(`tasks[${index}].intent must be a concrete intent.`);
    const route = routeOne(task.intent, permissions, env);
    return {
      task_id: task.task_id ?? `TASK-${String(index + 1).padStart(3, "0")}`,
      evidence_class: task.evidence_class ?? task.intent,
      ...route,
      limits: task.limits ?? request.limits ?? {},
    };
  });

  return {
    schema_version: "1.0",
    request_id: request.request_id,
    intent: request.intent,
    depth: request.depth,
    tasks,
    warnings: [
      "Providers are retrieval mechanisms, not independent evidence sources.",
      "This route does not start an MVP, marketing workflow, or external platform action.",
    ],
  };
}

function main() {
  const path = process.argv[2];
  if (!path) throw new Error("Usage: node route-research.mjs <request.json>");
  const request = JSON.parse(fs.readFileSync(path, "utf8"));
  process.stdout.write(`${JSON.stringify(buildRoute(request), null, 2)}\n`);
}

if (process.argv[1] && pathToFileURL(process.argv[1]).href === import.meta.url) {
  try { main(); } catch (error) { process.stderr.write(`${error.message}\n`); process.exitCode = 1; }
}
