"""Unit tests for the risk assessment tool."""

from __future__ import annotations

from tools.risk_assessment import assess_risk


def test_compliance_flagged_vendor_is_critical() -> None:
    """V-006 (Vertex Consulting) has a compliance flag → risk_level critical."""
    result = assess_risk("V-006")
    assert result["risk_level"] == "critical"
    assert result["compliance_flag"] is True
    assert "error" not in result


def test_expired_contract_vendor_is_high_risk() -> None:
    """V-010 (Crestview Print) has an expired contract → risk_level high."""
    result = assess_risk("V-010")
    assert result["risk_level"] == "high"
    assert result["contract_status"] == "expired"
    assert "error" not in result


def test_active_contract_vendor_is_low_risk() -> None:
    """V-002 (BlueSky Cloud Solutions) has an active contract and no flag → risk_level low."""
    result = assess_risk("V-002")
    assert result["risk_level"] == "low"
    assert result["compliance_flag"] is False
    assert result["contract_status"] == "active"


def test_unknown_vendor_returns_error_and_high_risk() -> None:
    """A vendor ID not in the database returns an error key and risk_level high."""
    result = assess_risk("V-999")
    assert "error" in result
    assert result["risk_level"] == "high"
    assert "V-999" in result["error"]


def test_result_contains_required_keys() -> None:
    """Every result must contain the seven standard keys."""
    result = assess_risk("V-007")
    for key in ("vendor_id", "vendor_name", "compliance_flag",
                "compliance_notes", "contract_status", "risk_level", "risk_summary"):
        assert key in result, f"Missing key: {key}"


def test_vendor_id_echoed_in_result() -> None:
    """The vendor_id in the result must match the input."""
    result = assess_risk("V-007")
    assert result["vendor_id"] == "V-007"


def test_risk_summary_is_non_empty() -> None:
    """risk_summary must be a non-empty string for every vendor."""
    result = assess_risk("V-002")
    assert isinstance(result["risk_summary"], str)
    assert result["risk_summary"].strip()
