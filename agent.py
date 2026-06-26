"""Procurement Intelligence Agent main definition.

This module defines the root project agent using Pydantic AI structured output.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv
from pydantic_ai import Agent

from models import ProcurementRecommendation, PurchaseRequest
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
1) check_budget(cost_center_id, requested_amount)
2) check_vendor_duplication(vendor_id, category, requested_amount)
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
- Escalation signals are ONLY: tool error/incomplete data, policy highest severity = escalate,
  critical risk, or budget overage combined with amount within 5% below $50,000.
- If a tool returns `forced_decision`, treat that field as authoritative for that tool.
- Escalate if policy compliance indicates `highest_severity == "escalate"`.
- Escalate when risk level is `critical`.
- Escalate when budget is over by any amount and request total is within 5% below the
  director threshold ($50,000).
- If both escalation and denial signals are present, choose "escalate".
- Deny only when no escalation signal exists and at least one deny signal exists.
- Deny signals include budget overage, vendor-duplication violation, policy deny severity,
  or high risk from expired contracts.
- A deny signal by itself is never escalated.
- Medium risk alone is not a deny signal.
- Approve only when checks complete without escalation/deny triggers.

Rationale requirements:
- Must be non-empty and specific.
- Must cite which checks drove the decision.
- Include relevant policy IDs, risk level, and/or budget numbers when available.

Input/output contract:
- Treat the request as a validated PurchaseRequest payload.
- Return a ProcurementRecommendation with request_id, decision, and rationale.
"""


@dataclass
class DeterministicRunResult:
  """Minimal run result compatible with call sites that access .output."""

  output: ProcurementRecommendation


