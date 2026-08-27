"""CLI validator for Project Harness SPEC.md and SPEC.execution.json pairs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _spec_core import load_json, validate_spec_pair


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec")
    parser.add_argument("manifest")
    parser.add_argument("--project-root")
    parser.add_argument("--policy")
    parser.add_argument("--skills-root")
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()
    script_dir = Path(__file__).resolve().parent
    policy_path = Path(args.policy).resolve() if args.policy else script_dir.parent / "assets" / "runtime-policy.json"
    markdown = Path(args.spec).read_text(encoding="utf-8-sig")
    manifest = load_json(args.manifest)
    policy = load_json(policy_path)
    errors = validate_spec_pair(markdown, manifest, policy, project_root=args.project_root, skills_root=args.skills_root, require_ready=args.require_ready)
    print(json.dumps({"valid": not errors, "spec": str(Path(args.spec).resolve()), "manifest": str(Path(args.manifest).resolve()), "errors": errors}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
