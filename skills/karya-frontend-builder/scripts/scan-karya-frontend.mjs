#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const root = process.cwd();
const strict = process.argv.includes("--strict");
const warnings = [];
const info = [];
const sourceExtensions = new Set([".ts", ".tsx", ".js", ".jsx"]);
const ignoredDirectories = new Set([
  "node_modules",
  ".git",
  "dist",
  "build",
  "coverage",
  ".vite",
  "playwright-report",
  "test-results",
]);

const resolve = (relativePath) => path.join(root, relativePath);
const exists = (relativePath) => fs.existsSync(resolve(relativePath));

function findProjectRoot() {
  return [root, path.dirname(root)].find(
    (candidate) =>
      fs.existsSync(path.join(candidate, ".codex")) &&
      fs.existsSync(path.join(candidate, "AGENTS.md")),
  );
}

function readJson(relativePath) {
  try {
    return JSON.parse(fs.readFileSync(resolve(relativePath), "utf8"));
  } catch {
    return null;
  }
}

function readText(relativePath) {
  try {
    return fs.readFileSync(resolve(relativePath), "utf8");
  } catch {
    return "";
  }
}

function walk(directory) {
  if (!fs.existsSync(directory)) return [];
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    if (ignoredDirectories.has(entry.name)) return [];
    const fullPath = path.join(directory, entry.name);
    if (entry.isDirectory()) return walk(fullPath);
    return sourceExtensions.has(path.extname(entry.name)) ? [fullPath] : [];
  });
}

function relative(file) {
  return path.relative(root, file).replaceAll("\\", "/");
}

function isUiFile(file) {
  return (
    /\/(?:pages|components|routes)\//.test(`/${file}`) ||
    /Page\.tsx?$/.test(file)
  );
}

function analyzePackage() {
  const pkg = readJson("package.json");
  if (!pkg) {
    warnings.push(
      "package.json not found; run the scanner from the frontend root.",
    );
    return;
  }

  const deps = { ...pkg.dependencies, ...pkg.devDependencies };
  const required = [
    ["react", "React"],
    ["typescript", "TypeScript"],
    ["vite", "Vite"],
    ["react-router-dom", "React Router"],
    ["primereact", "PrimeReact"],
    ["primeicons", "PrimeIcons"],
    ["@tanstack/react-query", "TanStack Query"],
    ["axios", "Axios"],
    ["react-hook-form", "React Hook Form"],
    ["zod", "Zod"],
    ["vitest", "Vitest"],
  ];

  const missing = required
    .filter(([name]) => !deps[name])
    .map(([, label]) => label);
  info.push(
    `Detected ${required.length - missing.length}/${required.length} baseline dependencies.`,
  );
  if (missing.length)
    warnings.push(`Missing baseline dependencies: ${missing.join(", ")}.`);

  const forbidden = [
    ["react-scripts", "Create React App"],
    ["@craco/craco", "CRACO"],
    ["tailwindcss", "Tailwind CSS"],
    ["styled-components", "Styled Components"],
    ["redux", "Redux"],
    ["zustand", "Zustand"],
  ].filter(([name]) => deps[name]);
  if (forbidden.length) {
    warnings.push(
      `Non-baseline dependencies require a documented exception: ${forbidden.map(([, label]) => label).join(", ")}.`,
    );
  }

  for (const [name, specifier] of Object.entries(deps)) {
    if (!/^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$/.test(specifier)) {
      warnings.push(
        `${name}: direct dependency is not pinned to an exact version (${specifier}).`,
      );
    }
  }

  if (!/^npm@11\.18\./.test(pkg.packageManager ?? "")) {
    warnings.push("packageManager must pin the approved npm 11.18.x CLI.");
  }

  const npmrc = readText(".npmrc");
  const requiredNpmConfig = [
    "registry=https://registry.npmjs.org/",
    "save-exact=true",
    "package-lock=true",
    "strict-peer-deps=true",
    "engine-strict=true",
    "audit-level=high",
    "ignore-scripts=true",
    "strict-allow-scripts=true",
    "min-release-age=7",
    "allow-git=none",
    "allow-remote=none",
    "allow-file=none",
    "allow-directory=none",
  ];
  for (const config of requiredNpmConfig) {
    if (!npmrc.includes(config))
      warnings.push(`Missing secure .npmrc config: ${config}.`);
  }

  const locks = [
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "bun.lock",
    "bun.lockb",
  ].filter(exists);
  if (!locks.includes("package-lock.json"))
    warnings.push("package-lock.json not found; npm is the factory standard.");
  if (locks.length > 1)
    warnings.push(`Multiple lockfiles found: ${locks.join(", ")}.`);

  if (!pkg.scripts?.typecheck) warnings.push("Missing npm script: typecheck.");
  if (!pkg.scripts?.lint) warnings.push("Missing npm script: lint.");
  if (!pkg.scripts?.build) warnings.push("Missing npm script: build.");
  if (!pkg.scripts?.test) warnings.push("Missing npm script: test.");
  for (const script of [
    "security:lockfile",
    "security:scripts",
    "security:signatures",
    "security:audit",
    "security:sbom",
  ]) {
    if (!pkg.scripts?.[script]) warnings.push(`Missing npm script: ${script}.`);
  }
}

