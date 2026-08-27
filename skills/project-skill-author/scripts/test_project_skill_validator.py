"""Tests for generic project-local Skill validation."""

from pathlib import Path

from validate_project_skill import validate_project_skill


def test_accepts_complete_skill_and_rejects_missing_invariant(tmp_path: Path) -> None:
    skill_dir = tmp_path / ".agents" / "skills" / "normalize-samples"
    (skill_dir / "agents").mkdir(parents=True)
    skill = """---
name: normalize-samples
description: Normalize approved sensor samples. Use when repeated laboratory imports need the documented normalization procedure. Do not use for methodology design or one-time data repair.
---

# Normalize Samples

## Required Context
Read the approved protocol.

## Workflow
Apply the repeatable sequence.

## Invariants
Preserve raw data.

## Validation
Compare the fixture checksum.

## Boundaries
Do not alter methodology.
"""
    (skill_dir / "SKILL.md").write_text(skill, encoding="utf-8")
    (skill_dir / "agents" / "openai.yaml").write_text("interface:\n  display_name: Normalize Samples\n  short_description: Normalize samples\n", encoding="utf-8")
    assert validate_project_skill(skill_dir, project_root=tmp_path) == []
    (skill_dir / "SKILL.md").write_text(skill.replace("## Invariants", "## TODO"), encoding="utf-8")
    assert any("Invariants" in item for item in validate_project_skill(skill_dir, project_root=tmp_path))
