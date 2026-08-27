"""Verify the pinned official Python Codex SDK without starting a live thread."""

from __future__ import annotations

import inspect
import json
import sys


def main() -> int:
    try:
        import openai_codex
        from openai_codex import Codex, Thread
        required = "0.147.0"
        python_supported = sys.version_info >= (3, 12)
        thread_start = "thread_start" in dir(Codex)
        thread_resume = "thread_resume" in dir(Codex)
        output_schema = "output_schema" in inspect.signature(Thread.run).parameters
        ready = python_supported and openai_codex.__version__ == required and thread_start and thread_resume and output_schema
        print(json.dumps({"ready": ready, "python": sys.version.split()[0], "python_supported": python_supported, "sdk": "openai-codex", "installed_version": openai_codex.__version__, "required_version": required, "thread_start": thread_start, "thread_resume": thread_resume, "output_schema": output_schema}, indent=2))
        return 0 if ready else 1
    except Exception as error:
        print(json.dumps({"ready": False, "python": sys.version.split()[0], "sdk": "openai-codex", "required_version": "0.147.0", "error": str(error), "remedy": "Install requirements.txt in an isolated Python 3.12+ environment."}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
