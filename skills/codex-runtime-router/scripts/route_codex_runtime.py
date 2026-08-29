"""Route a resolved Project Harness manifest through the official Python Codex SDK."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
from pathlib import Path
from types import ModuleType
from typing import Any

from _runtime_core import (
    append_lifecycle,
    build_handoff_prompt,
    capture_git_snapshot,
    commands_equivalent,
    execution_phase,
    output_contract,
    read_lifecycle,
    read_state,
    resolve_inside,
    runtime_for_phase,
    update_state,
    validate_completion,
    validate_lifecycle,
    validate_preflight,
    validate_review_evidence,
    validate_structured_output_schema,
    write_json_atomic,
)


def _load_sdk(module_path: str | None) -> ModuleType:
    if not module_path:
        import openai_codex

        return openai_codex
    path = Path(module_path).resolve()
    spec = importlib.util.spec_from_file_location(
        "project_harness_mock_codex_sdk", path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load SDK module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sdk_usage(usage: Any) -> dict[str, int] | None:
    if usage is None:
        return None
    total = getattr(usage, "total", usage)
    raw = (
        total.model_dump(mode="json")
        if hasattr(total, "model_dump")
        else total
        if isinstance(total, dict)
        else {
            key: getattr(total, key, 0)
            for key in (
                "input_tokens",
                "cached_input_tokens",
                "cache_write_input_tokens",
                "output_tokens",
                "reasoning_output_tokens",
            )
        }
    )
    return {
        key: int(raw.get(key, 0) or 0)
        for key in (
            "input_tokens",
            "cached_input_tokens",
            "cache_write_input_tokens",
            "output_tokens",
            "reasoning_output_tokens",
        )
    }


def _result_base() -> dict[str, Any]:
    return {
        "route": "preflight_blocked",
        "spec_id": None,
        "phase": None,
        "action": "none",
        "model": None,
        "reasoning": None,
        "thread_id": None,
        "completion_status": None,
        "artifacts": {},
        "errors": [],
    }


def _attempt_path(output_path: Path, phase: str) -> Path:
    directory = output_path.parent / "attempts"
    existing = list(directory.glob(f"{phase}-*.json")) if directory.exists() else []
    return directory / f"{phase}-{len(existing) + 1:03d}.json"


def _set_status(
    spec_path: Path,
    manifest_path: Path,
    markdown: str,
    manifest: dict[str, Any],
    status: str,
) -> None:
    manifest["status"] = status
    write_json_atomic(manifest_path, manifest)
    updated = re.sub(r"(?m)^status:\s*[^\r\n]+", f"status: {status}", markdown, count=1)
    temporary = spec_path.with_name(f"{spec_path.name}.tmp")
    temporary.write_text(updated, encoding="utf-8", newline="\n")
    os.replace(temporary, spec_path)


def _run_canonical_validations(
    evidence: dict[str, Any], manifest: dict[str, Any], cwd: Path
) -> list[str]:
    """Run required automatable VAL commands and inject canonical receipts."""
    errors: list[str] = []
    items = {
        item.get("validation_id"): item
        for item in evidence.get("validation_evidence", [])
        if isinstance(item, dict)
    }
    for validation in manifest.get("validation", []):
        item = items.get(validation["id"])
        if not item:
            continue
        reported = item.get("canonical_command")
        if reported is not None and not commands_equivalent(
            str(reported), validation["command"]
        ):
            errors.append(
                f"{validation['id']} reported a command different from the manifest"
            )
        item["canonical_command"] = validation["command"]
        if validation.get("kind") == "manual" or not validation.get("required"):
            item["verification"] = "reported"
            continue
        try:
            completed = subprocess.run(
                validation["command"],
                cwd=cwd,
                shell=True,
                text=True,
                capture_output=True,
                timeout=900,
                check=False,
            )
            item["verification"] = "router"
            item["exit_code"] = completed.returncode
            item["result"] = "passed" if completed.returncode == 0 else "failed"
            output = "\n".join(
                part.strip()
                for part in (completed.stdout, completed.stderr)
                if part.strip()
            )
            item["evidence"] = [
                f"router executed canonical {validation['id']}",
                output[-4000:] or "command produced no output",
            ]
        except (OSError, subprocess.TimeoutExpired) as error:
            item["verification"] = "router"
            item["exit_code"] = None
            item["result"] = "failed"
            item["evidence"] = [
                f"router could not complete canonical {validation['id']}: {error}"
            ]
    return errors


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
        policy = json.loads(policy_path.read_text(encoding="utf-8-sig"))
        state = read_state(state_path)
        phase = execution_phase(manifest)
        runtime = runtime_for_phase(manifest, phase)
        contract = output_contract(manifest, phase)
        version2 = manifest.get("schema_version") == "2.0"
        slot = "review_thread_id" if phase == "review" else "implementation_thread_id"
        state_entry = state.get("specs", {}).get(manifest.get("spec_id"), {})
        state_recorded = (
            state_entry.get(slot)
            if state_entry.get("contract_version") == manifest.get("contract_version")
            else None
        )
        lifecycle_path = (
            resolve_inside(
                project_root, manifest["lifecycle"]["output_path"], "Lifecycle path"
            )
            if version2
            else None
        )
        lifecycle_exists = bool(lifecycle_path and lifecycle_path.exists())
        lifecycle = read_lifecycle(lifecycle_path, manifest) if lifecycle_path else None
        lifecycle_errors: list[str] = []
        lifecycle_recorded = None
        if lifecycle_exists and lifecycle:
            lifecycle_errors.extend(validate_lifecycle(lifecycle, manifest))
            lifecycle_recorded = lifecycle.get(slot)
            if (
                state_recorded
                and lifecycle_recorded
                and state_recorded != lifecycle_recorded
            ):
                lifecycle_errors.append(
                    f"ephemeral state and durable lifecycle disagree on {slot}"
                )
        recorded = lifecycle_recorded or state_recorded
        action = "resume" if recorded else "start"
        if not version2:
            action = (
                "start"
                if manifest["execution"]["thread"]["mode"] == "new"
                else "resume"
            )
            recorded = manifest["execution"]["thread"].get("thread_id")
        base.update(
            {
                "spec_id": manifest.get("spec_id"),
                "phase": phase,
                "model": runtime.get("model"),
                "reasoning": runtime.get("reasoning"),
            }
        )
        recovery = {
            "manifest": manifest,
            "state": state,
            "state_path": state_path,
            "phase": phase,
            "action": action,
            "lifecycle": lifecycle,
            "lifecycle_path": lifecycle_path,
        }
        skills_root = args.skills_root or (
            Path(os.environ["CODEX_HOME"]) / "skills"
            if os.environ.get("CODEX_HOME")
            else Path.home() / ".codex" / "skills"
        )
        errors = validate_preflight(
            markdown=markdown,
            manifest=manifest,
            policy=policy,
            project_root=project_root,
            skills_root=skills_root,
            state=state,
            phase=phase,
        )
        errors.extend(lifecycle_errors)
        schema_path = resolve_inside(
            project_root, contract.get("schema_path", ""), "Output schema path"
        )
        schema = None
        if not schema_path.is_file():
            errors.append(
                f"declared output schema does not exist: {contract.get('schema_path')}"
            )
        else:
            try:
                schema = json.loads(schema_path.read_text(encoding="utf-8-sig"))
                errors.extend(validate_structured_output_schema(schema))
            except json.JSONDecodeError as error:
                errors.append(f"output schema is invalid JSON: {error}")

        baseline_snapshot = None
        snapshot_path = None
        if version2 and manifest.get("baseline", {}).get("required"):
            snapshot_path = resolve_inside(
                project_root,
                manifest["baseline"]["snapshot_path"],
                "Baseline snapshot path",
            )
            if snapshot_path.exists():
                baseline_snapshot = json.loads(
                    snapshot_path.read_text(encoding="utf-8-sig")
                )
            elif phase != "implementation" or action != "start":
                errors.append(
                    "structural baseline Git snapshot must exist before resume or review"
                )
        if errors:
            base["errors"] = errors
            print(json.dumps(base, indent=2))
            return 1
        prompt = build_handoff_prompt(
            manifest,
            spec_path.relative_to(project_root).as_posix(),
            manifest_path.relative_to(project_root).as_posix(),
            phase,
        )
        if args.dry_run:
            base.update(
                {
                    "route": "preview",
                    "action": action,
                    "artifacts": {
                        "state": state_path.relative_to(project_root).as_posix(),
                        "output": contract["output_path"],
                        "baseline_snapshot": manifest.get("baseline", {}).get(
                            "snapshot_path"
                        ),
                        "prompt": prompt,
                    },
                    "errors": [],
                }
            )
            print(json.dumps(base, indent=2))
            return 0
        if snapshot_path and baseline_snapshot is None:
            baseline_snapshot = capture_git_snapshot(
                project_root, manifest["spec_id"], manifest["contract_version"]
            )
            write_json_atomic(snapshot_path, baseline_snapshot)

        sdk = _load_sdk(args.sdk_module)
        sandbox = getattr(sdk.Sandbox, runtime["sandbox_mode"].replace("-", "_"))
        approval_mode = getattr(sdk.ApprovalMode, runtime["approval_mode"])
        working_directory = resolve_inside(
            project_root, runtime["working_directory"], "Working directory"
        )
        options = {
            "model": runtime["model"],
            "config": {"model_reasoning_effort": runtime["reasoning"]},
            "cwd": str(working_directory),
            "sandbox": sandbox,
            "approval_mode": approval_mode,
        }
        with sdk.Codex() as codex:
            thread = (
                codex.thread_start(**options)
                if action == "start"
                else codex.thread_resume(recorded, **options)
            )
            result = thread.run(prompt, output_schema=schema)
        thread_id = thread.id
        if not thread_id:
            raise RuntimeError("SDK did not expose a thread ID after the turn")
        write_json_atomic(
            state_path, update_state(state, manifest, thread_id, "failed", phase)
        )
        evidence = json.loads(result.final_response or "")
        evidence["thread_id"] = thread_id
        evidence["usage"] = _sdk_usage(result.usage)
        evidence_errors: list[str] = []
        if phase == "implementation" and version2:
            evidence_errors.extend(
                _run_canonical_validations(evidence, manifest, working_directory)
            )
        if phase == "review":
            evidence_errors.extend(
                validate_review_evidence(evidence, manifest, thread_id)
            )
        else:
            evidence_errors.extend(
                validate_completion(
                    evidence,
                    manifest,
                    markdown,
                    thread_id,
                    project_root=project_root,
                    baseline_snapshot=baseline_snapshot,
                )
            )
        if evidence_errors:
            if lifecycle_path:
                write_json_atomic(
                    lifecycle_path,
                    append_lifecycle(
                        lifecycle,
                        phase=phase,
                        action=action,
                        outcome="failed",
                        thread_id=thread_id,
                        evidence_path=None,
                    ),
                )
            base.update(
                {
                    "route": "failed",
                    "action": action,
                    "thread_id": thread_id,
                    "completion_status": evidence.get("status"),
                    "errors": evidence_errors,
                }
            )
            print(json.dumps(base, indent=2))
            return 1

        output_path = resolve_inside(
            project_root, contract["output_path"], "Output path"
        )
        if version2:
            attempt = _attempt_path(output_path, phase)
            write_json_atomic(attempt, evidence)
        write_json_atomic(output_path, evidence)
        transition = evidence["status"]
        if version2:
            if phase == "implementation" and transition == "completed":
                transition = (
                    "implemented"
                    if manifest.get("review", {}).get("required")
                    else "done"
                )
            elif phase == "review" and transition == "approved":
                transition = "done"
            write_json_atomic(
                lifecycle_path,
                append_lifecycle(
                    lifecycle,
                    phase=phase,
                    action=action,
                    outcome=transition,
                    thread_id=thread_id,
                    evidence_path=output_path.relative_to(project_root).as_posix(),
                ),
            )
            if transition in {
                "implemented",
                "done",
                "changes_requested",
                "needs_design",
            }:
                _set_status(spec_path, manifest_path, markdown, manifest, transition)
        write_json_atomic(
            state_path, update_state(state, manifest, thread_id, transition, phase)
        )
        base.update(
            {
                "route": transition,
                "action": action,
                "thread_id": thread_id,
                "completion_status": evidence["status"],
                "artifacts": {
                    "state": state_path.relative_to(project_root).as_posix(),
                    "output": output_path.relative_to(project_root).as_posix(),
                    "lifecycle": lifecycle_path.relative_to(project_root).as_posix()
                    if lifecycle_path
                    else None,
                },
                "errors": [],
            }
        )
        print(json.dumps(base, indent=2))
        return 0
    except Exception as error:
        recoverable_thread_id = getattr(thread, "id", None)
        if recoverable_thread_id and recovery:
            base["thread_id"] = recoverable_thread_id
            try:
                write_json_atomic(
                    recovery["state_path"],
                    update_state(
                        recovery["state"],
                        recovery["manifest"],
                        recoverable_thread_id,
                        "failed",
                        recovery["phase"],
                    ),
                )
                if recovery["lifecycle_path"]:
                    write_json_atomic(
                        recovery["lifecycle_path"],
                        append_lifecycle(
                            recovery["lifecycle"],
                            phase=recovery["phase"],
                            action=recovery["action"],
                            outcome="failed",
                            thread_id=recoverable_thread_id,
                            evidence_path=None,
                        ),
                    )
            except Exception as state_error:
                base["errors"].append(
                    f"unable to preserve thread mapping: {state_error}"
                )
        base["route"] = "failed"
        base["errors"].append(str(error))
        print(json.dumps(base, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
