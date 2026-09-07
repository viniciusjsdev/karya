"""Deterministic cross-domain safety tests for the optional economic execution router."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SPEC = """---
id: SPEC-024
title: Change a generic project value
status: ready
contract_version: 1
---

# SPEC-024: Change a generic project value

## Goal
Change one project value through an executor-neutral implementation contract.

## Context
The project uses a READY Spec and exact deterministic validation.

## Scope
- Change only `src/value.py`.

## Non-scope
- Do not alter project contracts, credentials, Git state, or external systems.

## Requirements
- REQ-001: The value must become `implemented`.

## Business or domain rules
- BR-001: The implementation remains local and deterministic.

## Decisions already made
- OpenCode may write implementation files only after exact external confirmation.

## Constraints
- No network, dependency installation, external action, or Spec change.

## Acceptance criteria
- AC-001: `src/value.py` contains `implemented`.

## Affected areas
- `src/value.py` only.

## References
- `docs/truth.md` defines the fixture contract.

## Skills
- No domain-specific skill is required for this generic fixture.

## Validation requirements
- VAL-001: Run `python tests/check_value.py`.

## Review requirements
Independent Codex review is required after external execution.

## Execution and runtime
Use `SPEC.execution.json`; OpenCode remains an optional action-time executor.
"""


def manifest() -> dict:
    return {
        "schema_version": "1.0",
        "spec_id": "SPEC-024",
        "contract_version": 1,
        "status": "ready",
        "automatic_handoff": False,
        "execution": {
            "classification": "normal_implementation",
            "role": "developer",
            "model": "gpt-5.6-terra",
            "reasoning": "medium",
            "routing_rationale": "The executor-neutral architecture and acceptance criteria are resolved.",
            "runtime_override": None,
            "working_directory": ".",
            "sandbox_mode": "workspace-write",
            "approval_mode": "auto_review",
            "thread": {"mode": "new", "purpose": "implementation", "thread_id": None},
            "handoff_prompt": "Execute SPEC-024 from durable project sources and return needs_design for consequential ambiguity.",
        },
        "skills": [],
        "references": [{"path": "docs/truth.md", "purpose": "fixture source of truth", "required": True}],
        "validation": [{"id": "VAL-001", "kind": "test", "command": "python tests/check_value.py", "required": True}],
        "review": {"required": True, "independence": "independent", "model": "gpt-5.6-sol", "reasoning": "high", "rationale": "External executor output requires independent Codex audit."},
        "escalation": {"policy_version": "1.0", "allowed": ["terra_high", "needs_design", "sol_high"]},
        "completion": {"schema_path": ".codex/schemas/project-spec-completion.schema.json", "output_path": ".harness/runtime/completions/SPEC-024.json"},
    }


FAKE_OPENCODE = r'''from __future__ import annotations
import json
import os
import re
import sys
from pathlib import Path

args = sys.argv[1:]
if args == ["--version"]:
    print("fake-opencode 1.0")
    raise SystemExit(0)
if args[:2] == ["auth", "list"]:
    print("fake authenticated")
    raise SystemExit(0)
if args[:1] == ["models"]:
    print("fake/model")
    raise SystemExit(0)

prompt = args[-1]
project = Path(args[args.index("--dir") + 1])
runtime_config = json.loads(os.environ["OPENCODE_CONFIG_CONTENT"])
read_permissions = runtime_config["permission"]["read"]
if read_permissions["*.env"] != "deny" or read_permissions["**/.env.*"] != "deny":
    raise SystemExit(5)
if runtime_config["permission"]["websearch"] != "deny" or runtime_config["permission"]["task"] != "deny":
    raise SystemExit(6)
if runtime_config["permission"]["grep"] != "deny" or runtime_config["permission"]["lsp"] != "deny":
    raise SystemExit(7)
completion_match = re.search(r"Write final completion evidence to (.+?) using ", prompt)
if not completion_match:
    raise SystemExit(4)
completion_path = Path(completion_match.group(1))
mode = os.environ.get("KARYA_FAKE_MODE", "allowed")
changed = []
status = "completed"
needs_design = None
if mode == "allowed":
    (project / "src/value.py").write_text("implemented\n", encoding="utf-8")
    changed = ["src/value.py"]
elif mode == "forbidden":
    spec = project / "specs/active/SPEC-024/SPEC.md"
    spec.write_text(spec.read_text(encoding="utf-8") + "\nforbidden\n", encoding="utf-8")
    changed = ["specs/active/SPEC-024/SPEC.md"]
elif mode == "blocked":
    status = "needs_design"
    needs_design = {"question": "Which value?", "reason": "The contract conflicts.", "impact": "Implementation stops.", "affected_areas": ["src/value.py"], "alternatives": []}

completion = {
    "task_id": "economic-router-test",
    "spec_id": "SPEC-024",
    "contract_version": 1,
    "status": status,
    "changed_files": changed,
    "acceptance_evidence": {"AC-001": {"result": "passed", "evidence": ["src/value.py"], "notes": []}} if status == "completed" else {},
    "validation_evidence": {"VAL-001": {"command": "python tests/check_value.py", "result": "passed", "exit_code": 0, "evidence": ["fixture"], "notes": []}} if status == "completed" else {},
    "deviations": ["authorization=secret-test-value"],
    "unresolved_items": [],
    "needs_design": needs_design,
}
completion_path.parent.mkdir(parents=True, exist_ok=True)
completion_path.write_text(json.dumps(completion), encoding="utf-8")
print(json.dumps({"type": "result", "status": status, "api_key": "sk-test-secret-value-12345"}))
'''


def make_project(root: Path, repository_root: Path) -> Path:
    project = root / "project"
    for directory in ("src", "tests", "docs", ".codex/references", ".codex/schemas", "specs/active/SPEC-024"):
        (project / directory).mkdir(parents=True, exist_ok=True)
    (project / "src/value.py").write_text("original\n", encoding="utf-8")
    (project / "tests/check_value.py").write_text(
        "from pathlib import Path\nraise SystemExit(0 if Path('src/value.py').read_text(encoding='utf-8').strip() == 'implemented' else 1)\n",
        encoding="utf-8",
    )
    (project / "docs/truth.md").write_text("# Fixture truth\n", encoding="utf-8")
    (project / "specs/active/SPEC-024/SPEC.md").write_text(SPEC, encoding="utf-8")
    (project / "specs/active/SPEC-024/SPEC.execution.json").write_text(json.dumps(manifest()), encoding="utf-8")
    policy = repository_root / "skills/project-spec-architect/assets/runtime-policy.json"
    (project / ".codex/references/runtime-policy.json").write_text(policy.read_text(encoding="utf-8"), encoding="utf-8")
    completion_schema = repository_root / "skills/project-spec-architect/assets/completion.schema.json"
    (project / ".codex/schemas/project-spec-completion.schema.json").write_text(
        completion_schema.read_text(encoding="utf-8"), encoding="utf-8"
    )
    return project


def request(project: Path, model: str = "fake/model") -> dict:
    confirmation = {
        "approved": True,
        "approved_at": "2026-08-28T12:00:00-03:00",
        "task_id": "economic-router-test",
        "spec_id": "SPEC-024",
        "contract_version": 1,
        "executor": "opencode",
        "provider": "fake",
        "model": model,
        "writable_paths": ["src/**"],
        "validation_ids": ["VAL-001"],
    }
    return {
        "schema_version": "1.0",
        "task_id": "economic-router-test",
        "project_root": str(project),
        "spec": {"markdown_path": "specs/active/SPEC-024/SPEC.md", "manifest_path": "specs/active/SPEC-024/SPEC.execution.json", "id": "SPEC-024", "contract_version": 1},
        "executor": "auto",
        "provider": "fake",
        "model": model,
        "provider_kind": "managed",
        "billing_mode": "unknown",
        "timeout_minutes": 1,
        "writable_paths": ["src/**"],
        "prohibited_actions": ["secrets_and_credentials", "environment_files", "external_actions", "spec_changes", "destructive_git", "web_access"],
        "baseline": {"mode": "full_snapshot"},
        "validation_ids": ["VAL-001"],
        "confirmation": confirmation,
    }


def run_router(router: Path, request_path: Path, fake: Path, *, mode: str = "allowed", dry_run: bool = False) -> tuple[int, dict, str]:
    env = {**os.environ, "KARYA_OPENCODE_COMMAND": f"{sys.executable} {fake}", "KARYA_FAKE_MODE": mode}
    command = [sys.executable, str(router), "--request", str(request_path)]
    if dry_run:
        command.append("--dry-run")
    completed = subprocess.run(command, text=True, capture_output=True, env=env, check=False)
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    assert len(lines) == 1, completed.stdout
    return completed.returncode, json.loads(lines[0]), completed.stderr


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    repository_root = script_dir.parents[2]
    router = script_dir / "route_economic_execution.py"
    with tempfile.TemporaryDirectory(prefix="karya-economic-router-") as temporary:
        root = Path(temporary)
        fake = root / "fake_opencode.py"
        fake.write_text(FAKE_OPENCODE, encoding="utf-8")

        project = make_project(root / "ready", repository_root)
        request_path = root / "approved-request.json"
        request_path.write_text(json.dumps(request(project)), encoding="utf-8")
        code, result, stderr = run_router(router, request_path, fake, dry_run=True)
        assert code == 0, stderr
        assert result["route"] == "opencode-ready"

        code, result, stderr = run_router(router, request_path, fake)
        assert code == 0, stderr
        assert result["route"] == "opencode-completed", result
        assert result["changed_files"] == ["src/value.py"]
        assert result["independent_validations"]["VAL-001"]["result"] == "passed"
        events = Path(result["artifacts"]["events"]).read_text(encoding="utf-8")
        assert "sk-test-secret-value-12345" not in events
        assert "[REDACTED]" in events
        completion = Path(result["artifacts"]["completion"]).read_text(encoding="utf-8")
        assert "secret-test-value" not in completion

        fallback_project = make_project(root / "fallback", repository_root)
        fallback_path = root / "fallback-request.json"
        fallback_path.write_text(json.dumps(request(fallback_project, "fake/missing")), encoding="utf-8")
        code, result, stderr = run_router(router, fallback_path, fake, dry_run=True)
        assert code == 0, stderr
        assert result["route"] == "codex-fallback-required"

        blocked_project = make_project(root / "blocked", repository_root)
        blocked_request = request(blocked_project)
        blocked_request["confirmation"]["model"] = "different/model"
        blocked_path = root / "blocked-request.json"
        blocked_path.write_text(json.dumps(blocked_request), encoding="utf-8")
        code, result, _ = run_router(router, blocked_path, fake, dry_run=True)
        assert code == 2
        assert result["route"] == "preflight-blocked"
        assert any("confirmation" in reason for reason in result["reasons"])

        forbidden_project = make_project(root / "forbidden", repository_root)
        forbidden_path = root / "forbidden-request.json"
        forbidden_path.write_text(json.dumps(request(forbidden_project)), encoding="utf-8")
        code, result, _ = run_router(router, forbidden_path, fake, mode="forbidden")
        assert code == 3
        assert result["route"] == "opencode-error"
        assert any("protected path changed" in reason for reason in result["reasons"])

    print("economic execution router tests passed")


def test_economic_execution_router() -> None:
    """Exercise the router in clean subprocesses under pytest and direct runs."""
    main()


def test_living_map_returns_codex_before_any_provider_command(tmp_path: Path) -> None:
    repository_root = Path(__file__).resolve().parents[3]
    project = make_project(tmp_path / "mapped", repository_root)
    before = (project / "src/value.py").read_bytes()
    (project / ".codex/references/project-map.json").write_text("{}", encoding="utf-8")
    (project / "scripts/harness").mkdir(parents=True)
    (project / "scripts/harness/project_map.py").write_text("raise RuntimeError('not executed in preflight')", encoding="utf-8")
    contract = manifest()
    contract["validation"].append({"id": "VAL-002", "kind": "test", "required": True,
        "command": "python scripts/harness/project_map.py check --project-root ."})
    (project / "specs/active/SPEC-024/SPEC.execution.json").write_text(json.dumps(contract), encoding="utf-8")
    approved = request(project)
    approved["validation_ids"].append("VAL-002")
    approved["confirmation"]["validation_ids"].append("VAL-002")
    request_path = tmp_path / "mapped-request.json"
    fake = tmp_path / "provider-must-not-run.py"
    fake.write_text("raise RuntimeError('provider must not run')", encoding="utf-8")
    router = Path(__file__).with_name("route_economic_execution.py")
    for executor, expected_code, expected_route in [("auto", 0, "codex-fallback-required"), ("opencode", 3, "opencode-unavailable")]:
        approved["executor"] = executor
        request_path.write_text(json.dumps(approved), encoding="utf-8")
        code, result, stderr = run_router(router, request_path, fake)
        assert code == expected_code, result
        assert result["route"] == expected_route, result
        assert "Codex-owned" in result["reasons"][0]
        assert "provider must not run" not in stderr
        assert "readiness" not in result
        assert (project / "src/value.py").read_bytes() == before


if __name__ == "__main__":
    main()
