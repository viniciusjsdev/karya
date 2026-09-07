"""Tests for accepted-plan validation and preserving Harness bootstrap."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from _harness_plan_core import validate_harness_plan
from bootstrap_project_harness import render_project_harness_navigation
from _project_map import MAP_PATH


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
        MAP_PATH, "scripts/harness/project_map.py",
    ):
        assert (project / path).exists()
    execution_template = json.loads((project / ".codex/templates/project-spec.execution.json").read_text(encoding="utf-8"))
    assert (project / "specs/active/SPEC-001" / execution_template["$schema"]).resolve() == (project / ".codex/schemas/project-spec-execution.schema.json").resolve()
    first_files = {path.relative_to(project): path.read_bytes() for path in project.rglob("*") if path.is_file()}
    rerun = subprocess.run(command, text=True, capture_output=True, check=False)
    assert rerun.returncode == 0
    assert "AGENTS.md" in json.loads(rerun.stdout)["preserved"]
    assert MAP_PATH in json.loads(rerun.stdout)["preserved"]
    assert json.loads(rerun.stdout)["created"] == []
    assert {path.relative_to(project): path.read_bytes() for path in project.rglob("*") if path.is_file()} == first_files


def _run_bootstrap(tmp_path: Path, plan: dict, *, dry_run: bool = False) -> tuple[Path, subprocess.CompletedProcess]:
    """Run the real CLI against a test-owned project and accepted-plan file."""
    project = tmp_path / "project"
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    command = [sys.executable, str(Path(__file__).with_name("bootstrap_project_harness.py")), "--project-root", str(project), "--plan", str(plan_path)]
    if dry_run:
        command.append("--dry-run")
    return project, subprocess.run(command, text=True, encoding="utf-8", capture_output=True, check=False)


def _navigation_plan() -> dict:
    """Provide non-default paths and declared future work to test plan fidelity."""
    plan = _plan()
    plan["sources_of_truth"] = [
        {"path": "documentation/requisitos.md", "kind": "product", "authority": "primary", "action": "preserve"},
        {"path": "documentation/operacao.md", "kind": "operation", "authority": "supporting", "action": "create"},
    ]
    plan["documentation"] = {
        "preserve": ["documentation/requisitos.md"],
        "create": [{"path": "documentation/operacao.md", "purpose": "Documentar operação"}],
        "path_mappings": [{"generic_role": "Product contract", "existing_path": "documentation/requisitos.md"}],
    }
    plan["decisions"] = {"durable_path": "decisions", "open": ["DEC-003"]}
    plan["workflows"] = [{"name": "Release", "path": "operations/release.md", "action": "preserve"}]
    plan["spec_strategy"] = {"root": "changes", "active_pattern": "changes/active/SPEC-NNN", "markdown_name": "SPEC.md", "execution_name": "SPEC.execution.json"}
    plan["validation"] = [
        {"id": "VAL-001", "command": "python -m pytest -q", "required": True},
        {"id": "VAL-002", "command": "python optional_check.py", "required": False},
    ]
    return plan


def test_bootstrap_generates_navigation_from_accepted_plan(tmp_path: Path) -> None:
    project, run = _run_bootstrap(tmp_path, _navigation_plan())
    assert run.returncode == 0, run.stdout + run.stderr
    result = json.loads(run.stdout)
    assert MAP_PATH in result["created"]
    navigation = json.loads((project / MAP_PATH).read_text(encoding="utf-8"))
    by_path = {node["path"]: node for node in navigation["nodes"]}
    assert by_path["documentation/requisitos.md"]["label"] == "Product contract"
    assert by_path["documentation/requisitos.md"]["status"] == "existing"
    assert by_path["documentation/operacao.md"]["status"] == "planned"
    assert by_path["documentation/operacao.md"]["summary"] == "Documentar operação"
    assert "DEC-003" in by_path["decisions"]["summary"]
    assert by_path["operations/release.md"]["label"] == "Release"
    assert by_path["changes"]["target"] == "directory"
    assert by_path["changes/active/SPEC-NNN"]["target"] == "pattern"
    assert any("python -m pytest -q [required]" in node["summary"] for node in navigation["nodes"])
    assert any("python optional_check.py [optional]" in node["summary"] for node in navigation["nodes"])
    assert by_path[".codex/references/runtime-policy.json"]["status"] == "existing"
    assert navigation["maintenance"]["reviewed_at"] is None
    assert not (project / ".codex/references/project-harness.md").exists()
    assert not (project / "documentation").exists()
    assert not (project / "changes").exists()
    agents = (project / "AGENTS.md").read_text(encoding="utf-8")
    assert MAP_PATH in agents


def test_dry_run_lists_navigation_without_creating_project(tmp_path: Path) -> None:
    project, preview = _run_bootstrap(tmp_path, _navigation_plan(), dry_run=True)
    assert preview.returncode == 0, preview.stdout + preview.stderr
    predicted = json.loads(preview.stdout)
    assert predicted["status"] == "preview"
    assert MAP_PATH in predicted["created"]
    assert not project.exists()
    _, run = _run_bootstrap(tmp_path, _navigation_plan())
    assert run.returncode == 0, run.stdout + run.stderr
    assert json.loads(run.stdout)["created"] == predicted["created"]


def test_existing_navigation_is_preserved_in_preview_and_bootstrap(tmp_path: Path) -> None:
    project = tmp_path / "project"
    navigation = project / ".codex/references/project-harness.md"
    navigation.parent.mkdir(parents=True)
    original = b"# Custom navigation\r\n\r\nPreserve these owner notes.\r\n"
    navigation.write_bytes(original)
    before = {path.relative_to(project): path.read_bytes() for path in project.rglob("*") if path.is_file()}
    _, preview = _run_bootstrap(tmp_path, _navigation_plan(), dry_run=True)
    assert preview.returncode == 0, preview.stdout + preview.stderr
    assert ".codex/references/project-harness.md" in json.loads(preview.stdout)["preserved"]
    assert {path.relative_to(project): path.read_bytes() for path in project.rglob("*") if path.is_file()} == before
    _, run = _run_bootstrap(tmp_path, _navigation_plan())
    assert run.returncode == 0, run.stdout + run.stderr
    assert ".codex/references/project-harness.md" in json.loads(run.stdout)["preserved"]
    assert navigation.read_bytes() == original
    assert not (project / MAP_PATH).exists()
    agents = (project / "AGENTS.md").read_text(encoding="utf-8")
    assert ".codex/references/project-harness.md" in agents
    assert MAP_PATH not in agents
    assert "project_map.py check" not in agents


def test_runtime_path_mismatch_is_visible_without_materializing_alternate_policy(tmp_path: Path) -> None:
    plan = _plan()
    plan["runtime_policy"]["project_path"] = "config/custom-policy.json"
    project, run = _run_bootstrap(tmp_path, plan)
    assert run.returncode == 0, run.stdout + run.stderr
    assert any("runtime policy path differs" in warning for warning in json.loads(run.stdout)["warnings"])
    navigation = (project / MAP_PATH).read_text(encoding="utf-8")
    assert "config/custom-policy.json" in navigation
    assert (project / ".codex/references/runtime-policy.json").is_file()
    assert not (project / "config/custom-policy.json").exists()


def test_navigation_preserves_command_content_and_handles_empty_sections() -> None:
    plan = _plan()
    plan["validation"] = [{"id": "VAL-001", "command": 'python check.py | findstr "<ok>"\npython next.py', "required": True}]
    navigation = render_project_harness_navigation(plan)
    assert 'python check.py &#124; findstr &quot;&lt;ok&gt;&quot;<br>python next.py' in navigation
    assert "None declared in the accepted plan." in navigation
    assert "No open decisions declared" in navigation
    assert navigation == render_project_harness_navigation(plan)


def test_unaccepted_plan_does_not_create_navigation_or_project(tmp_path: Path) -> None:
    plan = _plan()
    plan["status"] = "proposed"
    project, run = _run_bootstrap(tmp_path, plan)
    assert run.returncode == 1
    assert json.loads(run.stdout)["status"] == "blocked"
    assert not project.exists()
