"""Unit tests for the policy compliance tool."""

from __future__ import annotations

from tools.policy_compliance import check_policy_compliance


def test_catering_always_denied() -> None:
    """POL-004: any catering purchase is denied regardless of amount or vendor."""
    result = check_policy_compliance("V-017", "catering", 2_550.00)
    assert result["violation_count"] >= 1
    policy_ids = [v["policy_id"] for v in result["violations"]]
    assert "POL-004" in policy_ids
    forced = [v["forced_decision"] for v in result["violations"] if v["policy_id"] == "POL-004"]
    assert forced[0] == "deny"


def test_compliance_flagged_vendor_escalates() -> None:
    """POL-006: V-006 (Vertex Consulting) has a compliance flag → escalate."""
    result = check_policy_compliance("V-006", "professional_services", 35_000.00)
    assert result["highest_severity"] == "escalate"
    policy_ids = [v["policy_id"] for v in result["violations"]]
    assert "POL-006" in policy_ids


def test_expired_contract_vendor_denied() -> None:
    """POL-005: V-010 (Crestview Print) has an expired contract → deny."""
    result = check_policy_compliance("V-010", "marketing_materials", 5_400.00)
    policy_ids = [v["policy_id"] for v in result["violations"]]
    assert "POL-005" in policy_ids
    forced = [v["forced_decision"] for v in result["violations"] if v["policy_id"] == "POL-005"]
    assert forced[0] == "deny"


def test_director_threshold_escalates() -> None:
    """POL-003: amount >= $50,000 requires director approval → escalate."""
    result = check_policy_compliance("V-002", "software_licenses", 50_000.00)
    assert result["highest_severity"] == "escalate"
    policy_ids = [v["policy_id"] for v in result["violations"]]
    assert "POL-003" in policy_ids


def test_near_threshold_escalates() -> None:
    """POL-003 near-threshold: $47,500 is within 5% of $50,000 → escalate."""
    result = check_policy_compliance("V-016", "hardware", 47_500.00)
    assert result["highest_severity"] == "escalate"
    policy_ids = [v["policy_id"] for v in result["violations"]]
    assert "POL-003" in policy_ids


def test_clean_request_has_no_violations() -> None:
    """A straightforward low-amount request with a clean vendor returns no violations."""
    # V-002 BlueSky: active contract, no compliance flag; software_licenses; $24,000
    result = check_policy_compliance("V-002", "software_licenses", 24_000.00)
    assert result["violation_count"] == 0
    assert result["highest_severity"] == "none"
    assert result["violations"] == []


def test_result_always_contains_required_keys() -> None:
    """Every result must contain violations, violation_count, and highest_severity."""
    result = check_policy_compliance("V-007", "facilities", 8_500.00)
    assert "violations" in result
    assert "violation_count" in result
    assert "highest_severity" in result


def test_highest_severity_escalate_takes_priority_over_deny() -> None:
    """When both deny and escalate violations apply, highest_severity must be escalate."""
    # V-006 has compliance flag (escalate) and is in professional_services;
    # add a catering-style scenario: compliance flag vendor + catering = POL-004(deny) + POL-006(escalate)
    result = check_policy_compliance("V-006", "catering", 5_000.00)
    # POL-004 forces deny, POL-006 forces escalate → highest must be escalate
    assert result["highest_severity"] == "escalate"
