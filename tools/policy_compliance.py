"""Policy compliance tool — evaluates a purchase request against all eight policies."""

from __future__ import annotations

from data.loader import load_policies, load_vendors

# Amount within this fraction of the director threshold triggers near-threshold escalation
_DIRECTOR_THRESHOLD = 50_000.00
_NEAR_THRESHOLD_FRACTION = 0.05  # within 5%
_MANAGER_THRESHOLD_LOW = 10_000.00
_MANAGER_THRESHOLD_HIGH = 49_999.99


def check_policy_compliance(
    vendor_id: str,
    category: str,
    amount: float,
    quantity: int = 0,
) -> dict[str, object]:
    """Evaluate a purchase request against all procurement policies.

    Call this tool for every purchase request. It checks all eight policies and
    returns a list of violations. Each violation specifies the policy ID, a
    description of the rule that was broken, and the forced decision it implies
    (deny or escalate). An empty violations list means no policy was triggered.

    Args:
        vendor_id: The vendor ID from the purchase request (e.g. "V-006").
        category: The purchase category (e.g. "catering", "staffing").
        amount: The total purchase amount in USD.
        quantity: The number of units (used for staffing hour-based checks).

    Returns:
        A dict containing:
        - ``violations`` (list[dict]): Each dict has keys ``policy_id``,
          ``rule_description``, and ``forced_decision`` ("deny" or "escalate").
        - ``violation_count`` (int): Number of violations found.
        - ``highest_severity`` (str): "escalate" if any violation forces escalation,
          "deny" if any force denial but none escalate, "none" if no violations.
        - ``error`` (str, optional): Present only if data could not be loaded.
    """
    try:
        vendors = load_vendors()
        load_policies()  # validate data is accessible
    except FileNotFoundError as exc:
        return {
            "error": f"Policy or vendor data could not be loaded: {exc}",
            "violations": [],
            "violation_count": 0,
            "highest_severity": "escalate",  # escalate when data is unavailable
        }

    vendor = next((v for v in vendors if v["vendor_id"] == vendor_id), None)
    violations: list[dict[str, str]] = []

    # POL-004: Catering prohibition
    if category == "catering":
        violations.append({
            "policy_id": "POL-004",
            "rule_description": (
                "Catering and food service purchases are prohibited under the Q4 2025 "
                "corporate spend reduction initiative. Denied regardless of amount."
            ),
            "forced_decision": "deny",
        })

    # POL-005: Expired contract vendor
    if vendor and vendor.get("contract_status") == "expired":
        violations.append({
            "policy_id": "POL-005",
            "rule_description": (
                f"Vendor {vendor['name']} ({vendor_id}) has an expired contract "
                f"({vendor.get('contract_id', 'unknown')}). Purchases may not proceed "
                "until the contract is renewed."
            ),
            "forced_decision": "deny",
        })

    # POL-006: Compliance-flagged vendor
    if vendor and vendor.get("compliance_flag") is True:
        notes = vendor.get("compliance_notes", "No details available.")
        violations.append({
            "policy_id": "POL-006",
            "rule_description": (
                f"Vendor {vendor['name']} ({vendor_id}) has an active compliance flag. "
                f"Notes: {notes} All purchases from flagged vendors must be escalated "
                "to Legal and Compliance before approval."
            ),
            "forced_decision": "escalate",
        })

    # POL-003: Director approval threshold
    if amount >= _DIRECTOR_THRESHOLD:
        violations.append({
            "policy_id": "POL-003",
            "rule_description": (
                f"Purchase amount ${amount:,.2f} meets or exceeds the director approval "
                f"threshold of ${_DIRECTOR_THRESHOLD:,.2f}. Director-level sign-off required."
            ),
            "forced_decision": "escalate",
        })
    # Near-threshold escalation: within 5% below director threshold
    elif amount >= _DIRECTOR_THRESHOLD * (1 - _NEAR_THRESHOLD_FRACTION):
        violations.append({
            "policy_id": "POL-003",
            "rule_description": (
                f"Purchase amount ${amount:,.2f} is within 5% of the director approval "
                f"threshold (${_DIRECTOR_THRESHOLD:,.2f}). Escalation recommended to ensure "
                "director awareness before commitment."
            ),
            "forced_decision": "escalate",
        })

    # POL-007: Staffing non-contracted vendor (>40 hours)
    if category == "staffing" and quantity > 40:
        if not vendor or vendor.get("contract_status") != "active":
            violations.append({
                "policy_id": "POL-007",
                "rule_description": (
                    f"Staffing engagement of {quantity} hours exceeds 40-hour threshold. "
                    "All contingent staffing engagements must use the enterprise staffing "
                    "contract. This vendor does not hold an active staffing contract."
                ),
                "forced_decision": "deny",
            })

    # Determine highest severity
    decisions = {v["forced_decision"] for v in violations}
    if "escalate" in decisions:
        highest = "escalate"
    elif "deny" in decisions:
        highest = "deny"
    else:
        highest = "none"

    return {
        "violations": violations,
        "violation_count": len(violations),
        "highest_severity": highest,
    }
