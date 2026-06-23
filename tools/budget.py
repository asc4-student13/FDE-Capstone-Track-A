"""Budget check tool for cost-center remaining-capacity validation."""

from __future__ import annotations

from typing import Any

from data.loader import load_budgets


def check_budget(cost_center_id: str, requested_amount: float) -> dict[str, object]:
    """Evaluate whether a requested purchase amount fits a cost center's remaining budget.

    This tool loads budget records through :func:`data.loader.load_budgets`, locates the
    budget row for the provided cost center, and compares the request total against the
    remaining budget.

    Args:
        cost_center_id: Cost center identifier from a purchase request (for example,
            ``"CC-003"``).
        requested_amount: Requested total purchase amount in USD.

    Returns:
        A structured result dictionary containing:

        - ``within_budget`` (bool): ``True`` when ``requested_amount`` is less than or
          equal to remaining budget; otherwise ``False``.
        - ``cost_center_id`` (str): Echo of the evaluated cost center identifier.
        - ``remaining_budget`` (float): Remaining budget for the matched cost center.
          Returns ``0.0`` when budget data cannot be loaded or no matching cost center is
          found.
        - ``requested_amount`` (float): Echo of the requested amount argument.
        - ``overage`` (float): Positive difference between requested and remaining budget,
          or ``0.0`` when within budget.
        - ``error`` (str, optional): Present when the budget source cannot be loaded or
          when the provided cost center is unknown.

    Notes:
        Tool failures are surfaced in the returned ``error`` field instead of being raised,
        so calling agent code can incorporate the failure into a recommendation rationale.
    """
    normalized_requested_amount = float(requested_amount)

    try:
        budgets = load_budgets()
    except Exception as exc:  # pragma: no cover - defensive fallback for loader failures.
        return {
            "error": f"Budget data could not be loaded: {exc}",
            "within_budget": False,
            "cost_center_id": cost_center_id,
            "remaining_budget": 0.0,
            "requested_amount": normalized_requested_amount,
            "overage": max(0.0, normalized_requested_amount),
        }

    matched_budget: dict[str, Any] | None = next(
        (
            budget_record
            for budget_record in budgets
            if str(budget_record.get("cost_center_id")) == cost_center_id
        ),
        None,
    )

    if matched_budget is None:
        return {
            "error": f"Cost center '{cost_center_id}' not found in budget data.",
            "within_budget": False,
            "cost_center_id": cost_center_id,
            "remaining_budget": 0.0,
            "requested_amount": normalized_requested_amount,
            "overage": max(0.0, normalized_requested_amount),
        }

    remaining_budget = float(matched_budget.get("remaining_budget", 0.0))
    overage = max(0.0, normalized_requested_amount - remaining_budget)

    return {
        "within_budget": overage == 0.0,
        "cost_center_id": cost_center_id,
        "remaining_budget": remaining_budget,
        "requested_amount": normalized_requested_amount,
        "overage": round(overage, 2),
    }
