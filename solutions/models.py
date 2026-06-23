"""Pydantic v2 data models for the Procurement Intelligence Agent."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class PurchaseRequest(BaseModel):
    """A purchase request submitted to the procurement system for review.

    Fields match the records in mock_data/requests.json.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    request_id: str = Field(min_length=1, description="Unique identifier for the purchase request")
    requestor: str = Field(min_length=1, description="Name of the employee submitting the request")
    cost_center_id: str = Field(min_length=1, description="Cost center responsible for this purchase")
    vendor_name: str = Field(min_length=1, description="Display name of the vendor")
    vendor_id: str = Field(min_length=1, description="Unique vendor identifier (e.g. V-006)")
    category: str = Field(min_length=1, description="Purchase category (e.g. office_supplies, catering)")
    item_description: str = Field(min_length=1, description="Plain-language description of what is being purchased")
    quantity: int = Field(gt=0, description="Number of units")
    unit_price: float = Field(gt=0, description="Price per unit in USD")
    total_amount: float = Field(gt=0, description="Total purchase amount in USD (quantity × unit_price)")
    expected_outcome: Literal["approve", "deny", "escalate", "ambiguous"] | None = Field(
        default=None,
        description="Instructor reference outcome from sample data",
    )
    outcome_reason: str | None = Field(
        default=None,
        description="Instructor reference rationale from sample data",
    )

    @field_validator("outcome_reason")
    @classmethod
    def outcome_reason_non_empty(cls, value: str | None) -> str | None:
        """If provided, outcome_reason must not be blank."""
        if value is None:
            return value
        if not value.strip():
            raise ValueError("outcome_reason must be a non-empty string when provided")
        return value

    @model_validator(mode="after")
    def total_amount_matches_units(self) -> "PurchaseRequest":
        """Require total_amount to approximately equal quantity * unit_price."""
        expected_total = float(self.quantity) * float(self.unit_price)
        if abs(float(self.total_amount) - expected_total) > 0.01:
            raise ValueError("total_amount must approximately equal quantity * unit_price")
        return self


class ProcurementRecommendation(BaseModel):
    """The agent's structured recommendation for a purchase request.

    This is the sole output type of the procurement agent. The ``decision``
    field is always one of the three allowed literals. The ``rationale``
    must be a non-empty string referencing the specific check(s) that drove
    the decision — it is read directly by procurement officers.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    request_id: str = Field(description="The request_id from the originating PurchaseRequest")
    decision: Literal["approve", "deny", "escalate"] = Field(
        description="The agent's recommendation: approve, deny, or escalate"
    )
    rationale: str = Field(
        description=(
            "Non-empty explanation of the decision. Must name the specific check(s) "
            "that drove the outcome (e.g. policy ID, budget figures, vendor flags)."
        )
    )

    @field_validator("rationale")
    @classmethod
    def rationale_non_empty(cls, v: str) -> str:
        """Ensure the rationale is not blank after whitespace stripping."""
        if not v.strip():
            raise ValueError("rationale must be a non-empty string")
        return v
