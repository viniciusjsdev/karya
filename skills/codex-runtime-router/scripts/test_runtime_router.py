"""Mock-tested Python SDK routing for start, resume, failure recovery, and review."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

SPEC_MARKDOWN = """---
id: SPEC-023
title: Deterministic export
status: ready
contract_version: 1
---

# SPEC-023

## Goal
Produce a stable export.
## Context
Durable context is in the repository.
## Scope
- Export records.
## Non-scope
- No new storage.
## Requirements
- REQ-001: Stable order.
## Business or domain rules
- BR-001: Preserve ties.
## Decisions already made
- Use JSON.
## Constraints
- Work offline.
## Acceptance criteria
- AC-001: Export fixture passes.
## Affected areas
- Export module.
## References
- docs/truth.md.
## Skills
- No specialized skill.
## Validation requirements
- VAL-001: Run tests.
## Review requirements
Self-validation is sufficient.
## Execution and runtime
Use SPEC.execution.json.
"""


def _manifest() -> dict:
    return {
        "schema_version": "1.0",
        "spec_id": "SPEC-023",
        "contract_version": 1,
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
            "handoff_prompt": "Execute the bounded export change and return needs_design for consequential ambiguity.",
        },
        "skills": [],
        "references": [
            {
                "path": "docs/truth.md",
                "purpose": "durable domain truth",
                "required": True,
            }
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


def _legacy_schema(schema: dict, *, review: bool = False) -> dict:
    """Recreate the incompatible v1 schema shape that existing projects retain."""
    value = copy.deepcopy(schema)
    value["properties"]["status"].pop("type", None)
    usage = value["properties"]["usage"]
    usage["oneOf"] = usage.pop("anyOf")
    if review:
        value["properties"]["runtime"]["properties"]["classification"].pop("type", None)
        return value
    needs_design = value["properties"]["needs_design"]
    needs_design["oneOf"] = needs_design.pop("anyOf")
    value["properties"]["changed_files"] = {
        "type": "array",
        "items": {"type": "string"},
    }
    acceptance_item = copy.deepcopy(value["properties"]["acceptance_evidence"]["items"])
    acceptance_item["properties"].pop("id")
    acceptance_item["required"].remove("id")
    acceptance_item["properties"]["result"].pop("type", None)
    value["properties"]["acceptance_evidence"] = {
        "type": "object",
        "additionalProperties": acceptance_item,
    }
    validation_item = copy.deepcopy(value["properties"]["validation_evidence"]["items"])
    validation_item["properties"].pop("validation_id")
    validation_item["properties"].pop("verification")
    validation_item["properties"]["command"] = {"type": "string"}
    validation_item["properties"].pop("canonical_command")
    validation_item["properties"]["result"].pop("type", None)
    validation_item["required"] = [
        "command",
        "result",
        "exit_code",
        "evidence",
        "notes",
    ]
    value["properties"]["validation_evidence"] = {
        "type": "object",
        "additionalProperties": validation_item,
    }
    return value


def _run(
    router: Path, root: Path, spec: str, manifest: str, mock: Path, *extra: str
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(router),
            "--project-root",
            str(root),
            "--spec",
            spec,
            "--manifest",
            manifest,
            "--sdk-module",
            str(mock),
            *extra,
        ],
        text=True,
        capture_output=True,
        check=False,
    )


def test_router_start_resume_failure_recovery_and_review(tmp_path: Path) -> None:
    script_dir = Path(__file__).resolve().parent
    assets = script_dir.parents[1] / "project-spec-architect" / "assets"
    root = tmp_path
    spec_dir = root / "specs" / "active" / "SPEC-023"
    spec_dir.mkdir(parents=True)
    (root / "docs").mkdir()
    (root / "src").mkdir()
    (root / ".codex" / "schemas").mkdir(parents=True)
    (root / ".codex" / "references").mkdir(parents=True)
    (root / "AGENTS.md").write_text("# Project rules\n", encoding="utf-8")
    (root / "docs" / "truth.md").write_text("# Durable truth\n", encoding="utf-8")
    (root / "src" / "export.py").write_text("VALUE = 1\n", encoding="utf-8")
    completion_schema = json.loads(
        (assets / "completion.schema.json").read_text(encoding="utf-8")
    )
    review_schema = json.loads(
        (assets / "review-evidence.schema.json").read_text(encoding="utf-8")
    )
    (root / ".codex/schemas/project-spec-completion.schema.json").write_text(
        json.dumps(_legacy_schema(completion_schema)), encoding="utf-8"
    )
    (root / ".codex/schemas/project-spec-review.schema.json").write_text(
        json.dumps(_legacy_schema(review_schema, review=True)), encoding="utf-8"
    )
    (root / ".codex" / "references" / "runtime-policy.json").write_bytes(
        (assets / "runtime-policy.json").read_bytes()
    )
    spec_path = spec_dir / "SPEC.md"
    manifest_path = spec_dir / "SPEC.execution.json"
    spec_path.write_text(SPEC_MARKDOWN, encoding="utf-8")
    manifest = _manifest()
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    mock_path = root / "mock_sdk.py"
    mock_path.write_text(
        """from enum import Enum
