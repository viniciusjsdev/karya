"""Route a resolved Project Harness manifest through the official Python Codex SDK."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
from types import ModuleType
from typing import Any

from _runtime_core import build_handoff_prompt, read_state, resolve_inside, update_state, validate_completion, validate_preflight, validate_review_evidence, write_json_atomic


def _load_sdk(module_path: str | None) -> ModuleType:
    if not module_path:
        import openai_codex
        return openai_codex
    path = Path(module_path).resolve()
    spec = importlib.util.spec_from_file_location("project_harness_mock_codex_sdk", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load SDK module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sdk_usage(usage: Any) -> dict[str, int] | None:
    if usage is None:
        return None
    total = getattr(usage, "total", usage)
    if hasattr(total, "model_dump"):
        raw = total.model_dump(mode="json")
    elif isinstance(total, dict):
        raw = total
    else:
        raw = {key: getattr(total, key, 0) for key in ("input_tokens", "cached_input_tokens", "cache_write_input_tokens", "output_tokens", "reasoning_output_tokens")}
    return {key: int(raw.get(key, 0) or 0) for key in ("input_tokens", "cached_input_tokens", "cache_write_input_tokens", "output_tokens", "reasoning_output_tokens")}


def _result_base() -> dict[str, Any]:
    return {"route": "preflight_blocked", "spec_id": None, "action": "none", "model": None, "reasoning": None, "thread_id": None, "completion_status": None, "artifacts": {}, "errors": []}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--spec", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--policy", default=".codex/references/runtime-policy.json")
    parser.add_argument("--skills-root")
    parser.add_argument("--state", default=".harness/runtime/spec-threads.json")
    parser.add_argument("--sdk-module")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    project_root = Path(args.project_root).resolve()
    base = _result_base()
    recovery: dict[str, Any] | None = None
    thread: Any = None
    try:
        spec_path = resolve_inside(project_root, args.spec, "Spec path")
        manifest_path = resolve_inside(project_root, args.manifest, "Manifest path")
        policy_path = resolve_inside(project_root, args.policy, "Runtime policy path")
        state_path = resolve_inside(project_root, args.state, "State path")
        markdown = spec_path.read_text(encoding="utf-8-sig")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        review_run = manifest.get("execution", {}).get("thread", {}).get("purpose") == "review"
        policy = json.loads(policy_path.read_text(encoding="utf-8-sig"))
        state = read_state(state_path)
        recovery = {"manifest": manifest, "state": state, "state_path": state_path}
        base.update({"spec_id": manifest.get("spec_id"), "model": manifest.get("execution", {}).get("model"), "reasoning": manifest.get("execution", {}).get("reasoning")})
        skills_root = args.skills_root or (Path(os.environ["CODEX_HOME"]) / "skills" if os.environ.get("CODEX_HOME") else Path.home() / ".codex" / "skills")
        errors = validate_preflight(markdown=markdown, manifest=manifest, policy=policy, project_root=project_root, skills_root=skills_root, state=state)
        completion_schema_path = resolve_inside(project_root, manifest.get("completion", {}).get("schema_path", ""), "Completion schema path")
        completion_schema = None
        if not completion_schema_path.exists():
            errors.append(f"declared completion schema does not exist: {manifest.get('completion', {}).get('schema_path')}")
        else:
            try:
                completion_schema = json.loads(completion_schema_path.read_text(encoding="utf-8-sig"))
            except json.JSONDecodeError as error:
                errors.append(f"completion schema is invalid JSON: {error}")
        if errors:
            base["errors"] = errors
            print(json.dumps(base, indent=2))
            return 1
        action = "start" if manifest["execution"]["thread"]["mode"] == "new" else "resume"
        prompt = build_handoff_prompt(manifest, spec_path.relative_to(project_root).as_posix(), manifest_path.relative_to(project_root).as_posix())
        if args.dry_run:
            base.update({"route": "preview", "action": action, "artifacts": {"state": state_path.relative_to(project_root).as_posix(), "completion": manifest["completion"]["output_path"], "prompt": prompt}, "errors": []})
            print(json.dumps(base, indent=2))
            return 0

        sdk = _load_sdk(args.sdk_module)
        sandbox = getattr(sdk.Sandbox, manifest["execution"]["sandbox_mode"].replace("-", "_"))
        approval_mode = getattr(sdk.ApprovalMode, manifest["execution"]["approval_mode"])
        working_directory = resolve_inside(project_root, manifest["execution"]["working_directory"], "Working directory")
        thread_options = {"model": manifest["execution"]["model"], "config": {"model_reasoning_effort": manifest["execution"]["reasoning"]}, "cwd": str(working_directory), "sandbox": sandbox, "approval_mode": approval_mode}
        with sdk.Codex() as codex:
            thread = codex.thread_start(**thread_options) if action == "start" else codex.thread_resume(manifest["execution"]["thread"]["thread_id"], **thread_options)
            result = thread.run(prompt, output_schema=completion_schema)
        thread_id = thread.id
        if not thread_id:
            raise RuntimeError("SDK did not expose a thread ID after the turn")
        write_json_atomic(state_path, update_state(state, manifest, thread_id, "failed"))
        try:
            evidence = json.loads(result.final_response or "")
        except json.JSONDecodeError as error:
            raise ValueError(f"SDK final_response is not valid evidence JSON: {error}") from error
        evidence["thread_id"] = thread_id
        evidence["usage"] = _sdk_usage(result.usage)
        evidence_errors = validate_review_evidence(evidence, manifest, thread_id) if review_run else validate_completion(evidence, manifest, markdown, thread_id, project_root=project_root)
        if evidence_errors:
            base.update({"route": "failed", "action": action, "thread_id": thread_id, "completion_status": evidence.get("status"), "errors": evidence_errors})
            print(json.dumps(base, indent=2))
            return 1
        completion_path = resolve_inside(project_root, manifest["completion"]["output_path"], "Completion output path")
        write_json_atomic(completion_path, evidence)
        write_json_atomic(state_path, update_state(state, manifest, thread_id, evidence["status"]))
        base.update({"route": evidence["status"], "action": action, "thread_id": thread_id, "completion_status": evidence["status"], "artifacts": {"state": state_path.relative_to(project_root).as_posix(), "completion": completion_path.relative_to(project_root).as_posix()}, "errors": []})
        print(json.dumps(base, indent=2))
        return 0
    except Exception as error:
        recoverable_thread_id = getattr(thread, "id", None)
        if recoverable_thread_id and recovery:
            base["thread_id"] = recoverable_thread_id
            base["action"] = "start" if recovery["manifest"]["execution"]["thread"]["mode"] == "new" else "resume"
            try:
                write_json_atomic(recovery["state_path"], update_state(recovery["state"], recovery["manifest"], recoverable_thread_id, "failed"))
            except Exception as state_error:
                base["errors"].append(f"unable to preserve thread mapping: {state_error}")
        base["route"] = "failed"
        base["errors"].append(str(error))
        print(json.dumps(base, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
