"""Vendor duplication tool for POL-001 single-source checks."""

from __future__ import annotations

from data.loader import load_vendors

_POL001_THRESHOLD = 25_000.0


def check_vendor_duplication(
    vendor_id: str,
    category: str,
    amount: float,
) -> dict[str, object]:
    """Detect POL-001 single-source violations for a request.

    Call this tool for every purchase request to determine whether the selected
    vendor conflicts with active contracted vendors above the POL-001 threshold.

    Args:
        vendor_id: Requested vendor identifier.
        category: Requested purchase category.
        amount: Requested purchase amount.

    Returns:
        A structured result with violation status, conflict details, and reason.
        Includes an ``error`` field when vendor data is unavailable or invalid.
    """
    try:
        vendors = load_vendors()
    except FileNotFoundError as exc:
        return {
            "error": f"Vendor data could not be loaded: {exc}",
            "violation": False,
            "vendor_id": vendor_id,
            "category": category,
            "amount": amount,
            "conflicting_vendor_ids": [],
            "conflicting_vendor_names": [],
            "reason": "Vendor data unavailable; duplication check could not run.",
        }

    if not isinstance(vendors, list):
        return {
            "error": "Vendor data format is invalid; expected a list.",
            "violation": False,
            "vendor_id": vendor_id,
            "category": category,
            "amount": amount,
            "conflicting_vendor_ids": [],
            "conflicting_vendor_names": [],
            "reason": "Vendor data format is invalid.",
        }

    if amount <= _POL001_THRESHOLD:
        return {
            "violation": False,
            "vendor_id": vendor_id,
            "category": category,
            "amount": amount,
            "conflicting_vendor_ids": [],
            "conflicting_vendor_names": [],
            "reason": (
                f"Amount ${amount:,.2f} is at or below the ${_POL001_THRESHOLD:,.2f} "
                "single-source threshold."
            ),
        }

    conflicts = [
        vendor
        for vendor in vendors
        if isinstance(vendor, dict)
        and vendor.get("vendor_id") != vendor_id
        and vendor.get("category") == category
        and vendor.get("contract_status") == "active"
    ]

    if not conflicts:
        return {
            "violation": False,
            "vendor_id": vendor_id,
            "category": category,
            "amount": amount,
            "conflicting_vendor_ids": [],
            "conflicting_vendor_names": [],
            "reason": (
                f"No active-contract alternatives found for category '{category}'."
            ),
        }

    conflicting_ids = [str(vendor.get("vendor_id", "")) for vendor in conflicts]
    conflicting_names = [str(vendor.get("name", "")) for vendor in conflicts]
    return {
        "violation": True,
        "vendor_id": vendor_id,
        "category": category,
        "amount": amount,
        "conflicting_vendor_ids": conflicting_ids,
        "conflicting_vendor_names": conflicting_names,
        "reason": (
            f"POL-001 violation: amount ${amount:,.2f} exceeds ${_POL001_THRESHOLD:,.2f} "
            "and active contracted alternatives exist in the same category."
        ),
    }
