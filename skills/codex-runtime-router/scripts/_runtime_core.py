"""Deterministic preflight, state, handoff, and evidence rules for Codex routing."""

from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SPEC_SCRIPTS = Path(__file__).resolve().parents[2] / "project-spec-architect" / "scripts"
if str(SPEC_SCRIPTS) not in os.sys.path:
    os.sys.path.insert(0, str(SPEC_SCRIPTS))
from _spec_core import validate_spec_pair  # noqa: E402


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


def validate_completion(completion: Any, manifest: dict[str, Any], markdown: str, thread_id: str, *, project_root: str | Path | None = None) -> list[str]:
    """Reconcile implementation evidence with the manifest and repository."""
    errors: list[str] = []
    keys = ["spec_id", "contract_version", "status", "thread_id", "runtime", "changed_files", "artifacts", "acceptance_evidence", "validation_evidence", "deviations", "unresolved_items", "needs_design", "usage"]
    if not _require_keys(errors, completion, "completion", keys):
        return errors
    for key in completion:
        if key not in keys:
            errors.append(f"completion has unsupported property {key}")
    if completion.get("spec_id") != manifest.get("spec_id"):
        errors.append("completion spec_id does not match manifest")
    if completion.get("contract_version") != manifest.get("contract_version"):
        errors.append("completion contract_version does not match manifest")
    if completion.get("status") not in {"completed", "needs_design", "blocked", "failed"}:
        errors.append("completion status is invalid")
    if completion.get("thread_id") != thread_id:
        errors.append("completion thread_id does not match actual SDK thread")
    runtime = completion.get("runtime")
    if _require_keys(errors, runtime, "completion.runtime", ["classification", "model", "reasoning"]):
        for key in ("classification", "model", "reasoning"):
            if runtime.get(key) != manifest["execution"].get(key):
                errors.append(f"completion runtime {key} does not match manifest")
    for key in ("changed_files", "artifacts", "deviations", "unresolved_items"):
        if not isinstance(completion.get(key), list):
            errors.append(f"completion {key} must be an array")
    if project_root:
        for key in ("changed_files", "artifacts"):
            if not isinstance(completion.get(key), list):
                continue
            for value in completion[key]:
                try:
                    resolved = resolve_inside(project_root, value, f"completion {key} path")
                    if not resolved.exists():
                        errors.append(f"completion {key} path does not exist: {value}")
                    elif key == "changed_files" and not resolved.is_file():
                        errors.append(f"completion changed_files path is not a file: {value}")
                except ValueError as error:
                    errors.append(str(error))
    if not _is_object(completion.get("acceptance_evidence")):
        errors.append("acceptance_evidence must be an object")
    if not _is_object(completion.get("validation_evidence")):
        errors.append("validation_evidence must be an object")
    if completion.get("status") == "completed":
        if completion.get("needs_design") is not None:
            errors.append("completed evidence requires needs_design null")
        for acceptance_id in acceptance_ids(markdown):
            evidence = completion.get("acceptance_evidence", {}).get(acceptance_id)
            if not evidence or evidence.get("result") != "passed" or not isinstance(evidence.get("evidence"), list) or not evidence["evidence"]:
                errors.append(f"completed evidence is missing passing acceptance evidence for {acceptance_id}")
        for validation in (item for item in manifest.get("validation", []) if item.get("required")):
            evidence = completion.get("validation_evidence", {}).get(validation["id"])
            if not evidence:
                errors.append(f"completed evidence is missing {validation['id']}")
            else:
                if evidence.get("command") != validation.get("command"):
                    errors.append(f"{validation['id']} command differs from manifest")
                if evidence.get("result") != "passed" or evidence.get("exit_code") != 0:
                    errors.append(f"{validation['id']} did not pass with exit code zero")
    if completion.get("status") == "needs_design":
        if not _require_keys(errors, completion.get("needs_design"), "needs_design", ["question", "reason", "impact", "affected_areas", "alternatives"]):
            errors.append("needs_design status requires a structured needs_design payload")
    elif completion.get("status") != "completed" and completion.get("needs_design") is not None:
        errors.append(f"{completion.get('status')} evidence requires needs_design null")
    return errors


