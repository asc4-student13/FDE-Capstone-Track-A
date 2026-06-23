"""Budget evaluation tool for procurement requests."""

from __future__ import annotations

from data.loader import load_budgets


def check_budget(cost_center_id: str, requested_amount: float) -> dict[str, object]:
    """Check whether a purchase request fits within a cost center's remaining budget.

    Use this tool when evaluating any purchase request that includes a cost center
    and requested amount. The tool returns structured budget-check results the
    procurement agent can map into approve, deny, or escalate decisions.

    Args:
        cost_center_id: The request's cost center identifier.
        requested_amount: The total amount requested for the purchase.

    Returns:
        A structured result with these keys:
        - check: Literal value "budget".
        - status: "pass", "fail", or "error".
        - cost_center_id: Echo of the input cost center.
        - requested_amount: Echo of the input amount.
        - remaining_budget: Remaining budget for the matched cost center.
        - overage_amount: Positive amount over budget, or 0 when within budget.
        - message: Human-readable explanation.
    """
    try:
        budgets = load_budgets()
        center = next((item for item in budgets if item.get("cost_center_id") == cost_center_id), None)
        if center is None:
            return {
                "check": "budget",
                "status": "error",
                "cost_center_id": cost_center_id,
                "requested_amount": float(requested_amount),
                "remaining_budget": 0.0,
                "overage_amount": max(0.0, float(requested_amount)),
                "message": f"Cost center '{cost_center_id}' was not found.",
            }

        remaining_budget = float(center.get("remaining", 0.0))
        overage_amount = max(0.0, float(requested_amount) - remaining_budget)
        status = "fail" if overage_amount > 0 else "pass"
        message = (
            f"Requested amount exceeds remaining budget by ${overage_amount:,.2f}."
            if status == "fail"
            else "Requested amount is within remaining budget."
        )

        return {
            "check": "budget",
            "status": status,
            "cost_center_id": cost_center_id,
            "requested_amount": float(requested_amount),
            "remaining_budget": round(remaining_budget, 2),
            "overage_amount": round(overage_amount, 2),
            "message": message,
        }
    except Exception as exc:
        return {
            "check": "budget",
            "status": "error",
            "cost_center_id": cost_center_id,
            "requested_amount": float(requested_amount),
            "remaining_budget": 0.0,
            "overage_amount": max(0.0, float(requested_amount)),
            "message": str(exc) or "Budget evaluation failed unexpectedly.",
        }
