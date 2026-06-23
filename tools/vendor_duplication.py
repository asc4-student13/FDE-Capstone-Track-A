"""Vendor duplication and single-source policy check tool."""

from __future__ import annotations

from data.loader import load_policies, load_vendors


def check_vendor_duplication(vendor_id: str, category: str, total_amount: float) -> dict[str, object]:
    """Evaluate POL-001 single-source risk for a requested vendor and category.

    Use this tool when a request proposes a vendor for a specific category and
    amount. It identifies active contracted alternatives and applies the POL-001
    threshold rule for above-threshold purchases.

    Args:
        vendor_id: Requested vendor identifier from the purchase request.
        category: Requested procurement category.
        total_amount: Total requested purchase amount.

    Returns:
        A structured result with:
        - check: Literal value "vendor_duplication".
        - status: "pass", "fail", or "error".
        - triggered_policy_ids: Triggered policy IDs.
        - conflicting_vendor_ids: Active contracted alternatives in category.
        - conflicting_contracts: Contract details for conflicting alternatives.
        - is_requested_vendor_contracted: Whether requested vendor is actively contracted in category.
        - message: Human-readable summary of evaluation.
    """
    try:
        vendors = load_vendors()
        policies = load_policies()

        pol001 = next((p for p in policies if p.get("policy_id") == "POL-001"), None)
        threshold_amount = float(pol001.get("threshold_amount", 25_000.0)) if pol001 else 25_000.0
        affected_categories = set(pol001.get("affected_categories", [])) if pol001 else set()

        requested_vendor = next((v for v in vendors if v.get("vendor_id") == vendor_id), None)
        is_requested_vendor_contracted = bool(
            requested_vendor
            and requested_vendor.get("contract_status") == "active"
            and requested_vendor.get("category") == category
        )

        conflicting_contract_vendors = [
            v
            for v in vendors
            if v.get("vendor_id") != vendor_id
            and v.get("category") == category
            and v.get("contract_status") == "active"
        ]

        conflicting_vendor_ids = [str(v.get("vendor_id", "")) for v in conflicting_contract_vendors]
        conflicting_contracts = [
            {
                "vendor_id": v.get("vendor_id", ""),
                "vendor_name": v.get("name", ""),
                "contract_id": v.get("contract_id", ""),
                "contract_status": v.get("contract_status", ""),
            }
            for v in conflicting_contract_vendors
        ]

        should_trigger_pol001 = (
            float(total_amount) > threshold_amount
            and category in affected_categories
            and not is_requested_vendor_contracted
            and len(conflicting_vendor_ids) > 0
        )

        if should_trigger_pol001:
            return {
                "check": "vendor_duplication",
                "status": "fail",
                "triggered_policy_ids": ["POL-001"],
                "conflicting_vendor_ids": conflicting_vendor_ids,
                "conflicting_contracts": conflicting_contracts,
                "is_requested_vendor_contracted": is_requested_vendor_contracted,
                "message": "POL-001 triggered: above-threshold request uses non-contracted vendor where contracted alternatives exist.",
            }

        return {
            "check": "vendor_duplication",
            "status": "pass",
            "triggered_policy_ids": [],
            "conflicting_vendor_ids": conflicting_vendor_ids,
            "conflicting_contracts": conflicting_contracts,
            "is_requested_vendor_contracted": is_requested_vendor_contracted,
            "message": "No above-threshold single-source violation detected.",
        }
    except Exception as exc:
        return {
            "check": "vendor_duplication",
            "status": "error",
            "triggered_policy_ids": [],
            "conflicting_vendor_ids": [],
            "conflicting_contracts": [],
            "is_requested_vendor_contracted": False,
            "message": str(exc) or "Vendor duplication evaluation failed unexpectedly.",
        }
