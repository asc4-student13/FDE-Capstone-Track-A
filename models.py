"""Pydantic v2 models for procurement request and recommendation data."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class PurchaseRequest(BaseModel):
    """Purchase request input model with typed required fields."""

    request_id: str
    requestor: str
    cost_center_id: str
    vendor_id: str
    vendor_name: str
    category: str
    item_description: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    total_amount: float = Field(gt=0)


class ProcurementRecommendation(BaseModel):
    """Structured recommendation model with constrained decision outcomes."""

    decision: Literal["approve", "deny", "escalate"]
    rationale: str

    @field_validator("rationale")
    @classmethod
    def validate_rationale_non_empty(cls, value: str) -> str:
        """Reject blank or whitespace-only rationale values."""
        if not value.strip():
            raise ValueError("rationale must be a non-empty string")
        return value
