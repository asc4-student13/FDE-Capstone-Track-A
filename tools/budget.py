"""Budget validation tool for procurement requests."""

from __future__ import annotations

from typing import Any

from data.loader import load_budgets


def check_budget(cost_center_id: str, requested_amount: float) -> dict[str, Any]:
    """Evaluate whether a request fits the remaining budget for a cost center.

    This tool compares the requested purchase amount against the selected cost center's
    remaining budget and reports whether the request is within budget. If the request is
    over budget, the response includes the overage amount. If the cost center cannot be
    found, the response contains an explicit error field.

    Args:
        cost_center_id: The cost center identifier to evaluate, such as "CC-003".
        requested_amount: The requested purchase amount in USD.

    Returns:
        A structured dictionary with these keys:
        - within_budget: True when requested_amount is less than or equal to remaining budget.
        - cost_center_id: The cost center that was evaluated.
        - remaining_budget: Remaining budget for the cost center, in USD.
        - requested_amount: The requested purchase amount, in USD.
        - overage: Positive amount over budget, or 0.0 when within budget.

        When the cost center does not exist or budget data cannot be evaluated, an
        additional non-empty error key is included and within_budget is False.
    """
    try:
        budgets = load_budgets()
    except Exception as exc:  # pragma: no cover - defensive path
        return {
            "within_budget": False,
            "cost_center_id": cost_center_id,
            "remaining_budget": 0.0,
            "requested_amount": requested_amount,
            "overage": max(0.0, requested_amount),
            "error": f"Unable to load budget data: {exc}",
        }

    budget_record = next(
        (item for item in budgets if item.get("cost_center_id") == cost_center_id),
        None,
    )

    if budget_record is None:
        return {
            "within_budget": False,
            "cost_center_id": cost_center_id,
            "remaining_budget": 0.0,
            "requested_amount": requested_amount,
            "overage": max(0.0, requested_amount),
            "error": f"Cost center '{cost_center_id}' was not found in budget data.",
        }

    remaining_budget = float(budget_record.get("remaining", 0.0))
    overage = max(0.0, requested_amount - remaining_budget)

    return {
        "within_budget": overage == 0.0,
        "cost_center_id": cost_center_id,
        "remaining_budget": remaining_budget,
        "requested_amount": requested_amount,
        "overage": round(overage, 2),
    }
