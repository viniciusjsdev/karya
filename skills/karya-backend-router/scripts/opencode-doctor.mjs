#!/usr/bin/env node
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { inspectOpenCode, loadEnvFile } from "./_router-core.mjs";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const factoryRoot = resolve(scriptDir, "..", "..", "..");
const environmentFile = process.env.KARYA_ENV_FILE
  ? resolve(process.env.KARYA_ENV_FILE)
  : resolve(factoryRoot, ".env");
loadEnvFile(environmentFile);

const model = process.env.KARYA_OPENCODE_MODEL || "opencode-go/kimi-k2.7-code";
const command = process.env.KARYA_OPENCODE_COMMAND;
const report = await inspectOpenCode({ command, model });
process.stdout.write(`${JSON.stringify({ ...report, model }, null, 2)}\n`);
process.exitCode = report.ready ? 0 : 1;
