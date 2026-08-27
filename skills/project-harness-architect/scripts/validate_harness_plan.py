"""CLI for deterministic Project Harness plan validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _harness_plan_core import load_plan, validate_harness_plan


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("plan")
    parser.add_argument("--require-accepted", action="store_true")
    args = parser.parse_args()
    errors = validate_harness_plan(load_plan(args.plan), require_accepted=args.require_accepted)
    print(json.dumps({"valid": not errors, "plan": str(Path(args.plan).resolve()), "errors": errors}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
