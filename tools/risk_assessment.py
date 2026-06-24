"""Risk assessment tool for vendor compliance and contract-state evaluation."""

from __future__ import annotations

from typing import Any

from data.loader import load_vendors

_ALLOWED_RISK_LEVELS = {"low", "medium", "high", "critical"}


def assess_risk(vendor_id: str) -> dict[str, object]:
    """Assess procurement risk for a vendor ID using compliance and contract signals.

    This tool loads vendor records through :func:`data.loader.load_vendors` and
    computes a normalized risk level for agent decision-making.

    Risk decision order:
    - ``critical``: vendor has an active ``compliance_flag``.
    - ``high``: vendor has ``contract_status`` set to ``"expired"``.
    - ``medium``: vendor has ``contract_status`` set to ``"none"``.
    - ``low``: vendor has ``contract_status`` set to ``"active"`` and no
      compliance flag.

    Args:
        vendor_id: Vendor identifier from an incoming purchase request
            (for example, ``"V-006"``).

    Returns:
        A structured dictionary containing:

        - ``vendor_id`` (str): Echo of the input vendor ID.
        - ``vendor_name`` (str): Vendor display name when found; ``"Unknown"`` when
          vendor data cannot be matched.
        - ``compliance_flag`` (bool): Vendor compliance flag status.
        - ``contract_status`` (str): Vendor contract status (``active``, ``expired``,
          ``none``, or ``unknown``).
        - ``risk_level`` (str): Computed risk level (``low``, ``medium``, ``high``,
          or ``critical``).
        - ``error`` (str, optional): Explicit error context when vendor data cannot
          be loaded or the vendor ID is missing from the dataset.

    Notes:
        Tool failures are surfaced in ``error`` instead of raising exceptions so the
        calling agent can include that context in its final recommendation rationale.
    """
    try:
        vendors = load_vendors()
    except Exception as exc:  # pragma: no cover - defensive fallback for loader failures.
        return {
            "vendor_id": vendor_id,
            "vendor_name": "Unknown",
            "compliance_flag": False,
            "contract_status": "unknown",
            "risk_level": "critical",
            "error": f"Vendor data could not be loaded: {exc}",
        }

    vendor_record: dict[str, Any] | None = next(
        (
            vendor
            for vendor in vendors
            if isinstance(vendor, dict)
            and str(vendor.get("vendor_id", "")).strip() == vendor_id
        ),
        None,
    )

    if vendor_record is None:
        return {
            "vendor_id": vendor_id,
            "vendor_name": "Unknown",
            "compliance_flag": False,
            "contract_status": "unknown",
            "risk_level": "high",
            "error": (
                f"Vendor '{vendor_id}' not found in vendor records; "
                "risk assessment cannot verify compliance or contract status."
            ),
        }

    compliance_flag = bool(vendor_record.get("compliance_flag", False))
    contract_status = str(vendor_record.get("contract_status", "none")).strip().lower()

    if compliance_flag:
        risk_level = "critical"
    elif contract_status == "expired":
        risk_level = "high"
    elif contract_status == "none":
        risk_level = "medium"
    elif contract_status == "active":
        risk_level = "low"
    else:
        risk_level = "high"

    if risk_level not in _ALLOWED_RISK_LEVELS:  # pragma: no cover - defensive contract guard.
        risk_level = "high"

    return {
        "vendor_id": vendor_id,
        "vendor_name": str(vendor_record.get("name", "")).strip(),
        "compliance_flag": compliance_flag,
        "contract_status": contract_status or "unknown",
        "risk_level": risk_level,
    }
