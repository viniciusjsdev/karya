"""Build the SPEC-023 public deterministic JSON export without mutating samples."""

from __future__ import annotations

import json
from typing import Any


def export_normalized_samples(samples: list[dict[str, Any]]) -> str:
    """Validate public fields and stably order records by timestamp then input order."""
    records: list[tuple[int, dict[str, Any]]] = []
    for input_order, sample in enumerate(samples):
        for field in ("timestamp", "value", "unit", "source"):
            if field not in sample or sample[field] is None:
                raise ValueError(f"sample is missing {field}")
        records.append((input_order, {field: sample[field] for field in ("timestamp", "value", "unit", "source")}))
    records.sort(key=lambda item: (item[1]["timestamp"], item[0]))
    return json.dumps([record for _order, record in records], indent=2, ensure_ascii=False) + "\n"
