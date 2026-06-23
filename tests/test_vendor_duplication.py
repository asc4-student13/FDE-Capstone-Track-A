"""Tests for vendor duplication tool behavior using real mock data."""

from __future__ import annotations

from tools.vendor_duplication import check_vendor_duplication


def test_req008_finds_office_supply_conflicts_and_fails_pol001() -> None:
    """REQ-008 should fail POL-001 and identify V-001 and V-003 as conflicts."""
    result = check_vendor_duplication("V-012", "office_supplies", 28_500.0)

    assert result["check"] == "vendor_duplication"
    assert result["status"] == "fail"
    assert "POL-001" in result["triggered_policy_ids"]
    assert set(result["conflicting_vendor_ids"]) == {"V-001", "V-003"}
