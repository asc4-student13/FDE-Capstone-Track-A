"""Unit tests for the budget check tool."""

from __future__ import annotations

import pytest

from tools.budget import check_budget


def test_within_budget_returns_true() -> None:
    """A request well within the cost center budget should be approved."""
    # CC-001 has $187,550 remaining; request $24,000
    result = check_budget("CC-001", 24_000.00)
    assert result["check"] == "budget"
    assert result["status"] == "pass"
    assert result["within_budget"] is True
    assert result["overage_amount"] == 0.0
    assert result["remaining_budget"] > 24_000.00


def test_over_budget_returns_false() -> None:
    """REQ-006: CC-003 has $6,900 remaining; request $11,200 should be over budget."""
    result = check_budget("CC-003", 11_200.00)
    assert result["check"] == "budget"
    assert result["status"] == "fail"
    assert result["within_budget"] is False
    assert result["overage_amount"] == pytest.approx(4_300.00, abs=0.01)
    assert result["remaining_budget"] == pytest.approx(6_900.00, abs=0.01)


def test_exact_budget_boundary_is_within() -> None:
    """A request exactly equal to the remaining budget is within budget."""
    result = check_budget("CC-003", 6_900.00)
    assert result["status"] == "pass"
    assert result["within_budget"] is True
    assert result["overage_amount"] == 0.0


def test_unknown_cost_center_returns_error() -> None:
    """An unknown cost center should return status=error and a non-empty message."""
    result = check_budget("CC-999", 1_000.00)
    assert result["check"] == "budget"
    assert result["status"] == "error"
    assert result["within_budget"] is False
    assert result["message"].strip()
    assert "CC-999" in result["message"]


def test_result_contains_required_contract_keys() -> None:
    """The result dict must always contain required budget tool contract keys."""
    result = check_budget("CC-001", 500.00)
    for key in ("check", "status", "remaining_budget", "overage_amount", "message"):
        assert key in result
