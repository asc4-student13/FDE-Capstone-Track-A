from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class PurchaseRequest(BaseModel):
    """Validated input model for a procurement purchase request."""

    request_id: str
    requester: str
    cost_center: str
    vendor: str
    category: str
    item_details: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    total_amount: float = Field(gt=0)


class ProcurementRecommendation(BaseModel):
    """Validated output model for a procurement decision recommendation."""

    decision: Literal["approve", "deny", "escalate"]
    rationale: str

    @field_validator("rationale")
    @classmethod
    def rationale_must_be_non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("rationale must be non-empty")
        return value
