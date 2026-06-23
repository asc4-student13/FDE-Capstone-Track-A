"""Budget check tool for procurement purchase requests."""

from __future__ import annotations

from data.loader import load_budgets


def check_budget(cost_center_id: str, requested_amount: float) -> dict[str, object]:
    """Check whether a request fits the remaining budget for a cost center.

    Call this tool for every purchase request to provide budget evidence used by
    final recommendation orchestration.

    Args:
        cost_center_id: Cost center identifier to evaluate.
        requested_amount: Total amount requested for purchase.

    Returns:
        A structured result with budget status and overage details:
        - within_budget: True when requested amount is within remaining budget.
        - overage: Positive amount above remaining budget, otherwise 0.0.
        - remaining_budget: Remaining budget for the matched cost center.
        - error: Present when budget data cannot be loaded or parsed.
    """
    try:
        budgets = load_budgets()
    except FileNotFoundError as exc:
        return {
            "error": f"Budget data could not be loaded: {exc}",
            "within_budget": False,
            "overage": requested_amount,
            "remaining_budget": 0.0,
        }

    if not isinstance(budgets, list):
        return {
            "error": "Budget data format is invalid; expected a list.",
            "within_budget": False,
            "overage": requested_amount,
            "remaining_budget": 0.0,
        }

    center = next(
        (item for item in budgets if item.get("cost_center_id") == cost_center_id),
        None,
    )

    if center is None:
        return {
            "error": f"Cost center '{cost_center_id}' not found in budget data.",
            "within_budget": False,
            "overage": requested_amount,
            "remaining_budget": 0.0,
        }

    try:
        remaining_budget = float(center.get("remaining", 0.0))
    except (TypeError, ValueError):
        return {
            "error": (
                f"Budget record for cost center '{cost_center_id}' has an invalid "
                "remaining value."
            ),
            "within_budget": False,
            "overage": requested_amount,
            "remaining_budget": 0.0,
        }

    overage = max(0.0, requested_amount - remaining_budget)

    return {
        "within_budget": overage == 0.0,
        "overage": overage,
        "remaining_budget": remaining_budget,
    }
