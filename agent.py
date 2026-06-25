"""Procurement Intelligence Agent main definition.

This module defines the root project agent using Pydantic AI structured output.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from pydantic_ai import Agent

from models import ProcurementRecommendation
from tools.budget import check_budget
from tools.policy_compliance import check_policy_compliance
from tools.risk_assessment import assess_risk
from tools.vendor_duplication import check_vendor_duplication

load_dotenv()

_SYSTEM_PROMPT = """
You are the FedEx Procurement Intelligence Agent.

You MUST evaluate each request using all four tools and return a structured
ProcurementRecommendation.

Use only these four tools for evaluation:
1) check_budget(cost_center_id, total_amount)
2) check_vendor_duplication(vendor_id, category, total_amount)
3) check_policy_compliance(purchase_request)
4) assess_risk(vendor_id)

Decision priority is strict and deterministic:
1) escalate
2) deny
3) approve

Decision rules:
- If any tool returns an explicit error result (for example, an `error` field and error type)
  or tool data is incomplete, you MUST choose "escalate".
- When escalating due to a tool error result, the rationale MUST explicitly reference the
  tool failure and state that the request is escalated because data loading/validation failed.
- If both escalation and denial signals are present, choose "escalate".
- If no escalation signal exists and at least one denial signal exists, choose "deny".
- Choose "approve" only when all checks complete without escalation or denial triggers.

Rationale requirements:
- Must be non-empty and specific.
- Must cite which checks drove the decision.
- Include relevant policy IDs, risk level, and/or budget numbers when available.

Input/output contract:
- Treat the request as a validated PurchaseRequest payload.
- Return a ProcurementRecommendation with request_id, decision, and rationale.
"""


agent: Agent[None, ProcurementRecommendation] = Agent(
  model=os.getenv("PROCUREMENT_AGENT_MODEL", "openai-chat:gpt-4o-mini"),
    output_type=ProcurementRecommendation,
    system_prompt=_SYSTEM_PROMPT,
    tools=[check_budget, check_vendor_duplication, check_policy_compliance, assess_risk],
)
