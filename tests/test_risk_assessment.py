"""Tests for vendor risk assessment behavior."""

from __future__ import annotations

from tools.risk_assessment import assess_risk


def test_assess_risk_compliance_flagged_vendor_is_critical() -> None:
    """A compliance-flagged vendor is classified as critical risk."""
    result = assess_risk("V-006")

    assert result["compliance_flag"] is True
    assert result["contract_status"] == "active"
    assert result["risk_level"] == "critical"
    assert "error" not in result


def test_assess_risk_expired_contract_vendor_is_high() -> None:
    """An expired contract vendor is classified as high risk."""
    result = assess_risk("V-010")

    assert result["compliance_flag"] is False
    assert result["contract_status"] == "expired"
    assert result["risk_level"] == "high"
    assert "error" not in result


def test_assess_risk_no_contract_vendor_is_medium() -> None:
    """A no-contract vendor is classified as medium risk."""
    result = assess_risk("V-004")

    assert result["compliance_flag"] is False
    assert result["contract_status"] == "none"
    assert result["risk_level"] == "medium"
    assert "error" not in result


def test_assess_risk_active_compliant_vendor_is_low() -> None:
    """An active non-flagged vendor is classified as low risk."""
    result = assess_risk("V-002")

    assert result["compliance_flag"] is False
    assert result["contract_status"] == "active"
    assert result["risk_level"] == "low"
    assert "error" not in result


def test_assess_risk_missing_vendor_returns_error_context() -> None:
    """An unknown vendor ID returns explicit error context and non-low risk."""
    result = assess_risk("V-999")

    assert result["risk_level"] in {"high", "critical", "medium"}
    assert "error" in result
    assert "V-999" in str(result["error"])
    assert result["contract_status"] == "unknown"
    assert result["compliance_flag"] is False
