"""Tests for agent-level error handling behavior."""

from __future__ import annotations

from unittest.mock import patch

from agent import recommend_procurement_action
from data.loader import load_requests
from models import PurchaseRequest


def _request_by_id(request_id: str) -> PurchaseRequest:
    """Load and validate a sample request by ID from mock data."""
    requests = load_requests()
    payload = next((item for item in requests if item.get("request_id") == request_id), None)
    if payload is None:
        raise AssertionError(f"Request {request_id} was not found in mock_data/requests.json")
    return PurchaseRequest.model_validate(payload)


def test_agent_returns_recommendation_when_budget_loader_raises_runtime_error() -> None:
    """Patch budget loader failure and confirm a safe, schema-valid recommendation is returned."""
    request = _request_by_id("REQ-003")

    with patch("data.loader.load_budgets", side_effect=RuntimeError("simulated budget backend failure")):
        recommendation = recommend_procurement_action(request)

    assert recommendation.decision == "escalate"
    assert isinstance(recommendation.rationale, str)
    assert recommendation.rationale.strip()
    assert "budget" in recommendation.rationale.lower()
    assert "simulated budget backend failure" in recommendation.rationale


def test_agent_escalates_with_unknown_vendor_and_mentions_it_in_rationale() -> None:
    """Unknown vendor IDs should trigger escalation with explicit unknown-vendor context."""
    request = PurchaseRequest(
        request_id="REQ-UNKNOWN-VENDOR",
        requestor="test.user@fedex.com",
        cost_center_id="CC-001",
        vendor_name="Unknown Vendor",
        vendor_id="V-UNKNOWN",
        category="training",
        item_description="Training support",
        quantity=1,
        unit_price=1000.0,
        total_amount=1000.0,
    )

    recommendation = recommend_procurement_action(request)

    assert recommendation.decision == "escalate"
    assert isinstance(recommendation.rationale, str)
    assert recommendation.rationale.strip()
    assert "v-unknown" in recommendation.rationale.lower()
    assert "not found" in recommendation.rationale.lower()
