"""Regression tests for schema preflight, durable lifecycle, baseline, and two threads."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from _runtime_core import (
    capture_git_snapshot,
    commands_equivalent,
    produced_git_changes,
    validate_completion,
)


def _run(
    script: Path, root: Path, mock: Path, *extra: str
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(script),
            "--project-root",
            str(root),
            "--spec",
            "specs/active/SPEC-101/SPEC.md",
            "--manifest",
            "specs/active/SPEC-101/SPEC.execution.json",
            "--sdk-module",
            str(mock),
            *extra,
        ],
        text=True,
        capture_output=True,
        check=False,
    )


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=True)


def _fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    root = tmp_path / "project"
    spec_dir = root / "specs/active/SPEC-101"
    for path in (
        spec_dir / "evidence",
        root / ".codex/schemas",
        root / ".codex/references",
        root / "src",
        root / "tests",
        root / "docs/decisions",
    ):
        path.mkdir(parents=True, exist_ok=True)
    assets = Path(__file__).resolve().parents[2] / "project-spec-architect/assets"
    (root / ".codex/schemas/project-spec-completion.schema.json").write_bytes(
        (assets / "completion.schema.json").read_bytes()
    )
    (root / ".codex/schemas/project-spec-review.schema.json").write_bytes(
        (assets / "review-evidence.schema.json").read_bytes()
    )
    (root / ".codex/references/runtime-policy.json").write_bytes(
        (assets / "runtime-policy.json").read_bytes()
    )
    (root / ".codex/references/project-harness.md").write_text(
        "# Harness\n", encoding="utf-8"
    )
    (root / ".gitignore").write_text(
        ".harness/runtime/\n**/__pycache__/\n*.pyc\n", encoding="utf-8"
    )
    (root / "AGENTS.md").write_text("# Project rules\n", encoding="utf-8")
    (root / "src/value.py").write_text("VALUE = 1\n", encoding="utf-8")
    (root / "tests/test_value.py").write_text(
        "def test_value():\n    assert True\n", encoding="utf-8"
    )
    (root / "docs/decisions/archive.json").write_text(
        json.dumps({"decision": "archive legacy procedure", "status": "archived"}),
        encoding="utf-8",
    )
    markdown = """---
id: SPEC-101
title: Structural lifecycle regression
status: ready
contract_version: 2
---

# SPEC-101

