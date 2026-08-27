"""Tests for accepted-plan validation and preserving Harness bootstrap."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from _harness_plan_core import validate_harness_plan


def _plan() -> dict:
    return {
        "schema_version": "1.0", "status": "accepted", "project": {"name": "sample", "domain": "laboratory", "project_type": "research", "objective": "Keep a reproducible experiment record."},
        "sources_of_truth": [{"path": "notebooks", "kind": "methodology", "authority": "primary", "action": "preserve"}],
        "documentation": {"preserve": ["notebooks"], "create": [], "path_mappings": []}, "decisions": {"durable_path": ".codex/decisions", "open": []}, "workflows": [], "local_skill_candidates": [],
        "spec_strategy": {"root": "specs", "active_pattern": "specs/active/SPEC-NNN", "markdown_name": "SPEC.md", "execution_name": "SPEC.execution.json"}, "validation": [],
        "runtime_policy": {"policy_version": "1.0", "project_path": ".codex/references/runtime-policy.json"},
        "thread_policy": {"design": "new_or_existing_design_thread", "implementation": "new_clean_thread", "needs_design": "resume_implementation_after_design_resolution", "parallel_writes": "sequential_by_default", "subagents": "not_default"}, "automatic_handoff": False,
    }


def test_bootstrap_preserves_existing_files_and_is_idempotent(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    (project / "AGENTS.md").write_text("# Existing\n", encoding="utf-8")
    plan = _plan()
    assert validate_harness_plan(plan, require_accepted=True) == []
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    script = Path(__file__).with_name("bootstrap_project_harness.py")
    command = [sys.executable, str(script), "--project-root", str(project), "--plan", str(plan_path)]
    run = subprocess.run(command, text=True, capture_output=True, check=False)
    assert run.returncode == 0, run.stdout + run.stderr
    assert (project / "AGENTS.md").read_text(encoding="utf-8") == "# Existing\n"
    for path in (
        ".codex/references/runtime-policy.json", ".codex/schemas/project-spec-execution.schema.json",
        ".codex/schemas/project-spec-completion.schema.json", ".codex/schemas/project-spec-review.schema.json",
        ".codex/decisions/project-harness-bootstrap.json",
    ):
        assert (project / path).exists()
    execution_template = json.loads((project / ".codex/templates/project-spec.execution.json").read_text(encoding="utf-8"))
    assert (project / "specs/active/SPEC-001" / execution_template["$schema"]).resolve() == (project / ".codex/schemas/project-spec-execution.schema.json").resolve()
    rerun = subprocess.run(command, text=True, capture_output=True, check=False)
    assert rerun.returncode == 0
    assert "AGENTS.md" in json.loads(rerun.stdout)["preserved"]
