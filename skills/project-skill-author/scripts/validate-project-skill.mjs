#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

function parseFrontmatter(text) {
  const match = text.replace(/^\uFEFF/, "").match(/^---\s*\r?\n([\s\S]*?)\r?\n---(?:\s*\r?\n|$)/);
  if (!match) return {};
  const result = {};
  for (const line of match[1].split(/\r?\n/)) {
    const item = line.match(/^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*?)\s*$/);
    if (item) result[item[1]] = item[2].replace(/^("|')|("|')$/g, "");
  }
  return result;
}
function placeholder(value) { return /(?:\bTBD\b|\bTODO\b|\{\{|<[^>]+>|replace[_ -]?me)/i.test(value); }

const args = process.argv.slice(2);
const option = (name) => { const index = args.indexOf(name); return index >= 0 ? args[index + 1] : null; };
const skillDirArg = args.find((item, index) => !item.startsWith("--") && args[index - 1] !== "--project-root");
if (!skillDirArg) {
  process.stderr.write("Usage: node validate-project-skill.mjs <skill-dir> [--project-root <root>] [--allow-any-path]\n");
  process.exit(2);
}
const skillDir = path.resolve(skillDirArg);
const projectRoot = path.resolve(option("--project-root") ?? path.join(skillDir, "../../.."));
const errors = [];
const skillPath = path.join(skillDir, "SKILL.md");
const yamlPath = path.join(skillDir, "agents", "openai.yaml");
if (!fs.existsSync(skillPath)) errors.push("SKILL.md is missing");
if (!fs.existsSync(yamlPath)) errors.push("agents/openai.yaml is missing");
if (!args.includes("--allow-any-path")) {
  const expectedRoot = path.resolve(projectRoot, ".agents", "skills");
  const relative = path.relative(expectedRoot, skillDir);
  if (relative.startsWith("..") || path.isAbsolute(relative) || relative === "") errors.push("project-local skill must be under .agents/skills/<skill-name>");
}
if (fs.existsSync(skillPath)) {
  const text = fs.readFileSync(skillPath, "utf8");
  const fm = parseFrontmatter(text);
  const folderName = path.basename(skillDir);
  if (fm.name !== folderName) errors.push("frontmatter name must match the skill folder");
  if (!/^[a-z0-9-]+$/.test(fm.name ?? "") || String(fm.name ?? "").length > 64) errors.push("skill name must be lowercase hyphen-case and at most 64 characters");
  if (!fm.description || !/\bUse when\b/i.test(fm.description) || !/\bDo not use\b/i.test(fm.description)) errors.push("description must include discriminating Use when and Do not use boundaries");
  for (const heading of ["Required Context", "Workflow", "Invariants", "Validation", "Boundaries"]) if (!new RegExp(`^## ${heading}$`, "im").test(text)) errors.push(`SKILL.md is missing ## ${heading}`);
  if (placeholder(text)) errors.push("SKILL.md contains unresolved placeholder text");
  if (/\b(password|api[_ -]?key|secret|cookie|recovery code)\s*[:=]\s*\S+/i.test(text)) errors.push("SKILL.md appears to contain credential material");
  for (const match of text.matchAll(/\[[^\]]+\]\(([^)]+)\)/g)) {
    const target = match[1];
    if (/^(?:https?:|#)/.test(target)) continue;
    const resolved = path.resolve(skillDir, target.split("#")[0]);
    if (!fs.existsSync(resolved)) errors.push(`linked local reference does not exist: ${target}`);
  }
}
process.stdout.write(`${JSON.stringify({ valid: errors.length === 0, skill: skillDir, errors }, null, 2)}\n`);
if (errors.length) process.exitCode = 1;
