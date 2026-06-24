"""Tests for budget evaluation using real mock data."""

from __future__ import annotations

from tools.budget import check_budget


def test_check_budget_cc003_within_and_over_budget() -> None:
    """CC-003 should be within budget at 6900 and over budget above 6900."""
    within_result = check_budget("CC-003", 6_900.0)
    over_result = check_budget("CC-003", 11_200.0)

    assert within_result["within_budget"] is True
    assert within_result["overage"] == 0.0
    assert within_result["remaining_budget"] == 6_900.0

    assert over_result["within_budget"] is False
    assert over_result["overage"] == 4_300.0
    assert over_result["remaining_budget"] == 6_900.0
