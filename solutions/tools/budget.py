"""Budget check tool — verifies a request is within the cost center's remaining budget."""

from __future__ import annotations

from data.loader import load_budgets


def check_budget(cost_center_id: str, total_amount: float) -> dict[str, object]:
    """Check whether a purchase amount is within a cost center's remaining quarterly budget.

    Call this tool for every purchase request. If the request would exceed the
    remaining budget, return an over-budget result so the agent can deny or escalate.

    Args:
        cost_center_id: The cost center identifier from the purchase request (e.g. "CC-003").
        total_amount: The total purchase amount in USD.

    Returns:
        A dict containing at least:
        - ``check`` (str): Always ``budget``.
        - ``status`` (str): ``pass``, ``fail``, or ``error``.
        - ``remaining_budget`` (float): The cost center's current remaining budget in USD.
        - ``overage_amount`` (float): Amount by which the request exceeds budget.
        - ``message`` (str): Human-readable result summary.

        Backward-compatible keys are also included for existing callers:
        ``within_budget``, ``requested_amount``, and ``overage``.
    """
    try:
        budgets = load_budgets()
        center = next((b for b in budgets if b["cost_center_id"] == cost_center_id), None)
        if center is None:
            raise ValueError(f"Cost center '{cost_center_id}' not found in budget data.")

        remaining = float(center["remaining"])
        overage_amount = max(0.0, float(total_amount) - remaining)
        status = "fail" if overage_amount > 0 else "pass"
        message = (
            f"Request exceeds remaining budget by ${overage_amount:,.2f}."
            if status == "fail"
            else "Request is within remaining budget."
        )

        return {
            "check": "budget",
            "status": status,
            "cost_center_id": cost_center_id,
            "remaining_budget": round(remaining, 2),
            "overage_amount": round(overage_amount, 2),
            "message": message,
            "within_budget": status == "pass",
            "requested_amount": float(total_amount),
            "overage": round(overage_amount, 2),
        }
    except Exception as exc:
        overage_amount = max(0.0, float(total_amount))
        return {
            "check": "budget",
            "status": "error",
            "cost_center_id": cost_center_id,
            "remaining_budget": 0.0,
            "overage_amount": round(overage_amount, 2),
            "message": str(exc) or "Budget check failed unexpectedly.",
            "within_budget": False,
            "requested_amount": float(total_amount),
            "overage": round(overage_amount, 2),
            "error": str(exc) or "Budget check failed unexpectedly.",
        }