## Goal
Preserve behavior through a structural change.
## Context
The incident requires durable offline regression evidence.
## Scope
- Modify the value module.
## Non-scope
- No external calls.
## Requirements
- REQ-001: Preserve the public value.
## Business or domain rules
- BR-001: Archived decisions predate this Spec.
## Decisions already made
- The legacy procedure was archived before the Spec.
## Constraints
- Work offline.
## Acceptance criteria
- AC-001: The value test passes.
## Affected areas
- src and tests.
## References
- AGENTS.md.
## Skills
- No specialist skill.
## Validation requirements
- VAL-001: Run an offline command.
## Review requirements
Independent Sol/high review is required.
## Execution and runtime
Use the resolved v2 manifest.
"""
    (spec_dir / "SPEC.md").write_text(markdown, encoding="utf-8")
    validation_command = f'"{sys.executable}" -c "print(123)"'
    manifest = {
        "schema_version": "2.0",
        "spec_id": "SPEC-101",
        "contract_version": 2,
        "status": "ready",
        "automatic_handoff": False,
        "execution": {
            "classification": "normal_implementation",
            "role": "developer",
            "model": "gpt-5.6-terra",
            "reasoning": "medium",
            "routing_rationale": "The architecture and acceptance criteria are fully resolved.",
            "runtime_override": None,
            "working_directory": ".",
            "sandbox_mode": "workspace-write",
            "approval_mode": "auto_review",
            "thread": {"mode": "new", "purpose": "implementation", "thread_id": None},
            "handoff_prompt": "Implement the structural fixture and preserve every declared baseline contract.",
        },
        "skills": [],
        "references": [
            {"path": "AGENTS.md", "purpose": "project rules", "required": True}
        ],
        "validation": [
            {
                "id": "VAL-001",
                "kind": "test",
                "command": validation_command,
                "required": True,
            }
        ],
        "review": {
            "required": True,
            "independence": "independent",
            "model": "gpt-5.6-sol",
            "reasoning": "high",
            "rationale": "Structural migration requires independent review.",
            "schema_path": ".codex/schemas/project-spec-review.schema.json",
            "output_path": "specs/active/SPEC-101/evidence/review.json",
            "handoff_prompt": "Review the structural baseline, current diff, validations, and completion evidence independently.",
        },
        "escalation": {
            "policy_version": "1.0",
            "allowed": ["terra_high", "needs_design", "sol_high"],
        },
        "completion": {
            "schema_path": ".codex/schemas/project-spec-completion.schema.json",
            "output_path": "specs/active/SPEC-101/evidence/completion.json",
        },
        "baseline": {
            "required": True,
            "path": "specs/active/SPEC-101/baseline.json",
            "snapshot_path": "specs/active/SPEC-101/evidence/git-baseline.json",
            "rationale": "This is a structural migration.",
        },
        "lifecycle": {"output_path": "specs/active/SPEC-101/evidence/lifecycle.json"},
    }
    (spec_dir / "SPEC.execution.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    baseline = {
        "schema_version": "1.0",
        "spec_id": "SPEC-101",
        "contract_version": 2,
        "captured_at": "2026-08-28T00:00:00Z",
        "tests": {
            "count": 1,
            "paths": ["tests/test_value.py"],
            "commands": [validation_command],
            "notes": [],
        },
        "cli": [],
        "json_contracts": [],
        "persistence": [],
        "schemas": [],
        "protected_paths": [{"path": "tests", "kind": "directory"}],
        "decisions": [
            {
                "path": "docs/decisions/archive.json",
                "status": "archived",
                "effective_before_spec": True,
            }
        ],
    }
    (spec_dir / "baseline.json").write_text(json.dumps(baseline), encoding="utf-8")
    mock = root / "mock_sdk.py"
    mock.write_text(
        """from enum import Enum
from pathlib import Path
from types import SimpleNamespace
import json

class Sandbox(Enum):
    read_only = "read-only"
    workspace_write = "workspace-write"
    full_access = "full-access"
class ApprovalMode(Enum):
    deny_all = "deny_all"
    auto_review = "auto_review"

class MockThread:
    def __init__(self, thread_id, cwd, model): self.id, self.cwd, self.model = thread_id, Path(cwd), model
    def run(self, prompt, *, output_schema):
        if (self.cwd / "force-non-json").exists(): return SimpleNamespace(final_response="not-json", usage=None)
        counter_path = self.cwd / ".harness/runtime/mock-count.json"
        counter_path.parent.mkdir(parents=True, exist_ok=True)
        counts = json.loads(counter_path.read_text()) if counter_path.exists() else {"terra": 0, "sol": 0}
        key = "sol" if "sol" in self.model else "terra"
        counts[key] += 1
        counter_path.write_text(json.dumps(counts))
        usage = {"input_tokens": 1, "cached_input_tokens": 0, "cache_write_input_tokens": 0, "output_tokens": 1, "reasoning_output_tokens": 0}
        if key == "terra":
            (self.cwd / "src/value.py").write_text(f"VALUE = {counts[key] + 1}\\n")
            if counts[key] == 1:
                value = {"spec_id": "SPEC-101", "contract_version": 2, "status": "completed", "thread_id": None, "runtime": {"classification": "normal_implementation", "model": "gpt-5.6-terra", "reasoning": "medium"}, "changed_files": [{"path": "src/value.py", "change": "modified"}], "artifacts": [], "acceptance_evidence": [], "validation_evidence": [], "deviations": [], "unresolved_items": [], "needs_design": None, "usage": None}
            else:
                value = {"spec_id": "SPEC-101", "contract_version": 2, "status": "completed", "thread_id": None, "runtime": {"classification": "normal_implementation", "model": "gpt-5.6-terra", "reasoning": "medium"}, "changed_files": [{"path": "src/value.py", "change": "modified"}], "artifacts": [], "acceptance_evidence": [{"id": "AC-001", "result": "passed", "evidence": ["fixture"], "notes": []}], "validation_evidence": [{"validation_id": "VAL-001", "canonical_command": None, "verification": "reported", "result": "passed", "exit_code": 0, "evidence": ["reported"], "notes": []}], "deviations": [], "unresolved_items": [], "needs_design": None, "usage": None}
        else:
            assessment = [{"category": name, "result": "preserved", "evidence": ["baseline checked"], "notes": []} for name in ("tests", "cli", "json_contracts", "persistence", "schemas", "protected_paths", "decisions")]
            value = {"spec_id": "SPEC-101", "contract_version": 2, "status": "changes_requested" if counts[key] == 1 else "approved", "thread_id": None, "runtime": {"classification": "critical_review", "model": "gpt-5.6-sol", "reasoning": "high"}, "review_input": ["SPEC.md", "git diff", "completion evidence", "structural baseline including pre-Spec archive decision"], "baseline_assessment": assessment, "findings": ["correction required"] if counts[key] == 1 else [], "evidence": ["independent review"], "usage": None}
        return SimpleNamespace(final_response=json.dumps(value), usage=usage)

