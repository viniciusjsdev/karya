#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const root = process.cwd();
const warnings = [];
const errors = [];

function exists(relativePath) {
  return fs.existsSync(path.join(root, relativePath));
}

function read(relativePath) {
  try {
    return fs.readFileSync(path.join(root, relativePath), "utf8");
  } catch {
    return "";
  }
}

function listFiles(relativeDirectory, predicate) {
  const absoluteDirectory = path.join(root, relativeDirectory);
  if (!fs.existsSync(absoluteDirectory)) return [];

  const files = [];
  const ignoredDirectories = new Set([".git", ".terraform", "node_modules", ".venv", "venv"]);

  function visit(absolutePath) {
    for (const entry of fs.readdirSync(absolutePath, { withFileTypes: true })) {
      if (entry.isDirectory() && ignoredDirectories.has(entry.name)) continue;
      const entryPath = path.join(absolutePath, entry.name);
      if (entry.isDirectory()) {
        visit(entryPath);
      } else {
        const relativePath = path.relative(root, entryPath).replaceAll("\\", "/");
        if (predicate(relativePath)) files.push(relativePath);
      }
    }
  }

  visit(absoluteDirectory);
  return files;
}

function warnMissing(file, reason) {
  if (!exists(file)) warnings.push(`${file} missing: ${reason}`);
}

function isSkillCatalogRepository() {
  return (
    exists("skills/karya-infra-orchestrator/SKILL.md") &&
    !exists("frontend") &&
    !exists("backend")
  );
}

