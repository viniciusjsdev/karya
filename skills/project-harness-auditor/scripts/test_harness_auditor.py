"""Tests for blocking structural gaps and missing required review evidence."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from audit_project_harness import audit_project_harness
from test_runtime_router_v2 import _fixture, _run


def test_blocks_missing_agents_and_reports_unassessed_chat_knowledge(
    tmp_path: Path,
) -> None:
    report = audit_project_harness(tmp_path)
    assert report["status"] == "blocked"
    assert any("AGENTS.md" in item["message"] for item in report["findings"])
    assert any("Chat-only" in item for item in report["unassessed"])


def test_blocks_done_spec_when_required_review_receipt_is_missing(
    tmp_path: Path,
) -> None:
    example = (
        Path(__file__).resolve().parents[3]
        / "examples/project-harness/spec-023-sensor-export/project"
    )
    project = tmp_path / "example"
    shutil.copytree(example, project)
    (project / "specs/active/SPEC-023/evidence/review.json").unlink()
    report = audit_project_harness(project, skills_root=project / ".agents/skills")
    assert report["status"] == "blocked"
    assert any(
        item["category"] == "review" and item["severity"] == "high"
        for item in report["findings"]
    )


def test_blocks_incomplete_external_execution_evidence(tmp_path: Path) -> None:
    example = (
        Path(__file__).resolve().parents[3]
        / "examples/project-harness/spec-023-sensor-export/project"
    )
    project = tmp_path / "example"
    shutil.copytree(example, project)
    route_result = tmp_path / "route-result.json"
    route_result.write_text(
        json.dumps(
            {
                "executor": "opencode",
                "route": "opencode-completed",
                "request_fingerprint": "abc",
                "spec_id": "SPEC-023",
                "contract_version": 2,
                "scope_integrity": {"ok": True, "errors": []},
                "independent_validations": {"VAL-001": {"result": "passed"}},
                "changed_files": [],
                "artifacts": {},
            }
        ),
        encoding="utf-8",
    )
    report = audit_project_harness(
        project,
        skills_root=project / ".agents/skills",
        external_route_results=[route_result],
    )
    assert report["status"] == "blocked"
    assert any(
        item["category"] == "economic_execution"
        and "artifact is missing" in item["message"]
        for item in report["findings"]
    )
    assert any(
        item["category"] == "economic_execution" and "route result" in item["message"]
        for item in report["findings"]
    )


def test_done_v2_spec_is_auditable_without_runtime_and_preserves_pre_spec_decision(
    tmp_path: Path,
) -> None:
    project, spec_dir, mock = _fixture(tmp_path)
    router = (
        Path(__file__).resolve().parents[2]
        / "codex-runtime-router/scripts/route_codex_runtime.py"
    )
    assert _run(router, project, mock).returncode == 1
    for _ in range(4):
        result = _run(router, project, mock)
        assert result.returncode == 0, result.stdout + result.stderr
    shutil.rmtree(project / ".harness")
    report = audit_project_harness(project, skills_root=project / ".agents/skills")
    assert report["status"] == "approved", report["findings"]
    review = json.loads((spec_dir / "evidence/review.json").read_text())
    assert any("pre-Spec archive decision" in item for item in review["review_input"])


def test_v2_audit_blocks_multiple_review_threads_and_reduced_regression_suite(
    tmp_path: Path,
) -> None:
    project, spec_dir, mock = _fixture(tmp_path)
    router = (
        Path(__file__).resolve().parents[2]
        / "codex-runtime-router/scripts/route_codex_runtime.py"
    )
    _run(router, project, mock)
    for _ in range(4):
        _run(router, project, mock)
    lifecycle_path = spec_dir / "evidence/lifecycle.json"
    lifecycle = json.loads(lifecycle_path.read_text())
    lifecycle["events"].append(
        {
            **lifecycle["events"][-1],
            "sequence": 99,
            "thread_id": "duplicate-review-thread",
        }
    )
    lifecycle_path.write_text(json.dumps(lifecycle), encoding="utf-8")
    (project / "tests/test_value.py").unlink()
    report = audit_project_harness(project, skills_root=project / ".agents/skills")
    assert report["status"] == "blocked"
    assert any(item["category"] == "lifecycle" for item in report["findings"])
    assert any(item["category"] == "baseline" for item in report["findings"])


def test_audit_does_not_treat_nested_example_project_as_root_spec(
    tmp_path: Path,
) -> None:
    example = (
        Path(__file__).resolve().parents[3]
        / "examples/project-harness/spec-023-sensor-export/project"
    )
    (tmp_path / ".codex/references").mkdir(parents=True)
    (tmp_path / "AGENTS.md").write_text("# Root rules\n", encoding="utf-8")
    (tmp_path / ".codex/references/project-harness.md").write_text(
        "# Root harness\n", encoding="utf-8"
    )
    policy = (
        Path(__file__).resolve().parents[2]
        / "project-spec-architect/assets/runtime-policy.json"
    )
    (tmp_path / ".codex/references/runtime-policy.json").write_bytes(
        policy.read_bytes()
    )
    shutil.copytree(example, tmp_path / "examples/nested-project")

    report = audit_project_harness(tmp_path)

    assert report["status"] == "approved"
    assert report["summary"]["specs"] == 0
