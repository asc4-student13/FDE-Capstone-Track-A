"""Policy compliance tool for procurement requests."""

from __future__ import annotations

from typing import Any

from data import loader
from models import PurchaseRequest


def _normalize_request(request: PurchaseRequest | dict[str, Any]) -> PurchaseRequest:
    """Normalize a dict or model input into a validated PurchaseRequest."""
    if isinstance(request, PurchaseRequest):
        return request
    return PurchaseRequest.model_validate(request)


def _get_policy_map() -> dict[str, dict[str, Any]]:
    """Load all policy records and map them by policy_id."""
    policies = loader.load_policies()
    return {str(policy.get("policy_id", "")): policy for policy in policies}


def check_policy_compliance(request: PurchaseRequest | dict[str, Any]) -> dict[str, object]:
    """Evaluate a purchase request against all eight procurement policies.

    Use this tool whenever policy controls must be checked for a request. The
    result includes every triggered policy violation and a mapped status that can
    be consumed by the procurement agent.

    Args:
        request: A PurchaseRequest object or dict with PurchaseRequest fields.

    Returns:
        A structured result with:
        - check: Literal value "policy_compliance".
        - status: "pass", "fail", "escalate", or "error".
        - violations: List of triggered policy violations.
        - triggered_policy_ids: Ordered list of triggered policy IDs.
        - message: Human-readable summary.
    """
    try:
        parsed_request = _normalize_request(request)
        policies_by_id = _get_policy_map()
        vendors = loader.load_vendors()
        budgets = loader.load_budgets()

        vendor = next(
            (item for item in vendors if item.get("vendor_id") == parsed_request.vendor_id),
            None,
        )
        cost_center = next(
            (item for item in budgets if item.get("cost_center_id") == parsed_request.cost_center_id),
            None,
        )

        def policy_description(policy_id: str, fallback: str) -> str:
            return str(policies_by_id.get(policy_id, {}).get("description", fallback))

        violations: list[dict[str, str]] = []

        # POL-001: Single-Source Restriction
        pol001 = policies_by_id.get("POL-001", {})
        pol001_threshold = float(pol001.get("threshold_amount", 25_000.00))
        pol001_categories = set(pol001.get("affected_categories", []))
        requested_vendor_is_active_in_category = bool(
            vendor
            and vendor.get("contract_status") == "active"
            and vendor.get("category") == parsed_request.category
        )
        has_alternative_active_vendor = any(
            item.get("vendor_id") != parsed_request.vendor_id
            and item.get("category") == parsed_request.category
            and item.get("contract_status") == "active"
            for item in vendors
        )
        if (
            parsed_request.total_amount > pol001_threshold
            and parsed_request.category in pol001_categories
            and not requested_vendor_is_active_in_category
            and has_alternative_active_vendor
        ):
            violations.append(
                {
                    "policy_id": "POL-001",
                    "rule_description": policy_description(
                        "POL-001",
                        "Above-threshold spend must use contracted vendor in covered categories.",
                    ),
                    "forced_decision": "deny",
                }
            )

        # POL-002: Manager Approval Threshold
        pol002 = policies_by_id.get("POL-002", {})
        pol002_threshold = float(pol002.get("threshold_amount", 10_000.00))
        pol002_upper = float(pol002.get("upper_threshold", 49_999.99))
        if pol002_threshold <= parsed_request.total_amount <= pol002_upper:
            violations.append(
                {
                    "policy_id": "POL-002",
                    "rule_description": policy_description(
                        "POL-002",
                        "Manager approval is required between $10,000 and $49,999.99.",
                    ),
                    "forced_decision": "escalate",
                }
            )

        # POL-003: Director Approval Threshold
        pol003 = policies_by_id.get("POL-003", {})
        pol003_threshold = float(pol003.get("threshold_amount", 50_000.00))
        if parsed_request.total_amount >= pol003_threshold:
            violations.append(
                {
                    "policy_id": "POL-003",
                    "rule_description": policy_description(
                        "POL-003",
                        "Director approval is required for purchases at or above $50,000.",
                    ),
                    "forced_decision": "escalate",
                }
            )

        # POL-004: Prohibited Category - Catering
        pol004_categories = set(policies_by_id.get("POL-004", {}).get("affected_categories", []))
        if parsed_request.category in pol004_categories:
            violations.append(
                {
                    "policy_id": "POL-004",
                    "rule_description": policy_description(
                        "POL-004",
                        "Catering purchases are prohibited and must be denied.",
                    ),
                    "forced_decision": "deny",
                }
            )

        # POL-005: Expired Contract Vendor
        if vendor and vendor.get("contract_status") == "expired":
            violations.append(
                {
                    "policy_id": "POL-005",
                    "rule_description": policy_description(
                        "POL-005",
                        "Purchases from vendors with expired contracts must be denied.",
                    ),
                    "forced_decision": "deny",
                }
            )

        # POL-006: Compliance-Flagged Vendor Hold
        if vendor and bool(vendor.get("compliance_flag")):
            violations.append(
                {
                    "policy_id": "POL-006",
                    "rule_description": policy_description(
                        "POL-006",
                        "Purchases from compliance-flagged vendors must be escalated.",
                    ),
                    "forced_decision": "escalate",
                }
            )

        # POL-007: Staffing Vendor Single-Source
        if parsed_request.category == "staffing" and parsed_request.quantity > 40:
            staffing_vendor_is_active = bool(
                vendor
                and vendor.get("category") == "staffing"
                and vendor.get("contract_status") == "active"
            )
            if not staffing_vendor_is_active:
                violations.append(
                    {
                        "policy_id": "POL-007",
                        "rule_description": policy_description(
                            "POL-007",
                            "Staffing engagements above 40 hours require enterprise contract vendors.",
                        ),
                        "forced_decision": "deny",
                    }
                )

        # POL-008: Budget Overage Prohibition
        remaining_budget = float(cost_center.get("remaining", 0.0)) if cost_center else 0.0
        if parsed_request.total_amount > remaining_budget:
            violations.append(
                {
                    "policy_id": "POL-008",
                    "rule_description": policy_description(
                        "POL-008",
                        "Purchases that exceed remaining cost-center budget must be denied.",
                    ),
                    "forced_decision": "deny",
                }
            )

        triggered_policy_ids = [violation["policy_id"] for violation in violations]
        decisions = {violation["forced_decision"] for violation in violations}
        if "escalate" in decisions:
            status = "escalate"
        elif "deny" in decisions:
            status = "fail"
        else:
            status = "pass"

        message = (
            "No policy violations found."
            if not violations
            else f"{len(violations)} policy violation(s) detected."
        )

        return {
            "check": "policy_compliance",
            "status": status,
            "violations": violations,
            "triggered_policy_ids": triggered_policy_ids,
            "message": message,
        }
    except FileNotFoundError as exc:
        return {
            "check": "policy_compliance",
            "status": "error",
            "error_type": "file_not_found",
            "violations": [],
            "triggered_policy_ids": [],
            "message": f"Policy compliance data loading failure: {exc}",
        }
    except KeyError as exc:
        return {
            "check": "policy_compliance",
            "status": "error",
            "error_type": "missing_key",
            "violations": [],
            "triggered_policy_ids": [],
            "message": f"Policy compliance data missing required key: {exc}",
        }
    except Exception as exc:
        return {
            "check": "policy_compliance",
            "status": "error",
            "error_type": "unexpected_error",
            "violations": [],
            "triggered_policy_ids": [],
            "message": str(exc) or "Policy compliance evaluation failed unexpectedly.",
        }
