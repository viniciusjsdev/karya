"""Validate a project-local Skill's placement, metadata, boundaries, and links."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def _frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\s*\r?\n([\s\S]*?)\r?\n---(?:\s*\r?\n|$)", text.lstrip("\ufeff"))
    result: dict[str, str] = {}
    if match:
        for line in re.split(r"\r?\n", match.group(1)):
            item = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*?)\s*$", line)
            if item:
                result[item.group(1)] = item.group(2).strip("\"'")
    return result


def validate_project_skill(skill_dir: str | Path, *, project_root: str | Path | None = None, allow_any_path: bool = False) -> list[str]:
    """Return all deterministic project-local Skill validation errors."""
    directory = Path(skill_dir).resolve()
    root = Path(project_root).resolve() if project_root else directory.parents[2]
    errors: list[str] = []
    skill_path = directory / "SKILL.md"
    yaml_path = directory / "agents" / "openai.yaml"
    if not skill_path.exists():
        errors.append("SKILL.md is missing")
    if not yaml_path.exists():
        errors.append("agents/openai.yaml is missing")
    if not allow_any_path:
        expected = root / ".agents" / "skills"
        try:
            relative = directory.relative_to(expected)
            if not relative.parts:
                errors.append("project-local skill must be under .agents/skills/<skill-name>")
        except ValueError:
            errors.append("project-local skill must be under .agents/skills/<skill-name>")
    if skill_path.exists():
        text = skill_path.read_text(encoding="utf-8-sig")
        frontmatter = _frontmatter(text)
        name = frontmatter.get("name", "")
        if name != directory.name:
            errors.append("frontmatter name must match the skill folder")
        if not re.fullmatch(r"[a-z0-9-]+", name) or len(name) > 64:
            errors.append("skill name must be lowercase hyphen-case and at most 64 characters")
        description = frontmatter.get("description", "")
        if not description or not re.search(r"\bUse when\b", description, re.IGNORECASE) or not re.search(r"\bDo not use\b", description, re.IGNORECASE):
            errors.append("description must include discriminating Use when and Do not use boundaries")
        for heading in ("Required Context", "Workflow", "Invariants", "Validation", "Boundaries"):
            if not re.search(rf"^## {re.escape(heading)}$", text, re.IGNORECASE | re.MULTILINE):
                errors.append(f"SKILL.md is missing ## {heading}")
        if re.search(r"(?:\bTBD\b|\bTODO\b|\{\{|<[^>]+>|replace[_ -]?me)", text, re.IGNORECASE):
            errors.append("SKILL.md contains unresolved placeholder text")
        if re.search(r"\b(password|api[_ -]?key|secret|cookie|recovery code)\s*[:=]\s*\S+", text, re.IGNORECASE):
            errors.append("SKILL.md appears to contain credential material")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if re.match(r"^(?:https?:|#)", target):
                continue
            if not (directory / target.split("#", 1)[0]).resolve().exists():
                errors.append(f"linked local reference does not exist: {target}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("skill_dir")
    parser.add_argument("--project-root")
    parser.add_argument("--allow-any-path", action="store_true")
    args = parser.parse_args()
    errors = validate_project_skill(args.skill_dir, project_root=args.project_root, allow_any_path=args.allow_any_path)
    print(json.dumps({"valid": not errors, "skill": str(Path(args.skill_dir).resolve()), "errors": errors}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
