from typing import Literal

from pydantic import BaseModel, Field, field_validator


class PurchaseRequest(BaseModel):
    """Validated input model for a procurement purchase request."""

    request_id: str
    requestor: str
    cost_center_id: str
    vendor_name: str
    vendor_id: str
    category: str
    item_description: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    total_amount: float = Field(gt=0)


class ProcurementRecommendation(BaseModel):
    """Structured procurement decision output from the agent."""

    request_id: str
    decision: Literal["approve", "deny", "escalate"]
    rationale: str

    @field_validator("rationale")
    @classmethod
    def rationale_must_be_non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("rationale must be non-empty")
        return value