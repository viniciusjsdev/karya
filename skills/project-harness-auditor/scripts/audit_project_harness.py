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


def audit_project_harness(project_root: str | Path, *, skills_root: str | Path | None = None, external_route_results: list[str | Path] | None = None) -> dict[str, Any]:
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
    manifest_index: dict[tuple[str, int], tuple[Path, dict[str, Any]]] = {}
    for manifest_path in manifests:
        directory = manifest_path.parent
        spec_path = directory / "SPEC.md"
        if not spec_path.exists():
            add("high", "spec", "Execution manifest has no sibling SPEC.md.", [rel(manifest_path)])
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
            if isinstance(manifest.get("spec_id"), str) and isinstance(manifest.get("contract_version"), int):
                manifest_index[(manifest["spec_id"], manifest["contract_version"])] = (manifest_path, manifest)
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

    external_results = [Path(path).resolve() for path in (external_route_results or [])]
    for result_path in external_results:
        try:
            result_path.relative_to(root)
            add("high", "economic_execution", "External execution route results must remain outside the project repository.", [rel(result_path)])
            continue
        except ValueError:
            pass
        if not result_path.is_file():
            add("high", "economic_execution", "Declared external execution route result does not exist.", [str(result_path)])
            continue
        try:
            result = json.loads(result_path.read_text(encoding="utf-8-sig"))
            if result.get("executor") != "opencode":
                add("low", "economic_execution", "Route result did not execute OpenCode; no external implementation evidence was audited.", [str(result_path)])
                continue
            if result.get("route") != "opencode-completed":
                add("high", "economic_execution", "OpenCode route did not complete successfully and cannot support implementation approval.", [str(result_path)])
            if not result.get("request_fingerprint"):
                add("high", "economic_execution", "OpenCode route result has no external request fingerprint.", [str(result_path)])
            identity = (result.get("spec_id"), result.get("contract_version"))
            manifest_entry = manifest_index.get(identity)
            if manifest_entry is None:
                add("high", "economic_execution", "OpenCode route result does not match a project Spec identity/version.", [str(result_path)])
            elif manifest_entry[1].get("review", {}).get("required") is not True or manifest_entry[1].get("review", {}).get("independence") != "independent":
                add("high", "economic_execution", "External execution requires independent review in the matching Spec manifest.", [rel(manifest_entry[0]), str(result_path)])
            else:
                review_path = manifest_entry[0].parent / "evidence/review.json"
                if not review_path.is_file():
                    add("high", "economic_execution", "Completed OpenCode execution has no independent Codex review receipt.", [rel(manifest_entry[0]), rel(review_path), str(result_path)])
                else:
                    review = json.loads(review_path.read_text(encoding="utf-8-sig"))
                    if review.get("spec_id") != identity[0] or review.get("contract_version") != identity[1] or review.get("status") != "approved" or not review.get("thread_id"):
                        add("high", "economic_execution", "Independent Codex review is not approved or does not match the external execution contract.", [rel(review_path), str(result_path)])
                    review_inputs = " ".join(str(item).lower() for item in review.get("review_input", []))
                    required_inputs = {
                        "route result": ("route-result", "route result"),
                        "completion evidence": ("completion",),
                        "snapshot diff": ("snapshot-diff", "snapshot diff", "diff"),
                        "router validations": ("router-validations", "router validations", "validation"),
                    }
                    for label, terms in required_inputs.items():
                        if not any(term in review_inputs for term in terms):
                            add("high", "economic_execution", f"Independent Codex review does not declare {label} as an input.", [rel(review_path), str(result_path)])
            scope = result.get("scope_integrity")
            if not isinstance(scope, dict) or scope.get("ok") is not True:
                add("high", "economic_execution", "OpenCode route did not preserve approved writable scope.", [str(result_path)])
            validations = result.get("independent_validations")
            if not isinstance(validations, dict) or not validations or any(not isinstance(item, dict) or item.get("result") != "passed" for item in validations.values()):
                add("high", "economic_execution", "Router-run independent validations are missing or not all passing.", [str(result_path)])
            artifacts = result.get("artifacts") if isinstance(result.get("artifacts"), dict) else {}
            required_artifacts = ("request_receipt", "completion", "snapshot_before", "snapshot_after", "snapshot_diff", "router_validations")
            for name in required_artifacts:
                artifact = Path(str(artifacts.get(name, "")))
                if not artifacts.get(name) or not artifact.is_file():
                    add("high", "economic_execution", f"OpenCode route artifact is missing: {name}.", [str(result_path), str(artifact)])
            if all(artifacts.get(name) and Path(str(artifacts[name])).is_file() for name in ("completion", "snapshot_diff")):
                completion = json.loads(Path(str(artifacts["completion"])).read_text(encoding="utf-8-sig"))
                snapshot_diff = json.loads(Path(str(artifacts["snapshot_diff"])).read_text(encoding="utf-8-sig"))
                changed = set(result.get("changed_files", []))
                if changed != set(completion.get("changed_files", [])) or changed != set(snapshot_diff.get("changed", [])):
                    add("high", "economic_execution", "Changed files differ across route result, completion evidence, and snapshot diff.", [str(result_path), str(artifacts["completion"]), str(artifacts["snapshot_diff"])])
        except Exception as error:
            add("high", "economic_execution", f"Unable to parse or audit external execution result: {error}", [str(result_path)])

    local_skills_root = root / ".agents/skills"
    local_skill_dirs = sorted(path for path in local_skills_root.iterdir() if path.is_dir()) if local_skills_root.exists() else []
    for directory in local_skill_dirs:
        for error in validate_project_skill(directory, project_root=root):
            add("high" if "missing" in error else "medium", "skill", error, [rel(directory)])

    counts = {severity: sum(item["severity"] == severity for item in findings) for severity in ("high", "medium", "low")}
    counts.update({"specs": len(manifests), "local_skills": len(local_skill_dirs), "external_execution_results": len(external_results)})
    status = "blocked" if counts["high"] else "corrections_required" if counts["medium"] else "approved_with_notes" if counts["low"] else "approved"
    return {"status": status, "project_root": str(root), "findings": findings, "summary": counts, "unassessed": ["Semantic docs-to-reality drift requires domain inspection.", "Chat-only knowledge cannot be detected unless relevant chat evidence is supplied.", "Runtime cost and latency suitability require observed usage/evaluation data.", "Parallel-write safety requires branch/worktree and execution evidence when parallelism was used."]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--skills-root")
    parser.add_argument("--external-route-result", action="append", default=[])
    args = parser.parse_args()
    report = audit_project_harness(args.project_root, skills_root=args.skills_root, external_route_results=args.external_route_result)
    print(json.dumps(report, indent=2))
    return 1 if report["status"] in {"blocked", "corrections_required"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