function hasObviousSecret(content) {
  const patterns = [
    /SUPABASE_SERVICE_ROLE_KEY\s*=\s*(?!$|change-me|example|your-|<|REPLACE|xxx)[^\s#]+/i,
    /DJANGO_SECRET_KEY\s*=\s*(?!$|change-me|example|your-|<|REPLACE|xxx)[^\s#]+/i,
    /DATABASE_URL\s*=\s*postgres(?:ql)?:\/\/(?!postgres:postgres@db|user:password|example|<|REPLACE)[^\s#]+/i,
    /(?:API_KEY|TOKEN|SECRET)\s*=\s*(?!$|change-me|example|your-|<|REPLACE|xxx)[^\s#]+/i,
  ];
  return patterns.some((pattern) => pattern.test(content));
}

function hasHardcodedTerraformSecret(content) {
  const patterns = [
    /(?:RENDER_API_KEY|VERCEL_API_TOKEN|SUPABASE_ACCESS_TOKEN|SUPABASE_SERVICE_ROLE_KEY)\s*=\s*"(?!change-me|example|your-|<|REPLACE|xxx)[^"]+"/i,
    /(?:api_key|api_token|access_token|database_password|service_role_key)\s*=\s*"(?!change-me|example|your-|<|REPLACE|xxx)[^"]+"/i,
  ];
  return patterns.some((pattern) => pattern.test(content));
}

function checkEnvExamples() {
  warnMissing(".env.example", "root environment contract should be documented");
  if (exists("frontend")) warnMissing("frontend/.env.example", "frontend environment contract should be documented");
  if (exists("backend")) warnMissing("backend/.env.example", "backend environment contract should be documented");

  for (const file of [".env.example", "frontend/.env.example", "backend/.env.example"]) {
    if (exists(file) && hasObviousSecret(read(file))) {
      errors.push(`${file}: contains a value that looks like a real secret.`);
    }
  }

  if (exists("frontend/.env.example") && /SUPABASE_SERVICE_ROLE_KEY/i.test(read("frontend/.env.example"))) {
    errors.push("frontend/.env.example: SUPABASE_SERVICE_ROLE_KEY must stay server-side only.");
  }
}

function checkDocker() {
  warnMissing("docker-compose.yml", "local Docker orchestration is expected");
  if (exists("frontend")) {
    warnMissing("frontend/Dockerfile", "frontend local container is expected");
    warnMissing("frontend/Dockerfile.prod", "frontend production/container fallback is expected");
    warnMissing("frontend/.dockerignore", "frontend Docker context should be trimmed");
  }
  if (exists("backend")) {
    warnMissing("backend/Dockerfile", "backend local container is expected");
    warnMissing("backend/Dockerfile.prod", "backend production container is expected");
    warnMissing("backend/.dockerignore", "backend Docker context should be trimmed");
    warnMissing("backend/entrypoint.sh", "backend container startup should be explicit");
  }
}

function checkDocs() {
  warnMissing("Makefile", "root developer commands should be available");
  warnMissing("docs/architecture/infra-architecture.md", "infra architecture should be documented");
  warnMissing("docs/architecture/deploy.md", "deployment guidance should be documented");
  if (exists("AGENTS.md")) {
    const agents = read("AGENTS.md").toLowerCase();
    if (!agents.includes("docker") && !agents.includes("infra")) {
      warnings.push("AGENTS.md does not mention infra/Docker rules.");
    }
  } else {
    warnings.push("AGENTS.md missing: agent infra rules should be documented.");
  }
}

function checkVercel() {
  if (!exists("frontend")) return;
  const deployDocs = `${read("docs/architecture/deploy.md")}\n${read("README.md")}\n${read("frontend/vercel.json")}`.toLowerCase();
  if (!deployDocs.includes("vercel")) {
    warnings.push("Vercel guidance missing for frontend deployment.");
  }
  if (deployDocs.includes("vercel") && !deployDocs.includes("preview")) {
    warnings.push("Vercel guidance should document Preview environment behavior.");
  }
  if (deployDocs.includes("vercel") && !deployDocs.includes("production")) {
    warnings.push("Vercel guidance should document Production environment behavior.");
  }
  if (deployDocs.includes("vercel") && !deployDocs.includes("root directory") && !deployDocs.includes("frontend")) {
    warnings.push("Vercel monorepo guidance should document the frontend root directory.");
  }
}

function checkRender() {
  const renderText = `${read("render.yaml")}\n${read("docs/architecture/deploy.md")}\n${read("docs/architecture/infra-architecture.md")}\n${read("README.md")}`.toLowerCase();
  const mentionsRender = renderText.includes("render") || exists("render.yaml");
  if (!mentionsRender) return;

  if (!renderText.includes("build")) {
    warnings.push("Render guidance should document the backend build command.");
  }
  if (!renderText.includes("start") && !renderText.includes("gunicorn")) {
    warnings.push("Render guidance should document the backend start command.");
  }
  if (!renderText.includes("database_url")) {
    warnings.push("Render guidance should document DATABASE_URL.");
  }
  if (!renderText.includes("cors")) {
    warnings.push("Render guidance should document CORS from frontend domains to backend.");
  }
  if (exists("render.yaml")) {
    const blueprint = read("render.yaml");
    if (hasObviousSecret(blueprint)) {
      errors.push("render.yaml: contains a value that looks like a real secret.");
    }
    if (/SECRET|TOKEN|API_KEY|DATABASE_URL/i.test(blueprint) && !/sync:\s*false|generateValue:\s*true|fromDatabase:/i.test(blueprint)) {
      warnings.push("render.yaml references secret-like env vars without sync:false, generateValue:true, or fromDatabase.");
    }
  }
}

function checkSupabase() {
  const projectText = `${read("README.md")}\n${read("docs/architecture/infra-architecture.md")}\n${read(".env.example")}`.toLowerCase();
  const mentionsSupabase = projectText.includes("supabase") || exists("supabase");
  if (!mentionsSupabase) return;

  warnMissing("supabase", "Supabase is referenced but folder is missing");
  warnMissing("supabase/migrations", "Supabase migrations should be versioned when Supabase owns SQL resources");
  warnMissing("supabase/config.toml", "Supabase CLI config is expected after supabase init");
  if (!projectText.includes("rls") && !projectText.includes("row level security")) {
    warnings.push("Supabase production checklist should mention RLS.");
  }
  if (!projectText.includes("service role")) {
    warnings.push("Supabase docs should state that the service role key is server-side only.");
  }
  if (!projectText.includes("ssl")) {
    warnings.push("Supabase production checklist should mention SSL enforcement.");
  }
  if (!projectText.includes("network restriction")) {
    warnings.push("Supabase production checklist should mention network restrictions.");
  }
}

function checkTerraform() {
  const docsText = `${read("README.md")}\n${read("docs/architecture/infra-architecture.md")}\n${read("docs/architecture/deploy.md")}`.toLowerCase();
  const terraformRoot = "infra/terraform";
  const terraformSelected = exists(terraformRoot);

  if (!terraformSelected) {
    if (docsText.includes("terraform")) {
      warnings.push("Terraform is documented but infra/terraform is missing.");
    }
    return;
  }

  for (const file of ["versions.tf", "providers.tf", "variables.tf", "outputs.tf"]) {
    warnMissing(`${terraformRoot}/${file}`, "Terraform root contract is incomplete");
  }
  warnMissing(`${terraformRoot}/.terraform.lock.hcl`, "provider selections should be locked and committed");

  const terraformFiles = listFiles(terraformRoot, (file) => file.endsWith(".tf") || file.endsWith(".tfvars") || file.endsWith(".tfvars.example"));
  const terraformText = terraformFiles.map((file) => read(file)).join("\n");
  const normalizedTerraformText = terraformText.toLowerCase();

  if (!normalizedTerraformText.includes("required_providers")) {
    warnings.push("Terraform should declare required_providers with bounded version constraints.");
  }
  const providerVersionConstraints = [...read(`${terraformRoot}/versions.tf`).matchAll(/version\s*=\s*"([^"]+)"/gi)].map((match) => match[1]);
  if (!providerVersionConstraints.length) {
    warnings.push("Terraform providers should use reviewed bounded version constraints.");
  }
  for (const constraint of providerVersionConstraints) {
    if (/^\s*>=/.test(constraint) && !/[<~]/.test(constraint)) {
      warnings.push(`Terraform provider constraint "${constraint}" is not bounded against unreviewed major upgrades.`);
    }
  }
  const managesRender = /render-oss\/render|provider\s+"render"|resource\s+"render_/i.test(terraformText);
  const managesVercel = /vercel\/vercel|provider\s+"vercel"|resource\s+"vercel_/i.test(terraformText);
  const managesSupabase = /supabase\/supabase|provider\s+"supabase"|resource\s+"supabase_/i.test(terraformText);

  if (managesRender && !/source\s*=\s*"render-oss\/render"/i.test(terraformText)) {
    warnings.push("Terraform mentions Render without the official render-oss/render provider source.");
  }
  if (managesVercel && !/source\s*=\s*"vercel\/vercel"/i.test(terraformText)) {
    warnings.push("Terraform mentions Vercel without the official vercel/vercel provider source.");
  }
  if (managesSupabase && !/source\s*=\s*"supabase\/supabase"/i.test(terraformText)) {
    warnings.push("Terraform mentions Supabase without the official supabase/supabase provider source.");
  }

  if (exists("render.yaml") && /resource\s+"render_web_service"/i.test(terraformText)) {
    warnings.push("render.yaml and Terraform Render web services coexist; document distinct ownership and verify no service is managed twice.");
  }
  if (exists("backend") && /resource\s+"postgresql_|resource\s+"null_resource"|local-exec/i.test(terraformText)) {
    warnings.push("Terraform contains PostgreSQL or provisioner resources; verify Django domain tables and migrations remain outside Terraform.");
  }

  for (const file of terraformFiles) {
    if (hasHardcodedTerraformSecret(read(file))) {
      errors.push(`${file}: contains a Terraform value that looks like a hardcoded provider or database secret.`);
    }
  }

  const sensitiveArtifacts = listFiles(terraformRoot, (file) =>
    /(?:^|\/)(?:terraform\.tfstate(?:\..+)?|[^/]+\.tfstate(?:\..+)?|[^/]+\.tfplan|terraform\.tfvars|[^/]+\.auto\.tfvars|crash(?:\.[^/]+)?\.log)$/i.test(file),
  );
  for (const file of sensitiveArtifacts) {
    warnings.push(`${file}: local state, plan, crash log or secret variable file must remain ignored and uncommitted.`);
  }

  const gitignore = read(".gitignore");
  for (const pattern of [".terraform/", "*.tfstate", "*.tfstate.*", "*.tfplan", "*.auto.tfvars", "terraform.tfvars"]) {
    if (!gitignore.includes(pattern)) {
      warnings.push(`.gitignore should include ${pattern} for Terraform hygiene.`);
    }
  }

  if (!docsText.includes("ownership") && !docsText.includes("owner")) {
    warnings.push("Terraform docs should include a resource ownership matrix.");
  }
  if (!docsText.includes("import")) {
    warnings.push("Terraform docs should record create/import decisions for existing resources.");
  }
  if (!docsText.includes("state")) {
    warnings.push("Terraform docs should explain remote state, access and recovery.");
  }
  if (!docsText.includes("plan") || !docsText.includes("apply")) {
    warnings.push("Terraform docs should explain the reviewed plan and explicit apply approval flow.");
  }
}

function printResults() {
  console.log("Karya infra scan");
  console.log("======================");

  for (const warning of warnings) console.log(`warning: ${warning}`);
  for (const error of errors) console.log(`error: ${error}`);

  if (errors.length) {
    console.log(`failed: ${errors.length} error(s), ${warnings.length} warning(s)`);
    return 1;
  }
  if (warnings.length) {
    console.log(`ok with warnings: ${warnings.length} warning(s)`);
    return 0;
  }
  console.log("ok: no infra warnings found.");
  return 0;
}

if (isSkillCatalogRepository()) {
  console.log("Karya infra scan");
  console.log("======================");
  console.log("ok: skill catalog repository detected; run this scanner from a target app project for infra checks.");
  process.exitCode = 0;
} else {
  checkDocker();
  checkEnvExamples();
  checkDocs();
  checkVercel();
  checkRender();
  checkSupabase();
  checkTerraform();
  process.exitCode = printResults();
}
