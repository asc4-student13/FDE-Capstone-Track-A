"""Tests for the budget validation tool."""

from __future__ import annotations

import pytest

from tools.budget import check_budget


def test_check_budget_within_budget() -> None:
    """check_budget should return within_budget=True when funds are sufficient."""
    result = check_budget("CC-001", 24_000.00)

    assert result["within_budget"] is True
    assert result["overage"] == 0.0
    assert result["remaining_budget"] >= 24_000.00


def test_check_budget_over_budget() -> None:
    """check_budget should return positive overage when request exceeds remaining funds."""
    result = check_budget("CC-003", 11_200.00)

    assert result["within_budget"] is False
    assert result["remaining_budget"] == pytest.approx(6_900.00, abs=0.01)
    assert result["overage"] == pytest.approx(4_300.00, abs=0.01)


def test_check_budget_unknown_cost_center_returns_error() -> None:
    """check_budget should return an explicit error for unknown cost center IDs."""
    result = check_budget("CC-999", 1_000.00)

    assert result["within_budget"] is False
    assert "error" in result
    assert "CC-999" in str(result["error"])
