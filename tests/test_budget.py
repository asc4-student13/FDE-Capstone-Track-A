"""Tests for budget validation behavior using real loader-backed mock data."""

from __future__ import annotations

import pytest

from tools.budget import check_budget


def test_check_budget_within_and_over_budget_for_cc_003() -> None:
    """CC-003 should pass at $6,900 and fail above $6,900 without mocking the loader."""
    within_result = check_budget("CC-003", 6900.0)
    assert within_result["within_budget"] is True
    assert within_result["cost_center_id"] == "CC-003"
    assert within_result["requested_amount"] == 6900.0
    assert within_result["overage"] == 0.0

    over_result = check_budget("CC-003", 11200.0)
    assert over_result["within_budget"] is False
    assert over_result["cost_center_id"] == "CC-003"
    assert over_result["requested_amount"] == 11200.0
    assert over_result["overage"] == pytest.approx(4300.0, abs=0.01)
