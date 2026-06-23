"""Pydantic v2 models for procurement agent input and output."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PurchaseRequest(BaseModel):
    """Purchase request payload schema."""

    model_config = ConfigDict(str_strip_whitespace=True)

    request_id: str = Field(min_length=1)
    requestor: str = Field(min_length=1)
    cost_center_id: str = Field(min_length=1)
    vendor_name: str = Field(min_length=1)
    vendor_id: str = Field(min_length=1)
    category: str = Field(min_length=1)
    item_description: str = Field(min_length=1)
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    total_amount: float = Field(gt=0)
    expected_outcome: Literal["approve", "deny", "escalate", "ambiguous"] | None = None
    outcome_reason: str | None = None

    @field_validator("outcome_reason")
    @classmethod
    def validate_outcome_reason(cls, value: str | None) -> str | None:
        """Ensure optional outcome_reason is non-empty when provided."""
        if value is not None and not value.strip():
            raise ValueError("outcome_reason must be a non-empty string when provided")
        return value


class ProcurementRecommendation(BaseModel):
    """Structured recommendation output schema."""

    model_config = ConfigDict(str_strip_whitespace=True)

    decision: Literal["approve", "deny", "escalate"]
    rationale: str

    @field_validator("rationale")
    @classmethod
    def validate_rationale(cls, value: str) -> str:
        """Ensure rationale is non-empty after trimming whitespace."""
        if not value.strip():
            raise ValueError("rationale must be a non-empty string")
        return value
