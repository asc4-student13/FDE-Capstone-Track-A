"""Tests for vendor duplication policy checks."""

from __future__ import annotations

from tools.vendor_duplication import check_vendor_duplication


def test_req_008_detects_expected_conflicting_vendors() -> None:
    """REQ-008 should flag single-source conflict with V-001 and V-003."""
    result = check_vendor_duplication(
        vendor_id="V-012",
        category="office_supplies",
        requested_amount=28_500.0,
    )

    assert result["violation"] is True
    assert set(result["conflicting_vendor_ids"]) == {"V-001", "V-003"}
