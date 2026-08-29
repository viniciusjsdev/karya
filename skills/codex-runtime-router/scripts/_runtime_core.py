"""Deterministic preflight, lifecycle, Git, handoff, and evidence rules."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SPEC_SCRIPTS = (
    Path(__file__).resolve().parents[2] / "project-spec-architect" / "scripts"
)
if str(SPEC_SCRIPTS) not in os.sys.path:
    os.sys.path.insert(0, str(SPEC_SCRIPTS))
from _spec_core import validate_spec_pair
from _structured_output_schema import (
    normalize_legacy_output_schema as _normalize_legacy_output_schema,
)
from _structured_output_schema import (
    validate_structured_output_schema as _validate_structured_output_schema,
)

BASELINE_CATEGORIES = {
    "tests",
    "cli",
    "json_contracts",
    "persistence",
    "schemas",
    "protected_paths",
    "decisions",
}
LIFECYCLE_STATUSES = {
    "ready",
    "implementation",
    "implemented",
    "review",
    "changes_requested",
    "needs_design",
    "approved",
    "done",
    "blocked",
    "failed",
}


def normalize_legacy_output_schema(
    schema: Any, *, acceptance_ids: list[str], validation_ids: list[str]
) -> Any:
    """Expose the shared v1 migration helper through the runtime core."""
    return _normalize_legacy_output_schema(
        schema, acceptance_ids=acceptance_ids, validation_ids=validation_ids
    )


def validate_structured_output_schema(schema: Any) -> list[str]:
    """Expose the shared strict schema validator through the runtime core."""
    return _validate_structured_output_schema(schema)


def _is_object(value: Any) -> bool:
    return isinstance(value, dict)


def _require_keys(errors: list[str], value: Any, label: str, keys: list[str]) -> bool:
    if not _is_object(value):
        errors.append(f"{label} must be an object")
        return False
    for key in keys:
        if key not in value:
            errors.append(f"{label} is missing {key}")
    return True


def resolve_inside(root: str | Path, value: str, label: str) -> Path:
    """Resolve a project-relative path and reject traversal outside the project."""
    resolved_root = Path(root).resolve()
    resolved = (resolved_root / value).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as error:
        raise ValueError(f"{label} must remain inside project root: {value}") from error
    return resolved


def acceptance_ids(markdown: str) -> list[str]:
    """Return unique AC identifiers in source order."""
    return list(dict.fromkeys(re.findall(r"\bAC-[0-9]{3}\b", markdown)))


def commands_equivalent(left: str, right: str) -> bool:
    """Compare harmless textual command differences without shell interpretation."""
    try:
        return shlex.split(left, posix=os.name != "nt") == shlex.split(
            right, posix=os.name != "nt"
        )
    except ValueError:
        return left.strip() == right.strip()


def _index_unique(
    items: Any, key: str, label: str, errors: list[str]
) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list):
        errors.append(f"{label} must be an array")
        return {}
    indexed: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(items):
        if not isinstance(item, dict) or not isinstance(item.get(key), str):
            errors.append(f"{label}[{index}] must contain string {key}")
            continue
        identity = item[key]
        if identity in indexed:
            errors.append(f"{label} contains duplicate {identity}")
        indexed[identity] = item
    return indexed


def _sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def capture_git_snapshot(
    project_root: str | Path, spec_id: str, contract_version: int
) -> dict[str, Any]:
    """Capture dirty/untracked paths before execution so user changes stay distinguishable."""
    root = Path(project_root).resolve()
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
        raw = subprocess.run(
            ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
            cwd=root,
            capture_output=True,
            check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return {
            "schema_version": "1.0",
            "spec_id": spec_id,
            "contract_version": contract_version,
            "captured_at": _now(),
            "git_available": False,
            "head": None,
            "entries": [],
        }
    chunks = raw.decode(errors="replace").split("\0")
    entries: list[dict[str, Any]] = []
    index = 0
    while index < len(chunks):
        chunk = chunks[index]
        index += 1
        if not chunk:
            continue
        status, path = chunk[:2], chunk[3:]
        old_path = None
        if (status[0] in {"R", "C"} or status[1] in {"R", "C"}) and index < len(chunks):
            old_path = chunks[index]
            index += 1
        resolved = root / path
        entries.append(
            {
                "path": path.replace("\\", "/"),
                "status": status,
                "old_path": old_path.replace("\\", "/") if old_path else None,
                "exists": resolved.exists(),
                "is_file": resolved.is_file(),
                "sha256": _sha256(resolved),
            }
        )
    return {
        "schema_version": "1.0",
        "spec_id": spec_id,
        "contract_version": contract_version,
        "captured_at": _now(),
        "git_available": True,
        "head": head,
        "entries": entries,
    }


def _change_from_status(status: str, *, existed_before: bool, exists_now: bool) -> str:
    if not exists_now:
        return "deleted"
    if not existed_before and ("?" in status or "A" in status):
        return "added"
    return "modified"


def produced_git_changes(
    project_root: str | Path, baseline: dict[str, Any]
) -> dict[str, str] | None:
    """Return committed and working-tree changes since baseline, excluding user dirt."""
    if not baseline.get("git_available"):
        return None
    root = Path(project_root).resolve()
    current = capture_git_snapshot(
        root, baseline["spec_id"], baseline["contract_version"]
    )
    if not current.get("git_available"):
        return None
    try:
        raw_diff = (
            subprocess.run(
                [
                    "git",
                    "diff",
                    "--name-status",
                    "-z",
                    "--find-renames",
                    str(baseline["head"]),
                    "--",
                ],
                cwd=root,
                capture_output=True,
                check=True,
            )
            .stdout.decode(errors="replace")
            .split("\0")
        )
    except (OSError, subprocess.CalledProcessError, KeyError):
        return None
    before = {item["path"]: item for item in baseline.get("entries", [])}
    after = {item["path"]: item for item in current.get("entries", [])}
    changes: dict[str, str] = {}
    index = 0
    while index < len(raw_diff):
        status = raw_diff[index]
        index += 1
        if not status or index >= len(raw_diff):
            continue
        first_path = raw_diff[index].replace("\\", "/")
        index += 1
        code = status[0]
        if code in {"R", "C"} and index < len(raw_diff):
            second_path = raw_diff[index].replace("\\", "/")
            index += 1
            if code == "R":
                changes[first_path] = "deleted"
            changes[second_path] = "added"
        else:
            changes[first_path] = (
                "added" if code == "A" else "deleted" if code == "D" else "modified"
            )

    for path in sorted(set(before) | set(after)):
        old = before.get(path)
        new = after.get(path)
        resolved = root / path
        exists_now = resolved.exists()
        current_hash = _sha256(resolved)
        if old:
            unchanged_existing = old.get("exists") and current_hash == old.get("sha256")
            unchanged_absent = not old.get("exists") and not exists_now
            if unchanged_existing or unchanged_absent:
                changes.pop(path, None)
                if old.get("old_path"):
                    changes.pop(old["old_path"], None)
                continue
            changes[path] = "modified" if exists_now else "deleted"
            continue
        if new and not old:
            changes[path] = _change_from_status(
                new.get("status", ""), existed_before=False, exists_now=exists_now
            )
    return changes


def validate_completion(
    completion: Any,
    manifest: dict[str, Any],
    markdown: str,
    thread_id: str,
    *,
    project_root: str | Path | None = None,
    baseline_snapshot: dict[str, Any] | None = None,
) -> list[str]:
    """Reconcile implementation evidence with IDs, runtime, filesystem, and Git."""
    errors: list[str] = []
    keys = [
        "spec_id",
        "contract_version",
        "status",
        "thread_id",
        "runtime",
        "changed_files",
        "artifacts",
        "acceptance_evidence",
        "validation_evidence",
        "deviations",
        "unresolved_items",
        "needs_design",
        "usage",
    ]
    if not _require_keys(errors, completion, "completion", keys):
        return errors
    for key in completion:
        if key not in keys:
            errors.append(f"completion has unsupported property {key}")
    if completion.get("spec_id") != manifest.get("spec_id"):
        errors.append("completion spec_id does not match manifest")
    if completion.get("contract_version") != manifest.get("contract_version"):
        errors.append("completion contract_version does not match manifest")
    if completion.get("status") not in {
        "completed",
        "needs_design",
        "blocked",
        "failed",
    }:
        errors.append("completion status is invalid")
    if completion.get("thread_id") != thread_id:
        errors.append("completion thread_id does not match actual SDK thread")
    runtime = completion.get("runtime")
    if _require_keys(
        errors, runtime, "completion.runtime", ["classification", "model", "reasoning"]
    ):
        for key in ("classification", "model", "reasoning"):
            if runtime.get(key) != manifest["execution"].get(key):
                errors.append(f"completion runtime {key} does not match manifest")
    for key in ("artifacts", "deviations", "unresolved_items"):
        if not isinstance(completion.get(key), list):
            errors.append(f"completion {key} must be an array")

    version2 = manifest.get("schema_version") == "2.0"
    if version2:
        changed = _index_unique(
            completion.get("changed_files"), "path", "changed_files", errors
        )
        acceptance = _index_unique(
            completion.get("acceptance_evidence"), "id", "acceptance_evidence", errors
        )
        validations = _index_unique(
            completion.get("validation_evidence"),
            "validation_id",
            "validation_evidence",
            errors,
        )
        expected_acceptance = set(acceptance_ids(markdown))
        expected_validations = {item["id"] for item in manifest.get("validation", [])}
        if set(acceptance) != expected_acceptance:
            errors.append(
                "acceptance_evidence IDs must match every declared AC exactly once"
            )
        if set(validations) != expected_validations:
            errors.append(
                "validation_evidence IDs must match every declared VAL exactly once"
            )
        if project_root:
            for path, item in changed.items():
                try:
                    resolved = resolve_inside(project_root, path, "changed file path")
                    change = item.get("change")
                    if change in {"added", "modified"} and not resolved.is_file():
                        errors.append(
                            f"{change} changed file must exist and be a file: {path}"
                        )
                    if change == "deleted" and resolved.exists():
                        errors.append(f"deleted changed file must be absent: {path}")
                    if change not in {"added", "modified", "deleted"}:
                        errors.append(f"changed file has invalid change: {path}")
                except ValueError as error:
                    errors.append(str(error))
            if baseline_snapshot:
                git_changes = produced_git_changes(project_root, baseline_snapshot)
                if git_changes is not None:
                    owned = {
                        manifest.get("completion", {}).get("output_path"),
                        manifest.get("review", {}).get("output_path"),
                        manifest.get("lifecycle", {}).get("output_path"),
                        manifest.get("baseline", {}).get("snapshot_path"),
                    }
                    git_changes = {
                        path: change
                        for path, change in git_changes.items()
                        if path not in owned
                        and not path.startswith(".harness/")
                        and "/evidence/attempts/" not in path
                        and not path.endswith("/SPEC.md")
                        and not path.endswith("/SPEC.execution.json")
                    }
                if (
                    git_changes is not None
                    and {path: item.get("change") for path, item in changed.items()}
                    != git_changes
                ):
                    errors.append(
                        "changed_files do not reconcile with changes since the Git baseline"
                    )
    else:
        acceptance = (
            completion.get("acceptance_evidence")
            if isinstance(completion.get("acceptance_evidence"), dict)
            else {}
        )
        validations = (
            completion.get("validation_evidence")
            if isinstance(completion.get("validation_evidence"), dict)
            else {}
        )
        if not isinstance(completion.get("changed_files"), list):
            errors.append("completion changed_files must be an array")

    if project_root and isinstance(completion.get("artifacts"), list):
        for value in completion["artifacts"]:
            try:
                if not resolve_inside(project_root, value, "artifact path").exists():
                    errors.append(f"artifact path does not exist: {value}")
            except ValueError as error:
                errors.append(str(error))
    if completion.get("status") == "completed":
        if completion.get("needs_design") is not None:
            errors.append("completed evidence requires needs_design null")
        for acceptance_id in acceptance_ids(markdown):
            evidence = acceptance.get(acceptance_id)
            if (
                not evidence
                or evidence.get("result") != "passed"
                or not evidence.get("evidence")
            ):
                errors.append(
                    f"completed evidence is missing passing acceptance evidence for {acceptance_id}"
                )
        for validation in manifest.get("validation", []):
            evidence = validations.get(validation["id"])
            if not evidence:
                errors.append(f"completed evidence is missing {validation['id']}")
                continue
            command = (
                evidence.get("canonical_command")
                if version2
                else evidence.get("command")
            )
            if command is not None and not commands_equivalent(
                command, validation.get("command", "")
            ):
                errors.append(f"{validation['id']} command differs from manifest")
            if validation.get("required") and (
                evidence.get("result") != "passed" or evidence.get("exit_code") != 0
            ):
                errors.append(f"{validation['id']} did not pass with exit code zero")
    if completion.get("status") == "needs_design":
        _require_keys(
            errors,
            completion.get("needs_design"),
            "needs_design",
            ["question", "reason", "impact", "affected_areas", "alternatives"],
        )
    elif (
        completion.get("status") != "completed"
        and completion.get("needs_design") is not None
    ):
        errors.append(f"{completion.get('status')} evidence requires needs_design null")
    return errors


def validate_review_evidence(
    review: Any, manifest: dict[str, Any], thread_id: str
) -> list[str]:
    """Reconcile independent review output with the derived review runtime."""
    errors: list[str] = []
    version2 = manifest.get("schema_version") == "2.0"
    keys = [
        "spec_id",
        "contract_version",
        "status",
        "thread_id",
        "runtime",
        "review_input",
        "findings",
        "evidence",
        "usage",
    ]
    if version2:
        keys.insert(6, "baseline_assessment")
    if not _require_keys(errors, review, "review evidence", keys):
        return errors
    for key in review:
        if key not in keys:
            errors.append(f"review evidence has unsupported property {key}")
    if review.get("spec_id") != manifest.get("spec_id") or review.get(
        "contract_version"
    ) != manifest.get("contract_version"):
        errors.append("review evidence identity/version does not match manifest")
    if review.get("status") not in {
        "approved",
        "changes_requested",
        "blocked",
        "failed",
    }:
        errors.append("review evidence status is invalid")
    if review.get("thread_id") != thread_id:
        errors.append("review evidence thread_id does not match actual SDK thread")
    expected = (
        {
            "classification": "critical_review",
            "model": manifest.get("review", {}).get("model"),
            "reasoning": manifest.get("review", {}).get("reasoning"),
        }
        if version2
        else manifest.get("execution", {})
    )
    runtime = review.get("runtime")
    if _require_keys(
        errors,
        runtime,
        "review evidence runtime",
        ["classification", "model", "reasoning"],
    ):
        for key in ("classification", "model", "reasoning"):
            if runtime.get(key) != expected.get(key):
                errors.append(
                    f"review evidence runtime {key} does not match derived review runtime"
                )
    for key in ("review_input", "findings", "evidence"):
        if not isinstance(review.get(key), list):
            errors.append(f"review evidence {key} must be an array")
    inputs = " ".join(str(item).lower() for item in review.get("review_input", []))
    required_inputs = (
        ("completion", "diff", "baseline")
        if manifest.get("baseline", {}).get("required")
        else ("completion", "diff")
    )
    for label in required_inputs:
        if version2 and label not in inputs:
            errors.append(f"review evidence input must include {label}")
    if version2 and manifest.get("baseline", {}).get("required"):
        assessed = _index_unique(
            review.get("baseline_assessment"), "category", "baseline_assessment", errors
        )
        if set(assessed) != BASELINE_CATEGORIES:
            errors.append(
                "baseline_assessment must cover every baseline category exactly once"
            )
        if review.get("status") == "approved" and any(
            item.get("result") == "regressed" for item in assessed.values()
        ):
            errors.append(
                "approved review cannot contain a regressed baseline category"
            )
    if review.get("status") == "approved" and review.get("findings"):
        errors.append("approved review evidence must have no findings")
    return errors


def execution_phase(manifest: dict[str, Any]) -> str:
    """Derive v2 implementation/review phase without rewriting the runtime block."""
    if manifest.get("schema_version") != "2.0":
        return (
            "review"
            if manifest.get("execution", {}).get("thread", {}).get("purpose")
            == "review"
            else "implementation"
        )
    status = manifest.get("status")
    if status in {"ready", "in_progress", "changes_requested"}:
        return "implementation"
    if status in {"implemented", "review"}:
        return "review"
    raise ValueError(f"Spec status {status} has no executable phase")


def runtime_for_phase(manifest: dict[str, Any], phase: str) -> dict[str, Any]:
    if phase == "implementation":
        return manifest["execution"]
    review = manifest["review"]
    return {
        "classification": "critical_review",
        "role": "reviewer",
        "model": review["model"],
        "reasoning": review["reasoning"],
        "working_directory": manifest["execution"]["working_directory"],
        "sandbox_mode": "read-only",
        "approval_mode": "deny_all",
        "handoff_prompt": review.get(
            "handoff_prompt", "Review independently using durable evidence."
        ),
    }


def output_contract(manifest: dict[str, Any], phase: str) -> dict[str, str]:
    if phase == "implementation" or manifest.get("schema_version") != "2.0":
        return manifest["completion"]
    return {
        "schema_path": manifest["review"]["schema_path"],
        "output_path": manifest["review"]["output_path"],
    }


def build_handoff_prompt(
    manifest: dict[str, Any],
    spec_relative: str,
    manifest_relative: str,
    phase: str = "implementation",
) -> str:
    references = (
        "\n".join(
            f"- {item['path']}: {item['purpose']}"
            for item in manifest.get("references", [])
        )
        or "- No additional declared references."
    )
    skills = (
        "\n".join(
            f"- {item['name']} ({item['source']}{': ' + item['path'] if item.get('path') else ''})"
            for item in manifest.get("skills", [])
        )
        or "- No specialized skill is required."
    )
    baseline = manifest.get("baseline", {})
    baseline_text = (
        f"- {baseline.get('path')}\n- {baseline.get('snapshot_path')}"
        if baseline.get("required")
        else "- No structural baseline required."
    )
    return "\n".join(
        (
            f"{phase.title()} {manifest['spec_id']}.",
            "",
            "Source of truth:",
            f"- {spec_relative}",
            f"- {manifest_relative}",
            "- AGENTS.md",
            "",
            "Declared references:",
            references,
            "",
            "Applicable skills:",
            skills,
            "",
            "Structural baseline:",
            baseline_text,
            "",
            runtime_for_phase(manifest, phase)["handoff_prompt"],
            "",
            "Load only durable inputs and relevant repository files. Do not use design-chat history or create subagents by default.",
            "Return JSON conforming to the supplied output schema. Set thread_id, usage, and validation canonical_command values to null; the router records actual values and runs canonical automated validations.",
        )
    )


def validate_preflight(
    *,
    markdown: str,
    manifest: dict[str, Any],
    policy: dict[str, Any],
    project_root: str | Path,
    skills_root: str | Path | None,
    state: dict[str, Any],
    phase: str | None = None,
) -> list[str]:
    phase = phase or execution_phase(manifest)
    version2 = manifest.get("schema_version") == "2.0"
    errors = validate_spec_pair(
        markdown,
        manifest,
        policy,
        project_root=project_root,
        skills_root=skills_root,
        require_ready=manifest.get("status") == "ready",
    )
    if not version2:
        review_run = phase == "review"
        if review_run and manifest.get("status") != "review":
            errors.append("review thread purpose requires Spec status review")
        if not review_run and manifest.get("status") != "ready":
            errors.append(
                "implementation or worker execution requires Spec status ready"
            )
    slot = "review_thread_id" if phase == "review" else "implementation_thread_id"
    state_entry = state.get("specs", {}).get(manifest.get("spec_id"), {})
    recorded = (
        state_entry.get(slot)
        if state_entry.get("contract_version") == manifest.get("contract_version")
        else None
    )
    if not version2:
        thread = manifest.get("execution", {}).get("thread", {})
        if thread.get("mode") == "new" and recorded:
            errors.append(
                f"new thread rejected because {slot} is already recorded; use resume"
            )
        if (
            thread.get("mode") == "resume"
            and recorded
            and recorded != thread.get("thread_id")
        ):
            errors.append(f"resume thread_id does not match recorded {slot}")
    return errors


def read_state(file: str | Path) -> dict[str, Any]:
    path = Path(file)
    if not path.exists():
        return {"schema_version": "1.0", "specs": {}}
    state = json.loads(path.read_text(encoding="utf-8-sig"))
    if state.get("schema_version") != "1.0" or not isinstance(state.get("specs"), dict):
        raise ValueError("thread state is invalid")
    return state


def update_state(
    state: dict[str, Any],
    manifest: dict[str, Any],
    thread_id: str,
    status: str,
    phase: str | None = None,
) -> dict[str, Any]:
    phase = phase or execution_phase(manifest)
    current = state["specs"].get(manifest["spec_id"])
    if not current or current.get("contract_version") != manifest["contract_version"]:
        current = {
            "contract_version": manifest["contract_version"],
            "implementation_thread_id": None,
            "review_thread_id": None,
            "last_status": status,
            "updated_at": "",
        }
    slot = "review_thread_id" if phase == "review" else "implementation_thread_id"
    existing = current.get(slot)
    if existing and existing != thread_id:
        raise ValueError(f"refusing to replace existing {slot}")
    state["specs"][manifest["spec_id"]] = {
        **current,
        "contract_version": manifest["contract_version"],
        slot: thread_id,
        "last_status": status,
        "updated_at": _now(),
    }
    return state


def read_lifecycle(file: str | Path, manifest: dict[str, Any]) -> dict[str, Any]:
    path = Path(file)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8-sig"))
    return {
        "schema_version": "1.0",
        "spec_id": manifest["spec_id"],
        "contract_version": manifest["contract_version"],
        "status": manifest["status"],
        "implementation_thread_id": None,
        "review_thread_id": None,
        "events": [],
    }


def validate_lifecycle(lifecycle: Any, manifest: dict[str, Any]) -> list[str]:
    """Validate durable lifecycle identity, shape, sequence, and thread uniqueness."""
    errors: list[str] = []
    keys = {
        "schema_version",
        "spec_id",
        "contract_version",
        "status",
        "implementation_thread_id",
        "review_thread_id",
        "events",
    }
    if not isinstance(lifecycle, dict):
        return ["durable lifecycle must be an object"]
    if set(lifecycle) != keys:
        errors.append("durable lifecycle fields do not match the lifecycle contract")
    if lifecycle.get("schema_version") != "1.0":
        errors.append("durable lifecycle schema_version must be 1.0")
    if lifecycle.get("spec_id") != manifest.get("spec_id") or lifecycle.get(
        "contract_version"
    ) != manifest.get("contract_version"):
        errors.append("durable lifecycle identity/version does not match the Spec")
    if lifecycle.get("status") not in LIFECYCLE_STATUSES:
        errors.append("durable lifecycle status is invalid")
    events = lifecycle.get("events")
    if not isinstance(events, list):
        return [*errors, "durable lifecycle events must be an array"]
    phase_ids = {"implementation": set(), "review": set()}
    event_keys = {
        "sequence",
        "phase",
        "action",
        "outcome",
        "thread_id",
        "evidence_path",
        "recorded_at",
    }
    for index, event in enumerate(events, start=1):
        if not isinstance(event, dict) or set(event) != event_keys:
            errors.append(f"durable lifecycle event {index} has invalid fields")
            continue
        if event.get("sequence") != index:
            errors.append("durable lifecycle event sequence must be contiguous")
        phase = event.get("phase")
        if phase not in phase_ids:
            errors.append(f"durable lifecycle event {index} has invalid phase")
        elif isinstance(event.get("thread_id"), str) and event["thread_id"]:
            phase_ids[phase].add(event["thread_id"])
        else:
            errors.append(f"durable lifecycle event {index} has invalid thread_id")
        if event.get("action") not in {"start", "resume"}:
            errors.append(f"durable lifecycle event {index} has invalid action")
    for phase, slot in (
        ("implementation", "implementation_thread_id"),
        ("review", "review_thread_id"),
    ):
        recorded = lifecycle.get(slot)
        if recorded is not None and not isinstance(recorded, str):
            errors.append(f"durable lifecycle {slot} must be a string or null")
        if len(phase_ids[phase]) > 1 or (
            phase_ids[phase] and recorded not in phase_ids[phase]
        ):
            errors.append(f"durable lifecycle must preserve exactly one {slot}")
    valid_events = [
        event
        for event in events
        if isinstance(event, dict) and set(event) == event_keys
    ]
    previous_outcome: str | None = None
    previous_phase: str | None = None
    index = 0
    while index < len(valid_events):
        entry = valid_events[index]
        phase = entry.get("phase")
        if entry.get("outcome") != phase or phase not in {"implementation", "review"}:
            errors.append("durable lifecycle run must begin with its phase outcome")
            break
        allowed_next_phase = {
            None: {"implementation"},
            "failed": {previous_phase},
            "blocked": {previous_phase},
            "needs_design": {"implementation"},
            "implemented": {"review"},
            "changes_requested": {"implementation"},
        }.get(previous_outcome, set())
        if phase not in allowed_next_phase:
            errors.append(
                f"durable lifecycle cannot transition from {previous_outcome} to {phase}"
            )
        if index + 1 >= len(valid_events):
            errors.append("durable lifecycle phase entry has no outcome")
            break
        terminal = valid_events[index + 1]
        allowed_terminal = (
            {"implemented", "needs_design", "blocked", "failed"}
            if phase == "implementation"
            else {"approved", "changes_requested", "blocked", "failed"}
        )
        if (
            terminal.get("phase") != phase
            or terminal.get("thread_id") != entry.get("thread_id")
            or terminal.get("action") != entry.get("action")
            or terminal.get("outcome") not in allowed_terminal
        ):
            errors.append(f"durable lifecycle {phase} run has an invalid outcome")
            break
        previous_outcome = terminal.get("outcome")
        previous_phase = phase
        index += 2
        closes_without_review = (
            phase == "implementation"
            and previous_outcome == "implemented"
            and not manifest.get("review", {}).get("required")
        )
        if previous_outcome == "approved" or closes_without_review:
            if (
                index >= len(valid_events)
                or valid_events[index].get("outcome") != "done"
            ):
                errors.append(
                    "durable lifecycle successful terminal outcome must close as done"
                )
                break
            done = valid_events[index]
            if (
                done.get("phase") != phase
                or done.get("thread_id") != entry.get("thread_id")
                or done.get("action") != entry.get("action")
            ):
                errors.append("durable lifecycle done event does not match its run")
            previous_outcome = "done"
            index += 1
            if index != len(valid_events):
                errors.append("durable lifecycle has events after done")
                break
    if valid_events and lifecycle.get("status") != valid_events[-1].get("outcome"):
        errors.append("durable lifecycle status must match its final event outcome")
    return errors


def append_lifecycle(
    lifecycle: dict[str, Any],
    *,
    phase: str,
    action: str,
    outcome: str,
    thread_id: str,
    evidence_path: str | None,
) -> dict[str, Any]:
    slot = "review_thread_id" if phase == "review" else "implementation_thread_id"
    if lifecycle.get(slot) not in {None, thread_id}:
        raise ValueError(f"lifecycle already records a different {slot}")
    lifecycle[slot] = thread_id
    lifecycle["status"] = outcome
    lifecycle["events"].append(
        {
            "sequence": len(lifecycle["events"]) + 1,
            "phase": phase,
            "action": action,
            "outcome": outcome,
            "thread_id": thread_id,
            "evidence_path": evidence_path,
            "recorded_at": _now(),
        }
    )
    return lifecycle


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def write_json_atomic(file: str | Path, value: Any) -> None:
    target = Path(file)
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f"{target.name}.", suffix=".tmp", dir=target.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.replace(temporary, target)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise
