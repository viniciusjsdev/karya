"""Validate Project Harness Specs and manifests without executing project work."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from _structured_output_schema import validate_structured_output_schema

STATUSES = {
    "draft",
    "design",
    "ready",
    "in_progress",
    "needs_design",
    "implemented",
    "review",
    "changes_requested",
    "done",
}
CLASSIFICATIONS = {"design", "normal_implementation", "mechanical", "critical_review"}
MODELS = {"gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna"}
REASONING = {"low", "medium", "high", "xhigh", "max"}
REQUIRED_SECTIONS = (
    "Goal",
    "Context",
    "Scope",
    "Non-scope",
    "Requirements",
    "Business or domain rules",
    "Decisions already made",
    "Constraints",
    "Acceptance criteria",
    "Affected areas",
    "References",
    "Skills",
    "Validation requirements",
    "Review requirements",
    "Execution and runtime",
)


def load_json(file: str | Path) -> dict[str, Any]:
    """Load one UTF-8 JSON object."""
    return json.loads(Path(file).read_text(encoding="utf-8-sig"))


def parse_frontmatter(text: str) -> dict[str, str]:
    """Parse the intentionally flat YAML frontmatter used by SPEC.md."""
    match = re.match(
        r"^---\s*\r?\n([\s\S]*?)\r?\n---(?:\s*\r?\n|$)", text.lstrip("\ufeff")
    )
    if not match:
        return {}
    result: dict[str, str] = {}
    for line in re.split(r"\r?\n", match.group(1)):
        item = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*?)\s*$", line)
        if item:
            result[item.group(1)] = item.group(2).strip("\"'")
    return result


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


def _has_placeholder(value: Any) -> bool:
    return bool(
        re.search(
            r"(?:\bTBD\b|\bTODO\b|replace[_ -]?me|\{\{|<[^>]+>)",
            str(value),
            re.IGNORECASE,
        )
    )


def _unsafe_command(command: str) -> bool:
    return bool(re.search(r"[;&|><`\r\n]|\$\(", command))


def validate_runtime_policy(policy: Any) -> list[str]:
    """Validate the deterministic runtime policy fields consumed by the Harness."""
    errors: list[str] = []
    if not _require_keys(
        errors,
        policy,
        "runtime policy",
        ["policy_version", "models", "reasoning_levels", "defaults", "escalations"],
    ):
        return errors
    for classification in CLASSIFICATIONS:
        item = policy.get("defaults", {}).get(classification)
        if not item:
            errors.append(f"runtime policy is missing default {classification}")
        elif (
            item.get("model") not in MODELS
            or item.get("reasoning") not in REASONING
            or not item.get("role")
        ):
            errors.append(f"runtime policy default {classification} is invalid")
    return errors


def validate_execution_manifest(manifest: Any, policy: dict[str, Any]) -> list[str]:
    """Validate one resolved execution manifest against its pinned policy."""
    errors: list[str] = []
    version = manifest.get("schema_version") if isinstance(manifest, dict) else None
    root_keys = [
        "schema_version",
        "spec_id",
        "contract_version",
        "status",
        "automatic_handoff",
        "execution",
        "skills",
        "references",
        "validation",
        "review",
        "escalation",
        "completion",
    ]
    if version == "2.0":
        root_keys.extend(["baseline", "lifecycle"])
    if not _require_keys(errors, manifest, "execution manifest", root_keys):
        return errors
    if version not in {"1.0", "2.0"}:
        errors.append("schema_version must be 1.0 or 2.0")
    if not re.fullmatch(r"SPEC-[0-9]{3,}", str(manifest.get("spec_id", ""))):
        errors.append("spec_id must match SPEC-NNN")
    if (
        not isinstance(manifest.get("contract_version"), int)
        or manifest["contract_version"] < 1
    ):
        errors.append("contract_version must be a positive integer")
    if manifest.get("status") not in STATUSES:
        errors.append("status is invalid")
    if manifest.get("automatic_handoff") is not False:
        errors.append("automatic_handoff must be false")

    execution = manifest.get("execution")
    execution_keys = [
        "classification",
        "role",
        "model",
        "reasoning",
        "routing_rationale",
        "runtime_override",
        "working_directory",
        "sandbox_mode",
        "approval_mode",
        "thread",
        "handoff_prompt",
    ]
    if _require_keys(errors, execution, "execution", execution_keys):
        if execution.get("classification") not in CLASSIFICATIONS:
            errors.append("execution.classification is invalid")
        if execution.get("model") not in MODELS:
            errors.append("execution.model is invalid")
        if execution.get("reasoning") not in REASONING:
            errors.append("execution.reasoning is invalid")
        if execution.get("role") not in {
            "architect",
            "developer",
            "worker",
            "reviewer",
        }:
            errors.append("execution.role is invalid")
        if len(str(execution.get("routing_rationale", ""))) < 20:
            errors.append("execution.routing_rationale is too short")
        if len(str(execution.get("handoff_prompt", ""))) < 40:
            errors.append("execution.handoff_prompt is too short")
        if execution.get("sandbox_mode") not in {
            "read-only",
            "workspace-write",
            "full-access",
        }:
            errors.append("execution.sandbox_mode is invalid")
        if execution.get("approval_mode") not in {"deny_all", "auto_review"}:
            errors.append("execution.approval_mode is invalid")
        thread = execution.get("thread")
        if _require_keys(
            errors, thread, "execution.thread", ["mode", "purpose", "thread_id"]
        ):
            if thread.get("mode") not in {"new", "resume"}:
                errors.append("execution.thread.mode is invalid")
            if thread.get("purpose") not in {
                "design",
                "implementation",
                "worker",
                "review",
            }:
                errors.append("execution.thread.purpose is invalid")
            if thread.get("mode") == "resume" and not thread.get("thread_id"):
                errors.append("resume mode requires execution.thread.thread_id")
            if thread.get("mode") == "new" and thread.get("thread_id") is not None:
                errors.append("new mode requires a null execution.thread.thread_id")
        defaults = policy.get("defaults", {}).get(execution.get("classification"))
        if defaults:
            differs = any(
                defaults.get(key) != execution.get(key)
                for key in ("model", "reasoning", "role")
            )
            override = execution.get("runtime_override")
            if differs and (
                not _is_object(override) or len(str(override.get("reason", ""))) < 20
            ):
                errors.append(
                    "runtime differing from policy defaults requires runtime_override.reason"
                )
            if (
                differs
                and _is_object(override)
                and (
                    override.get("default_model") != defaults.get("model")
                    or override.get("default_reasoning") != defaults.get("reasoning")
                )
            ):
                errors.append(
                    "runtime_override defaults do not match the runtime policy"
                )
            if not differs and override is not None:
                errors.append(
                    "runtime_override must be null when policy defaults are used"
                )

    skills = manifest.get("skills")
    if not isinstance(skills, list):
        errors.append("skills must be an array")
    else:
        for index, skill in enumerate(skills):
            if not _require_keys(
                errors,
                skill,
                f"skills[{index}]",
                ["name", "source", "path", "required"],
            ):
                continue
            if not re.fullmatch(r"[a-z0-9-]+", str(skill.get("name", ""))):
                errors.append(f"skills[{index}].name is invalid")
            if skill.get("source") not in {"project", "installed"}:
                errors.append(f"skills[{index}].source is invalid")
            if skill.get("source") == "project" and not skill.get("path"):
                errors.append(f"skills[{index}] project source requires path")
            if skill.get("source") == "installed" and skill.get("path") is not None:
                errors.append(f"skills[{index}] installed source requires null path")

    references = manifest.get("references")
    if not isinstance(references, list):
        errors.append("references must be an array")
    else:
        for index, reference in enumerate(references):
            _require_keys(
                errors,
                reference,
                f"references[{index}]",
                ["path", "purpose", "required"],
            )

    validations = manifest.get("validation")
    if not isinstance(validations, list) or not validations:
        errors.append("validation must contain at least one item")
    else:
        ids: set[str] = set()
        for index, item in enumerate(validations):
            if not _require_keys(
                errors,
                item,
                f"validation[{index}]",
                ["id", "kind", "command", "required"],
            ):
                continue
            validation_id = str(item.get("id", ""))
            if not re.fullmatch(r"VAL-[0-9]{3}", validation_id):
                errors.append(f"validation[{index}].id is invalid")
            if validation_id in ids:
                errors.append(f"duplicate validation id {validation_id}")
            ids.add(validation_id)
            if _unsafe_command(str(item.get("command", ""))):
                errors.append(
                    f"validation {validation_id} contains shell control operators"
                )

    review = manifest.get("review")
    if _require_keys(
        errors,
        review,
        "review",
        ["required", "independence", "model", "reasoning", "rationale"],
    ):
        if review.get("required") and (
            review.get("model") not in MODELS
            or review.get("reasoning") not in REASONING
        ):
            errors.append("required review needs a supported model and reasoning")
        if not review.get("required") and (
            review.get("model") is not None or review.get("reasoning") is not None
        ):
            errors.append("non-required review must use null model and reasoning")
        if (
            execution
            and execution.get("classification") == "critical_review"
            and (
                not review.get("required")
                or review.get("model") != "gpt-5.6-sol"
                or review.get("reasoning") != "high"
                or review.get("independence") != "independent"
            )
        ):
            errors.append("critical_review requires independent Sol/high review")
        if version == "2.0":
            _require_keys(
                errors,
                review,
                "review",
                ["schema_path", "output_path", "handoff_prompt"],
            )
            if len(str(review.get("handoff_prompt", ""))) < 40:
                errors.append("review.handoff_prompt is too short")

    escalation = manifest.get("escalation")
    if _require_keys(
        errors, escalation, "escalation", ["policy_version", "allowed"]
    ) and escalation.get("policy_version") != policy.get("policy_version"):
        errors.append("escalation.policy_version does not match the runtime policy")
    _require_keys(
        errors, manifest.get("completion"), "completion", ["schema_path", "output_path"]
    )
    if version == "2.0":
        baseline = manifest.get("baseline")
        if _require_keys(
            errors,
            baseline,
            "baseline",
            ["required", "path", "snapshot_path", "rationale"],
        ):
            if baseline.get("required") and (
                not baseline.get("path") or not baseline.get("snapshot_path")
            ):
                errors.append(
                    "required structural baseline needs path and snapshot_path"
                )
            if not baseline.get("required") and (
                baseline.get("path") is not None
                or baseline.get("snapshot_path") is not None
            ):
                errors.append(
                    "non-required baseline must use null path and snapshot_path"
                )
        _require_keys(errors, manifest.get("lifecycle"), "lifecycle", ["output_path"])
    if _has_placeholder(json.dumps(manifest, ensure_ascii=False)):
        errors.append("execution manifest contains unresolved placeholder text")
    return errors


def _section_body(markdown: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\s*\r?\n([\s\S]*?)(?=^## |\Z)",
        markdown,
        re.IGNORECASE | re.MULTILINE,
    )
    return match.group(1).strip() if match else ""


def validate_spec_pair(
    markdown: str,
    manifest: dict[str, Any],
    policy: dict[str, Any],
    *,
    project_root: str | Path | None = None,
    skills_root: str | Path | None = None,
    require_ready: bool = False,
) -> list[str]:
    """Validate the human/machine Spec pair and clean-thread READY invariant."""
    errors = [
        *validate_runtime_policy(policy),
        *validate_execution_manifest(manifest, policy),
    ]
    frontmatter = parse_frontmatter(markdown)
    for key in ("id", "title", "status", "contract_version"):
        if not frontmatter.get(key):
            errors.append(f"SPEC.md frontmatter is missing {key}")
    if frontmatter.get("id") and frontmatter["id"] != manifest.get("spec_id"):
        errors.append("Spec ID differs between Markdown and manifest")
    if frontmatter.get("status") and frontmatter["status"] != manifest.get("status"):
        errors.append("Spec status differs between Markdown and manifest")
    if frontmatter.get("contract_version") and int(
        frontmatter["contract_version"]
    ) != manifest.get("contract_version"):
        errors.append("contract_version differs between Markdown and manifest")
    if require_ready and manifest.get("status") != "ready":
        errors.append("--require-ready requires status ready")
    if manifest.get("status") in {"ready", "review"} or require_ready:
        for heading in REQUIRED_SECTIONS:
            body = _section_body(markdown, heading)
            if not body:
                errors.append(f"READY Spec section is empty or missing: {heading}")
            elif _has_placeholder(body):
                errors.append(
                    f"READY Spec section contains placeholder text: {heading}"
                )
        if not re.search(
            r"\bAC-[0-9]{3}\b", _section_body(markdown, "Acceptance criteria")
        ):
            errors.append("READY Spec needs at least one AC-NNN acceptance criterion")
        if _has_placeholder(markdown):
            errors.append("READY Spec contains unresolved placeholder text")
        if project_root:
            root = Path(project_root).resolve()
            for reference in manifest.get("references", []):
                if (
                    reference.get("required")
                    and not (root / reference["path"]).resolve().exists()
                ):
                    errors.append(
                        f"required reference does not exist: {reference['path']}"
                    )
            for skill in manifest.get("skills", []):
                if not skill.get("required"):
                    continue
                resolved = (
                    (root / skill["path"]).resolve()
                    if skill.get("source") == "project"
                    else (
                        Path(skills_root).resolve() / skill["name"] / "SKILL.md"
                        if skills_root
                        else None
                    )
                )
                if resolved is not None and not resolved.exists():
                    errors.append(f"required skill does not exist: {skill['name']}")
            schema_paths = [manifest.get("completion", {}).get("schema_path")]
            if manifest.get("schema_version") == "2.0" and manifest.get(
                "review", {}
            ).get("required"):
                schema_paths.append(manifest.get("review", {}).get("schema_path"))
            for schema_path in filter(None, schema_paths):
                resolved_schema = (root / schema_path).resolve()
                if not resolved_schema.is_file():
                    errors.append(
                        f"declared output schema does not exist: {schema_path}"
                    )
                    continue
                try:
                    schema = json.loads(resolved_schema.read_text(encoding="utf-8-sig"))
                    errors.extend(
                        f"{schema_path}: {item}"
                        for item in validate_structured_output_schema(schema)
                    )
                except (OSError, json.JSONDecodeError) as error:
                    errors.append(
                        f"declared output schema is invalid: {schema_path}: {error}"
                    )
            baseline = manifest.get("baseline", {})
            if manifest.get("schema_version") == "2.0" and baseline.get("required"):
                baseline_path = (root / baseline["path"]).resolve()
                if not baseline_path.is_file():
                    errors.append(
                        f"required structural baseline does not exist: {baseline['path']}"
                    )
                else:
                    try:
                        value = json.loads(
                            baseline_path.read_text(encoding="utf-8-sig")
                        )
                        categories = (
                            "tests",
                            "cli",
                            "json_contracts",
                            "persistence",
                            "schemas",
                            "protected_paths",
                            "decisions",
                        )
                        if value.get("spec_id") != manifest.get("spec_id") or value.get(
                            "contract_version"
                        ) != manifest.get("contract_version"):
                            errors.append(
                                "structural baseline identity/version differs from manifest"
                            )
                        for category in categories:
                            if category not in value:
                                errors.append(
                                    f"structural baseline is missing {category}"
                                )
                    except (OSError, json.JSONDecodeError) as error:
                        errors.append(f"structural baseline is invalid: {error}")
    return errors
