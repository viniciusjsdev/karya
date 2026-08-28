"""Tests for blocking structural gaps and missing required review evidence."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from audit_project_harness import audit_project_harness


def test_blocks_missing_agents_and_reports_unassessed_chat_knowledge(tmp_path: Path) -> None:
    report = audit_project_harness(tmp_path)
    assert report["status"] == "blocked"
    assert any("AGENTS.md" in item["message"] for item in report["findings"])
    assert any("Chat-only" in item for item in report["unassessed"])


def test_blocks_done_spec_when_required_review_receipt_is_missing(tmp_path: Path) -> None:
    example = Path(__file__).resolve().parents[3] / "examples/project-harness/spec-023-sensor-export/project"
    project = tmp_path / "example"
    shutil.copytree(example, project)
    (project / "specs/active/SPEC-023/evidence/review.json").unlink()
    report = audit_project_harness(project, skills_root=project / ".agents/skills")
    assert report["status"] == "blocked"
    assert any(item["category"] == "review" and item["severity"] == "high" for item in report["findings"])


def test_blocks_incomplete_external_execution_evidence(tmp_path: Path) -> None:
    example = Path(__file__).resolve().parents[3] / "examples/project-harness/spec-023-sensor-export/project"
    project = tmp_path / "example"
    shutil.copytree(example, project)
    route_result = tmp_path / "route-result.json"
    route_result.write_text(json.dumps({
        "executor": "opencode",
        "route": "opencode-completed",
        "request_fingerprint": "abc",
        "spec_id": "SPEC-023",
        "contract_version": 2,
        "scope_integrity": {"ok": True, "errors": []},
        "independent_validations": {"VAL-001": {"result": "passed"}},
        "changed_files": [],
        "artifacts": {},
    }), encoding="utf-8")
    report = audit_project_harness(project, skills_root=project / ".agents/skills", external_route_results=[route_result])
    assert report["status"] == "blocked"
    assert any(item["category"] == "economic_execution" and "artifact is missing" in item["message"] for item in report["findings"])
    assert any(item["category"] == "economic_execution" and "route result" in item["message"] for item in report["findings"])
