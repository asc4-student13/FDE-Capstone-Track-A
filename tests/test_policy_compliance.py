"""Tests for policy compliance behavior using real mock data."""

from __future__ import annotations

from tools.policy_compliance import check_policy_compliance


def test_pol004_catering_prohibition_req009_denies() -> None:
    """POL-004 must deny catering requests regardless of amount."""
    result = check_policy_compliance(
        {
            "request_id": "REQ-009",
            "requestor": "P. Harrington",
            "cost_center_id": "CC-005",
            "vendor_name": "Summit Catering Co.",
            "vendor_id": "V-017",
            "category": "catering",
            "item_description": "Executive leadership offsite lunch service",
            "quantity": 1,
            "unit_price": 3200.00,
            "total_amount": 3200.00,
            "expected_outcome": "deny",
            "outcome_reason": "POL-004 prohibited category.",
        }
    )

    assert result["check"] == "policy_compliance"
    assert result["status"] == "fail"
    assert "POL-004" in result["triggered_policy_ids"]

    pol004 = [item for item in result["violations"] if item["policy_id"] == "POL-004"]
    assert len(pol004) == 1
    assert pol004[0]["forced_decision"] == "deny"
    assert pol004[0]["rule_description"]


def test_pol002_manager_threshold_between_10000_and_49999_escalates() -> None:
    """POL-002 should escalate requests in manager-approval range."""
    result = check_policy_compliance(
        {
            "request_id": "REQ-005",
            "requestor": "A. Patel",
            "cost_center_id": "CC-001",
            "vendor_name": "Ironclad Security Systems",
            "vendor_id": "V-011",
            "category": "security",
            "item_description": "Access control support",
            "quantity": 1,
            "unit_price": 14200.00,
            "total_amount": 14200.00,
            "expected_outcome": "approve",
            "outcome_reason": "Within budget.",
        }
    )

    assert result["status"] == "escalate"
    assert "POL-002" in result["triggered_policy_ids"]

    pol002 = [item for item in result["violations"] if item["policy_id"] == "POL-002"]
    assert len(pol002) == 1
    assert pol002[0]["forced_decision"] == "escalate"
    assert pol002[0]["rule_description"]


def test_pol005_expired_contract_req007_denies() -> None:
    """POL-005 must deny requests that use an expired-contract vendor."""
    result = check_policy_compliance(
        {
            "request_id": "REQ-007",
            "requestor": "C. Johnson",
            "cost_center_id": "CC-010",
            "vendor_name": "Crestview Print and Media",
            "vendor_id": "V-010",
            "category": "marketing_materials",
            "item_description": "Campaign collateral",
            "quantity": 1,
            "unit_price": 5400.00,
            "total_amount": 5400.00,
            "expected_outcome": "deny",
            "outcome_reason": "Expired contract.",
        }
    )

    assert result["status"] == "fail"
    assert "POL-005" in result["triggered_policy_ids"]

    pol005 = [item for item in result["violations"] if item["policy_id"] == "POL-005"]
    assert len(pol005) == 1
    assert pol005[0]["forced_decision"] == "deny"
    assert pol005[0]["rule_description"]
