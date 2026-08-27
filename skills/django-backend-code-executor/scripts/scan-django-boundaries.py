#!/usr/bin/env python3
"""Run the strict Karya Django boundary scan.

This file intentionally mirrors the architect skill scanner so the executor skill
remains independently installable.
"""

from __future__ import annotations

import runpy
from pathlib import Path


LOCAL_SCANNER = Path(__file__).with_name("_boundary_scanner.py")

if __name__ == "__main__":
    runpy.run_path(str(LOCAL_SCANNER), run_name="__main__")