function analyzeStructure(files) {
  for (const folder of [
    "src/app",
    "src/routes",
    "src/features",
    "src/shared",
    "src/services",
  ]) {
    if (!exists(folder))
      warnings.push(`Missing architecture folder: ${folder}.`);
  }

  if (!exists("src/app/styles/tokens.scss"))
    warnings.push("Missing design tokens: src/app/styles/tokens.scss.");
  if (!exists(".env.example")) warnings.push("Missing .env.example.");

  const projectRoot = findProjectRoot();
  if (!projectRoot) {
    warnings.push(
      "Project-root Codex context not found at the frontend root or its parent.",
    );
  } else {
    info.push(`Project context: ${path.relative(root, projectRoot) || "."}`);
    for (const contextPath of [
      ".agents/skills",
      ".codex/references/stack.md",
      ".codex/references/frontend-architecture.md",
      ".codex/references/code-standards.md",
      ".codex/references/npm-supply-chain-security.md",
      ".codex/references/sites-composition.md",
      ".codex/workflows/frontend-development.md",
      ".codex/workflows/frontend-validation.md",
      ".codex/checklists/frontend-validation.md",
      ".codex/checklists/npm-security.md",
      ".codex/goals/mvp-goals.md",
      ".codex/templates/domain-skill-spec.md",
    ]) {
      if (!fs.existsSync(path.join(projectRoot, contextPath))) {
        warnings.push(`Missing project context: ${contextPath}.`);
      }
    }
  }
  for (const requiredFile of [
    "src/shared/components/AppErrorBoundary/AppErrorBoundary.tsx",
    "src/shared/components/RouteLoading/RouteLoading.tsx",
    "src/routes/NotFoundRoute.tsx",
    "src/services/storage/storage.adapter.ts",
    "scripts/verify-lockfile.mjs",
  ]) {
    if (!exists(requiredFile))
      warnings.push(`Missing baseline file: ${requiredFile}.`);
  }

  const jsSource = files.filter((file) =>
    [".js", ".jsx"].includes(path.extname(file)),
  );
  if (jsSource.length)
    warnings.push(
      `JavaScript source found in a TypeScript baseline: ${jsSource.slice(0, 5).map(relative).join(", ")}${jsSource.length > 5 ? "..." : ""}.`,
    );

  for (const file of files) {
    const rel = relative(file);
    const content = fs.readFileSync(file, "utf8");
    const lines = content.split(/\r?\n/).length;
    const ui = isUiFile(rel);
    const route =
      rel.startsWith("src/routes/") || rel.startsWith("src/app/router/");

    if (ui && lines > 250)
      warnings.push(
        `${rel}: ${lines} lines; review component responsibilities.`,
      );
    if (route && lines > 100)
      warnings.push(
        `${rel}: route/router module is ${lines} lines; keep route composition thin.`,
      );

    if (
      ui &&
      /from\s+["'][^"']*(?:mock|mocks|fixtures|fake-data)[^"']*["']/.test(
        content,
      )
    ) {
      warnings.push(`${rel}: UI imports mock data directly.`);
    }
    if (
      ui &&
      /\baxios\.(?:get|post|put|patch|delete)\s*\(|\bfetch\s*\(/.test(content)
    ) {
      warnings.push(
        `${rel}: UI calls HTTP directly; use a service/repository.`,
      );
    }
    if (ui && /\b(?:localStorage|sessionStorage)\./.test(content)) {
      warnings.push(
        `${rel}: UI accesses browser storage directly; use an adapter.`,
      );
    }
    if (ui && /\bimport\.meta\.env\b/.test(content)) {
      warnings.push(
        `${rel}: UI reads environment variables directly; parse them in app config.`,
      );
    }
    if (
      /\/hooks\//.test(`/${rel}`) &&
      /<([A-Z][A-Za-z0-9]*|[a-z][a-z0-9-]*)(?:\s|>|\/)/.test(content)
    ) {
      warnings.push(`${rel}: hook file appears to contain JSX.`);
    }
  }
}

function print() {
  console.log("Karya frontend architecture scan");
  console.log("======================================");
  info.forEach((item) => console.log(`info: ${item}`));

  if (!warnings.length) {
    console.log("ok: no architecture warnings found by the heuristic scan.");
    return;
  }

  console.log(`warnings: ${warnings.length}`);
  warnings.forEach((warning) => console.log(`- ${warning}`));
  console.log(
    "This scan is heuristic; review intentional exceptions in project documentation.",
  );
  if (strict) process.exitCode = 1;
}

analyzePackage();
const files = walk(resolve("src"));
if (!files.length) warnings.push("No source files found under src/.");
else analyzeStructure(files);
print();
