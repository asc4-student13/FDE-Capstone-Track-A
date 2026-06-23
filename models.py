"""Pydantic v2 data models for the Procurement Intelligence Agent."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PurchaseRequest(BaseModel):
    """A purchase request submitted to the procurement system for review.

    Fields match the records in mock_data/requests.json.
    The ``expected_outcome`` and ``outcome_reason`` fields present in the JSON
    are intentionally excluded — the agent must derive its own decision.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    request_id: str = Field(description="Unique identifier for the purchase request")
    requestor: str = Field(description="Name of the employee submitting the request")
    cost_center_id: str = Field(description="Cost center responsible for this purchase")
    vendor_name: str = Field(description="Display name of the vendor")
    vendor_id: str = Field(description="Unique vendor identifier (e.g. V-006)")
    category: str = Field(description="Purchase category (e.g. office_supplies, catering)")
    item_description: str = Field(description="Plain-language description of what is being purchased")
    quantity: int = Field(gt=0, description="Number of units")
    unit_price: float = Field(gt=0, description="Price per unit in USD")
    total_amount: float = Field(gt=0, description="Total purchase amount in USD (quantity × unit_price)")


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
