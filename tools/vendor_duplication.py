"""Vendor duplication check tool for single-source policy validation."""

from __future__ import annotations

from typing import Any

import data.loader as data_loader


def check_vendor_duplication(
    vendor_id: str,
    category: str,
    requested_amount: float,
) -> dict[str, Any]:
    """Evaluate single-source vendor conflict risk for a purchase request.

    This tool checks whether a request violates the single-source restriction
    policy by using policy and vendor records loaded from data.loader.

    Args:
        vendor_id: Vendor identifier from the request, such as "V-012".
        category: Purchase category from the request, such as "office_supplies".
        requested_amount: Total requested amount in USD.

    Returns:
        A dictionary containing violation context:
        - violation: True when a single-source policy conflict is detected.
        - vendor_id: The requested vendor identifier.
        - category: The request category used for evaluation.
        - requested_amount: The amount evaluated.
        - threshold_amount: Policy threshold used for single-source checks.
        - policy_id: Policy identifier used for evaluation.
        - conflicting_vendor_ids: Active contracted alternatives in the category.
        - reason: Human-readable explanation of why the result was triggered.

        If vendor or policy data cannot be loaded, an error key is included and
        violation is set to False so callers can safely escalate if needed.
    """
    try:
        vendors = data_loader.load_vendors()
        policies = data_loader.load_policies()
    except FileNotFoundError as exc:
        return {
            "violation": False,
            "vendor_id": vendor_id,
            "category": category,
            "requested_amount": requested_amount,
            "threshold_amount": 0.0,
            "policy_id": "POL-001",
            "conflicting_vendor_ids": [],
            "reason": "Unable to evaluate single-source restrictions because data load failed.",
            "error_type": "file_not_found",
            "error": f"Vendor duplication check data load failed: {exc}",
        }
    except KeyError as exc:
        return {
            "violation": False,
            "vendor_id": vendor_id,
            "category": category,
            "requested_amount": requested_amount,
            "threshold_amount": 0.0,
            "policy_id": "POL-001",
            "conflicting_vendor_ids": [],
            "reason": "Unable to evaluate single-source restrictions because data is incomplete.",
            "error_type": "key_error",
            "error": f"Vendor duplication data missing required field: {exc}",
        }
    except Exception as exc:  # pragma: no cover - defensive integration path
        return {
            "violation": False,
            "vendor_id": vendor_id,
            "category": category,
            "requested_amount": requested_amount,
            "threshold_amount": 0.0,
            "policy_id": "POL-001",
            "conflicting_vendor_ids": [],
            "reason": "Unable to evaluate single-source restrictions because data load failed.",
            "error_type": "exception",
            "error": f"Vendor duplication check data load failed: {exc}",
        }

    single_source_policy = next(
        (policy for policy in policies if policy.get("policy_id") == "POL-001"),
        None,
    )
    if single_source_policy is None:
        return {
            "violation": False,
            "vendor_id": vendor_id,
            "category": category,
            "requested_amount": requested_amount,
            "threshold_amount": 0.0,
            "policy_id": "POL-001",
            "conflicting_vendor_ids": [],
            "reason": "Single-source restriction policy POL-001 was not found.",
            "error": "Missing policy record for POL-001.",
        }

    threshold_amount = float(single_source_policy.get("threshold_amount", 0.0))
    covered_categories = {
        str(item) for item in single_source_policy.get("affected_categories", [])
    }

    if requested_amount <= threshold_amount:
        return {
            "violation": False,
            "vendor_id": vendor_id,
            "category": category,
            "requested_amount": requested_amount,
            "threshold_amount": threshold_amount,
            "policy_id": "POL-001",
            "conflicting_vendor_ids": [],
            "reason": (
                f"No violation: requested amount ${requested_amount:,.2f} is at or below the "
                f"single-source threshold ${threshold_amount:,.2f}."
            ),
        }

    if category not in covered_categories:
        return {
            "violation": False,
            "vendor_id": vendor_id,
            "category": category,
            "requested_amount": requested_amount,
            "threshold_amount": threshold_amount,
            "policy_id": "POL-001",
            "conflicting_vendor_ids": [],
            "reason": (
                "No violation: this category is not covered by the single-source restriction "
                "policy.")
        }

    conflicting_vendor_ids = [
        str(vendor.get("vendor_id"))
        for vendor in vendors
        if vendor.get("vendor_id") != vendor_id
        and vendor.get("category") == category
        and vendor.get("contract_status") == "active"
    ]

    if conflicting_vendor_ids:
        conflicting_ids_text = ", ".join(conflicting_vendor_ids)
        return {
            "violation": True,
            "vendor_id": vendor_id,
            "category": category,
            "requested_amount": requested_amount,
            "threshold_amount": threshold_amount,
            "policy_id": "POL-001",
            "conflicting_vendor_ids": conflicting_vendor_ids,
            "reason": (
                "Violation: request exceeds the single-source threshold and there are active "
                f"contracted alternatives in this category ({conflicting_ids_text})."
            ),
        }

    return {
        "violation": False,
        "vendor_id": vendor_id,
        "category": category,
        "requested_amount": requested_amount,
        "threshold_amount": threshold_amount,
        "policy_id": "POL-001",
        "conflicting_vendor_ids": [],
        "reason": (
            "No violation: no conflicting active contracted vendors were found in this category "
            "for a request above the single-source threshold."
        ),
    }