"""Route one approved project implementation to OpenCode and return one final result."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from _execution_core import (
    PROTECTED_PATTERNS,
    READ_ONLY_GIT_COMMANDS,
    _command_prefix,
    compare_snapshots,
    inspect_opencode,
    load_json,
    portable,
    redact_file,
    redact_structure,
    request_fingerprint,
    run_validations,
    snapshot_project,
    validate_changed_paths,
    validate_completion,
    validate_request,
    write_json,
)


def emit(run_dir: Path | None, result: dict[str, Any]) -> None:
    if run_dir is not None:
        write_json(run_dir / "route-result.json", result)
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


def run_quiet(command: list[str], *, cwd: Path, env: dict[str, str], timeout_seconds: float, stdout_path: Path, stderr_path: Path) -> dict[str, Any]:
    timed_out = False
    try:
        with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
            child = subprocess.Popen(command, cwd=cwd, env=env, shell=False, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, text=True)
            try:
                code = child.wait(timeout=timeout_seconds)
            except subprocess.TimeoutExpired:
                timed_out = True
                child.kill()
                code = child.wait(timeout=30)
        return {"exit_code": code, "timed_out": timed_out, "error": None}
    except (OSError, subprocess.SubprocessError) as error:
        return {"exit_code": None, "timed_out": timed_out, "error": str(error)}


def build_runtime_config(skill_root: Path, request: dict[str, Any], run_dir: Path, validation_commands: dict[str, str]) -> dict[str, Any]:
    base = load_json(skill_root / "assets" / "opencode.executor.json")
    edit: dict[str, str] = {"*": "deny"}
    for pattern in request["writable_paths"]:
        edit[pattern.replace("\\", "/")] = "allow"
    for pattern in PROTECTED_PATTERNS:
        edit[pattern] = "deny"
    edit[f"{portable(run_dir)}/**"] = "allow"
    bash = {"*": "deny", **{command: "allow" for command in READ_ONLY_GIT_COMMANDS}}
    bash.update({command: "allow" for command in validation_commands.values()})
    permission = {
        **base["permission"],
        "edit": edit,
        "bash": bash,
        "external_directory": {"*": "deny", f"{portable(run_dir)}/**": "allow"},
    }
    model = request["model"]
    return {
        **base,
        "model": model,
        "enabled_providers": [request["provider"]],
        "instructions": [portable(skill_root / "SKILL.md"), f"{portable(skill_root / 'references')}/*.md"],
        "permission": permission,
        "agent": {
            "karya-economic-executor": {
                "description": "Implement only one explicitly approved READY Karya Spec",
                "mode": "primary",
                "model": model,
                "permission": permission,
            }
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    request_path = Path(args.request).resolve()
    skill_root = Path(__file__).resolve().parent.parent

    try:
        request = load_json(request_path)
        fingerprint = request_fingerprint(request)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        emit(None, {"task_id": "unknown", "route": "preflight-blocked", "executor": "none", "provider": "unknown", "model": "unknown", "project_root": "unknown", "reasons": [str(error)], "artifacts": {}})
        return 2

    run_dir = Path(tempfile.gettempdir()) / "karya-execution-runs" / request.get("task_id", "invalid") / fingerprint[:16]
    run_dir.mkdir(parents=True, exist_ok=True)
    base_result = {
        "task_id": request.get("task_id", "unknown"),
        "spec_id": request.get("spec", {}).get("id", "unknown"),
        "contract_version": request.get("spec", {}).get("contract_version"),
        "provider": request.get("provider", "unknown"),
        "model": request.get("model", "unknown"),
        "project_root": str(Path(str(request.get("project_root", "."))).resolve()),
        "request_fingerprint": fingerprint,
        "reasons": [],
        "artifacts": {"run_dir": str(run_dir), "route_result": str(run_dir / "route-result.json")},
    }
    preflight = validate_request(request, request_path, skill_root)
    if not preflight["ok"]:
        emit(run_dir, {**base_result, "route": "preflight-blocked", "executor": "none", "reasons": preflight["errors"]})
        return 2

    project_root = Path(preflight["project_root"])
    readiness = inspect_opencode(request["provider"], request["model"], request["provider_kind"])
    sanitized_readiness = {
        "ready": readiness["ready"],
        "cli": readiness["cli"],
        "authenticated": readiness["authenticated"],
        "model_available": readiness["model_available"],
        "reasons": readiness["reasons"],
    }
    if not readiness["ready"]:
        route = "opencode-unavailable" if request["executor"] == "opencode" else "codex-fallback-required"
        executor = "none" if route == "opencode-unavailable" else "codex"
        emit(run_dir, {**base_result, "route": route, "executor": executor, "reasons": readiness["reasons"], "readiness": sanitized_readiness})
        return 3 if route == "opencode-unavailable" else 0
    if args.dry_run:
        emit(run_dir, {**base_result, "route": "opencode-ready", "executor": "opencode", "readiness": sanitized_readiness})
        return 0

    completion_path = run_dir / "completion.json"
    events_path = run_dir / "opencode-events.ndjson"
    stderr_path = run_dir / "opencode-stderr.log"
    before_path = run_dir / "snapshot-before.json"
    after_path = run_dir / "snapshot-after.json"
    diff_path = run_dir / "snapshot-diff.json"
    validation_path = run_dir / "router-validations.json"
    receipt_path = run_dir / "request-receipt.json"
    if completion_path.exists():
        completion_path.unlink()

    write_json(receipt_path, {
        "request_fingerprint": fingerprint,
        "task_id": request["task_id"],
        "spec_id": request["spec"]["id"],
        "contract_version": request["spec"]["contract_version"],
        "executor": "opencode",
        "provider": request["provider"],
        "model": request["model"],
        "provider_kind": request["provider_kind"],
        "billing_mode": request["billing_mode"],
        "approved_at": request["confirmation"]["approved_at"],
        "writable_paths": request["writable_paths"],
        "validation_ids": request["validation_ids"],
    })
    before = snapshot_project(project_root)
    write_json(before_path, before)

    runtime_config = build_runtime_config(skill_root, request, run_dir, preflight["validation_commands"])
    prompt = "\n".join([
        "Implement only the explicitly approved READY project Spec.",
        f"Task ID: {request['task_id']}. Spec: {request['spec']['id']} version {request['spec']['contract_version']}.",
        f"Read {portable(project_root / request['spec']['markdown_path'])} and {portable(project_root / request['spec']['manifest_path'])}.",
        f"Writable paths are limited to: {json.dumps(request['writable_paths'])}.",
        "Do not redesign, change Specs or project instructions, access secrets or environment files, use web access, perform external actions, mutate Git, install dependencies, or use subagents.",
        "If a consequential decision is missing, return needs_design instead of inventing it.",
        f"Write final completion evidence to {portable(completion_path)} using {portable(skill_root / 'assets' / 'completion.schema.json')}.",
        "Completion evidence must cover every AC and required validation ID. Process exit is the only wake-up signal for Codex.",
    ])
    child_env = {
        **os.environ,
        "OPENCODE_CONFIG_CONTENT": json.dumps(runtime_config, separators=(",", ":")),
        "OPENCODE_DISABLE_AUTOUPDATE": "true",
        "OPENCODE_AUTO_SHARE": "false",
    }
    command = [
        *_command_prefix(), "--pure", "run", "--format", "json", "--model", request["model"],
        "--agent", "karya-economic-executor", "--auto", "--dir", str(project_root),
        "--title", f"Karya economic execution {request['task_id']}", prompt,
    ]
    process = run_quiet(
        command,
        cwd=project_root,
        env=child_env,
        timeout_seconds=float(request["timeout_minutes"]) * 60,
        stdout_path=events_path,
        stderr_path=stderr_path,
    )
    redact_file(events_path)
    redact_file(stderr_path)

    after = snapshot_project(project_root)
    diff = compare_snapshots(before, after)
    write_json(after_path, after)
    write_json(diff_path, diff)
    scope_errors = validate_changed_paths(diff["changed"], request["writable_paths"])

    completion: dict[str, Any] | None = None
    completion_errors: list[str] = []
    if completion_path.is_file():
        try:
            completion = redact_structure(load_json(completion_path))
            write_json(completion_path, completion)
            completion_errors = validate_completion(
                completion,
                request=request,
                acceptance_ids=preflight["acceptance_ids"],
                validation_commands=preflight["validation_commands"],
                actual_changed=diff["changed"],
            )
        except (OSError, ValueError, json.JSONDecodeError) as error:
            completion_errors = [f"completion evidence is invalid JSON: {error}"]
    else:
        completion_errors = ["OpenCode did not write completion.json"]

    router_validations: dict[str, Any] = {}
    if process["exit_code"] == 0 and not process["timed_out"] and not scope_errors and completion and completion.get("status") == "completed":
        router_validations = run_validations(preflight["validation_commands"], project_root)
    write_json(validation_path, router_validations)
    validation_errors = [f"router validation failed: {validation_id}" for validation_id, evidence in router_validations.items() if evidence.get("result") != "passed"]
    if completion and completion.get("status") == "completed" and not router_validations:
        validation_errors.append("router did not run independent validations")

    reasons: list[str] = []
    if process["timed_out"]:
        reasons.append(f"OpenCode exceeded {request['timeout_minutes']} minute(s)")
    if process["error"]:
        reasons.append(process["error"])
    if process["exit_code"] != 0:
        reasons.append(f"OpenCode exited with code {process['exit_code']}")
    reasons.extend(scope_errors)
    reasons.extend(completion_errors)
    reasons.extend(validation_errors)

    route = "opencode-error"
    if completion and completion.get("status") in {"blocked", "needs_design"} and not scope_errors:
        route = "opencode-reported-blocked"
    elif completion and completion.get("status") == "completed" and process["exit_code"] == 0 and not reasons:
        route = "opencode-completed"

    artifacts = {
        "run_dir": str(run_dir),
        "request_receipt": str(receipt_path),
        "events": str(events_path),
        "stderr": str(stderr_path),
        "completion": str(completion_path),
        "snapshot_before": str(before_path),
        "snapshot_after": str(after_path),
        "snapshot_diff": str(diff_path),
        "router_validations": str(validation_path),
        "route_result": str(run_dir / "route-result.json"),
    }
    emit(run_dir, {
        **base_result,
        "route": route,
        "executor": "opencode",
        "reasons": reasons,
        "readiness": sanitized_readiness,
        "process": process,
        "completion_status": completion.get("status") if completion else None,
        "changed_files": diff["changed"],
        "scope_integrity": {"ok": not scope_errors, "errors": scope_errors},
        "independent_validations": router_validations,
        "artifacts": artifacts,
    })
    return 0 if route == "opencode-completed" else 3


if __name__ == "__main__":
    raise SystemExit(main())