from types import SimpleNamespace

class Sandbox(Enum):
    read_only = "read-only"
    workspace_write = "workspace-write"
    full_access = "full-access"

class ApprovalMode(Enum):
    deny_all = "deny_all"
    auto_review = "auto_review"

class MockThread:
    def __init__(self, thread_id): self.id = thread_id
    def run(self, prompt, *, output_schema):
        if "SPEC-024" in prompt: return SimpleNamespace(final_response="not-json", usage=None)
        usage = {"input_tokens": 10, "cached_input_tokens": 2, "cache_write_input_tokens": 0, "output_tokens": 5, "reasoning_output_tokens": 1}
        if "SPEC-025" in prompt:
            value = {"spec_id": "SPEC-025", "contract_version": 1, "status": "approved", "thread_id": None, "runtime": {"classification": "critical_review", "model": "gpt-5.6-sol", "reasoning": "high"}, "review_input": ["SPEC.md", "git diff and artifacts", "completion evidence"], "findings": [], "evidence": ["independent review passed"], "usage": None}
        else:
            value = {"spec_id": "SPEC-023", "contract_version": 1, "status": "completed", "thread_id": None, "runtime": {"classification": "normal_implementation", "model": "gpt-5.6-terra", "reasoning": "medium"}, "changed_files": ["src/export.py"], "artifacts": [], "acceptance_evidence": {"AC-001": {"result": "passed", "evidence": ["fixture checksum"], "notes": []}}, "validation_evidence": {"VAL-001": {"command": "python -m pytest tests/test_export.py -q", "result": "passed", "exit_code": 0, "evidence": ["1 test passed"], "notes": []}}, "deviations": [], "unresolved_items": [], "needs_design": None, "usage": None}
        return SimpleNamespace(final_response=__import__("json").dumps(value), usage=usage)

class Codex:
    def __enter__(self): return self
    def __exit__(self, *_args): return None
    def thread_start(self, **options):
        assert options["config"]["model_reasoning_effort"] in {"medium", "high"}
        if options["model"] == "gpt-5.6-sol": return MockThread("thread-review-025")
        if options["model"] == "gpt-5.6-terra": return MockThread("thread-start-023")
        raise AssertionError("wrong runtime")
    def thread_resume(self, thread_id, **options):
        assert thread_id == "thread-start-023" and options["model"] == "gpt-5.6-terra"
        return MockThread(thread_id)
