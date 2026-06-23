"""Load procurement mock data files from the project root."""

from __future__ import annotations

import json
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_MOCK_DATA_DIR = _PROJECT_ROOT / "mock_data"


def _load_json_list(filename: str) -> list[object]:
    """Read a JSON file from mock_data and return its top-level list."""
    file_path = _MOCK_DATA_DIR / filename
    with file_path.open("r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def load_budgets() -> list[object]:
    """Load and return budget records from mock_data/budgets.json."""
    return _load_json_list("budgets.json")


def load_vendors() -> list[object]:
    """Load and return vendor records from mock_data/vendors.json."""
    return _load_json_list("vendors.json")


def load_policies() -> list[object]:
    """Load and return policy records from mock_data/policies.json."""
    return _load_json_list("policies.json")


def load_requests() -> list[object]:
    """Load and return request records from mock_data/requests.json."""
    return _load_json_list("requests.json")
