"""Audit Project Harness structure, contracts, local skills, and evidence without repair."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

SKILLS_ROOT = Path(__file__).resolve().parents[2]
for scripts in (SKILLS_ROOT / "project-spec-architect" / "scripts", SKILLS_ROOT / "codex-runtime-router" / "scripts", SKILLS_ROOT / "project-skill-author" / "scripts"):
    if str(scripts) not in os.sys.path:
        os.sys.path.insert(0, str(scripts))
from _runtime_core import validate_completion  # noqa: E402
from _spec_core import validate_spec_pair  # noqa: E402
from validate_project_skill import validate_project_skill  # noqa: E402


def audit_project_harness(project_root: str | Path, *, skills_root: str | Path | None = None) -> dict[str, Any]:
    """Return one deterministic audit report and explicit semantic limitations."""
    root = Path(project_root).resolve()
    findings: list[dict[str, Any]] = []

    def rel(path: Path) -> str:
        try:
            return path.resolve().relative_to(root).as_posix()
        except ValueError:
            return str(path.resolve())

    def add(severity: str, category: str, message: str, evidence: list[str]) -> None:
        findings.append({"id": f"HARNESS-{len(findings) + 1:03d}", "severity": severity, "category": category, "message": message, "evidence": evidence})

    if not (root / "AGENTS.md").exists():
        add("high", "agents", "AGENTS.md is missing.", ["AGENTS.md"])
    if not (root / ".codex/references/project-harness.md").exists():
        add("medium", "navigation", "Project Harness navigation reference is missing.", [".codex/references/project-harness.md"])
    project_policy = root / ".codex/references/runtime-policy.json"
    fallback_policy = SKILLS_ROOT / "project-spec-architect/assets/runtime-policy.json"
    if not project_policy.exists():
        add("medium", "runtime", "Project runtime policy copy is missing; audit used the Factory fallback.", [".codex/references/runtime-policy.json"])
    try:
        policy = json.loads((project_policy if project_policy.exists() else fallback_policy).read_text(encoding="utf-8-sig"))
    except Exception as error:
        add("high", "runtime", f"Runtime policy is invalid JSON: {error}", [rel(project_policy)])
        policy = json.loads(fallback_policy.read_text(encoding="utf-8-sig"))
    gitignore = root / ".gitignore"
    runtime_root = root / ".harness/runtime"
    if runtime_root.exists() and (not gitignore.exists() or ".harness/runtime/" not in gitignore.read_text(encoding="utf-8-sig").splitlines()):
        add("medium", "runtime_state", "Temporary .harness/runtime state is not ignored by version control.", [".harness/runtime/", ".gitignore"])

    manifests = [path for path in root.rglob("*.execution.json") if not {".git", "node_modules", ".venv", "venv", "__pycache__"}.intersection(path.parts)]
    for manifest_path in manifests:
        directory = manifest_path.parent
        spec_path = directory / "SPEC.md"
        if not spec_path.exists():
            add("high", "spec", "Execution manifest has no sibling SPEC.md.", [rel(manifest_path)])
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
            markdown = spec_path.read_text(encoding="utf-8-sig")
            errors = validate_spec_pair(markdown, manifest, policy, project_root=root, skills_root=skills_root, require_ready=manifest.get("status") == "ready")
            for error in errors:
                add("high" if manifest.get("status") == "ready" else "medium", "spec", error, [rel(spec_path), rel(manifest_path)])
            if manifest.get("status") in {"implemented", "review", "done"}:
                completion_path = (root / manifest.get("completion", {}).get("output_path", "")).resolve()
                if not completion_path.exists():
                    add("high", "completion", f"{manifest.get('status')} Spec has no declared completion evidence.", [rel(manifest_path), rel(completion_path)])
                else:
                    completion = json.loads(completion_path.read_text(encoding="utf-8-sig"))
                    for error in validate_completion(completion, manifest, markdown, completion.get("thread_id"), project_root=root):
                        add("high", "completion", error, [rel(completion_path)])
            if manifest.get("status") == "done" and manifest.get("review", {}).get("required"):
                review_path = directory / "evidence/review.json"
                if not review_path.exists():
                    add("high", "review", "DONE Spec requires the declared independent review evidence.", [rel(manifest_path), rel(review_path)])
                else:
                    review = json.loads(review_path.read_text(encoding="utf-8-sig"))
                    if review.get("spec_id") != manifest.get("spec_id") or review.get("contract_version") != manifest.get("contract_version"):
                        add("high", "review", "Review evidence does not match the Spec identity/version.", [rel(review_path)])
                    if not review.get("thread_id"):
                        add("high", "review", "Review evidence has no thread ID.", [rel(review_path)])
                    if review.get("runtime", {}).get("model") != manifest["review"].get("model") or review.get("runtime", {}).get("reasoning") != manifest["review"].get("reasoning"):
                        add("high", "review", "Review evidence runtime differs from the manifest review policy.", [rel(review_path)])
                    if review.get("status") != "approved":
                        add("high", "review", "DONE Spec does not have an approved review result.", [rel(review_path)])
                    inputs = review.get("review_input")
                    if not isinstance(inputs, list) or not any("completion" in str(item).lower() for item in inputs) or not any("diff" in str(item).lower() or "artifact" in str(item).lower() for item in inputs):
                        add("medium", "review", "Independent review input must include completion evidence and diff/artifacts.", [rel(review_path)])
        except Exception as error:
            add("high", "spec", f"Unable to parse or audit Spec: {error}", [rel(spec_path), rel(manifest_path)])

    local_skills_root = root / ".agents/skills"
    local_skill_dirs = sorted(path for path in local_skills_root.iterdir() if path.is_dir()) if local_skills_root.exists() else []
    for directory in local_skill_dirs:
        for error in validate_project_skill(directory, project_root=root):
            add("high" if "missing" in error else "medium", "skill", error, [rel(directory)])

    counts = {severity: sum(item["severity"] == severity for item in findings) for severity in ("high", "medium", "low")}
    counts.update({"specs": len(manifests), "local_skills": len(local_skill_dirs)})
    status = "blocked" if counts["high"] else "corrections_required" if counts["medium"] else "approved_with_notes" if counts["low"] else "approved"
    return {"status": status, "project_root": str(root), "findings": findings, "summary": counts, "unassessed": ["Semantic docs-to-reality drift requires domain inspection.", "Chat-only knowledge cannot be detected unless relevant chat evidence is supplied.", "Runtime cost and latency suitability require observed usage/evaluation data.", "Parallel-write safety requires branch/worktree and execution evidence when parallelism was used."]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--skills-root")
    args = parser.parse_args()
    report = audit_project_harness(args.project_root, skills_root=args.skills_root)
    print(json.dumps(report, indent=2))
    return 1 if report["status"] in {"blocked", "corrections_required"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
