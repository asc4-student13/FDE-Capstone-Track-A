"""Tests for risk assessment tool behavior using real mock data."""

from __future__ import annotations

from tools.risk_assessment import assess_risk


def test_assess_risk_compliance_flag_escalates() -> None:
    """V-006 has a compliance flag and must be critical/escalate."""
    result = assess_risk("V-006")

    assert result["check"] == "risk_assessment"
    assert result["status"] == "escalate"
    assert result["risk_level"] == "critical"
    assert result["compliance_flag"] is True
    assert "compliance_flag" in result["risk_factors"]


def test_assess_risk_expired_contract_escalates() -> None:
    """V-010 has an expired contract and should escalate with high risk."""
    result = assess_risk("V-010")

    assert result["status"] == "escalate"
    assert result["risk_level"] == "high"
    assert result["contract_status"] == "expired"
    assert "expired_contract" in result["risk_factors"]


def test_assess_risk_active_contract_passes() -> None:
    """V-002 has an active contract and no flag, so risk should pass."""
    result = assess_risk("V-002")

    assert result["status"] == "pass"
    assert result["risk_level"] == "low"
    assert result["contract_status"] == "active"


def test_assess_risk_unknown_vendor_errors() -> None:
    """Unknown vendors should return a structured error result."""
    result = assess_risk("V-999")

    assert result["status"] == "error"
    assert result["risk_level"] == "high"
    assert result["contract_status"] == "unknown"
    assert "vendor_not_found" in result["risk_factors"]
    assert "V-999" in result["message"]


def test_assess_risk_near_director_threshold_escalates_contextually() -> None:
    """Near-threshold requests may escalate even when base vendor risk is low."""
    result = assess_risk("V-016", total_amount=47_500.0)

    assert result["risk_level"] == "low"
    assert result["status"] == "escalate"
    assert "near_director_threshold" in result["risk_factors"]
