"""Audit Project Harness structure, contracts, local skills, and evidence without repair."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

SKILLS_ROOT = Path(__file__).resolve().parents[2]
for scripts in (
    SKILLS_ROOT / "project-spec-architect" / "scripts",
    SKILLS_ROOT / "codex-runtime-router" / "scripts",
    SKILLS_ROOT / "project-skill-author" / "scripts",
    SKILLS_ROOT / "project-harness-architect" / "scripts",
):
    if str(scripts) not in os.sys.path:
        os.sys.path.insert(0, str(scripts))
from _runtime_core import (
    validate_completion,
    validate_lifecycle,
    validate_review_evidence,
)
from _spec_core import validate_spec_pair, validate_structural_baseline
from validate_project_skill import validate_project_skill
from _project_map import MAP_PATH, check_map, load_map


def audit_project_harness(
    project_root: str | Path,
    *,
    skills_root: str | Path | None = None,
    external_route_results: list[str | Path] | None = None,
) -> dict[str, Any]:
    """Return one deterministic audit report and explicit semantic limitations."""
    root = Path(project_root).resolve()
    findings: list[dict[str, Any]] = []

    def rel(path: Path) -> str:
        try:
            return path.resolve().relative_to(root).as_posix()
        except ValueError:
            return str(path.resolve())

    def add(severity: str, category: str, message: str, evidence: list[str]) -> None:
        findings.append(
            {
                "id": f"HARNESS-{len(findings) + 1:03d}",
                "severity": severity,
                "category": category,
                "message": message,
                "evidence": evidence,
            }
        )

    if not (root / "AGENTS.md").exists():
        add("high", "agents", "AGENTS.md is missing.", ["AGENTS.md"])
    if (root / MAP_PATH).exists():
        try:
            navigation = check_map(root, load_map(root))
            for error in navigation["errors"]:
                add("high", "navigation", error, [MAP_PATH])
            for pending in navigation["pending"]:
                add("medium", "navigation", pending, [MAP_PATH])
            if (root / "AGENTS.md").is_file() and MAP_PATH not in (root / "AGENTS.md").read_text(encoding="utf-8-sig"):
                add("medium", "navigation", "AGENTS.md does not point to the JSON navigation map.", ["AGENTS.md", MAP_PATH])
        except (ValueError, OSError, TypeError, KeyError) as error:
            add("high", "navigation", f"Invalid navigation map: {error}", [MAP_PATH])
    elif (root / "AGENTS.md").is_file() and MAP_PATH in (root / "AGENTS.md").read_text(encoding="utf-8-sig"):
        add("high", "navigation", "JSON navigation map is missing despite AGENTS routing to it.", ["AGENTS.md", MAP_PATH])
    elif not (root / ".codex/references/project-harness.md").exists():
        add(
            "medium",
            "navigation",
            "Project Harness navigation reference is missing.",
            [".codex/references/project-harness.md"],
        )
    project_policy = root / ".codex/references/runtime-policy.json"
    fallback_policy = SKILLS_ROOT / "project-spec-architect/assets/runtime-policy.json"
    if not project_policy.exists():
        add(
            "medium",
            "runtime",
            "Project runtime policy copy is missing; audit used the Factory fallback.",
            [".codex/references/runtime-policy.json"],
        )
    try:
        policy = json.loads(
            (project_policy if project_policy.exists() else fallback_policy).read_text(
                encoding="utf-8-sig"
            )
        )
    except Exception as error:  # noqa: BLE001 - audit must convert parse failures to findings
        add(
            "high",
            "runtime",
            f"Runtime policy is invalid JSON: {error}",
            [rel(project_policy)],
        )
        policy = json.loads(fallback_policy.read_text(encoding="utf-8-sig"))
    gitignore = root / ".gitignore"
    runtime_root = root / ".harness/runtime"
    if runtime_root.exists() and (
        not gitignore.exists()
        or ".harness/runtime/"
        not in gitignore.read_text(encoding="utf-8-sig").splitlines()
    ):
        add(
            "medium",
            "runtime_state",
            "Temporary .harness/runtime state is not ignored by version control.",
            [".harness/runtime/", ".gitignore"],
        )

    project_specs_root = root / "specs"
    manifests = (
        [
            path
            for path in project_specs_root.rglob("*.execution.json")
            if not {
                ".git",
                "node_modules",
                ".venv",
                "venv",
                "__pycache__",
            }.intersection(path.parts)
        ]
        if project_specs_root.is_dir()
        else []
    )
    manifest_index: dict[tuple[str, int], tuple[Path, dict[str, Any]]] = {}
    for manifest_path in manifests:
        directory = manifest_path.parent
        spec_path = directory / "SPEC.md"
        if not spec_path.exists():
            add(
                "high",
                "spec",
                "Execution manifest has no sibling SPEC.md.",
                [rel(manifest_path)],
            )
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
            if isinstance(manifest.get("spec_id"), str) and isinstance(
                manifest.get("contract_version"), int
            ):
                manifest_index[(manifest["spec_id"], manifest["contract_version"])] = (
                    manifest_path,
                    manifest,
                )
            markdown = spec_path.read_text(encoding="utf-8-sig")
            errors = validate_spec_pair(
                markdown,
                manifest,
                policy,
                project_root=root,
                skills_root=skills_root,
                require_ready=manifest.get("status") == "ready",
            )
            for error in errors:
                add(
                    "high" if manifest.get("status") == "ready" else "medium",
                    "spec",
                    error,
                    [rel(spec_path), rel(manifest_path)],
                )
            version2 = manifest.get("schema_version") == "2.0"
            lifecycle = None
            review_evidence = None
            if version2 and manifest.get("status") not in {"draft", "design", "ready"}:
                lifecycle_path = (
                    root / manifest.get("lifecycle", {}).get("output_path", "")
                ).resolve()
                if not lifecycle_path.is_file():
                    add(
                        "high",
                        "lifecycle",
                        "Version 2 Spec has no durable lifecycle evidence.",
                        [rel(manifest_path), rel(lifecycle_path)],
                    )
                else:
                    lifecycle = json.loads(
                        lifecycle_path.read_text(encoding="utf-8-sig")
                    )
                    for error in validate_lifecycle(lifecycle, manifest):
                        add("high", "lifecycle", error, [rel(lifecycle_path)])
                    if lifecycle.get("spec_id") != manifest.get(
                        "spec_id"
                    ) or lifecycle.get("contract_version") != manifest.get(
                        "contract_version"
                    ):
                        add(
                            "high",
                            "lifecycle",
                            "Lifecycle identity/version differs from the Spec.",
                            [rel(lifecycle_path)],
                        )
                    if (
                        manifest.get("status") == "done"
                        and lifecycle.get("status") != "done"
                    ):
                        add(
                            "high",
                            "lifecycle",
                            "DONE Spec does not have a done durable lifecycle.",
                            [rel(lifecycle_path)],
                        )
                    for phase, slot in (
                        ("implementation", "implementation_thread_id"),
                        ("review", "review_thread_id"),
                    ):
                        ids = {
                            event.get("thread_id")
                            for event in lifecycle.get("events", [])
                            if event.get("phase") == phase
                        }
                        ids.discard(None)
                        if len(ids) > 1 or (ids and lifecycle.get(slot) not in ids):
                            add(
                                "high",
                                "lifecycle",
                                f"Lifecycle must preserve exactly one {slot}.",
                                [rel(lifecycle_path)],
                            )
            if manifest.get("status") in {
                "implemented",
                "review",
                "changes_requested",
                "done",
            }:
                completion_path = (
                    root / manifest.get("completion", {}).get("output_path", "")
                ).resolve()
                if not completion_path.exists():
                    add(
                        "high",
                        "completion",
                        f"{manifest.get('status')} Spec has no declared completion evidence.",
                        [rel(manifest_path), rel(completion_path)],
                    )
                else:
                    completion = json.loads(
                        completion_path.read_text(encoding="utf-8-sig")
                    )
                    baseline_snapshot = None
                    snapshot_value = manifest.get("baseline", {}).get("snapshot_path")
                    if (
                        version2
                        and snapshot_value
                        and (root / snapshot_value).is_file()
                    ):
                        baseline_snapshot = json.loads(
                            (root / snapshot_value).read_text(encoding="utf-8-sig")
                        )
                    for error in validate_completion(
                        completion,
                        manifest,
                        markdown,
                        completion.get("thread_id"),
                        project_root=root,
                        baseline_snapshot=baseline_snapshot,
                    ):
                        add("high", "completion", error, [rel(completion_path)])
                    if lifecycle and completion.get("thread_id") != lifecycle.get(
                        "implementation_thread_id"
                    ):
                        add(
                            "high",
                            "lifecycle",
                            "Completion thread differs from durable implementation_thread_id.",
                            [rel(completion_path), rel(lifecycle_path)],
                        )
            if manifest.get("status") == "done" and manifest.get("review", {}).get(
                "required"
            ):
                review_path = (
                    (root / manifest.get("review", {}).get("output_path", "")).resolve()
                    if version2
                    else directory / "evidence/review.json"
                )
                if not review_path.exists():
                    add(
                        "high",
                        "review",
                        "DONE Spec requires the declared independent review evidence.",
                        [rel(manifest_path), rel(review_path)],
                    )
                else:
                    review = json.loads(review_path.read_text(encoding="utf-8-sig"))
                    review_evidence = review
                    if version2:
                        for error in validate_review_evidence(
                            review, manifest, review.get("thread_id")
                        ):
                            add("high", "review", error, [rel(review_path)])
                    else:
                        if review.get("spec_id") != manifest.get(
                            "spec_id"
                        ) or review.get("contract_version") != manifest.get(
                            "contract_version"
                        ):
                            add(
                                "high",
                                "review",
                                "Review evidence does not match the Spec identity/version.",
                                [rel(review_path)],
                            )
                        if review.get("runtime", {}).get("model") != manifest[
                            "review"
                        ].get("model") or review.get("runtime", {}).get(
                            "reasoning"
                        ) != manifest["review"].get("reasoning"):
                            add(
                                "high",
                                "review",
                                "Review evidence runtime differs from the manifest review policy.",
                                [rel(review_path)],
                            )
                    if (
                        not review.get("thread_id")
                        or review.get("status") != "approved"
                    ):
                        add(
                            "high",
                            "review",
                            "DONE Spec does not have an approved review result and thread ID.",
                            [rel(review_path)],
                        )
                    if lifecycle and review.get("thread_id") != lifecycle.get(
                        "review_thread_id"
                    ):
                        add(
                            "high",
                            "lifecycle",
                            "Review thread differs from durable review_thread_id.",
                            [rel(review_path), rel(lifecycle_path)],
                        )
            if version2 and manifest.get("baseline", {}).get("required"):
                baseline_path = (root / manifest["baseline"]["path"]).resolve()
                if baseline_path.is_file():
                    baseline = json.loads(baseline_path.read_text(encoding="utf-8-sig"))
                    for error in validate_structural_baseline(baseline, manifest):
                        add("high", "baseline", error, [rel(baseline_path)])
                    baseline_count = baseline.get("tests", {}).get("count")
                    patterns = (
                        "test*.py",
                        "*.test.ts",
                        "*.test.tsx",
                        "*.spec.ts",
                        "*.spec.tsx",
                        "*.test.js",
                        "*.spec.js",
                    )
                    current_tests = sorted(
                        {
                            path
                            for pattern in patterns
                            for path in root.rglob(pattern)
                            if not {
                                ".git",
                                ".venv",
                                "venv",
                                "node_modules",
                                "__pycache__",
                            }.intersection(path.parts)
                        }
                    )
                    if (
                        isinstance(baseline_count, int)
                        and len(current_tests) < baseline_count
                    ):
                        add(
                            "high",
                            "baseline",
                            "Current regression test inventory is smaller than the structural baseline.",
                            [
                                rel(baseline_path),
                                *[rel(path) for path in current_tests],
                            ],
                        )
                    assessments = {
                        item.get("category"): item
                        for item in (review_evidence or {}).get(
                            "baseline_assessment", []
                        )
                        if isinstance(item, dict)
                    }

                    def audit_baseline_paths(
                        category: str,
                        paths: list[str],
                        *,
                        allow_approved_move: bool,
                        assessments: dict[str, Any] = assessments,
                        baseline_path: Path = baseline_path,
                    ) -> None:
                        missing = [path for path in paths if not (root / path).exists()]
                        if not missing:
                            return
                        assessment = assessments.get(category, {})
                        evidence_text = " ".join(
                            str(item) for item in assessment.get("evidence", [])
                        )
                        explicitly_moved = (
                            allow_approved_move
                            and assessment.get("result") == "changed_as_approved"
                            and all(path in evidence_text for path in missing)
                        )
                        if not explicitly_moved:
                            add(
                                "high",
                                "baseline",
                                f"Structural baseline {category} paths are missing without explicit approved migration evidence.",
                                [rel(baseline_path), *missing],
                            )

                    audit_baseline_paths(
                        "tests",
                        baseline.get("tests", {}).get("paths", []),
                        allow_approved_move=True,
                    )
                    for category in ("json_contracts", "persistence", "schemas"):
                        audit_baseline_paths(
                            category,
                            [
                                item.get("path", "")
                                for item in baseline.get(category, [])
                                if isinstance(item, dict)
                            ],
                            allow_approved_move=True,
                        )
                    audit_baseline_paths(
                        "protected_paths",
                        [
                            item.get("path", "")
                            for item in baseline.get("protected_paths", [])
                            if isinstance(item, dict)
                        ],
                        allow_approved_move=False,
                    )
                    audit_baseline_paths(
                        "decisions",
                        [
                            item.get("path", "")
                            for item in baseline.get("decisions", [])
                            if isinstance(item, dict)
                        ],
                        allow_approved_move=False,
                    )
        except Exception as error:  # noqa: BLE001 - one bad Spec must not abort the audit
            add(
                "high",
                "spec",
                f"Unable to parse or audit Spec: {error}",
                [rel(spec_path), rel(manifest_path)],
            )

    external_results = [Path(path).resolve() for path in (external_route_results or [])]
    for result_path in external_results:
        try:
            result_path.relative_to(root)
            add(
                "high",
                "economic_execution",
                "External execution route results must remain outside the project repository.",
                [rel(result_path)],
            )
            continue
        except ValueError:
            pass
        if not result_path.is_file():
            add(
                "high",
                "economic_execution",
                "Declared external execution route result does not exist.",
                [str(result_path)],
            )
            continue
        try:
            result = json.loads(result_path.read_text(encoding="utf-8-sig"))
            if result.get("executor") != "opencode":
                add(
                    "low",
                    "economic_execution",
                    "Route result did not execute OpenCode; no external implementation evidence was audited.",
                    [str(result_path)],
                )
                continue
            if result.get("route") != "opencode-completed":
                add(
                    "high",
                    "economic_execution",
                    "OpenCode route did not complete successfully and cannot support implementation approval.",
                    [str(result_path)],
                )
            if not result.get("request_fingerprint"):
                add(
                    "high",
                    "economic_execution",
                    "OpenCode route result has no external request fingerprint.",
                    [str(result_path)],
                )
            identity = (result.get("spec_id"), result.get("contract_version"))
            manifest_entry = manifest_index.get(identity)
            if manifest_entry is None:
                add(
                    "high",
                    "economic_execution",
                    "OpenCode route result does not match a project Spec identity/version.",
                    [str(result_path)],
                )
            elif (
                manifest_entry[1].get("review", {}).get("required") is not True
                or manifest_entry[1].get("review", {}).get("independence")
                != "independent"
            ):
                add(
                    "high",
                    "economic_execution",
                    "External execution requires independent review in the matching Spec manifest.",
                    [rel(manifest_entry[0]), str(result_path)],
                )
            else:
                review_path = manifest_entry[0].parent / "evidence/review.json"
                if not review_path.is_file():
                    add(
                        "high",
                        "economic_execution",
                        "Completed OpenCode execution has no independent Codex review receipt.",
                        [rel(manifest_entry[0]), rel(review_path), str(result_path)],
                    )
                else:
                    review = json.loads(review_path.read_text(encoding="utf-8-sig"))
                    if (
                        review.get("spec_id") != identity[0]
                        or review.get("contract_version") != identity[1]
                        or review.get("status") != "approved"
                        or not review.get("thread_id")
                    ):
                        add(
                            "high",
                            "economic_execution",
                            "Independent Codex review is not approved or does not match the external execution contract.",
                            [rel(review_path), str(result_path)],
                        )
                    review_inputs = " ".join(
                        str(item).lower() for item in review.get("review_input", [])
                    )
                    required_inputs = {
                        "route result": ("route-result", "route result"),
                        "completion evidence": ("completion",),
                        "snapshot diff": ("snapshot-diff", "snapshot diff", "diff"),
                        "router validations": (
                            "router-validations",
                            "router validations",
                            "validation",
                        ),
                    }
                    for label, terms in required_inputs.items():
                        if not any(term in review_inputs for term in terms):
                            add(
                                "high",
                                "economic_execution",
                                f"Independent Codex review does not declare {label} as an input.",
                                [rel(review_path), str(result_path)],
                            )
            scope = result.get("scope_integrity")
            if not isinstance(scope, dict) or scope.get("ok") is not True:
                add(
                    "high",
                    "economic_execution",
                    "OpenCode route did not preserve approved writable scope.",
                    [str(result_path)],
                )
            validations = result.get("independent_validations")
            if (
                not isinstance(validations, dict)
                or not validations
                or any(
                    not isinstance(item, dict) or item.get("result") != "passed"
                    for item in validations.values()
                )
            ):
                add(
                    "high",
                    "economic_execution",
                    "Router-run independent validations are missing or not all passing.",
                    [str(result_path)],
                )
            artifacts = (
                result.get("artifacts")
                if isinstance(result.get("artifacts"), dict)
                else {}
            )
            required_artifacts = (
                "request_receipt",
                "completion",
                "snapshot_before",
                "snapshot_after",
                "snapshot_diff",
                "router_validations",
            )
            for name in required_artifacts:
                artifact = Path(str(artifacts.get(name, "")))
                if not artifacts.get(name) or not artifact.is_file():
                    add(
                        "high",
                        "economic_execution",
                        f"OpenCode route artifact is missing: {name}.",
                        [str(result_path), str(artifact)],
                    )
            if all(
                artifacts.get(name) and Path(str(artifacts[name])).is_file()
                for name in ("completion", "snapshot_diff")
            ):
                completion = json.loads(
                    Path(str(artifacts["completion"])).read_text(encoding="utf-8-sig")
                )
                snapshot_diff = json.loads(
                    Path(str(artifacts["snapshot_diff"])).read_text(
                        encoding="utf-8-sig"
                    )
                )
                changed = set(result.get("changed_files", []))
                if changed != set(
                    completion.get("changed_files", [])
                ) or changed != set(snapshot_diff.get("changed", [])):
                    add(
                        "high",
                        "economic_execution",
                        "Changed files differ across route result, completion evidence, and snapshot diff.",
                        [
                            str(result_path),
                            str(artifacts["completion"]),
                            str(artifacts["snapshot_diff"]),
                        ],
                    )
        except Exception as error:  # noqa: BLE001 - external receipts are untrusted input
            add(
                "high",
                "economic_execution",
                f"Unable to parse or audit external execution result: {error}",
                [str(result_path)],
            )

    local_skills_root = root / ".agents/skills"
    local_skill_dirs = (
        sorted(path for path in local_skills_root.iterdir() if path.is_dir())
        if local_skills_root.exists()
        else []
    )
    for directory in local_skill_dirs:
        for error in validate_project_skill(directory, project_root=root):
            add(
                "high" if "missing" in error else "medium",
                "skill",
                error,
                [rel(directory)],
            )

    counts = {
        severity: sum(item["severity"] == severity for item in findings)
        for severity in ("high", "medium", "low")
    }
    counts.update(
        {
            "specs": len(manifests),
            "local_skills": len(local_skill_dirs),
            "external_execution_results": len(external_results),
        }
    )
    status = (
        "blocked"
        if counts["high"]
        else "corrections_required"
        if counts["medium"]
        else "approved_with_notes"
        if counts["low"]
        else "approved"
    )
    return {
        "status": status,
        "project_root": str(root),
        "findings": findings,
        "summary": counts,
        "unassessed": [
            "Semantic docs-to-reality drift requires domain inspection.",
            "Chat-only knowledge cannot be detected unless relevant chat evidence is supplied.",
            "Runtime cost and latency suitability require observed usage/evaluation data.",
            "Parallel-write safety requires branch/worktree and execution evidence when parallelism was used.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--skills-root")
    parser.add_argument("--external-route-result", action="append", default=[])
    args = parser.parse_args()
    report = audit_project_harness(
        args.project_root,
        skills_root=args.skills_root,
        external_route_results=args.external_route_result,
    )
    print(json.dumps(report, indent=2))
    return 1 if report["status"] in {"blocked", "corrections_required"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
