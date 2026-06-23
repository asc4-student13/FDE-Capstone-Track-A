from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_MOCK_DATA_DIR = _PROJECT_ROOT / "mock_data"


def load_budgets() -> list[dict[str, Any]]:
    """Load and return budget records from mock_data/budgets.json."""
    path = _MOCK_DATA_DIR / "budgets.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_vendors() -> list[dict[str, Any]]:
    """Load and return vendor records from mock_data/vendors.json."""
    path = _MOCK_DATA_DIR / "vendors.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_policies() -> list[dict[str, Any]]:
    """Load and return procurement policy records from mock_data/policies.json."""
    path = _MOCK_DATA_DIR / "policies.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_requests() -> list[dict[str, Any]]:
    """Load and return sample purchase request records from mock_data/requests.json."""
    path = _MOCK_DATA_DIR / "requests.json"
    return json.loads(path.read_text(encoding="utf-8"))