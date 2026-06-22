"""Mock data loader — single point of access for all reference data files.

All functions resolve paths relative to the project root (the directory
containing mock_data/). No other module should import from mock_data/ directly.
"""

from __future__ import annotations

import json
from pathlib import Path

# Project root is two levels up from this file (solutions/data/loader.py → root)
_ROOT = Path(__file__).resolve().parent.parent.parent / "mock_data"


def _load(filename: str) -> list[dict[str, object]]:
    """Read and parse a JSON file from mock_data/."""
    path = _ROOT / filename
    if not path.exists():
        raise FileNotFoundError(f"Mock data file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_budgets() -> list[dict[str, object]]:
    """Return all cost center budget records from mock_data/budgets.json.

    Returns:
        A list of dicts with keys: cost_center_id, department, quarterly_budget,
        spent_to_date, remaining_budget.
    """
    return _load("budgets.json")


def load_vendors() -> list[dict[str, object]]:
    """Return all vendor records from mock_data/vendors.json.

    Returns:
        A list of dicts with keys: vendor_id, name, category, contract_status,
        contract_id, compliance_flag, compliance_notes.
    """
    return _load("vendors.json")


def load_policies() -> list[dict[str, object]]:
    """Return all procurement policy records from mock_data/policies.json.

    Returns:
        A list of dicts with keys: policy_id, name, description,
        threshold_amount, affected_categories, violation_severity.
    """
    return _load("policies.json")


def load_requests() -> list[dict[str, object]]:
    """Return all sample purchase request records from mock_data/requests.json.

    Returns:
        A list of dicts matching the PurchaseRequest schema plus
        expected_outcome and outcome_reason (for instructor reference only).
    """
    return _load("requests.json")
