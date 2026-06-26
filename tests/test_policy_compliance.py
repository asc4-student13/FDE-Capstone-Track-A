"""Tests for policy compliance checks."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from data.loader import load_requests
from models import PurchaseRequest
from tools.policy_compliance import check_policy_compliance


def _request_by_id(request_id: str) -> dict[str, object]:
    """Return a request payload from fixture data by request ID."""
    requests = load_requests()
    return next(req for req in requests if req["request_id"] == request_id)


def _to_purchase_request(payload: dict[str, object]) -> PurchaseRequest:
    """Convert fixture payload to PurchaseRequest model input."""
    return PurchaseRequest(
        request_id=str(payload["request_id"]),
        requestor=str(payload["requestor"]),
        cost_center_id=str(payload["cost_center_id"]),
        vendor_name=str(payload["vendor_name"]),
        vendor_id=str(payload["vendor_id"]),
        category=str(payload["category"]),
        item_description=str(payload["item_description"]),
        quantity=int(payload["quantity"]),
        unit_price=float(payload["unit_price"]),
        total_amount=float(payload["total_amount"]),
    )


def test_pol_004_req_009_catering_prohibition_denies() -> None:
    """POL-004: REQ-009 catering request is denied at $3,200."""
    payload = _request_by_id("REQ-009")
    payload = dict(payload)
    payload["unit_price"] = 3200.0
    payload["quantity"] = 1
    payload["total_amount"] = 3200.0

    result = check_policy_compliance(_to_purchase_request(payload))

    assert result["highest_severity"] == "deny"
    assert any(
        violation["policy_id"] == "POL-004"
        and violation["forced_decision"] == "deny"
        for violation in result["violations"]
    )


def test_pol_002_manager_threshold_range_is_process_note_only() -> None:
    """POL-002 range does not force escalation without explicit approval metadata fields."""
    payload = _request_by_id("REQ-002")
    result = check_policy_compliance(_to_purchase_request(payload))

    assert 10_000.0 <= float(payload["total_amount"]) <= 49_999.99
    assert result["highest_severity"] == "none"
    assert not any(
        violation["policy_id"] == "POL-002" for violation in result["violations"]
    )


def test_pol_003_near_director_threshold_escalates() -> None:
    """Amounts within 5% below director threshold should escalate."""
    payload = _request_by_id("REQ-014")
    result = check_policy_compliance(_to_purchase_request(payload))

    assert result["highest_severity"] == "escalate"
    assert any(
        violation["policy_id"] == "POL-003"
        and violation["forced_decision"] == "escalate"
        for violation in result["violations"]
    )


def test_pol_005_req_007_expired_contract_denies() -> None:
    """POL-005: REQ-007 with Crestview Print is denied due to expired contract."""
    payload = _request_by_id("REQ-007")
    result = check_policy_compliance(_to_purchase_request(payload))

    assert result["highest_severity"] == "deny"
    assert any(
        violation["policy_id"] == "POL-005"
        and violation["forced_decision"] == "deny"
        for violation in result["violations"]
    )


def test_purchase_request_missing_vendor_id_fails_validation() -> None:
    """PurchaseRequest rejects payloads that omit required vendor_id."""
    payload = _request_by_id("REQ-001")

    with pytest.raises(ValidationError) as exc_info:
        PurchaseRequest(
            request_id=str(payload["request_id"]),
            requestor=str(payload["requestor"]),
            cost_center_id=str(payload["cost_center_id"]),
            vendor_name=str(payload["vendor_name"]),
            category=str(payload["category"]),
            item_description=str(payload["item_description"]),
            quantity=int(payload["quantity"]),
            unit_price=float(payload["unit_price"]),
            total_amount=float(payload["total_amount"]),
        )

    assert "vendor_id" in str(exc_info.value)
