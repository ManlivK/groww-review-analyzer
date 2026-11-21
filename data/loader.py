"""Load report data from a local JSON file, falling back to sample data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from data.sample_data import SAMPLE_DATA

DEFAULT_REPORT_PATH = Path(__file__).with_name("report.json")


def load_report_data(path: str | Path | None = None) -> dict[str, Any]:
    """Return report data as a dictionary.

    If *path* exists it is parsed as JSON. Otherwise the built-in illustrative
    sample data is returned. The returned structure is identical in both cases,
    so UI components do not need to change when real data is added.
    """
    report_path = Path(path) if path is not None else DEFAULT_REPORT_PATH

    if report_path.is_file():
        with report_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            raise ValueError("Report JSON must contain an object at the top level.")
        return data

    return SAMPLE_DATA


def is_sample_data(data: dict[str, Any]) -> bool:
    """Convenience helper for the UI to decide which labels to display."""
    return bool(data.get("meta", {}).get("is_sample", False))
