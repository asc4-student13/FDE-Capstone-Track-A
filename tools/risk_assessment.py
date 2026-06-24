"""Risk assessment tool for procurement vendor and request context."""

from __future__ import annotations

from data import loader


def assess_risk(
    vendor_id: str,
    total_amount: float | None = None,
    category: str | None = None,
    cost_center_id: str | None = None,
) -> dict[str, object]:
    """Assess procurement risk for a vendor using deterministic policy-aligned logic.

    Use this tool to determine whether a request should be escalated based on
    vendor compliance state, contract status, and optional request context.

    Args:
        vendor_id: Vendor identifier from the purchase request.
        total_amount: Optional request amount for context-aware escalation.
        category: Optional request category for context-aware risk factors.
        cost_center_id: Optional cost center for context traceability.

    Returns:
        A structured risk result with:
        - check: Literal value "risk_assessment".
        - status: "pass", "escalate", or "error".
        - vendor_id: Echo of the input vendor ID.
        - compliance_flag: Whether the vendor has an active compliance hold.
        - contract_status: One of "active", "expired", "none", or "unknown".
        - risk_level: One of "low", "medium", "high", or "critical".
        - risk_factors: Deterministic list of factors that contributed to risk.
        - message: Human-readable summary.
    """
    try:
        vendors = loader.load_vendors()
        policies = loader.load_policies()

        vendor = next((item for item in vendors if item.get("vendor_id") == vendor_id), None)
        if vendor is None:
            return {
                "check": "risk_assessment",
                "status": "error",
                "vendor_id": vendor_id,
                "compliance_flag": False,
                "contract_status": "unknown",
                "risk_level": "high",
                "risk_factors": ["vendor_not_found"],
                "message": f"Vendor '{vendor_id}' was not found.",
            }

        compliance_flag = bool(vendor.get("compliance_flag", False))
        contract_status = str(vendor.get("contract_status", "unknown"))
        risk_factors: list[str] = []

        if compliance_flag:
            risk_level = "critical"
            risk_factors.append("compliance_flag")
        elif contract_status == "expired":
            risk_level = "high"
            risk_factors.append("expired_contract")
        elif contract_status == "none":
            risk_level = "medium"
            risk_factors.append("no_contract")
        elif contract_status == "active":
            risk_level = "low"
        else:
            risk_level = "high"
            risk_factors.append("unknown_contract_status")

        pol003 = next((item for item in policies if item.get("policy_id") == "POL-003"), {})
        director_threshold = float(pol003.get("threshold_amount", 50_000.0))
        if total_amount is not None:
            amount_value = float(total_amount)
            if amount_value >= director_threshold:
                risk_factors.append("director_threshold")
            elif amount_value >= director_threshold * 0.95:
                risk_factors.append("near_director_threshold")

        if category == "staffing":
            risk_factors.append("staffing_category")
        if cost_center_id:
            risk_factors.append("cost_center_context")

        should_escalate = risk_level in {"critical", "high"}
        if not should_escalate and "near_director_threshold" in risk_factors:
            should_escalate = True

        status = "escalate" if should_escalate else "pass"

        if status == "escalate":
            message = (
                "Risk assessment indicates escalation is required based on vendor/profile context."
            )
        else:
            message = "Risk assessment indicates no escalation is required."

        return {
            "check": "risk_assessment",
            "status": status,
            "vendor_id": vendor_id,
            "compliance_flag": compliance_flag,
            "contract_status": contract_status,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "message": message,
        }
    except FileNotFoundError as exc:
        return {
            "check": "risk_assessment",
            "status": "error",
            "error_type": "file_not_found",
            "vendor_id": vendor_id,
            "compliance_flag": False,
            "contract_status": "unknown",
            "risk_level": "high",
            "risk_factors": ["data_loading_failure"],
            "message": f"Risk data loading failure: {exc}",
        }
    except KeyError as exc:
        return {
            "check": "risk_assessment",
            "status": "error",
            "error_type": "missing_key",
            "vendor_id": vendor_id,
            "compliance_flag": False,
            "contract_status": "unknown",
            "risk_level": "high",
            "risk_factors": ["data_missing_key"],
            "message": f"Risk assessment data missing required key: {exc}",
        }
    except Exception as exc:
        return {
            "check": "risk_assessment",
            "status": "error",
            "error_type": "unexpected_error",
            "vendor_id": vendor_id,
            "compliance_flag": False,
            "contract_status": "unknown",
            "risk_level": "high",
            "risk_factors": ["evaluation_error"],
            "message": str(exc) or "Risk assessment failed unexpectedly.",
        }
