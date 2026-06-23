"""Tests for policy compliance checks."""

from __future__ import annotations

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


def test_pol_002_manager_threshold_range_flags_request() -> None:
    """POL-002: any request from $10,000 to $49,999 triggers manager-approval escalation."""
    payload = _request_by_id("REQ-002")
    result = check_policy_compliance(_to_purchase_request(payload))

    assert 10_000.0 <= float(payload["total_amount"]) <= 49_999.99
    assert result["highest_severity"] == "escalate"
    assert any(
        violation["policy_id"] == "POL-002"
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
