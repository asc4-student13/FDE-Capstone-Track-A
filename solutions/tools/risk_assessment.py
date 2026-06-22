"""Risk assessment tool — returns a vendor's risk profile for agent decision-making."""

from __future__ import annotations

from data.loader import load_vendors

# Risk level mapping based on vendor attributes
_RISK_LEVELS = ("low", "medium", "high", "critical")


def assess_risk(vendor_id: str) -> dict[str, object]:
    """Return the risk profile for a vendor.

    Call this tool to check a vendor's compliance flag, contract status, and
    computed risk level before recommending approval of any purchase.

    Risk level computation:
    - ``critical``: compliance_flag is True (active legal/ethics investigation)
    - ``high``: contract_status is "expired" (no valid contract)
    - ``medium``: contract_status is "none" (no existing relationship)
    - ``low``: contract_status is "active" and no compliance flag

    Args:
        vendor_id: The vendor identifier from the purchase request (e.g. "V-006").

    Returns:
        A dict containing:
        - ``vendor_id`` (str): The vendor that was assessed.
        - ``vendor_name`` (str): Display name of the vendor.
        - ``compliance_flag`` (bool): True if an active compliance investigation exists.
        - ``compliance_notes`` (str): Details of any compliance flag.
        - ``contract_status`` (str): "active", "expired", or "none".
        - ``risk_level`` (str): One of "low", "medium", "high", "critical".
        - ``risk_summary`` (str): One-sentence explanation of the risk level.
        - ``error`` (str, optional): Present only if the vendor was not found or data failed.
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
            "risk_summary": "Vendor data unavailable — treat as critical risk.",
        }

    vendor = next((v for v in vendors if v["vendor_id"] == vendor_id), None)
    if vendor is None:
        return {
            "error": f"Vendor '{vendor_id}' not found in vendor database.",
            "vendor_id": vendor_id,
            "vendor_name": "Unknown",
            "compliance_flag": False,
            "compliance_notes": "",
            "contract_status": "unknown",
            "risk_level": "high",
            "risk_summary": (
                f"Vendor '{vendor_id}' is not in the approved vendor database. "
                "Treat as high risk — verify vendor identity before proceeding."
            ),
        }

    compliance_flag = bool(vendor.get("compliance_flag", False))
    contract_status = str(vendor.get("contract_status", "none"))
    notes = str(vendor.get("compliance_notes", ""))

    if compliance_flag:
        risk_level = "critical"
        risk_summary = (
            f"Vendor has an active compliance flag ({notes or 'see compliance team'}). "
            "All purchases must be escalated to Legal and Compliance."
        )
    elif contract_status == "expired":
        risk_level = "high"
        risk_summary = (
            f"Vendor contract has expired. Purchases may not proceed until "
            f"contract {vendor.get('contract_id', '')} is renewed."
        )
    elif contract_status == "none":
        risk_level = "medium"
        risk_summary = (
            "Vendor has no existing contract with FedEx. "
            "Procurement officer should verify vendor qualifications."
        )
    else:
        risk_level = "low"
        risk_summary = (
            f"Vendor holds an active contract ({vendor.get('contract_id', '')}) "
            "with no compliance issues."
        )

    return {
        "vendor_id": vendor_id,
        "vendor_name": str(vendor.get("name", "")),
        "compliance_flag": compliance_flag,
        "compliance_notes": notes,
        "contract_status": contract_status,
        "risk_level": risk_level,
        "risk_summary": risk_summary,
    }