""",
        encoding="utf-8",
    )
    router = script_dir / "route_codex_runtime.py"
    common = (
        "specs/active/SPEC-023/SPEC.md",
        "specs/active/SPEC-023/SPEC.execution.json",
    )
    preview = _run(router, root, *common, mock_path, "--dry-run")
    assert preview.returncode == 0, preview.stdout + preview.stderr
    assert json.loads(preview.stdout)["action"] == "start"
    started = _run(router, root, *common, mock_path)
    assert started.returncode == 0, started.stdout + started.stderr
    assert json.loads(started.stdout)["thread_id"] == "thread-start-023"
    completion = json.loads(
        (root / ".harness/runtime/completions/SPEC-023.json").read_text(
            encoding="utf-8"
        )
    )
    assert completion["usage"]["input_tokens"] == 10
    duplicate = _run(router, root, *common, mock_path, "--dry-run")
    assert duplicate.returncode == 1
    assert any(
        "already recorded" in item for item in json.loads(duplicate.stdout)["errors"]
    )
    manifest["execution"]["thread"] = {
        "mode": "resume",
        "purpose": "implementation",
        "thread_id": "thread-start-023",
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    resumed = _run(router, root, *common, mock_path)
    assert resumed.returncode == 0 and json.loads(resumed.stdout)["action"] == "resume"

    bad_dir = root / "specs" / "active" / "SPEC-024"
    bad_dir.mkdir()
    (bad_dir / "SPEC.md").write_text(
        SPEC_MARKDOWN.replace("SPEC-023", "SPEC-024"), encoding="utf-8"
    )
    bad_manifest = copy.deepcopy(manifest)
    bad_manifest["spec_id"] = "SPEC-024"
    bad_manifest["execution"]["thread"] = {
        "mode": "new",
        "purpose": "implementation",
        "thread_id": None,
    }
    bad_manifest["completion"]["output_path"] = (
        ".harness/runtime/completions/SPEC-024.json"
    )
    (bad_dir / "SPEC.execution.json").write_text(
        json.dumps(bad_manifest), encoding="utf-8"
    )
    invalid = _run(
        router,
        root,
        "specs/active/SPEC-024/SPEC.md",
        "specs/active/SPEC-024/SPEC.execution.json",
        mock_path,
    )
    assert (
        invalid.returncode == 1
        and json.loads(invalid.stdout)["thread_id"] == "thread-start-023"
    )
    failed_state = json.loads(
        (root / ".harness/runtime/spec-threads.json").read_text(encoding="utf-8")
    )
    assert failed_state["specs"]["SPEC-024"]["last_status"] == "failed"

    review_dir = root / "specs" / "active" / "SPEC-025"
    review_dir.mkdir()
    (review_dir / "SPEC.md").write_text(
        SPEC_MARKDOWN.replace("SPEC-023", "SPEC-025").replace(
            "status: ready", "status: review"
        ),
        encoding="utf-8",
    )
    review_manifest = copy.deepcopy(manifest)
    review_manifest.update({"spec_id": "SPEC-025", "status": "review"})
    review_manifest["execution"] = {
        "classification": "critical_review",
        "role": "reviewer",
        "model": "gpt-5.6-sol",
        "reasoning": "high",
        "routing_rationale": "The public contract requires an independent critical review.",
        "runtime_override": None,
        "working_directory": ".",
        "sandbox_mode": "read-only",
        "approval_mode": "deny_all",
        "thread": {"mode": "new", "purpose": "review", "thread_id": None},
        "handoff_prompt": "Review SPEC-025 independently using its contract, diff and artifacts, tests, and completion evidence.",
    }
    review_manifest["review"] = {
        "required": True,
        "independence": "independent",
        "model": "gpt-5.6-sol",
        "reasoning": "high",
        "rationale": "Public contract review is required.",
    }
    review_manifest["escalation"]["allowed"] = ["sol_xhigh"]
    review_manifest["completion"] = {
        "schema_path": ".codex/schemas/project-spec-review.schema.json",
        "output_path": ".harness/runtime/reviews/SPEC-025.json",
    }
    (review_dir / "SPEC.execution.json").write_text(
        json.dumps(review_manifest), encoding="utf-8"
    )
    review = _run(
        router,
        root,
        "specs/active/SPEC-025/SPEC.md",
        "specs/active/SPEC-025/SPEC.execution.json",
        mock_path,
    )
    assert review.returncode == 0, review.stdout + review.stderr
    assert json.loads(review.stdout)["route"] == "approved"
    review_state = json.loads(
        (root / ".harness/runtime/spec-threads.json").read_text(encoding="utf-8")
    )
    assert review_state["specs"]["SPEC-025"]["review_thread_id"] == "thread-review-025"
