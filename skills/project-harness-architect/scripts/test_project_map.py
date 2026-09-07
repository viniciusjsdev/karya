"""Behavioral tests for living navigation, preservation, coverage and offline export."""
from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from _project_map import HTML_PATH, LEGACY_PATH, MAP_PATH, atomic_write, check_map, load_map, map_from_plan, render_html, review_map, validate_map
from project_map import initialize
from test_harness_bootstrap import _plan, _run_bootstrap


def fixture(tmp_path: Path) -> tuple[Path, dict]:
    """Build a real fresh project whose existing sources can be reviewed."""
    root = tmp_path / "project"
    (root / "notebooks").mkdir(parents=True)
    (root / "notebooks/method.md").write_text("# Method\nApproved experiment procedure.\n", encoding="utf-8")
    (root / "src").mkdir()
    (root / "src/main.py").write_text("result = 1\n", encoding="utf-8")
    root, run = _run_bootstrap(tmp_path, _plan())
    assert run.returncode == 0, run.stdout + run.stderr
    data = load_map(root)
    assert check_map(root, data)["status"] == "review_required"
    return root, data


def persist(root: Path, data: dict) -> None:
    """Write test-owned map edits exactly as a project executor would."""
    atomic_write(root / MAP_PATH, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def reviewed(root: Path, data: dict) -> dict:
    """Record an explicit synthetic-source review and verify the resulting state."""
    result = review_map(root, data, "Reviewed method and code fixture; existing navigation remains accurate.")
    persist(root, result)
    assert check_map(root, result)["status"] == "current"
    return result


def test_checkout_line_endings_preserve_review_but_content_changes_do_not(tmp_path: Path) -> None:
    root, data = fixture(tmp_path)
    text = root / "src/main.py"
    text.write_bytes(b"result = 1\n")
    data = reviewed(root, data)
    text.write_bytes(b"result = 1\r\n")
    assert check_map(root, data)["status"] == "current"
    text.write_bytes(b"result = 2\r\n")
    assert check_map(root, data)["status"] == "review_required"


@pytest.mark.parametrize("prefix", [b"\x00", b"\xff"])
def test_binary_line_endings_are_not_normalized(tmp_path: Path, prefix: bytes) -> None:
    root, data = fixture(tmp_path)
    binary = root / "sample.bin"
    binary.write_bytes(prefix + b"sample\n")
    data = reviewed(root, data)
    binary.write_bytes(prefix + b"sample\r\n")
    assert check_map(root, data)["status"] == "review_required"


@pytest.mark.parametrize("change", ["edit_code", "edit_doc", "add", "remove", "rename"])
def test_project_changes_require_explicit_review(tmp_path: Path, change: str) -> None:
    root, data = fixture(tmp_path)
    data = reviewed(root, data)
    source = root / "src/main.py"
    if change == "edit_code":
        source.write_text("result = 2\n", encoding="utf-8")  # same length; mtime is not the contract
    elif change == "edit_doc":
        (root / "notebooks/method.md").write_text("# Changed methodology\n", encoding="utf-8")
    elif change == "add":
        (root / "new.py").write_text("new = True\n", encoding="utf-8")
    elif change == "remove":
        source.unlink()
    else:
        source.rename(root / "src/renamed.py")
    before = (root / MAP_PATH).read_bytes()
    report = check_map(root, data)
    assert report["status"] == "review_required"
    assert (root / MAP_PATH).read_bytes() == before
    reviewed(root, data)


def test_relation_edits_require_review_and_dangling_relations_block_it(tmp_path: Path) -> None:
    root, data = fixture(tmp_path)
    data = reviewed(root, data)
    ids = [node["id"] for node in data["nodes"]]
    data["relations"].append({"from": ids[0], "to": ids[-1], "type": "references", "rationale": "Verified explicit fixture link."})
    persist(root, data)
    assert check_map(root, data)["status"] == "review_required"
    data = reviewed(root, data)
    data["relations"][-1]["to"] = "absent"
    assert check_map(root, data)["status"] == "invalid"
    with pytest.raises(ValueError, match="Dangling"):
        review_map(root, data, "Cannot acknowledge invalid relations")


def test_planned_targets_must_be_reconciled_when_created(tmp_path: Path) -> None:
    root, data = fixture(tmp_path)
    data = reviewed(root, data)
    (root / "specs").mkdir()
    assert any("Planned target now exists" in item for item in check_map(root, data)["pending"])
    with pytest.raises(ValueError, match="planned status"):
        review_map(root, data, "Review without reconciliation must fail")
    next(node for node in data["nodes"] if node["path"] == "specs")["status"] = "existing"
    reviewed(root, data)


def test_missing_source_requires_path_repair_with_stable_id(tmp_path: Path) -> None:
    root, data = fixture(tmp_path)
    node = next(node for node in data["nodes"] if node["path"] == "notebooks")
    original_id = node["id"]
    (root / "notebooks").rename(root / "methods")
    assert any("missing directory" in item for item in validate_map(root, data))
    node["path"] = "methods"
    reviewed(root, data)
    assert node["id"] == original_id


@pytest.mark.parametrize("target", ["../outside", "C:/outside", "/outside", "docs/../../outside", ".env", ".harness/runtime/state.json"])
def test_unsafe_or_sensitive_local_targets_are_rejected(tmp_path: Path, target: str) -> None:
    root, data = fixture(tmp_path)
    data["nodes"][0].update(path=target, status="planned", target="file")
    assert validate_map(root, data)


@pytest.mark.parametrize("url,valid", [("https://example.com/spec", True), ("javascript:alert(1)", False), ("file:///etc/passwd", False), ("https://user:password@example.com", False)])
def test_external_references_are_validated_without_fetching(tmp_path: Path, url: str, valid: bool) -> None:
    root, data = fixture(tmp_path)
    data["nodes"][0].update(path=url, target="external", authority="external")
    assert (validate_map(root, data) == []) is valid


def test_malformed_map_and_duplicate_ids_are_errors_not_success(tmp_path: Path) -> None:
    root, data = fixture(tmp_path)
    assert check_map(root, []) ["status"] == "invalid"
    data["nodes"].append(copy.deepcopy(data["nodes"][0]))
    assert any("Duplicate node" in item for item in validate_map(root, data))
    data["nodes"][0]["unknown"] = "not allowed"
    assert any("unknown field" in item for item in validate_map(root, data))


def test_generated_and_secret_files_do_not_invalidate_map(tmp_path: Path) -> None:
    root, data = fixture(tmp_path)
    data = reviewed(root, data)
    for name in (".harness/views/project-map.html", "__pycache__/x.pyc", ".env", "node_modules/module.js"):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("synthetic excluded fixture", encoding="utf-8")
    assert check_map(root, data)["status"] == "current"
    assert "file_count" in check_map(root, data)["coverage"]


def test_lifecycle_receipts_do_not_loop_but_spec_intent_and_other_evidence_do(tmp_path: Path) -> None:
    root, data = fixture(tmp_path)
    folder = root / "changes/SPEC-001"
    folder.mkdir(parents=True)
    spec = folder / "SPEC.md"
    manifest = folder / "SPEC.execution.json"
    spec.write_text("---\nid: SPEC-001\nstatus: ready\n---\nRequirement: preserve behavior.\n", encoding="utf-8")
    manifest.write_text(json.dumps({"schema_version": "2.0", "status": "ready", "contract_version": 1}), encoding="utf-8")
    data = reviewed(root, data)
    spec.write_text(spec.read_text().replace("ready", "in_progress"), encoding="utf-8")
    manifest.write_text(json.dumps({"schema_version": "2.0", "status": "in_progress", "contract_version": 1}), encoding="utf-8")
    (folder / "evidence").mkdir()
    (folder / "evidence/completion.json").write_text("{}", encoding="utf-8")
    assert check_map(root, data)["status"] == "current"
    spec.write_text(spec.read_text().replace("preserve behavior", "change behavior"), encoding="utf-8")
    assert check_map(root, data)["status"] == "review_required"
    data = reviewed(root, data)
    (root / "evidence").mkdir()
    (root / "evidence/research.md").write_text("Domain evidence", encoding="utf-8")
    assert check_map(root, data)["status"] == "review_required"


def test_git_inventory_honors_ignores_but_covers_explicit_ignored_file(tmp_path: Path) -> None:
    root, data = fixture(tmp_path)
    subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
    (root / ".gitignore").write_text("cache/\nlocal.md\n", encoding="utf-8")
    (root / "local.md").write_text("Approved local reference", encoding="utf-8")
    data["nodes"].append({**data["nodes"][0], "id": "local", "path": "local.md", "target": "file"})
    data = reviewed(root, data)
    (root / "cache").mkdir()
    (root / "cache/noise.txt").write_text("ignored", encoding="utf-8")
    assert check_map(root, data)["status"] == "current"
    (root / "local.md").write_text("Changed local reference", encoding="utf-8")
    report = check_map(root, data)
    assert report["status"] == "review_required"
    assert any("Source changed: local" in pending for pending in report["pending"])
    assert report["coverage"]["mode"].startswith("git")


def test_migration_preserves_manual_sources_and_instructions(tmp_path: Path) -> None:
    root = tmp_path / "legacy"
    (root / "notebooks").mkdir(parents=True)
    (root / LEGACY_PATH).parent.mkdir(parents=True)
    (root / LEGACY_PATH).write_bytes(b"# Owner map\r\nUnique domain guidance.\r\n")
    (root / "AGENTS.md").write_text("# Owner rules\nNever change approved contracts.\n", encoding="utf-8")
    before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    preview = initialize(root, _plan(), dry_run=True, migrate=True)
    assert MAP_PATH in preview["created"]
    assert before == {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    initialize(root, _plan(), migrate=True)
    assert (root / LEGACY_PATH).read_bytes() == before[Path(LEGACY_PATH)]
    assert "Never change approved contracts." in (root / "AGENTS.md").read_text(encoding="utf-8")
    assert MAP_PATH in (root / "AGENTS.md").read_text(encoding="utf-8")
    assert any(n["path"] == LEGACY_PATH for n in load_map(root)["nodes"])
    after = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    initialize(root, _plan(), migrate=True)
    assert after == {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def test_migration_does_not_misattribute_new_declarations_to_old_archive(tmp_path: Path) -> None:
    root = tmp_path / "legacy"
    archive = root / ".codex/decisions/project-harness-bootstrap.json"
    archive.parent.mkdir(parents=True)
    archive.write_text(json.dumps(_plan()), encoding="utf-8")
    plan = _plan()
    plan["validation"] = [{"id": "VAL-NEW", "command": "python new_check.py", "required": True}]
    before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    with pytest.raises(ValueError, match="differs from the preserved bootstrap archive"):
        initialize(root, plan, migrate=True)
    assert before == {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def test_installed_cli_review_check_query_and_html_are_standalone(tmp_path: Path) -> None:
    root, data = fixture(tmp_path)
    command = [sys.executable, str(root / "scripts/harness/project_map.py")]

    def run(*args: str):
        return subprocess.run(command + list(args) + ["--project-root", str(root)], cwd=tmp_path, capture_output=True, text=True, encoding="utf-8")

    assert run("check").returncode == 1
    review = run("review", "--note", "Checked original fixture sources and relationships.")
    assert review.returncode == 0, review.stdout + review.stderr
    assert run("check").returncode == 0
    before = (root / MAP_PATH).read_bytes()
    query = run("query", "--text", "notebooks", "--limit", "1")
    assert query.returncode == 0 and len(json.loads(query.stdout)["nodes"]) == 1
    exported = run("render")
    assert exported.returncode == 0, exported.stdout + exported.stderr
    assert (root / HTML_PATH).is_file()
    assert (root / MAP_PATH).read_bytes() == before
    assert run("check").returncode == 0


def test_router_replays_map_check_and_rejects_false_completion_claim(tmp_path: Path, monkeypatch) -> None:
    root, data = fixture(tmp_path)
    data = reviewed(root, data)
    (root / "src/main.py").write_text("result = 42\n", encoding="utf-8")
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2] / "codex-runtime-router/scripts"))
    monkeypatch.setenv("PATH", str(Path(sys.executable).parent) + os.pathsep + os.environ["PATH"])
    from route_codex_runtime import _run_canonical_validations
    manifest = {"validation": [{"id": "VAL-001", "kind": "test", "required": True,
                                "command": "python scripts/harness/project_map.py check --project-root ."}]}
    evidence = {"validation_evidence": [{"validation_id": "VAL-001", "result": "passed", "exit_code": 0}]}
    before = (root / MAP_PATH).read_bytes()
    assert _run_canonical_validations(evidence, manifest, root) == []
    assert evidence["validation_evidence"][0]["result"] == "failed"
    assert evidence["validation_evidence"][0]["verification"] == "router"
    assert (root / MAP_PATH).read_bytes() == before
    reviewed(root, data)
    _run_canonical_validations(evidence, manifest, root)
    assert evidence["validation_evidence"][0]["result"] == "passed"
    assert evidence["validation_evidence"][0]["exit_code"] == 0


def test_html_does_not_execute_source_strings_or_acknowledge_staleness(tmp_path: Path) -> None:
    root, data = fixture(tmp_path)
    attack = '</script><script>window.INJECTED=true</script><img src=x onerror=alert(1)>'
    data["project"]["name"] = attack
    data["nodes"][0]["summary"] = attack
    output = render_html(root, data)
    assert attack not in output
    assert "\\u003c/script\\u003e" in output
    assert 'connect-src \'none\'' in output
    assert 'src="http' not in output and 'href="http' not in output
    assert "review_required" in output
    assert data["maintenance"]["reviewed_at"] is None


def area_fixture(tmp_path: Path) -> tuple[Path, dict]:
    """Declare a source-backed area without changing existing node or edge meaning."""
    root, data = fixture(tmp_path)
    ids = [node["id"] for node in data["nodes"]]
    data["schema_version"] = "1.1"
    data["navigation"] = {"root": ids[0], "areas": [{"id": "analysis", "label": "Analysis area",
        "rationale": "Method source defines this fixture capability.", "sources": [ids[0]], "members": [ids[1]]}]}
    return root, data


@pytest.mark.parametrize("change", ["old_version", "root", "member", "source", "duplicate_id", "duplicate_member", "root_member"])
def test_area_integrity_rejects_broken_references(tmp_path: Path, change: str) -> None:
    root, data = area_fixture(tmp_path)
    assert validate_map(root, data) == []
    area = data["navigation"]["areas"][0]
    if change == "old_version":
        data["schema_version"] = "1.0"
    elif change == "root":
        data["navigation"]["root"] = "missing"
    elif change in {"member", "source"}:
        area["members" if change == "member" else "sources"] = ["missing"]
    elif change == "duplicate_id":
        data["navigation"]["areas"].append(copy.deepcopy(area))
    elif change == "duplicate_member":
        area["members"] *= 2
    else:
        area["members"] = [data["navigation"]["root"]]
    assert check_map(root, data)["status"] == "invalid"
    with pytest.raises(ValueError):
        review_map(root, data, "Broken membership cannot be acknowledged.")


def test_area_edits_require_review_and_query_returns_membership(tmp_path: Path) -> None:
    root, data = area_fixture(tmp_path)
    data = reviewed(root, data)
    data["navigation"]["areas"][0]["label"] = "Measured capability"
    persist(root, data)
    assert check_map(root, data)["status"] == "review_required"
    reviewed(root, data)
    before = (root / MAP_PATH).read_bytes()
    result = subprocess.run([sys.executable, str(root / "scripts/harness/project_map.py"), "query",
        "--project-root", str(root), "--text", "Measured capability"], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    queried = json.loads(result.stdout)
    assert [node["id"] for node in queried["nodes"]] == data["navigation"]["areas"][0]["members"]
    assert queried["areas"][0]["sources"] == data["navigation"]["areas"][0]["sources"]
    assert (root / MAP_PATH).read_bytes() == before


def test_area_partial_and_multiple_membership_remain_explicit(tmp_path: Path) -> None:
    root, data = area_fixture(tmp_path)
    second = copy.deepcopy(data["navigation"]["areas"][0])
    second["id"] = "second"
    data["navigation"]["areas"].append(second)
    assert validate_map(root, data) == []
    assert data["navigation"]["areas"][0]["members"] == second["members"]
    assert len(second["members"]) < len(data["nodes"]) - 1
    assert '"navigation"' in render_html(root, data)