class Codex:
    def __enter__(self): return self
    def __exit__(self, *_args): return None
    def thread_start(self, **options): return MockThread("thread-review" if "sol" in options["model"] else "thread-implementation", options["cwd"], options["model"])
    def thread_resume(self, thread_id, **options):
        expected = "thread-review" if "sol" in options["model"] else "thread-implementation"
        assert thread_id == expected
        return MockThread(thread_id, options["cwd"], options["model"])
""",
        encoding="utf-8",
    )
    _git(root, "init")
    _git(root, "config", "user.email", "tests@example.invalid")
    _git(root, "config", "user.name", "Harness Tests")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "fixture")
    return root, spec_dir, mock


def test_doctor_rejects_incompatible_schema_without_sdk_call(tmp_path: Path) -> None:
    invalid = tmp_path / "invalid.json"
    invalid.write_text(
        json.dumps(
            {
                "type": "object",
                "properties": {
                    "value": {"oneOf": [{"type": "string"}, {"type": "null"}]}
                },
                "required": ["value"],
                "additionalProperties": False,
            }
        ),
        encoding="utf-8",
    )
    doctor = Path(__file__).resolve().parent / "codex_runtime_doctor.py"
    result = subprocess.run(
        [sys.executable, str(doctor), "--schema", str(invalid), "--schema-only"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    assert "oneOf" in result.stdout


def test_router_dry_run_rejects_incompatible_schema_before_sdk_call(
    tmp_path: Path,
) -> None:
    root, _, mock = _fixture(tmp_path)
    schema_path = root / ".codex/schemas/project-spec-completion.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema["properties"]["status"] = {"oneOf": [{"type": "string"}, {"type": "null"}]}
    schema_path.write_text(json.dumps(schema), encoding="utf-8")
    router = Path(__file__).resolve().parent / "route_codex_runtime.py"

    result = _run(router, root, mock, "--dry-run")

    assert result.returncode == 1
    assert "oneOf" in result.stdout
    assert not (root / ".harness/runtime/mock-count.json").exists()


def test_router_preserves_thread_durably_after_unparseable_output(
    tmp_path: Path,
) -> None:
    root, spec_dir, mock = _fixture(tmp_path)
    (root / "force-non-json").write_text("1\n", encoding="utf-8")
    router = Path(__file__).resolve().parent / "route_codex_runtime.py"

    failed = _run(router, root, mock)

    assert failed.returncode == 1
    lifecycle = json.loads((spec_dir / "evidence/lifecycle.json").read_text())
    assert lifecycle["implementation_thread_id"] == "thread-implementation"
    assert lifecycle["events"][-1]["outcome"] == "failed"
    (root / ".harness/runtime/spec-threads.json").unlink()
    (root / "force-non-json").unlink()
    preview = _run(router, root, mock, "--dry-run")
    assert json.loads(preview.stdout)["action"] == "resume"


def test_canonical_command_comparison_allows_only_harmless_textual_differences() -> (
    None
):
    assert commands_equivalent(
        "python   -m pytest tests/test_value.py -q",
        "python -m pytest tests/test_value.py -q",
    )
    assert not commands_equivalent(
        "python -m pytest tests/test_value.py -q",
        "python -m pytest tests/test_other.py -q",
    )


def test_v2_reuses_two_threads_and_preserves_attempts_through_review_cycle(
    tmp_path: Path,
) -> None:
    root, spec_dir, mock = _fixture(tmp_path)
    router = Path(__file__).resolve().parent / "route_codex_runtime.py"
    preview = _run(router, root, mock, "--dry-run")
    assert preview.returncode == 0 and json.loads(preview.stdout)["action"] == "start"
    invalid = _run(router, root, mock)
    assert (
        invalid.returncode == 1
        and json.loads(invalid.stdout)["thread_id"] == "thread-implementation"
    )
    assert (
        json.loads((spec_dir / "SPEC.execution.json").read_text())["status"] == "ready"
    )
    (root / ".harness/runtime/spec-threads.json").unlink()
    implemented = _run(router, root, mock)
    assert (
        implemented.returncode == 0
        and json.loads(implemented.stdout)["action"] == "resume"
    )
    assert (
        json.loads((spec_dir / "SPEC.execution.json").read_text())["status"]
        == "implemented"
    )
    requested = _run(router, root, mock)
    assert json.loads(requested.stdout)["route"] == "changes_requested"
    corrected = _run(router, root, mock)
    assert json.loads(corrected.stdout)["route"] == "implemented"
    approved = _run(router, root, mock)
    assert json.loads(approved.stdout)["route"] == "done"
    manifest = json.loads((spec_dir / "SPEC.execution.json").read_text())
    assert manifest["execution"]["model"] == "gpt-5.6-terra"
    assert manifest["execution"]["thread"] == {
        "mode": "new",
        "purpose": "implementation",
        "thread_id": None,
    }
    lifecycle = json.loads((spec_dir / "evidence/lifecycle.json").read_text())
    assert lifecycle["implementation_thread_id"] == "thread-implementation"
    assert lifecycle["review_thread_id"] == "thread-review"
    assert lifecycle["status"] == "done"
    outcomes = [event["outcome"] for event in lifecycle["events"]]
    assert "implementation" in outcomes
    assert "implemented" in outcomes
    assert "review" in outcomes
    assert "approved" in outcomes
    assert outcomes[-1] == "done"
    assert (
        len(list((spec_dir / "evidence/attempts").glob("implementation-*.json"))) == 2
    )
    assert len(list((spec_dir / "evidence/attempts").glob("review-*.json"))) == 2
    completion = json.loads((spec_dir / "evidence/completion.json").read_text())
    assert completion["validation_evidence"][0]["verification"] == "router"
    assert completion["validation_evidence"][0]["canonical_command"]


def test_changed_file_evidence_reconciles_added_modified_and_deleted(
    tmp_path: Path,
) -> None:
    root = tmp_path / "git-project"
    root.mkdir()
    (root / "modified.py").write_text("before\n", encoding="utf-8")
    (root / "deleted.py").write_text("before\n", encoding="utf-8")
    _git(root, "init")
    _git(root, "config", "user.email", "tests@example.invalid")
    _git(root, "config", "user.name", "Harness Tests")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "baseline")
    (root / "dirty.py").write_text("user state before route\n", encoding="utf-8")
    (root / "untouched.py").write_text("preserve me\n", encoding="utf-8")
    snapshot = capture_git_snapshot(root, "SPEC-102", 1)
    (root / "modified.py").write_text("after\n", encoding="utf-8")
    (root / "deleted.py").unlink()
    (root / "added.py").write_text("after\n", encoding="utf-8")
    (root / "dirty.py").write_text("implementation changed me\n", encoding="utf-8")
    manifest = {
        "schema_version": "2.0",
        "spec_id": "SPEC-102",
        "contract_version": 1,
        "execution": {
            "classification": "normal_implementation",
            "model": "gpt-5.6-terra",
            "reasoning": "medium",
        },
        "validation": [],
        "completion": {},
        "review": {},
        "baseline": {},
        "lifecycle": {},
    }
    completion = {
        "spec_id": "SPEC-102",
        "contract_version": 1,
        "status": "completed",
        "thread_id": "thread",
        "runtime": {
            "classification": "normal_implementation",
            "model": "gpt-5.6-terra",
            "reasoning": "medium",
        },
        "changed_files": [
            {"path": "added.py", "change": "added"},
            {"path": "dirty.py", "change": "modified"},
            {"path": "modified.py", "change": "modified"},
            {"path": "deleted.py", "change": "deleted"},
        ],
        "artifacts": [],
        "acceptance_evidence": [
            {"id": "AC-001", "result": "passed", "evidence": ["fixture"], "notes": []}
        ],
        "validation_evidence": [],
        "deviations": [],
        "unresolved_items": [],
        "needs_design": None,
        "usage": None,
    }
    assert (
        validate_completion(
            completion,
            manifest,
            "## Acceptance criteria\n- AC-001: Files reconcile.",
            "thread",
            project_root=root,
            baseline_snapshot=snapshot,
        )
        == []
    )

    _git(root, "add", ".")
    _git(root, "commit", "-m", "implementation")
    assert (
        validate_completion(
            completion,
            manifest,
            "## Acceptance criteria\n- AC-001: Files reconcile.",
            "thread",
            project_root=root,
            baseline_snapshot=snapshot,
        )
        == []
    )

    duplicated = dict(completion)
    duplicated["acceptance_evidence"] = completion["acceptance_evidence"] * 2
    errors = validate_completion(
        duplicated,
        manifest,
        "## Acceptance criteria\n- AC-001: Files reconcile.",
        "thread",
        project_root=root,
        baseline_snapshot=snapshot,
    )
    assert any("duplicate AC-001" in error for error in errors)


def test_git_reconciliation_treats_dirty_to_clean_as_modified(tmp_path: Path) -> None:
    root = tmp_path / "dirty-project"
    root.mkdir()
    tracked = root / "tracked.py"
    tracked.write_text("clean\n", encoding="utf-8")
    _git(root, "init")
    _git(root, "config", "user.email", "tests@example.invalid")
    _git(root, "config", "user.name", "Harness Tests")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "baseline")
    tracked.write_text("user dirt\n", encoding="utf-8")
    snapshot = capture_git_snapshot(root, "SPEC-103", 1)

    tracked.write_text("clean\n", encoding="utf-8")

    assert produced_git_changes(root, snapshot) == {"tracked.py": "modified"}


def test_git_reconciliation_ignores_preexisting_deletion_and_rename(
    tmp_path: Path,
) -> None:
    root = tmp_path / "preexisting-dirt"
    root.mkdir()
    (root / "deleted.py").write_text("tracked\n", encoding="utf-8")
    (root / "old_name.py").write_text("tracked\n", encoding="utf-8")
    _git(root, "init")
    _git(root, "config", "user.email", "tests@example.invalid")
    _git(root, "config", "user.name", "Harness Tests")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "baseline")
    (root / "deleted.py").unlink()
    _git(root, "mv", "old_name.py", "new_name.py")
    snapshot = capture_git_snapshot(root, "SPEC-104", 1)

    assert produced_git_changes(root, snapshot) == {}


def test_router_rejects_malformed_structural_baseline_before_sdk_call(
    tmp_path: Path,
) -> None:
    root, spec_dir, mock = _fixture(tmp_path)
    baseline_path = spec_dir / "baseline.json"
    baseline = json.loads(baseline_path.read_text())
    baseline["tests"]["count"] = 2
    baseline_path.write_text(json.dumps(baseline), encoding="utf-8")
    router = Path(__file__).resolve().parent / "route_codex_runtime.py"

    result = _run(router, root, mock, "--dry-run")

    assert result.returncode == 1
    assert "tests.count must equal" in result.stdout
    assert not (root / ".harness/runtime/mock-count.json").exists()
