"""Report sanitized OpenCode readiness for one external Karya execution request."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _execution_core import inspect_opencode, load_json, validate_request


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    args = parser.parse_args()
    request_path = Path(args.request).resolve()
    skill_root = Path(__file__).resolve().parent.parent
    try:
        request = load_json(request_path)
        preflight = validate_request(request, request_path, skill_root)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"ready": False, "errors": [str(error)]}, ensure_ascii=False))
        return 2
    if not preflight["ok"]:
        print(json.dumps({"ready": False, "errors": preflight["errors"]}, ensure_ascii=False))
        return 2
    readiness = inspect_opencode(request["provider"], request["model"], request["provider_kind"])
    print(json.dumps({
        "ready": readiness["ready"],
        "provider": request["provider"],
        "model": request["model"],
        "provider_kind": request["provider_kind"],
        "billing_mode": request["billing_mode"],
        "checks": {key: readiness[key] for key in ("cli", "authenticated", "model_available")},
        "reasons": readiness["reasons"],
    }, ensure_ascii=False))
    return 0 if readiness["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
