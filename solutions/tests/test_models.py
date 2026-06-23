"""Unit tests for Pydantic procurement models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from models import ProcurementRecommendation, PurchaseRequest


def _valid_request_payload() -> dict[str, object]:
    return {
        "request_id": "REQ-001",
        "requestor": "M. Okonkwo",
        "cost_center_id": "CC-001",
        "vendor_name": "BlueSky Cloud Solutions",
        "vendor_id": "V-002",
        "category": "software_licenses",
        "item_description": "Annual license renewal",
        "quantity": 500,
        "unit_price": 48.0,
        "total_amount": 24_000.0,
    }


def test_purchase_request_accepts_valid_payload() -> None:
    req = PurchaseRequest(**_valid_request_payload())
    assert req.request_id == "REQ-001"


def test_purchase_request_rejects_non_positive_numeric_fields() -> None:
    payload = _valid_request_payload()
    payload["quantity"] = 0
    with pytest.raises(ValidationError):
        PurchaseRequest(**payload)


def test_purchase_request_rejects_inconsistent_total_amount() -> None:
    payload = _valid_request_payload()
    payload["total_amount"] = 24_001.0
    with pytest.raises(ValidationError):
        PurchaseRequest(**payload)


def test_purchase_request_expected_outcome_is_optional_and_constrained() -> None:
    payload = _valid_request_payload()
    payload["expected_outcome"] = "ambiguous"
    req = PurchaseRequest(**payload)
    assert req.expected_outcome == "ambiguous"

    payload["expected_outcome"] = "maybe"
    with pytest.raises(ValidationError):
        PurchaseRequest(**payload)


def test_purchase_request_outcome_reason_if_provided_must_be_non_empty() -> None:
    payload = _valid_request_payload()
    payload["outcome_reason"] = "   "
    with pytest.raises(ValidationError):
        PurchaseRequest(**payload)


def test_procurement_recommendation_decision_and_rationale_constraints() -> None:
    valid = ProcurementRecommendation(
        request_id="REQ-001",
        decision="approve",
        rationale="All checks passed.",
    )
    assert valid.decision == "approve"

    with pytest.raises(ValidationError):
        ProcurementRecommendation(
            request_id="REQ-001",
            decision="invalid",
            rationale="test",
        )

    with pytest.raises(ValidationError):
        ProcurementRecommendation(
            request_id="REQ-001",
            decision="deny",
            rationale="   ",
        )
