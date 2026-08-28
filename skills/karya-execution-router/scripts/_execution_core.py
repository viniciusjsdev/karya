"""Deterministic contracts, readiness, snapshots, and evidence for economic execution."""

from __future__ import annotations

import fnmatch
import hashlib
import importlib.util
import json
import os
import re
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Any

MANDATORY_PROHIBITIONS = {
    "secrets_and_credentials",
    "environment_files",
    "external_actions",
    "spec_changes",
    "destructive_git",
    "web_access",
}

PROTECTED_PATTERNS = (
    ".git/**",
    "**/.git/**",
    ".env",
    ".env.*",
    "**/.env",
    "**/.env.*",
    "AGENTS.md",
    "**/AGENTS.md",
    ".agents/**",
    "**/.agents/**",
    ".codex/**",
    "**/.codex/**",
    "specs/**",
    "**/specs/**",
    "opencode.json",
    "**/opencode.json",
)

IGNORED_SNAPSHOT_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}

READ_ONLY_GIT_COMMANDS = (
    "git status",
    "git status --short",
    "git diff",
    "git diff --check",
    "git diff --stat",
    "git ls-files",
    "git rev-parse --show-toplevel",
)

SENSITIVE_OUTPUT_PATTERNS = (
    re.compile(r"(?i)\b(api[_-]?key|access[_-]?token|refresh[_-]?token|secret|password|authorization)\b([\"']?\s*[:=]\s*[\"']?)([^\"'\s,;}]+)"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b"),
)


def load_json(path: str | Path) -> dict[str, Any]:
    """Load one UTF-8 JSON object."""
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path: str | Path, value: Any) -> None:
    """Write deterministic UTF-8 JSON."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def redact_sensitive_output(value: str) -> str:
    """Redact common credential forms before external executor output is persisted."""
    redacted = value
    for index, pattern in enumerate(SENSITIVE_OUTPUT_PATTERNS):
        if index == 0:
            redacted = pattern.sub(lambda match: f"{match.group(1)}{match.group(2)}[REDACTED]", redacted)
        else:
            redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def redact_file(path: str | Path) -> None:
    """Sanitize a UTF-8 executor log in place without moving it into the project."""
    target = Path(path)
    if not target.is_file():
        return
    content = target.read_text(encoding="utf-8", errors="replace")
    target.write_text(redact_sensitive_output(content), encoding="utf-8")


def redact_structure(value: Any) -> Any:
    """Recursively sanitize strings in structured executor evidence."""
    if isinstance(value, str):
        return redact_sensitive_output(value)
    if isinstance(value, list):
        return [redact_structure(item) for item in value]
    if isinstance(value, dict):
        return {key: redact_structure(item) for key, item in value.items()}
    return value


def portable(path: str | Path) -> str:
    """Return an absolute forward-slash path for runtime configuration."""
    return Path(path).resolve().as_posix()


def request_fingerprint(request: dict[str, Any]) -> str:
    """Hash the exact external request without copying it into the project."""
    payload = json.dumps(request, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _is_inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def matches_any(relative: str, patterns: list[str] | tuple[str, ...]) -> bool:
    """Match a portable project-relative path against approved glob patterns."""
    normalized = relative.replace("\\", "/").lstrip("./")
    return any(fnmatch.fnmatchcase(normalized, pattern.replace("\\", "/").lstrip("./")) for pattern in patterns)


def is_protected(relative: str) -> bool:
    """Return whether a project-relative path is always immutable."""
    return matches_any(relative, PROTECTED_PATTERNS)


def _file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def snapshot_project(project_root: str | Path) -> dict[str, dict[str, Any]]:
    """Hash regular project files while excluding dependency and VCS internals."""
    root = Path(project_root).resolve()
    snapshot: dict[str, dict[str, Any]] = {}
    for directory, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in IGNORED_SNAPSHOT_DIRECTORIES]
        current = Path(directory)
        if current.name == "runtime" and current.parent.name == ".harness":
            dirnames[:] = []
            continue
        for filename in filenames:
            path = current / filename
            if path.is_symlink() or not path.is_file():
                continue
            relative = path.relative_to(root).as_posix()
            snapshot[relative] = {"sha256": _file_digest(path), "size": path.stat().st_size}
    return snapshot


def compare_snapshots(before: dict[str, Any], after: dict[str, Any]) -> dict[str, list[str]]:
    """Return created, modified, removed, and combined changed paths."""
    before_paths = set(before)
    after_paths = set(after)
    created = sorted(after_paths - before_paths)
    removed = sorted(before_paths - after_paths)
    modified = sorted(path for path in before_paths & after_paths if before[path] != after[path])
    return {"created": created, "modified": modified, "removed": removed, "changed": sorted(created + modified + removed)}


def validate_changed_paths(changed: list[str], writable_paths: list[str]) -> list[str]:
    """Reject protected or out-of-scope changes."""
    errors: list[str] = []
    for path in changed:
        if is_protected(path):
            errors.append(f"protected path changed: {path}")
        elif not matches_any(path, writable_paths):
            errors.append(f"path changed outside approved writable scope: {path}")
    return errors


def _unsafe_validation_command(command: str) -> str | None:
    if re.search(r"[;&|><`\r\n]|\$\(", command):
        return "contains shell control operators"
    lowered = f" {command.lower()} "
    blocked = (
        " git commit ", " git push ", " git reset ", " git clean ", " git checkout ",
        " git switch ", " git merge ", " git rebase ", " git tag ", " git branch ",
        " rm ", " rmdir ", " remove-item ", " del ", " erase ", " format ",
        " curl ", " wget ", " invoke-webrequest ", " invoke-restmethod ",
        " pip install ", " npm install ", " npm ci ", " pnpm install ", " yarn install ",
        " docker push ", " terraform apply ", " terraform destroy ", " kubectl apply ",
    )
    if any(token in lowered for token in blocked):
        return "contains a blocked mutation, installation, network, or external-action command"
    try:
        parts = shlex.split(command, posix=os.name != "nt")
    except ValueError as error:
        return f"cannot be parsed safely: {error}"
    if not parts:
        return "is empty"
    return None


def load_spec_validator(skill_root: Path):
    """Load the sibling Project Spec validator in source and installed layouts."""
    spec_core = skill_root.parent / "project-spec-architect" / "scripts" / "_spec_core.py"
    if not spec_core.exists():
        raise FileNotFoundError(f"missing sibling project-spec-architect validator: {spec_core}")
    module_spec = importlib.util.spec_from_file_location("karya_project_spec_core", spec_core)
    if module_spec is None or module_spec.loader is None:
        raise RuntimeError(f"cannot load project Spec validator: {spec_core}")
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module


def validate_request(request: Any, request_path: str | Path, skill_root: str | Path) -> dict[str, Any]:
    """Validate the external request, READY Spec, safety scope, and confirmation."""
    errors: list[str] = []
    if not isinstance(request, dict):
        return {"ok": False, "errors": ["execution request must be an object"]}
    required = {
        "schema_version", "task_id", "project_root", "spec", "executor", "provider", "model",
        "provider_kind", "billing_mode", "timeout_minutes", "writable_paths", "prohibited_actions",
        "baseline", "validation_ids", "confirmation",
    }
    missing = sorted(required - set(request))
    if missing:
        return {"ok": False, "errors": [f"execution request is missing {item}" for item in missing]}
    for key in sorted(set(request) - required):
        errors.append(f"execution request has unsupported property {key}")
    if request.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    task_id = str(request.get("task_id", ""))
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,95}", task_id):
        errors.append("task_id must be a safe lowercase identifier")
    executor = request.get("executor")
    if executor not in {"auto", "opencode"}:
        errors.append("executor must be auto or opencode")
    if request.get("provider_kind") not in {"managed", "byok", "local"}:
        errors.append("provider_kind is invalid")
    if request.get("billing_mode") not in {"subscription", "credits", "provider_billed", "local_compute", "unknown"}:
        errors.append("billing_mode is invalid")
    try:
        timeout = float(request.get("timeout_minutes"))
        if timeout <= 0 or timeout > 1440:
            errors.append("timeout_minutes must be greater than zero and at most 1440")
    except (TypeError, ValueError):
        errors.append("timeout_minutes must be numeric")

    project_root = Path(str(request.get("project_root", ""))).resolve()
    if not project_root.is_dir():
        errors.append("project_root does not exist")
    if _is_inside(Path(request_path), project_root):
        errors.append("execution request must remain outside the target project repository")

    provider = str(request.get("provider", "")).strip()
    model = str(request.get("model", "")).strip()
    if not provider or not re.fullmatch(r"[a-zA-Z0-9._-]+", provider):
        errors.append("provider is invalid")
    if not model or "/" not in model or model.split("/", 1)[0] != provider:
        errors.append("model must use the exact provider/model form")

    writable_paths = request.get("writable_paths")
    if not isinstance(writable_paths, list) or not writable_paths or any(not isinstance(item, str) or not item.strip() for item in writable_paths):
        errors.append("writable_paths must contain non-empty project-relative patterns")
        writable_paths = []
    else:
        for pattern in writable_paths:
            candidate = pattern.replace("\\", "/")
            if candidate in {".", "*", "**", "**/*"}:
                errors.append(f"writable path is broader than an auditable project area: {pattern}")
            if candidate.startswith("/") or re.match(r"^[A-Za-z]:", candidate) or ".." in candidate.split("/"):
                errors.append(f"writable path must stay project-relative: {pattern}")
            if matches_any(candidate.replace("/**", "/sentinel"), PROTECTED_PATTERNS) or is_protected(candidate):
                errors.append(f"writable path overlaps protected project state: {pattern}")

    prohibitions = request.get("prohibited_actions")
    if not isinstance(prohibitions, list) or set(prohibitions) != MANDATORY_PROHIBITIONS:
        errors.append("prohibited_actions must contain the complete mandatory prohibition set")
    if request.get("baseline") != {"mode": "full_snapshot"}:
        errors.append("baseline.mode must be full_snapshot")

    spec = request.get("spec")
    manifest: dict[str, Any] = {}
    markdown = ""
    validation_commands: dict[str, str] = {}
    acceptance_ids: list[str] = []
    if not isinstance(spec, dict):
        errors.append("spec must be an object")
    elif project_root.is_dir():
        for key in sorted(set(spec) - {"markdown_path", "manifest_path", "id", "contract_version"}):
            errors.append(f"spec has unsupported property {key}")
        for key in ("markdown_path", "manifest_path", "id", "contract_version"):
            if key not in spec:
                errors.append(f"spec is missing {key}")
        markdown_path = (project_root / str(spec.get("markdown_path", ""))).resolve()
        manifest_path = (project_root / str(spec.get("manifest_path", ""))).resolve()
        if not _is_inside(markdown_path, project_root) or not _is_inside(manifest_path, project_root):
            errors.append("Spec paths must stay inside project_root")
        elif not markdown_path.is_file() or not manifest_path.is_file():
            errors.append("Spec Markdown or execution manifest does not exist")
        else:
            try:
                markdown = markdown_path.read_text(encoding="utf-8-sig")
                manifest = load_json(manifest_path)
                policy_path = project_root / ".codex" / "references" / "runtime-policy.json"
                if not policy_path.is_file():
                    errors.append("project-pinned .codex/references/runtime-policy.json is required")
                else:
                    validator = load_spec_validator(Path(skill_root))
                    policy = load_json(policy_path)
                    errors.extend(validator.validate_spec_pair(
                        markdown,
                        manifest,
                        policy,
                        project_root=project_root,
                        skills_root=Path(skill_root).parent,
                        require_ready=True,
                    ))
            except (OSError, ValueError, json.JSONDecodeError) as error:
                errors.append(f"cannot load Spec contract: {error}")

    if manifest:
        if manifest.get("spec_id") != spec.get("id") or manifest.get("contract_version") != spec.get("contract_version"):
            errors.append("external request Spec identity differs from the execution manifest")
        execution = manifest.get("execution", {})
        if execution.get("classification") in {"design", "critical_review"} or execution.get("role") in {"architect", "reviewer"}:
            errors.append("design and critical review work cannot be delegated to OpenCode")
        review = manifest.get("review", {})
        if review.get("required") is not True or review.get("independence") != "independent":
            errors.append("external execution requires an independent Codex review in the manifest")
        for item in manifest.get("validation", []):
            if item.get("required"):
                validation_id = str(item.get("id", ""))
                command = str(item.get("command", ""))
                validation_commands[validation_id] = command
                unsafe_reason = _unsafe_validation_command(command)
                if unsafe_reason:
                    errors.append(f"validation {validation_id} {unsafe_reason}")
        acceptance_ids = sorted(set(re.findall(r"\bAC-[0-9]{3}\b", markdown)))

    validation_ids = request.get("validation_ids")
    if not isinstance(validation_ids, list) or set(validation_ids) != set(validation_commands):
        errors.append("validation_ids must exactly match every required manifest validation")

    confirmation = request.get("confirmation")
    if not isinstance(confirmation, dict):
        errors.append("confirmation must be an object")
    else:
        allowed_confirmation = {"approved", "approved_at", "task_id", "spec_id", "contract_version", "executor", "provider", "model", "writable_paths", "validation_ids"}
        for key in sorted(set(confirmation) - allowed_confirmation):
            errors.append(f"confirmation has unsupported property {key}")
        expected = {
            "approved": True,
            "task_id": task_id,
            "spec_id": spec.get("id") if isinstance(spec, dict) else None,
            "contract_version": spec.get("contract_version") if isinstance(spec, dict) else None,
            "executor": "opencode",
            "provider": provider,
            "model": model,
            "writable_paths": writable_paths,
            "validation_ids": validation_ids,
        }
        for key, value in expected.items():
            if confirmation.get(key) != value:
                errors.append(f"confirmation does not exactly approve {key}")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})", str(confirmation.get("approved_at", ""))):
            errors.append("confirmation.approved_at must be an ISO-8601 timestamp")

    return {
        "ok": not errors,
        "errors": errors,
        "project_root": str(project_root),
        "manifest": manifest,
        "markdown": markdown,
        "validation_commands": validation_commands,
        "acceptance_ids": acceptance_ids,
    }


def _command_prefix() -> list[str]:
    override = os.environ.get("KARYA_OPENCODE_COMMAND", "").strip()
    if override:
        return shlex.split(override, posix=os.name != "nt")
    if os.name == "nt" and os.environ.get("APPDATA"):
        native = Path(os.environ["APPDATA"]) / "npm" / "node_modules" / "opencode-ai" / "bin" / "opencode.exe"
        if native.exists():
            return [str(native)]
    resolved = shutil.which("opencode") or shutil.which("opencode.exe") or shutil.which("opencode.cmd")
    return [resolved or "opencode"]


def run_capture(args: list[str], *, cwd: str | Path | None = None, timeout: float = 30) -> subprocess.CompletedProcess[str]:
    """Run a subprocess without a shell and capture text."""
    return subprocess.run(args, cwd=cwd, shell=False, capture_output=True, text=True, timeout=timeout, check=False)


def inspect_opencode(provider: str, model: str, provider_kind: str) -> dict[str, Any]:
    """Check CLI, authentication when applicable, and exact model availability."""
    prefix = _command_prefix()
    reasons: list[str] = []
    report: dict[str, Any] = {"ready": False, "command": prefix, "cli": False, "authenticated": False, "model_available": False, "reasons": reasons}
    try:
        version = run_capture([*prefix, "--version"])
        report["cli"] = version.returncode == 0
        report["version"] = (version.stdout or version.stderr).strip().splitlines()[:1]
        if not report["cli"]:
            reasons.append("OpenCode CLI is unavailable")
            return report
        if provider_kind == "local":
            report["authenticated"] = True
        else:
            auth = run_capture([*prefix, "auth", "list"])
            auth_text = f"{auth.stdout}\n{auth.stderr}".lower()
            report["authenticated"] = auth.returncode == 0 and provider.lower() in auth_text
            if not report["authenticated"]:
                reasons.append(f"OpenCode provider is not authenticated: {provider}")
        models = run_capture([*prefix, "models", provider])
        model_text = f"{models.stdout}\n{models.stderr}".lower()
        report["model_available"] = models.returncode == 0 and model.lower() in model_text
        if not report["model_available"]:
            reasons.append(f"configured model is unavailable: {model}")
        report["ready"] = report["cli"] and report["authenticated"] and report["model_available"]
        return report
    except (OSError, subprocess.SubprocessError) as error:
        reasons.append(f"OpenCode readiness failed: {error}")
        return report


def validate_completion(
    completion: Any,
    *,
    request: dict[str, Any],
    acceptance_ids: list[str],
    validation_commands: dict[str, str],
    actual_changed: list[str],
) -> list[str]:
    """Validate external executor evidence against the active run and actual diff."""
    errors: list[str] = []
    if not isinstance(completion, dict):
        return ["completion evidence must be an object"]
    required = {
        "task_id", "spec_id", "contract_version", "status", "changed_files", "acceptance_evidence",
        "validation_evidence", "deviations", "unresolved_items", "needs_design",
    }
    for key in sorted(required - set(completion)):
        errors.append(f"completion evidence is missing {key}")
    spec = request["spec"]
    if completion.get("task_id") != request["task_id"]:
        errors.append("completion task_id differs from the active run")
    if completion.get("spec_id") != spec["id"] or completion.get("contract_version") != spec["contract_version"]:
        errors.append("completion Spec identity differs from the active contract")
    if completion.get("status") not in {"completed", "blocked", "needs_design", "failed"}:
        errors.append("completion status is invalid")
    reported_changed = completion.get("changed_files")
    if not isinstance(reported_changed, list) or set(reported_changed) != set(actual_changed):
        errors.append("completion changed_files do not match the snapshot diff")
    if completion.get("status") == "completed":
        acceptance = completion.get("acceptance_evidence")
        if not isinstance(acceptance, dict) or set(acceptance) != set(acceptance_ids):
            errors.append("completion acceptance_evidence must cover every AC ID exactly")
        else:
            for acceptance_id, evidence in acceptance.items():
                if not isinstance(evidence, dict) or evidence.get("result") != "passed" or not evidence.get("evidence"):
                    errors.append(f"completion evidence for {acceptance_id} is not passing and observable")
        validation = completion.get("validation_evidence")
        if not isinstance(validation, dict) or set(validation) != set(validation_commands):
            errors.append("completion validation_evidence must cover every required validation exactly")
        else:
            for validation_id, command in validation_commands.items():
                evidence = validation[validation_id]
                if not isinstance(evidence, dict) or evidence.get("command") != command or evidence.get("result") != "passed" or evidence.get("exit_code") != 0:
                    errors.append(f"completion validation evidence is invalid for {validation_id}")
        if completion.get("needs_design") is not None:
            errors.append("completed evidence must use needs_design null")
    elif completion.get("status") == "needs_design" and not isinstance(completion.get("needs_design"), dict):
        errors.append("needs_design status requires a structured needs_design object")
    return errors


def run_validations(commands: dict[str, str], project_root: str | Path, timeout_seconds: float = 900) -> dict[str, Any]:
    """Independently run exact approved validation commands after executor exit."""
    results: dict[str, Any] = {}
    for validation_id, command in commands.items():
        try:
            parts = shlex.split(command, posix=os.name != "nt")
            completed = run_capture(parts, cwd=project_root, timeout=timeout_seconds)
            results[validation_id] = {
                "command": command,
                "result": "passed" if completed.returncode == 0 else "failed",
                "exit_code": completed.returncode,
                "stdout": redact_sensitive_output(completed.stdout[-12000:]),
                "stderr": redact_sensitive_output(completed.stderr[-12000:]),
            }
        except (OSError, subprocess.SubprocessError, ValueError) as error:
            results[validation_id] = {"command": command, "result": "failed", "exit_code": None, "stdout": "", "stderr": redact_sensitive_output(str(error))}
    return results
