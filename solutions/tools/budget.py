"""Budget check tool — verifies a request is within the cost center's remaining budget."""

from __future__ import annotations

from data.loader import load_budgets


def check_budget(cost_center_id: str, requested_amount: float) -> dict[str, object]:
    """Check whether a purchase amount is within a cost center's remaining quarterly budget.

    Call this tool for every purchase request. If the request would exceed the
    remaining budget, return an over-budget result so the agent can deny or escalate.

    Args:
        cost_center_id: The cost center identifier from the purchase request (e.g. "CC-003").
        requested_amount: The total purchase amount in USD.

    Returns:
        A dict containing:
        - ``within_budget`` (bool): True if the request fits within the remaining budget.
        - ``remaining_budget`` (float): The cost center's current remaining budget in USD.
        - ``requested_amount`` (float): The amount passed in (echoed for context).
        - ``overage`` (float): Amount by which the request exceeds the budget (0 if within).
        - ``cost_center_id`` (str): The cost center that was checked.
        - ``error`` (str, optional): Present only if the cost center was not found.
    """
    try:
        budgets = load_budgets()
    except FileNotFoundError as exc:
        return {
            "error": f"Budget data could not be loaded: {exc}",
            "within_budget": False,
            "cost_center_id": cost_center_id,
            "requested_amount": requested_amount,
            "remaining_budget": 0.0,
            "overage": requested_amount,
        }

    center = next(
        (b for b in budgets if b["cost_center_id"] == cost_center_id), None
    )
    if center is None:
        return {
            "error": f"Cost center '{cost_center_id}' not found in budget data.",
            "within_budget": False,
            "cost_center_id": cost_center_id,
            "requested_amount": requested_amount,
            "remaining_budget": 0.0,
            "overage": requested_amount,
        }

    remaining = float(center["remaining_budget"])
    overage = max(0.0, requested_amount - remaining)

    return {
        "within_budget": overage == 0.0,
        "cost_center_id": cost_center_id,
        "remaining_budget": remaining,
        "requested_amount": requested_amount,
        "overage": round(overage, 2),
    }
