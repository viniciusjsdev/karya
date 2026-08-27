#!/usr/bin/env node

try {
  const sdk = await import("@openai/codex-sdk");
  process.stdout.write(`${JSON.stringify({ ready: typeof sdk.Codex === "function", node: process.version, sdk: "@openai/codex-sdk", required_version: "0.150.0" }, null, 2)}\n`);
  if (typeof sdk.Codex !== "function") process.exitCode = 1;
} catch (error) {
  process.stdout.write(`${JSON.stringify({ ready: false, node: process.version, sdk: "@openai/codex-sdk", required_version: "0.150.0", error: error.message, remedy: "Install the exact dependency in the codex-runtime-router skill directory." }, null, 2)}\n`);
  process.exitCode = 1;
}