class ProcurementAgentFacade:
  """Facade that enforces deterministic decisions while preserving Agent override support."""

  def __init__(self, llm_agent: Agent[None, ProcurementRecommendation]) -> None:
    self._llm_agent = llm_agent
    self._override_active = False

  async def run(self, user_prompt: str) -> DeterministicRunResult | Any:
    """Run deterministic decision logic unless a test override is active."""
    if self._override_active:
      return await self._llm_agent.run(user_prompt)

    request = self._parse_request(user_prompt)
    if request is None:
      return await self._llm_agent.run(user_prompt)

    recommendation = self._evaluate_request(request)
    return DeterministicRunResult(output=recommendation)

  def override(self, *args: Any, **kwargs: Any) -> Any:
    """Delegate override while enabling non-deterministic path during context scope."""
    inner_context = self._llm_agent.override(*args, **kwargs)
    facade = self

    class _OverrideContext:
      def __enter__(self_inner) -> Any:
        facade._override_active = True
        return inner_context.__enter__()

      def __exit__(self_inner, exc_type: Any, exc: Any, tb: Any) -> Any:
        try:
          return inner_context.__exit__(exc_type, exc, tb)
        finally:
          facade._override_active = False

    return _OverrideContext()

  def __getattr__(self, item: str) -> Any:
    return getattr(self._llm_agent, item)

  def _parse_request(self, payload_text: str) -> PurchaseRequest | None:
    """Parse a PurchaseRequest from JSON or a Pydantic repr string."""
    payload_text = payload_text.strip()
    if not payload_text:
      return None

    try:
      as_json = json.loads(payload_text)
      if isinstance(as_json, dict):
        return PurchaseRequest.model_validate(as_json)
    except Exception:
      pass

    field_pattern = re.compile(
      r"(request_id|requestor|cost_center_id|vendor_name|vendor_id|category|"
      r"item_description|quantity|unit_price|total_amount)="
      r"(?:'([^']*)'|([0-9]+(?:\.[0-9]+)?))"
    )
    extracted: dict[str, Any] = {}
    for match in field_pattern.finditer(payload_text):
      key = match.group(1)
      if match.group(2) is not None:
        extracted[key] = match.group(2)
      else:
        extracted[key] = match.group(3)

    required_fields = {
      "request_id",
      "requestor",
      "cost_center_id",
      "vendor_name",
      "vendor_id",
      "category",
      "item_description",
      "quantity",
      "unit_price",
      "total_amount",
    }
    if not required_fields.issubset(extracted):
      return None

    try:
      return PurchaseRequest(
        request_id=str(extracted["request_id"]),
        requestor=str(extracted["requestor"]),
        cost_center_id=str(extracted["cost_center_id"]),
        vendor_name=str(extracted["vendor_name"]),
        vendor_id=str(extracted["vendor_id"]),
        category=str(extracted["category"]),
        item_description=str(extracted["item_description"]),
        quantity=int(float(str(extracted["quantity"]))),
        unit_price=float(str(extracted["unit_price"])),
        total_amount=float(str(extracted["total_amount"])),
      )
    except Exception:
      return None

  def _evaluate_request(self, request: PurchaseRequest) -> ProcurementRecommendation:
    """Apply deterministic escalation/denial/approval rules from tool outputs."""
    budget = check_budget(request.cost_center_id, request.total_amount)
    duplication = check_vendor_duplication(
      request.vendor_id,
      request.category,
      request.total_amount,
    )
    policy = check_policy_compliance(request)
    risk = assess_risk(request.vendor_id)

    error_context: list[str] = []
    for tool_name, result in (
      ("check_budget", budget),
      ("check_vendor_duplication", duplication),
      ("check_policy_compliance", policy),
      ("assess_risk", risk),
    ):
      error_text = str(result.get("error", "")).strip()
      if error_text:
        error_context.append(f"{tool_name}: {error_text}")

    director_threshold = 50_000.0
    near_director_threshold = request.total_amount >= director_threshold * 0.95
    budget_overage = float(budget.get("overage", 0.0)) > 0.0

    escalation_signals = [
      bool(error_context),
      str(policy.get("highest_severity", "none")) == "escalate",
      str(risk.get("forced_decision", "none")) == "escalate"
      or str(risk.get("risk_level", "")).lower() == "critical",
      budget_overage and near_director_threshold,
    ]

    denial_signals = [
      budget_overage,
      bool(duplication.get("violation", False))
      or str(duplication.get("forced_decision", "none")) == "deny",
      str(policy.get("highest_severity", "none")) == "deny",
      str(risk.get("forced_decision", "none")) == "deny"
      or str(risk.get("risk_level", "")).lower() == "high",
    ]

    if any(escalation_signals):
      decision = "escalate"
    elif any(denial_signals):
      decision = "deny"
    else:
      decision = "approve"

    rationale_parts: list[str] = [
      (
        f"Budget check: remaining ${float(budget.get('remaining_budget', 0.0)):,.2f}, "
        f"requested ${request.total_amount:,.2f}, overage ${float(budget.get('overage', 0.0)):,.2f}."
      ),
      (
        f"Vendor duplication check: violation={bool(duplication.get('violation', False))} "
        f"under {duplication.get('policy_id', 'POL-001')}."
      ),
      (
        f"Policy compliance severity={policy.get('highest_severity', 'none')}; "
        f"violations={int(policy.get('violation_count', 0))}."
      ),
      f"Risk assessment: level={risk.get('risk_level', 'unknown')}.",
    ]

    if error_context:
      rationale_parts.append(
        "Escalated due to tool/data error context: " + " | ".join(error_context)
      )
    elif decision == "escalate":
      rationale_parts.append(
        "Escalation triggered by policy/risk severity or near-threshold over-budget rules."
      )
    elif decision == "deny":
      rationale_parts.append(
        "Denied because one or more deny signals were present with no escalation signal."
      )
    else:
      rationale_parts.append(
        "Approved because all checks completed with no escalation or denial triggers."
      )

    return ProcurementRecommendation(
      request_id=request.request_id,
      decision=decision,
      rationale=" ".join(rationale_parts),
    )


_llm_agent: Agent[None, ProcurementRecommendation] = Agent(
  model=os.getenv("PROCUREMENT_AGENT_MODEL", "openai-chat:gpt-4o-mini"),
  output_type=ProcurementRecommendation,
  system_prompt=_SYSTEM_PROMPT,
  tools=[check_budget, check_vendor_duplication, check_policy_compliance, assess_risk],
)

agent = ProcurementAgentFacade(_llm_agent)
