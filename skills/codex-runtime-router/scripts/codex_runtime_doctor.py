"""Verify the pinned official Python Codex SDK without starting a live thread."""

from __future__ import annotations

import argparse
import inspect
import json
import os
import sys
from pathlib import Path

SPEC_SCRIPTS = (
    Path(__file__).resolve().parents[2] / "project-spec-architect" / "scripts"
)
if str(SPEC_SCRIPTS) not in os.sys.path:
    os.sys.path.insert(0, str(SPEC_SCRIPTS))
from _structured_output_schema import validate_structured_output_schema  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema", action="append", default=[])
    parser.add_argument("--schema-only", action="store_true")
    args = parser.parse_args()
    schema_errors: list[str] = []
    for value in args.schema:
        path = Path(value).resolve()
        try:
            schema = json.loads(path.read_text(encoding="utf-8-sig"))
            schema_errors.extend(
                f"{path}: {error}"
                for error in validate_structured_output_schema(schema)
            )
        except Exception as error:
            schema_errors.append(f"{path}: {error}")
    if args.schema_only:
        print(
            json.dumps(
                {
                    "ready": not schema_errors,
                    "schemas": args.schema,
                    "schema_errors": schema_errors,
                },
                indent=2,
            )
        )
        return 0 if not schema_errors else 1
    try:
        import openai_codex
        from openai_codex import Codex, Thread

        required = "0.147.0"
        python_supported = sys.version_info >= (3, 12)
        thread_start = "thread_start" in dir(Codex)
        thread_resume = "thread_resume" in dir(Codex)
        output_schema = "output_schema" in inspect.signature(Thread.run).parameters
        ready = (
            python_supported
            and openai_codex.__version__ == required
            and thread_start
            and thread_resume
            and output_schema
            and not schema_errors
        )
        print(
            json.dumps(
                {
                    "ready": ready,
                    "python": sys.version.split()[0],
                    "python_supported": python_supported,
                    "sdk": "openai-codex",
                    "installed_version": openai_codex.__version__,
                    "required_version": required,
                    "thread_start": thread_start,
                    "thread_resume": thread_resume,
                    "output_schema": output_schema,
                    "schema_errors": schema_errors,
                },
                indent=2,
            )
        )
        return 0 if ready else 1
    except Exception as error:
        print(
            json.dumps(
                {
                    "ready": False,
                    "python": sys.version.split()[0],
                    "sdk": "openai-codex",
                    "required_version": "0.147.0",
                    "error": str(error),
                    "remedy": "Install requirements.txt in an isolated Python 3.12+ environment.",
                },
                indent=2,
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
