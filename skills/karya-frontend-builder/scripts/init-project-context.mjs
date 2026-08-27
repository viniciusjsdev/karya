#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const args = process.argv.slice(2);
const dryRun = args.includes("--dry-run");
const targetArgument = args.find((argument) => !argument.startsWith("--"));
const targetRoot = path.resolve(targetArgument ?? process.cwd());
const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const sourceRoot = path.resolve(
  scriptDirectory,
  "../assets/project-context-starter",
);
let created = 0;
let skipped = 0;

if (!fs.existsSync(sourceRoot)) {
  throw new Error(`Project context starter not found: ${sourceRoot}`);
}

const targetInsideSource = path.relative(sourceRoot, targetRoot);
if (
  targetInsideSource === "" ||
  (!targetInsideSource.startsWith("..") && !path.isAbsolute(targetInsideSource))
) {
  throw new Error(
    "Target root must not be the project-context starter or one of its descendants.",
  );
}

if (fs.existsSync(targetRoot) && !fs.statSync(targetRoot).isDirectory()) {
  throw new Error(`Target root is not a directory: ${targetRoot}`);
}

function copyMissing(sourceDirectory, targetDirectory) {
  if (!dryRun) fs.mkdirSync(targetDirectory, { recursive: true });

  for (const entry of fs.readdirSync(sourceDirectory, {
    withFileTypes: true,
  })) {
    const sourcePath = path.join(sourceDirectory, entry.name);
    const targetPath = path.join(targetDirectory, entry.name);

    if (entry.isDirectory()) {
      copyMissing(sourcePath, targetPath);
      continue;
    }

    if (fs.existsSync(targetPath)) {
      skipped += 1;
      console.log(`skip: ${path.relative(targetRoot, targetPath)}`);
      continue;
    }

    created += 1;
    console.log(
      `${dryRun ? "would create" : "create"}: ${path.relative(targetRoot, targetPath)}`,
    );
    if (!dryRun)
      fs.copyFileSync(sourcePath, targetPath, fs.constants.COPYFILE_EXCL);
  }
}

copyMissing(sourceRoot, targetRoot);
console.log(
  `Project context ${dryRun ? "preview" : "initialized"}: ${created} created, ${skipped} preserved.`,
);
