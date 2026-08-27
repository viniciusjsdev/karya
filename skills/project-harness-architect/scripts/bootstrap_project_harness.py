"""Materialize only missing Project Harness starter files from an accepted plan."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from _harness_plan_core import load_plan, validate_harness_plan


def _inside(parent: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    project_root = Path(args.project_root).resolve()
    plan_path = Path(args.plan).resolve()
    skill_root = Path(__file__).resolve().parent.parent
    starter_root = skill_root / "assets" / "project-harness-starter"
    spec_assets = skill_root.parent / "project-spec-architect" / "assets"
    plan = load_plan(plan_path)
    errors = validate_harness_plan(plan, require_accepted=True)
    if errors:
        print(json.dumps({"status": "blocked", "errors": errors}, indent=2))
        return 1
    for required in (starter_root, spec_assets):
        if not required.exists():
            raise FileNotFoundError(f"Required sibling Factory resource not found: {required}")
        if _inside(required, project_root):
            raise ValueError("Project root must not be a bundled skill asset or descendant")
    if project_root.exists() and not project_root.is_dir():
        raise ValueError(f"Project root is not a directory: {project_root}")

    created: list[str] = []
    preserved: list[str] = []

    def copy_missing(source: Path, target: Path) -> None:
        relative = target.relative_to(project_root).as_posix()
        if target.exists():
            preserved.append(relative)
            return
        created.append(relative)
        if not args.dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)

    for source in sorted(starter_root.rglob("*")):
        if source.is_file():
            copy_missing(source, project_root / source.relative_to(starter_root))
    for source_name, target_relative in (
        ("runtime-policy.json", ".codex/references/runtime-policy.json"),
        ("spec-execution.schema.json", ".codex/schemas/project-spec-execution.schema.json"),
        ("completion.schema.json", ".codex/schemas/project-spec-completion.schema.json"),
        ("review-evidence.schema.json", ".codex/schemas/project-spec-review.schema.json"),
        ("SPEC.template.md", ".codex/templates/project-spec.md"),
        ("SPEC.execution.template.json", ".codex/templates/project-spec.execution.json"),
    ):
        copy_missing(spec_assets / source_name, project_root / target_relative)
    copy_missing(plan_path, project_root / ".codex/decisions/project-harness-bootstrap.json")

    warnings: list[str] = []
    gitignore = project_root / ".gitignore"
    if gitignore.exists() and ".harness/runtime/" not in gitignore.read_text(encoding="utf-8-sig").splitlines():
        warnings.append("Existing .gitignore was preserved; add .harness/runtime/ after review.")
    print(json.dumps({"status": "preview" if args.dry_run else "initialized", "project_root": str(project_root), "created": created, "preserved": preserved, "warnings": warnings}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
