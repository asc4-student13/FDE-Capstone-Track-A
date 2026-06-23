"""Data loader functions for procurement mock datasets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_MOCK_DATA_DIR = _PROJECT_ROOT / "mock_data"


def load_budgets() -> list[dict[str, Any]]:
    """Load budget records from the mock data source."""
    file_path = _MOCK_DATA_DIR / "budgets.json"
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_vendors() -> list[dict[str, Any]]:
    """Load vendor records from the mock data source."""
    file_path = _MOCK_DATA_DIR / "vendors.json"
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_policies() -> list[dict[str, Any]]:
    """Load policy records from the mock data source."""
    file_path = _MOCK_DATA_DIR / "policies.json"
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_requests() -> list[dict[str, Any]]:
    """Load purchase request records from the mock data source."""
    file_path = _MOCK_DATA_DIR / "requests.json"
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)
