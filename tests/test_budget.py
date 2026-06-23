"""Tests for budget tool behavior using real mock data."""

from __future__ import annotations

from tools.budget import check_budget


def test_check_budget_within_and_over_budget_for_cc003() -> None:
    """CC-003 should pass at 6,900 and fail at 11,200 using real loader data."""
    within_result = check_budget("CC-003", 6_900.0)
    assert within_result["check"] == "budget"
    assert within_result["status"] == "pass"
    assert within_result["remaining_budget"] == 6_900.0
    assert within_result["overage_amount"] == 0.0

    over_result = check_budget("CC-003", 11_200.0)
    assert over_result["check"] == "budget"
    assert over_result["status"] == "fail"
    assert over_result["remaining_budget"] == 6_900.0
    assert over_result["overage_amount"] == 4_300.0
