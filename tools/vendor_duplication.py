"""Vendor duplication tool — checks for single-source policy violations (POL-001)."""

from __future__ import annotations

from data.loader import load_vendors

# POL-001 threshold: single-source restriction applies above this amount
_POL001_THRESHOLD = 25_000.00


def check_vendor_duplication(
    vendor_id: str, category: str, amount: float
) -> dict[str, object]:
    """Detect single-source restriction violations per POL-001.

    Call this tool when the purchase category is one covered by the single-source
    restriction (office_supplies, software_licenses, hardware, facilities, security,
    fleet_parts, staffing). If the amount exceeds $25,000 and other vendors hold
    active contracts in the same category, this is a policy violation.

    Args:
        vendor_id: The vendor ID from the purchase request (e.g. "V-012").
        category: The purchase category (e.g. "office_supplies").
        amount: The total purchase amount in USD.

    Returns:
        A dict containing:
        - ``violation`` (bool): True if a single-source violation is detected.
        - ``vendor_id`` (str): The requested vendor.
        - ``category`` (str): The purchase category checked.
        - ``amount`` (float): The amount checked.
        - ``conflicting_vendor_ids`` (list[str]): Vendor IDs with active contracts in the same category.
        - ``conflicting_vendor_names`` (list[str]): Display names of conflicting vendors.
        - ``reason`` (str): Human-readable explanation of the result.
        - ``error`` (str, optional): Present only if vendor data could not be loaded.
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
            "reason": "Vendor data unavailable — could not perform duplication check.",
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
                "single-source restriction threshold. POL-001 does not apply."
            ),
        }

    # Find other vendors with active contracts in the same category
    conflicts = [
        v for v in vendors
        if v["vendor_id"] != vendor_id
        and v.get("category") == category
        and v.get("contract_status") == "active"
    ]

    if conflicts:
        names = [str(v["name"]) for v in conflicts]
        ids = [str(v["vendor_id"]) for v in conflicts]
        return {
            "violation": True,
            "vendor_id": vendor_id,
            "category": category,
            "amount": amount,
            "conflicting_vendor_ids": ids,
            "conflicting_vendor_names": names,
            "reason": (
                f"POL-001 violation: amount ${amount:,.2f} exceeds the ${_POL001_THRESHOLD:,.2f} "
                f"single-source threshold. Active contract vendor(s) for '{category}': "
                + ", ".join(f"{n} ({i})" for n, i in zip(names, ids))
                + ". Request must use a contracted vendor."
            ),
        }

    return {
        "violation": False,
        "vendor_id": vendor_id,
        "category": category,
        "amount": amount,
        "conflicting_vendor_ids": [],
        "conflicting_vendor_names": [],
        "reason": (
            f"No other active-contract vendors found for category '{category}'. "
            "No single-source violation."
        ),
    }