def validate_review_evidence(review: Any, manifest: dict[str, Any], thread_id: str) -> list[str]:
    """Reconcile independent review output with the materialized review runtime."""
    errors: list[str] = []
    keys = ["spec_id", "contract_version", "status", "thread_id", "runtime", "review_input", "findings", "evidence", "usage"]
    if not _require_keys(errors, review, "review evidence", keys):
        return errors
    for key in review:
        if key not in keys:
            errors.append(f"review evidence has unsupported property {key}")
    if review.get("spec_id") != manifest.get("spec_id"):
        errors.append("review evidence spec_id does not match manifest")
    if review.get("contract_version") != manifest.get("contract_version"):
        errors.append("review evidence contract_version does not match manifest")
    if review.get("status") not in {"approved", "changes_requested", "blocked", "failed"}:
        errors.append("review evidence status is invalid")
    if review.get("thread_id") != thread_id:
        errors.append("review evidence thread_id does not match actual SDK thread")
    runtime = review.get("runtime")
    if _require_keys(errors, runtime, "review evidence runtime", ["classification", "model", "reasoning"]):
        for key in ("classification", "model", "reasoning"):
            if runtime.get(key) != manifest["execution"].get(key):
                errors.append(f"review evidence runtime {key} does not match manifest execution")
    for key in ("review_input", "findings", "evidence"):
        if not isinstance(review.get(key), list):
            errors.append(f"review evidence {key} must be an array")
    review_input = review.get("review_input")
    if isinstance(review_input, list) and (not any(re.search("completion", str(item), re.IGNORECASE) for item in review_input) or not any(re.search("diff|artifact", str(item), re.IGNORECASE) for item in review_input)):
        errors.append("review evidence input must include completion evidence and diff/artifacts")
    if review.get("status") == "approved" and isinstance(review.get("findings"), list) and review["findings"]:
        errors.append("approved review evidence must have no findings")
    return errors


def build_handoff_prompt(manifest: dict[str, Any], spec_relative: str, manifest_relative: str) -> str:
    """Build the bounded clean-thread handoff from durable inputs only."""
    references = "\n".join(f"- {item['path']}: {item['purpose']}" for item in manifest.get("references", [])) or "- No additional declared references."
    skills = "\n".join(f"- {item['name']} ({item['source']}{': ' + item['path'] if item.get('path') else ''})" for item in manifest.get("skills", [])) or "- No specialized skill is required."
    return "\n".join((
        f"Execute {manifest['spec_id']}.", "", "Source of truth:", f"- {spec_relative}", f"- {manifest_relative}", "- AGENTS.md", "",
        "Declared references:", references, "", "Applicable skills:", skills, "", manifest["execution"]["handoff_prompt"], "",
        "Load only these durable inputs and directly relevant repository files. Do not use design-conversation history or create subagents by default.",
        "Return JSON conforming to the supplied completion schema. Set thread_id and usage to null; the router records actual SDK values.",
    ))


def validate_preflight(*, markdown: str, manifest: dict[str, Any], policy: dict[str, Any], project_root: str | Path, skills_root: str | Path | None, state: dict[str, Any]) -> list[str]:
    """Validate lifecycle and purpose-specific start/resume state before SDK access."""
    review_run = manifest.get("execution", {}).get("thread", {}).get("purpose") == "review"
    errors = validate_spec_pair(markdown, manifest, policy, project_root=project_root, skills_root=skills_root, require_ready=not review_run)
    if review_run and manifest.get("status") != "review":
        errors.append("review thread purpose requires Spec status review")
    if not review_run and manifest.get("status") != "ready":
        errors.append("implementation or worker execution requires Spec status ready")
    slot = "review_thread_id" if review_run else "implementation_thread_id"
    recorded = state.get("specs", {}).get(manifest.get("spec_id"), {}).get(slot)
    thread = manifest.get("execution", {}).get("thread", {})
    if thread.get("mode") == "new" and recorded:
        errors.append(f"new thread rejected because {slot} is already recorded; use resume")
    if thread.get("mode") == "resume" and recorded and recorded != thread.get("thread_id"):
        errors.append(f"resume thread_id does not match recorded {slot}")
    return errors


def read_state(file: str | Path) -> dict[str, Any]:
    """Load ephemeral Harness state or return a new empty state object."""
    path = Path(file)
    if not path.exists():
        return {"schema_version": "1.0", "specs": {}}
    state = json.loads(path.read_text(encoding="utf-8-sig"))
    if state.get("schema_version") != "1.0" or not isinstance(state.get("specs"), dict):
        raise ValueError("thread state is invalid")
    return state


def update_state(state: dict[str, Any], manifest: dict[str, Any], thread_id: str, status: str) -> dict[str, Any]:
    """Update the purpose-specific thread mapping in ephemeral state."""
    current = state["specs"].get(manifest["spec_id"], {"contract_version": manifest["contract_version"], "implementation_thread_id": None, "review_thread_id": None, "last_status": status, "updated_at": ""})
    slot = "review_thread_id" if manifest["execution"]["thread"]["purpose"] == "review" else "implementation_thread_id"
    state["specs"][manifest["spec_id"]] = {**current, "contract_version": manifest["contract_version"], slot: thread_id, "last_status": status, "updated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z")}
    return state


def write_json_atomic(file: str | Path, value: Any) -> None:
    """Write JSON atomically without exposing a partial state/receipt."""
    target = Path(file)
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f"{target.name}.", suffix=".tmp", dir=target.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.replace(temporary, target)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise
