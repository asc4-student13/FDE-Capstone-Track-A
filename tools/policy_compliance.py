"""Policy compliance tool for procurement rule checks."""

from __future__ import annotations

from data.loader import load_policies, load_vendors

_DIRECTOR_THRESHOLD = 50_000.0
_NEAR_THRESHOLD_FRACTION = 0.05


def check_policy_compliance(
    vendor_id: str,
    category: str,
    amount: float,
    quantity: int = 0,
) -> dict[str, object]:
    """Evaluate a purchase request against procurement policies.

    Call this tool for every purchase request to identify policy violations and
    produce forced decision signals for orchestration.

    Args:
        vendor_id: Requested vendor identifier.
        category: Requested purchase category.
        amount: Requested purchase amount.
        quantity: Requested quantity or hours (used for staffing checks).

    Returns:
        A structured result with violation details, violation count, and highest
        severity. Includes an ``error`` field when required data is unavailable
        or invalid.
    """
    try:
        vendors = load_vendors()
        policies = load_policies()
    except FileNotFoundError as exc:
        return {
            "error": f"Policy or vendor data could not be loaded: {exc}",
            "violations": [],
            "violation_count": 0,
            "highest_severity": "escalate",
        }

    if not isinstance(vendors, list) or not isinstance(policies, list):
        return {
            "error": "Policy or vendor data format is invalid; expected list values.",
            "violations": [],
            "violation_count": 0,
            "highest_severity": "escalate",
        }

    vendor = next(
        (
            item
            for item in vendors
            if isinstance(item, dict) and item.get("vendor_id") == vendor_id
        ),
        None,
    )
    violations: list[dict[str, str]] = []

    if category == "catering":
        violations.append(
            {
                "policy_id": "POL-004",
                "rule_description": "Catering requests are prohibited and must be denied.",
                "forced_decision": "deny",
            }
        )

    if vendor and vendor.get("contract_status") == "expired":
        violations.append(
            {
                "policy_id": "POL-005",
                "rule_description": "Vendor contract is expired and cannot be used.",
                "forced_decision": "deny",
            }
        )

    if vendor and vendor.get("compliance_flag") is True:
        violations.append(
            {
                "policy_id": "POL-006",
                "rule_description": (
                    "Vendor has an active compliance flag and must be escalated "
                    "for legal/compliance review."
                ),
                "forced_decision": "escalate",
            }
        )

    if amount >= _DIRECTOR_THRESHOLD:
        violations.append(
            {
                "policy_id": "POL-003",
                "rule_description": "Amount requires director-level approval.",
                "forced_decision": "escalate",
            }
        )
    elif amount >= _DIRECTOR_THRESHOLD * (1 - _NEAR_THRESHOLD_FRACTION):
        violations.append(
            {
                "policy_id": "POL-003",
                "rule_description": (
                    "Amount is within 5% of director threshold and should be escalated."
                ),
                "forced_decision": "escalate",
            }
        )

    if category == "staffing" and quantity > 40:
        if not vendor or vendor.get("contract_status") != "active":
            violations.append(
                {
                    "policy_id": "POL-007",
                    "rule_description": (
                        "Staffing engagement above 40 hours requires an active "
                        "contracted staffing vendor."
                    ),
                    "forced_decision": "deny",
                }
            )

    decisions = {entry.get("forced_decision") for entry in violations}
    if "escalate" in decisions:
        highest_severity = "escalate"
    elif "deny" in decisions:
        highest_severity = "deny"
    else:
        highest_severity = "none"

    return {
        "violations": violations,
        "violation_count": len(violations),
        "highest_severity": highest_severity,
    }
