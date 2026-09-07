"""Validate accepted Project Harness bootstrap plans before materialization."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def load_plan(file: str | Path) -> dict[str, Any]:
    """Load one UTF-8 Harness plan."""
    return json.loads(Path(file).read_text(encoding="utf-8-sig"))


def _require_keys(errors: list[str], value: Any, label: str, keys: list[str]) -> bool:
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return False
    for key in keys:
        if key not in value:
            errors.append(f"{label} is missing {key}")
    return True


def validate_harness_plan(plan: Any, *, require_accepted: bool = False) -> list[str]:
    """Return deterministic structural and materialization-gate errors."""
    errors: list[str] = []
    required = ["schema_version", "status", "project", "sources_of_truth", "documentation", "decisions", "workflows", "local_skill_candidates", "spec_strategy", "validation", "runtime_policy", "thread_policy", "automatic_handoff"]
    if not _require_keys(errors, plan, "harness plan", required):
        return errors
    if plan.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    if plan.get("status") not in {"proposed", "accepted"}:
        errors.append("status must be proposed or accepted")
    if require_accepted and plan.get("status") != "accepted":
        errors.append("materialization requires an accepted plan")
    if plan.get("automatic_handoff") is not False:
        errors.append("automatic_handoff must be false")
    _require_keys(errors, plan.get("project"), "project", ["name", "domain", "project_type", "objective"])
    sources = plan.get("sources_of_truth")
    if not isinstance(sources, list) or not sources:
        errors.append("sources_of_truth must contain at least one item")
    else:
        for index, source in enumerate(sources):
            if _require_keys(errors, source, f"sources_of_truth[{index}]", ["path", "kind", "authority", "action"]) and source.get("action") not in {"preserve", "map", "create"}:
                errors.append(f"sources_of_truth[{index}].action is invalid")
    _require_keys(errors, plan.get("documentation"), "documentation", ["preserve", "create", "path_mappings"])
    _require_keys(errors, plan.get("decisions"), "decisions", ["durable_path", "open"])
    _require_keys(errors, plan.get("spec_strategy"), "spec_strategy", ["root", "active_pattern", "markdown_name", "execution_name"])
    _require_keys(errors, plan.get("runtime_policy"), "runtime_policy", ["policy_version", "project_path"])
    _require_keys(errors, plan.get("thread_policy"), "thread_policy", ["design", "implementation", "needs_design", "parallel_writes", "subagents"])
    if not all(isinstance(plan.get(key), list) for key in ("workflows", "local_skill_candidates", "validation")):
        errors.append("workflows, local_skill_candidates, and validation must be arrays")
    if require_accepted and re.search(r"(?:\breplace[_ -]?me\b|\bTBD\b|\bTODO\b|\{\{|<[^>]+>)", json.dumps(plan), re.IGNORECASE):
        errors.append("accepted plan contains unresolved placeholder text")
    return errors
