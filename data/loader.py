from __future__ import annotations

import json
from pathlib import Path
from typing import Any


_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_MOCK_DATA_DIR = _PROJECT_ROOT / "mock_data"


def load_budgets() -> list[dict[str, Any]]:
    """Load and return budget records from mock_data/budgets.json."""
    file_path = _MOCK_DATA_DIR / "budgets.json"
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_vendors() -> list[dict[str, Any]]:
    """Load and return vendor records from mock_data/vendors.json."""
    file_path = _MOCK_DATA_DIR / "vendors.json"
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_policies() -> list[dict[str, Any]]:
    """Load and return policy records from mock_data/policies.json."""
    file_path = _MOCK_DATA_DIR / "policies.json"
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_requests() -> list[dict[str, Any]]:
    """Load and return purchase request records from mock_data/requests.json."""
    file_path = _MOCK_DATA_DIR / "requests.json"
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)
