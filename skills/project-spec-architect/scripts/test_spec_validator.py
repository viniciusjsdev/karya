"""Deterministic tests for Project Harness Spec and runtime validation."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from _spec_core import load_json, validate_spec_pair
from _structured_output_schema import validate_structured_output_schema


def _markdown() -> str:
    return """---
id: SPEC-023
title: Add deterministic export
status: ready
contract_version: 2
---

# SPEC-023

## Goal
Produce a deterministic export.
## Context
The clean thread uses only durable inputs.
## Scope
- Export one format.
## Non-scope
- No new storage.
## Requirements
- REQ-001: Stable order.
## Business or domain rules
- BR-001: Preserve source order ties.
## Decisions already made
- JSON is the selected format.
## Constraints
- No network access.
## Acceptance criteria
- AC-001: Fixture output is stable.
## Affected areas
- Export module.
## References
- docs/truth.md.
## Skills
- No specialized skill is required.
## Validation requirements
- VAL-001: Run the test.
## Review requirements
Self-validation is sufficient for this bounded change.
## Execution and runtime
Use SPEC.execution.json.
"""


def _manifest() -> dict:
    return {
        "schema_version": "1.0",
        "spec_id": "SPEC-023",
        "contract_version": 2,
        "status": "ready",
        "automatic_handoff": False,
        "execution": {
            "classification": "normal_implementation",
            "role": "developer",
            "model": "gpt-5.6-terra",
            "reasoning": "medium",
            "routing_rationale": "Architecture and acceptance criteria are already resolved.",
            "runtime_override": None,
            "working_directory": ".",
            "sandbox_mode": "workspace-write",
            "approval_mode": "auto_review",
            "thread": {"mode": "new", "purpose": "implementation", "thread_id": None},
            "handoff_prompt": "Execute SPEC-023 from durable sources and return needs_design for consequential ambiguity.",
        },
        "skills": [],
        "references": [
            {"path": "docs/truth.md", "purpose": "source of truth", "required": True}
        ],
        "validation": [
            {
                "id": "VAL-001",
                "kind": "test",
                "command": "python -m pytest tests/test_export.py -q",
                "required": True,
            }
        ],
        "review": {
            "required": False,
            "independence": "self",
            "model": None,
            "reasoning": None,
            "rationale": "Bounded low-risk change.",
        },
        "escalation": {
            "policy_version": "1.0",
            "allowed": ["terra_high", "needs_design"],
        },
        "completion": {
            "schema_path": ".codex/schemas/project-spec-completion.schema.json",
            "output_path": ".harness/runtime/completions/SPEC-023.json",
        },
    }


def test_valid_ready_pair_and_schema_files(tmp_path: Path) -> None:
    assets = Path(__file__).resolve().parent.parent / "assets"
    policy = load_json(assets / "runtime-policy.json")
    for name in (
        "runtime-policy.schema.json",
        "spec-execution.schema.json",
        "completion.schema.json",
        "review-evidence.schema.json",
    ):
        json.loads((assets / name).read_text(encoding="utf-8"))
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "truth.md").write_text("# Truth\n", encoding="utf-8")
    (tmp_path / ".codex" / "schemas").mkdir(parents=True)
    (
        tmp_path / ".codex" / "schemas" / "project-spec-completion.schema.json"
    ).write_bytes((assets / "completion.schema.json").read_bytes())
    assert (
        validate_spec_pair(
            _markdown(), _manifest(), policy, project_root=tmp_path, require_ready=True
        )
        == []
    )


def test_rejects_chat_dependency_override_drift_policy_drift_and_unsafe_command(
    tmp_path: Path,
) -> None:
    assets = Path(__file__).resolve().parent.parent / "assets"
    policy = load_json(assets / "runtime-policy.json")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "truth.md").write_text("# Truth\n", encoding="utf-8")
    manifest = _manifest()
    errors = validate_spec_pair(
        _markdown().replace(
            "The clean thread uses only durable inputs.", "TBD from the design chat."
        ),
        manifest,
        policy,
        project_root=tmp_path,
        require_ready=True,
    )
    assert any("placeholder" in item for item in errors)
    override = copy.deepcopy(manifest)
    override["execution"]["model"] = "gpt-5.6-sol"
    assert any(
        "runtime_override" in item
        for item in validate_spec_pair(
            _markdown(), override, policy, project_root=tmp_path, require_ready=True
        )
    )
    override["execution"]["runtime_override"] = {
        "default_model": "gpt-5.6-luna",
        "default_reasoning": "low",
        "reason": "The implementation has an exceptional documented constraint.",
    }
    assert any(
        "do not match" in item
        for item in validate_spec_pair(
            _markdown(), override, policy, project_root=tmp_path, require_ready=True
        )
    )
    stale = copy.deepcopy(manifest)
    stale["escalation"]["policy_version"] = "0.9"
    assert any(
        "policy_version" in item
        for item in validate_spec_pair(
            _markdown(), stale, policy, project_root=tmp_path, require_ready=True
        )
    )
    unsafe = copy.deepcopy(manifest)
    unsafe["validation"][0]["command"] = "python -m pytest; Remove-Item docs/truth.md"
    assert any(
        "shell control" in item
        for item in validate_spec_pair(
            _markdown(), unsafe, policy, project_root=tmp_path, require_ready=True
        )
    )


def test_rejects_structured_output_keywords_dynamic_maps_and_incomplete_required() -> (
    None
):
    invalid = {
        "type": "object",
        "additionalProperties": False,
        "required": ["choice", "evidence"],
        "properties": {
            "choice": {"oneOf": [{"type": "string"}, {"type": "null"}]},
            "evidence": {
                "type": "object",
                "additionalProperties": {"type": "string"},
                "properties": {},
                "required": [],
            },
            "status": {"enum": ["ok"]},
            "dynamic": {
                "type": "string",
                "unevaluatedProperties": False,
                "const": 1,
            },
        },
    }
    errors = validate_structured_output_schema(invalid)
    assert any("oneOf" in error for error in errors)
    assert any("additionalProperties must be false" in error for error in errors)
    assert any("enum/const must declare type" in error for error in errors)
    assert any("unsupported schema keyword" in error for error in errors)
    assert any("const is outside its declared type" in error for error in errors)
    assert any("required must contain every property" in error for error in errors)


def test_factory_output_schemas_match_strict_structured_outputs_subset() -> None:
    assets = Path(__file__).resolve().parent.parent / "assets"
    for name in ("completion.schema.json", "review-evidence.schema.json"):
        schema = json.loads((assets / name).read_text(encoding="utf-8"))
        assert validate_structured_output_schema(schema) == []


def test_rejects_structured_output_enum_count_over_platform_limit() -> None:
    schema = {
        "type": "object",
        "additionalProperties": False,
        "required": ["value"],
        "properties": {
            "value": {"type": "string", "enum": [str(i) for i in range(1001)]}
        },
    }

    assert any(
        "1000 total enum values" in error
        for error in validate_structured_output_schema(schema)
    )


def test_rejects_unresolved_non_string_and_external_structured_output_refs() -> None:
    schema = {
        "type": "object",
        "additionalProperties": False,
        "required": ["missing", "typed", "external"],
        "properties": {
            "missing": {"$ref": "#/$defs/absent"},
            "typed": {"$ref": 42},
            "external": {"$ref": "other.json#/value"},
        },
        "$defs": {},
    }

    errors = validate_structured_output_schema(schema)

    assert any("does not resolve" in error for error in errors)
    assert any("must be a string" in error for error in errors)
    assert any("local JSON pointer" in error for error in errors)


def test_rejects_structured_output_ref_to_non_schema_value() -> None:
    schema = {
        "title": "Not a schema target",
        "type": "object",
        "additionalProperties": False,
        "required": ["value"],
        "properties": {"value": {"$ref": "#/title"}},
    }

    assert any(
        "$ref target must be a schema object" in error
        for error in validate_structured_output_schema(schema)
    )
