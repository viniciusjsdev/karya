"""Tests for blocking structural gaps and missing required review evidence."""

from __future__ import annotations

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
