"""Risk assessment tool for vendor risk classification."""

from __future__ import annotations

from data.loader import load_vendors


def assess_risk(vendor_id: str) -> dict[str, object]:
    """Compute a vendor risk profile for procurement orchestration.

    Call this tool for every purchase request to classify vendor risk from
    compliance status and contract state.

    Args:
        vendor_id: Vendor identifier from the request.

    Returns:
        A structured risk profile including risk_level and risk_summary.
        Includes an ``error`` field when vendor data is unavailable or vendor
        lookup fails.
    """
    try:
        vendors = load_vendors()
    except FileNotFoundError as exc:
        return {
            "error": f"Vendor data could not be loaded: {exc}",
            "vendor_id": vendor_id,
            "vendor_name": "Unknown",
            "compliance_flag": False,
            "compliance_notes": "",
            "contract_status": "unknown",
            "risk_level": "critical",
            "risk_summary": "Vendor data unavailable; treat as critical risk.",
        }

    if not isinstance(vendors, list):
        return {
            "error": "Vendor data format is invalid; expected a list.",
            "vendor_id": vendor_id,
            "vendor_name": "Unknown",
            "compliance_flag": False,
            "compliance_notes": "",
            "contract_status": "unknown",
            "risk_level": "critical",
            "risk_summary": "Vendor data format invalid; treat as critical risk.",
        }

    vendor = next(
        (
            item
            for item in vendors
            if isinstance(item, dict) and item.get("vendor_id") == vendor_id
        ),
        None,
    )
    if vendor is None:
        return {
            "error": f"Vendor '{vendor_id}' not found in vendor data.",
            "vendor_id": vendor_id,
            "vendor_name": "Unknown",
            "compliance_flag": False,
            "compliance_notes": "",
            "contract_status": "unknown",
            "risk_level": "high",
            "risk_summary": "Vendor is unknown and should be treated as high risk.",
        }

    compliance_flag = bool(vendor.get("compliance_flag", False))
    contract_status = str(vendor.get("contract_status", "none"))
    compliance_notes = str(vendor.get("compliance_notes", ""))

    if compliance_flag:
        risk_level = "critical"
        risk_summary = (
            "Vendor has an active compliance flag and must be escalated for "
            "legal/compliance review."
        )
    elif contract_status == "expired":
        risk_level = "high"
        risk_summary = "Vendor contract is expired and cannot be used for direct approval."
    elif contract_status == "none":
        risk_level = "medium"
        risk_summary = "Vendor has no contract and requires additional procurement review."
    else:
        risk_level = "low"
        risk_summary = "Vendor has an active contract and no compliance flag."

    return {
        "vendor_id": vendor_id,
        "vendor_name": str(vendor.get("name", "")),
        "compliance_flag": compliance_flag,
        "compliance_notes": compliance_notes,
        "contract_status": contract_status,
        "risk_level": risk_level,
        "risk_summary": risk_summary,
    }
