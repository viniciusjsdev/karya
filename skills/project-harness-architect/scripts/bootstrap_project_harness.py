"""Materialize only missing Project Harness starter files from an accepted plan."""

from __future__ import annotations

import argparse
import html
import json
import shutil
from pathlib import Path

from _harness_plan_core import load_plan, validate_harness_plan
from _project_map import MAP_PATH
from project_map import initialize, install_kit


NAVIGATION_PATH = ".codex/references/project-harness.md"
RUNTIME_POLICY_PATH = ".codex/references/runtime-policy.json"


def _navigation_value(value: object) -> str:
    """Keep plan values readable without breaking Markdown tables or adding HTML."""
    text = json.dumps(value, ensure_ascii=False, sort_keys=True) if isinstance(value, (dict, list)) else str(value)
    return html.escape(text).replace("|", "&#124;").replace("`", "&#96;").replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>")


def render_project_harness_navigation(plan: dict) -> str:
    """Render accepted-plan navigation, without claiming sources exist or checks ran."""
    lines = [
        "# Project Harness navigation", "",
        "Generated from the accepted Harness plan supplied to bootstrap. Paths below are relative to the project root unless explicitly external.", "",
        "This is a navigation index, not domain truth or execution evidence. Read the original sources. Entries describe the plan; existence and completion are not verified here. Bootstrap preserves this file on subsequent runs.", "",
    ]

    def table(title: str, columns: tuple[str, ...], rows: list[tuple]) -> None:
        lines.extend([f"## {title}", ""])
        if rows:
            lines.extend(["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"])
            lines.extend("| " + " | ".join(_navigation_value(value) for value in row) + " |" for row in rows)
        else:
            lines.append("None declared in the accepted plan.")
        lines.append("")

    table("Sources of truth", ("Path", "Kind", "Authority", "Planned action"), [
        (item["path"], item["kind"], item["authority"], item["action"])
        for item in plan["sources_of_truth"]
    ])
    table("Path mappings", ("Generic role", "Existing path"), [
        (item["generic_role"], item["existing_path"])
        for item in plan["documentation"]["path_mappings"]
    ])
    table("Planned documentation additions", ("Path", "Purpose"), [
        (item["path"], item["purpose"]) for item in plan["documentation"]["create"]
    ])
    lines.extend(["## Decisions", "", f"- Durable path: {_navigation_value(plan['decisions']['durable_path'])}"])
    open_decisions = plan["decisions"]["open"]
    if open_decisions:
        lines.append("- Open decisions declared at bootstrap:")
        lines.extend(f"  - {_navigation_value(item)}" for item in open_decisions)
    else:
        lines.append("- No open decisions declared in the accepted plan.")
    lines.append("")
    table("Workflows", ("Name", "Path", "Planned action"), [
        (item["name"], item["path"], item["action"]) for item in plan["workflows"]
    ])
    strategy = plan["spec_strategy"]
    lines.extend([
        "## Specs", "",
        f"- Root: {_navigation_value(strategy['root'])}",
        f"- Active Spec path pattern (not a selected active Spec): {_navigation_value(strategy['active_pattern'])}",
        f"- Human intent filename: {_navigation_value(strategy['markdown_name'])}",
        f"- Execution manifest filename: {_navigation_value(strategy['execution_name'])}", "",
    ])
    table("Validation", ("ID", "Declared command (not executed by bootstrap)", "Required"), [
        (item["id"], item["command"], "yes" if item["required"] else "no")
        for item in plan["validation"]
    ])
    policy = plan["runtime_policy"]
    lines.extend([
        "## Runtime", "",
        f"- Policy path declared in the plan: {_navigation_value(policy['project_path'])}",
        f"- Policy version declared in the plan: {_navigation_value(policy['policy_version'])}",
        f"- Bootstrap policy destination (existing files are preserved): {RUNTIME_POLICY_PATH}",
    ])
    if policy["project_path"] != RUNTIME_POLICY_PATH:
        lines.append("- Path mismatch: reconcile the declared policy path with the bootstrap destination before execution; bootstrap does not copy a policy to the alternate path.")
    return "\n".join(lines) + "\n"


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
    legacy_mode = (project_root / NAVIGATION_PATH).is_file() and not (project_root / MAP_PATH).exists()
    for required in (starter_root, spec_assets):
        if not required.exists():
            raise FileNotFoundError(f"Required sibling Factory resource not found: {required}")
        if _inside(required, project_root):
            raise ValueError("Project root must not be a bundled skill asset or descendant")
    if project_root.exists() and not project_root.is_dir():
        raise ValueError(f"Project root is not a directory: {project_root}")
    if not legacy_mode:
        # Check new map paths/provenance before any starter writes.
        initialize(project_root, plan, dry_run=True)

    created: list[str] = []
    preserved: list[str] = []

    def copy_missing(source: Path, target: Path, content: str | None = None) -> None:
        relative = target.relative_to(project_root).as_posix()
        if target.exists():
            preserved.append(relative)
            return
        created.append(relative)
        if not args.dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            if content is None:
                shutil.copyfile(source, target)
            else:
                target.write_text(content, encoding="utf-8")

    for source in sorted(starter_root.rglob("*")):
        # Generate plan-specific navigation instead of copying the generic starter.
        if source.is_file() and source.relative_to(starter_root).as_posix() != NAVIGATION_PATH:
            content = None
            if legacy_mode and source.relative_to(starter_root).as_posix() == "AGENTS.md":
                lines = source.read_text(encoding="utf-8").splitlines()
                lines = [line for line in lines if MAP_PATH not in line and "project_map.py" not in line]
                lines.insert(3, f"- Use `{NAVIGATION_PATH}` to locate original sources, decisions, workflows, Specs and validation. Review affected sources and navigation with every change.")
                content = "\n".join(lines) + "\n"
            copy_missing(source, project_root / source.relative_to(starter_root), content)
    for source_name, target_relative in (
        ("runtime-policy.json", RUNTIME_POLICY_PATH),
        ("spec-execution.schema.json", ".codex/schemas/project-spec-execution.schema.json"),
        ("completion.schema.json", ".codex/schemas/project-spec-completion.schema.json"),
        ("review-evidence.schema.json", ".codex/schemas/project-spec-review.schema.json"),
        ("SPEC.template.md", ".codex/templates/project-spec.md"),
        ("SPEC.execution.template.json", ".codex/templates/project-spec.execution.json"),
    ):
        copy_missing(spec_assets / source_name, project_root / target_relative)
    copy_missing(plan_path, project_root / ".codex/decisions/project-harness-bootstrap.json")

    if legacy_mode:
        preserved.append(NAVIGATION_PATH)
        kit = install_kit(project_root, dry_run=args.dry_run)
    else:
        kit = initialize(project_root, plan, dry_run=args.dry_run)
    created.extend(kit["created"])
    preserved.extend(kit["preserved"])
    created = list(dict.fromkeys(created))
    preserved = [path for path in dict.fromkeys(preserved) if path not in created]

    warnings: list[str] = []
    if legacy_mode:
        warnings.append("Legacy Markdown navigation preserved. Use project_map.py migrate with an accepted plan to adopt JSON explicitly.")
    else:
        warnings.append("JSON map requires source/relationship review before its initial check can pass; review never runs automatically.")
    if plan["runtime_policy"]["project_path"] != RUNTIME_POLICY_PATH:
        warnings.append("Declared runtime policy path differs from the bootstrap destination; reconcile paths before execution.")
    gitignore = project_root / ".gitignore"
    if gitignore.exists() and ".harness/runtime/" not in gitignore.read_text(encoding="utf-8-sig").splitlines():
        warnings.append("Existing .gitignore was preserved; add .harness/runtime/ after review.")
    print(json.dumps({"status": "preview" if args.dry_run else "initialized", "project_root": str(project_root), "created": created, "preserved": preserved, "warnings": warnings}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
