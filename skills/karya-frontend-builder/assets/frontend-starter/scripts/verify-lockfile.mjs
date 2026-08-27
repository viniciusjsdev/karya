#!/usr/bin/env node

import fs from "node:fs";
import process from "node:process";

const errors = [];
const packageJson = readJson("package.json");
const lockfile = readJson("package-lock.json");
const npmrc = fs.readFileSync(".npmrc", "utf8");

function readJson(file) {
  try {
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch (error) {
    errors.push(`${file} could not be parsed: ${error.message}`);
    return {};
  }
}

function packageNameFromLockPath(lockPath) {
  return lockPath.split("node_modules/").at(-1);
}

function isExactRegistryVersion(specifier) {
  return /^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$/.test(specifier);
}

if (lockfile.lockfileVersion !== 3) {
  errors.push("package-lock.json must use lockfileVersion 3.");
}

if (packageJson.packageManager !== "npm@11.18.0") {
  errors.push("packageManager must pin the reviewed npm CLI version.");
}

for (const setting of [
  "registry=https://registry.npmjs.org/",
  "save-exact=true",
  "package-lock=true",
  "ignore-scripts=true",
  "strict-allow-scripts=true",
  "min-release-age=7",
  "allow-git=none",
  "allow-remote=none",
  "allow-file=none",
  "allow-directory=none"
]) {
  if (!npmrc.includes(setting)) errors.push(`.npmrc is missing ${setting}.`);
}

for (const section of ["dependencies", "devDependencies", "optionalDependencies"]) {
  for (const [name, specifier] of Object.entries(packageJson[section] ?? {})) {
    if (!isExactRegistryVersion(specifier)) {
      errors.push(`${section}.${name} is not pinned to an exact registry version: ${specifier}`);
    }
  }
}

for (const [lockPath, metadata] of Object.entries(lockfile.packages ?? {})) {
  if (!lockPath) continue;
  const name = packageNameFromLockPath(lockPath);

  if (metadata.resolved) {
    const resolved = new URL(metadata.resolved);
    if (resolved.protocol !== "https:" || resolved.hostname !== "registry.npmjs.org") {
      errors.push(`${name}@${metadata.version} resolves outside the approved npm registry.`);
    }
    if (!metadata.integrity?.startsWith("sha512-")) {
      errors.push(`${name}@${metadata.version} is missing sha512 integrity metadata.`);
    }
  }

  if (metadata.hasInstallScript) {
    const approval = `${name}@${metadata.version}`;
    if (packageJson.allowScripts?.[approval] !== true) {
      errors.push(`${approval} has an install script but is not explicitly approved.`);
    }
  }
}

if (errors.length) {
  console.error("npm supply-chain verification failed:");
  errors.forEach((error) => console.error(`- ${error}`));
  process.exitCode = 1;
} else {
  console.log(
    "ok: lockfile sources, integrity hashes, exact versions, and install scripts are approved."
  );
}
