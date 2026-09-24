"""Maintain and inspect a project's explicit navigation map; review is always deliberate."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from _harness_plan_core import load_plan, validate_harness_plan
from _project_map import HTML_PATH, LEGACY_PATH, MAP_PATH, TOOL_PATH, atomic_write, check_map, load_map, local_path, map_from_plan, render_html, resource, review_map

MANAGED_START = "<!-- karya-project-map:start -->"
MANAGED_END = "<!-- karya-project-map:end -->"
GUIDANCE = f"""{MANAGED_START}
## Project navigation map

Use `{MAP_PATH}` as the current navigation index. Existing Markdown navigation remains a preserved source, not a competing generated map.
Before changes, run `python {TOOL_PATH} check --project-root .`, query relevant nodes, and read their original sources and applicable contracts. A pending check calls for reconciliation, not blind refresh; source reading and required tests remain mandatory.
Before completion, inspect changed code and docs, update affected sources, paths and explicit relations, then run `python {TOOL_PATH} review --project-root . --note "Explain source/map reconciliation and any unchanged-map decision"`. Run `check` again. For a chosen Spec, include the check in its required validation. Never run review automatically just to make a check pass.
Use `query --project-root . --text "topic"` for bounded navigation. When the user wants to see the map, run `render --project-root .` and show `.harness/views/project-map.html`; regenerate after changes. HTML is a read-only snapshot, not an editor or source of truth.
{MANAGED_END}
"""


def install_kit(root: Path, *, dry_run: bool = False) -> dict:
    """Copy a self-contained maintenance kit only where files are missing."""
    scripts = Path(__file__).resolve().parent
    files = {name: scripts / name for name in ("project_map.py", "_project_map.py", "_harness_plan_core.py")}
    files.update({name: resource(name) for name in ("project-map.schema.json", "project-map.html", "karya-icon.png")})
    result = {"created": [], "preserved": []}
    for name, source in files.items():
        relative = "scripts/harness/" + name
        target = local_path(root, relative)
        result["preserved" if target.exists() else "created"].append(relative)
        if not target.exists() and not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    return result


def initialize(root: Path, plan: dict, *, dry_run: bool = False, migrate: bool = False) -> dict:
    """Initialize JSON navigation, optionally adopting an existing project's instructions."""
    errors = validate_harness_plan(plan, require_accepted=True)
    if errors:
        raise ValueError("; ".join(errors))
    # Validate plan-derived paths before installing or changing anything.
    data = map_from_plan(root, plan)
    archive_relative = ".codex/decisions/project-harness-bootstrap.json"
    archive = local_path(root, archive_relative)
    for node in data["nodes"]:
        if node["path"] == archive_relative:
            node["status"] = "existing"  # The operation below creates or preserves this input.
    from _project_map import validate_map
    errors = validate_map(root, data, check_paths=False)
    if errors:
        raise ValueError("; ".join(errors))
    agents = None
    existing = updated = ""
    if migrate:
        agents = local_path(root, "AGENTS.md")
        existing = agents.read_text(encoding="utf-8-sig") if agents.exists() else "# Project agent guidance\n"
        if MANAGED_START in existing or MANAGED_END in existing:
            if existing.count(MANAGED_START) != 1 or existing.count(MANAGED_END) != 1 or existing.index(MANAGED_START) > existing.index(MANAGED_END):
                raise ValueError("Malformed managed AGENTS block; reconcile it manually.")
            before, rest = existing.split(MANAGED_START, 1)
            _, after = rest.split(MANAGED_END, 1)
            updated = before + GUIDANCE.rstrip() + after
        else:
            updated = existing.rstrip() + "\n\n" + GUIDANCE
    target = local_path(root, MAP_PATH)
    if target.exists() and not target.is_file():
        raise ValueError("Existing navigation map is not a file")
    if not target.exists() and archive.exists() and load_plan(archive) != plan:
        raise ValueError("The supplied plan differs from the preserved bootstrap archive. Seed navigation from that accepted archive, then reconcile current facts in the JSON map; historical input will not be overwritten.")
    result = install_kit(root, dry_run=dry_run)
    result["preserved" if archive.exists() else "created"].append(archive_relative)
    if not archive.exists() and not dry_run:
        atomic_write(archive, json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
    if target.exists():
        result["preserved"].append(MAP_PATH)
    else:
        result["created"].append(MAP_PATH)
        if not dry_run:
            atomic_write(target, json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    if migrate:
        result["agents_updated"] = existing != updated
        if existing != updated and not dry_run:
            atomic_write(agents, updated)
    result.update({"status": "preview" if dry_run else "initialized", "map": MAP_PATH, "next": "Reconcile planned/existing targets and relations, then run review with a source-based note and check."})
    return result


def main() -> int:
    """Expose explicit init/migrate, read-only check/query/render and review commands."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("init", "migrate", "check", "review", "query", "render"))
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--plan")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--note", default="")
    parser.add_argument("--text", default="")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    root = Path(args.project_root).resolve()
    try:
        if args.command in {"init", "migrate"}:
            if not args.plan:
                raise ValueError("init/migrate require --plan pointing to an accepted Harness plan")
            result = initialize(root, load_plan(args.plan), dry_run=args.dry_run, migrate=args.command == "migrate")
        else:
            if args.dry_run:
                raise ValueError("--dry-run is supported only for init/migrate")
            data = load_map(root)
            if args.command == "review":
                reviewed = review_map(root, data, args.note)
                atomic_write(local_path(root, MAP_PATH), json.dumps(reviewed, ensure_ascii=False, indent=2) + "\n")
                result = check_map(root, reviewed)
                result["semantic_review"] = "Executor attestation recorded; independent correctness is not established by this command."
            elif args.command == "render":
                report = check_map(root, data)
                atomic_write(local_path(root, HTML_PATH), render_html(root, data))
                result = {"status": report["status"], "output": str(root / HTML_PATH), "pending": report["pending"]}
            elif args.command == "query":
                report = check_map(root, data)
                if report["errors"]:
                    raise ValueError("; ".join(report["errors"]))
                if not 1 <= args.limit <= 200:
                    raise ValueError("--limit must be between 1 and 200")
                terms = args.text.casefold().split()
                areas = data.get("navigation", {}).get("areas", [])
                area_labels = {node["id"]: " ".join(area["label"] for area in areas if node["id"] in area["members"]) for node in data["nodes"]}
                matches = [node for node in data["nodes"] if all(term in (node["id"] + " " + node["label"] + " " + node["path"] + " " + node["summary"] + " " + area_labels[node["id"]]).casefold() for term in terms)]
                selected = matches[:args.limit]
                ids = {node["id"] for node in selected}
                result = {"status": report["status"], "pending": report["pending"], "total_matches": len(matches), "nodes": selected, "relations": [edge for edge in data["relations"] if edge["from"] in ids or edge["to"] in ids][:args.limit * 5]}
                if areas:
                    result["areas"] = [{**area, "members": [member for member in area["members"] if member in ids]} for area in areas if ids.intersection(area["members"])]
            else:
                result = check_map(root, data)
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 1 if args.command in {"check", "review"} and result["status"] != "current" else 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({"status": "invalid", "errors": [str(error)]}, ensure_ascii=True, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
