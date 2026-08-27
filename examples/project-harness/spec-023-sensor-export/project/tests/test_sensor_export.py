"""Contract tests for SPEC-023 and ADR-004 deterministic sensor export."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from sensor_export import export_normalized_samples  # noqa: E402

SAMPLES = [
    {"timestamp": "2026-08-26T10:00:00Z", "value": 21.5, "unit": "C", "source": "sensor-b"},
    {"timestamp": "2026-08-26T09:00:00Z", "value": 20, "unit": "C", "source": "sensor-a"},
    {"timestamp": "2026-08-26T10:00:00Z", "value": 21.4, "unit": "C", "source": "sensor-c"},
]


def test_export_matches_approved_fixture() -> None:
    fixture = (Path(__file__).parent / "fixtures/sensor-export.json").read_text(encoding="utf-8")
    assert export_normalized_samples(SAMPLES) == fixture


def test_equal_timestamps_preserve_input_order() -> None:
    equal_timestamp_sources = [item["source"] for item in json.loads(export_normalized_samples(SAMPLES)) if item["timestamp"] == "2026-08-26T10:00:00Z"]
    assert equal_timestamp_sources == ["sensor-b", "sensor-c"]
