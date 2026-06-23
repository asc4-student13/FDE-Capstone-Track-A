"""Policy compliance checks for procurement purchase requests."""

from __future__ import annotations

from typing import Literal

from data.loader import load_policies, load_vendors
from models import PurchaseRequest

Severity = Literal["deny", "escalate", "none"]
ForcedDecision = Literal["deny", "escalate"]


def _get_policy_index() -> dict[str, dict[str, object]]:
    """Load policy records and index them by policy_id for quick lookups."""
    policies = load_policies()
    return {
        str(policy.get("policy_id")): policy
        for policy in policies
        if isinstance(policy, dict) and "policy_id" in policy
    }


def _build_violation(
    policy_id: str,
    rule_details: str,
    forced_decision: ForcedDecision,
) -> dict[str, str]:
    """Create a normalized policy violation payload."""
    return {
        "policy_id": policy_id,
        "rule_details": rule_details,
        "forced_decision": forced_decision,
    }


def _determine_highest_severity(violations: list[dict[str, str]]) -> Severity:
    """Return the aggregate highest severity using escalate > deny > none."""
    forced_decisions = {item["forced_decision"] for item in violations}
    if "escalate" in forced_decisions:
        return "escalate"
    if "deny" in forced_decisions:
        return "deny"
    return "none"


def check_policy_compliance(purchase_request: PurchaseRequest) -> dict[str, object]:
    """Evaluate a purchase request against policy compliance rules.

    The check uses policy and vendor datasets loaded through ``data.loader`` and
    returns machine-readable policy violations. Each violation includes the
    policy identifier, human-readable violated rule details, and a forced decision
    signal (``deny`` or ``escalate``). It also returns aggregate highest severity
    computed as ``escalate`` > ``deny`` > ``none``.

    Evaluated rules:
    - ``POL-004``: Category ``catering`` is prohibited and must be denied.
        - ``POL-002``: Requests in the manager threshold range are non-compliant
            without documented manager approval metadata and are escalated.
        - ``POL-005``: Vendors with expired contracts must be denied.
    - ``POL-006``: Vendors with an active compliance flag must be escalated.
    - ``POL-003``: Requests with total amount at or above director threshold
      must be escalated.

    Args:
        purchase_request: Validated purchase request payload.

    Returns:
        A dictionary with:
        - ``violations``: List of violations with ``policy_id``, ``rule_details``,
          and ``forced_decision``.
        - ``violation_count``: Total number of violations found.
        - ``highest_severity``: ``deny``, ``escalate``, or ``none``.
        - ``error`` (optional): Present when policy/vendor data cannot be loaded
          or parsed; error conditions force aggregate escalation.
    """
    violations: list[dict[str, str]] = []

    try:
        policy_index = _get_policy_index()
        vendors = load_vendors()
    except Exception as exc:
        return {
            "violations": [],
            "violation_count": 0,
            "highest_severity": "escalate",
            "error": f"Policy compliance data load failure: {exc}",
        }

    vendor_name_normalized = purchase_request.vendor_name.strip().casefold()
    vendor_record = next(
        (
            vendor
            for vendor in vendors
            if isinstance(vendor, dict)
            and str(vendor.get("name", "")).strip().casefold() == vendor_name_normalized
        ),
        None,
    )

    if purchase_request.category.strip().casefold() == "catering":
        policy_id = "POL-004"
        policy = policy_index.get(policy_id, {})
        rule_details = str(
            policy.get(
                "description",
                "Catering requests are prohibited and must be denied.",
            )
        )
        violations.append(_build_violation(policy_id, rule_details, "deny"))

    policy_id = "POL-002"
    policy = policy_index.get(policy_id, {})
    manager_threshold = float(policy.get("threshold_amount", 10_000.0))
    manager_upper_threshold = float(policy.get("upper_threshold", 49_999.99))
    if manager_threshold <= purchase_request.total_amount <= manager_upper_threshold:
        rule_details = (
            f"Request total ${purchase_request.total_amount:,.2f} is within manager approval "
            f"range ${manager_threshold:,.2f}-${manager_upper_threshold:,.2f}. "
            "Manager approval evidence is not present in PurchaseRequest and requires escalation."
        )
        violations.append(_build_violation(policy_id, rule_details, "escalate"))

    if isinstance(vendor_record, dict) and str(vendor_record.get("contract_status", "")).strip() == "expired":
        policy_id = "POL-005"
        policy = policy_index.get(policy_id, {})
        contract_id = str(vendor_record.get("contract_id", "")).strip() or "unknown"
        rule_details = str(
            policy.get(
                "description",
                "Purchases from expired-contract vendors are denied until renewal.",
            )
        )
        violations.append(
            _build_violation(
                policy_id,
                f"{rule_details} Vendor: {purchase_request.vendor_name}. Contract: {contract_id}.",
                "deny",
            )
        )

    if isinstance(vendor_record, dict) and bool(vendor_record.get("compliance_flag")):
        policy_id = "POL-006"
        policy = policy_index.get(policy_id, {})
        notes = str(vendor_record.get("compliance_notes", "")).strip()
        base_details = str(
            policy.get(
                "description",
                "Compliance-flagged vendors require legal/compliance escalation.",
            )
        )
        details = base_details if not notes else f"{base_details} Notes: {notes}"
        violations.append(_build_violation(policy_id, details, "escalate"))

    policy_id = "POL-003"
    policy = policy_index.get(policy_id, {})
    director_threshold = float(policy.get("threshold_amount", 50_000.0))
    if purchase_request.total_amount >= director_threshold:
        rule_details = (
            f"Request total ${purchase_request.total_amount:,.2f} meets/exceeds "
            f"director threshold ${director_threshold:,.2f}. "
            "Director-level approval is required."
        )
        violations.append(_build_violation(policy_id, rule_details, "escalate"))

    highest_severity = _determine_highest_severity(violations)
    return {
        "violations": violations,
        "violation_count": len(violations),
        "highest_severity": highest_severity,
    }
