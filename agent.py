"""Procurement Intelligence Agent — main agent definition.

This module defines the Pydantic AI agent that accepts a PurchaseRequest,
runs all four procurement checks, and returns a ProcurementRecommendation.
"""

from __future__ import annotations

import os
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
You are the FedEx Procurement Intelligence Agent. Your job is to evaluate purchase
requests and produce structured recommendations. You are advisory — procurement
officers make the final decision.

## Decision Priority (enforced strictly in this order)

1. ESCALATE (highest priority) — use when any of the following are true:
   - assess_risk returns risk_level "critical" (compliance-flagged vendor)
   - check_policy_compliance returns a violation with forced_decision "escalate"
     (POL-006 compliance flag, POL-003 director threshold, near-threshold within 5%)
   - check_budget shows an overage AND the amount is within 5% of the $50,000 director threshold
   - Any tool returns an error (data unavailable → escalate for safety)

2. DENY — use when any of the following are true AND no escalation condition applies:
   - check_budget returns within_budget=False (budget overage)
   - check_vendor_duplication returns violation=True (POL-001 single-source breach)
   - check_policy_compliance returns a violation with forced_decision "deny"
     (POL-004 catering, POL-005 expired contract, POL-007 staffing)
   - assess_risk returns risk_level "high" (expired contract)

3. APPROVE (lowest priority) — use only when all checks pass:
   - Budget is sufficient
   - No policy violations
   - No vendor duplication above threshold
   - Risk level is "low" or "medium" with no specific policy trigger

## Tool Execution

Call ALL FOUR tools for every request. Do not short-circuit after the first finding —
the rationale must reference all relevant checks to be useful to the procurement officer.

Tools to call:
- check_budget(cost_center_id, total_amount)
- check_vendor_duplication(vendor_id, category, total_amount)
- check_policy_compliance(vendor_id, category, total_amount, quantity)
- assess_risk(vendor_id)

## Rationale Requirements

The rationale is read by procurement officers who make final decisions. It must:
- Be 2–4 complete sentences
- Name the specific check(s) that drove the decision (e.g. "POL-006", "CC-003 budget")
- Include relevant figures (amounts, remaining budget, overage)
- Never be vague (not acceptable: "The request was denied due to policy issues")

## Error Handling

If any tool returns an "error" key, include the error context in the rationale
and escalate the request rather than approving or denying without complete information.
"""


def _build_rationale(
   request: PurchaseRequest,
   budget: dict[str, Any],
   duplication: dict[str, Any],
   policy: dict[str, Any],
   risk: dict[str, Any],
   decision: str,
) -> str:
   """Build a concise, traceable rationale referencing all major checks."""
   reasons: list[str] = []
   if "error" in budget or "error" in duplication or "error" in policy or "error" in risk:
      errors = [
         str(result["error"])
         for result in (budget, duplication, policy, risk)
         if "error" in result
      ]
      reasons.append("Tool error detected: " + " | ".join(errors))

   reasons.append(
      (
         f"Budget check for {request.cost_center_id}: requested ${request.total_amount:,.2f}, "
         f"remaining ${float(budget.get('remaining_budget', 0.0)):,.2f}, "
         f"overage ${float(budget.get('overage', 0.0)):,.2f}."
      )
   )

   if bool(duplication.get("violation")):
      reasons.append(str(duplication.get("reason", "POL-001 violation detected.")))

   if int(policy.get("violation_count", 0)) > 0:
      policy_ids = ", ".join(v["policy_id"] for v in policy["violations"])
      reasons.append(
         f"Policy check triggered {int(policy['violation_count'])} violation(s): {policy_ids}."
      )

   reasons.append(
      f"Risk assessment for {request.vendor_id}: {risk.get('risk_level', 'unknown')} risk."
   )
   reasons.append(f"Final recommendation: {decision}.")
   return " ".join(reasons)


def evaluate_request(request: PurchaseRequest) -> ProcurementRecommendation:
   """Evaluate one purchase request with deterministic, no-network decision logic."""
   budget = check_budget(request.cost_center_id, request.total_amount)
   duplication = check_vendor_duplication(request.vendor_id, request.category, request.total_amount)
   policy = check_policy_compliance(
      request.vendor_id,
      request.category,
      request.total_amount,
      request.quantity,
   )
   risk = assess_risk(request.vendor_id)

   has_tool_error = any("error" in result for result in (budget, duplication, policy, risk))
   risk_level = str(risk.get("risk_level", "unknown"))
   policy_severity = str(policy.get("highest_severity", "none"))
   budget_over = not bool(budget.get("within_budget", False))
   near_director = abs(request.total_amount - 50_000.00) <= 2_500.00

   if has_tool_error or risk_level == "critical" or policy_severity == "escalate" or (
      budget_over and near_director
   ):
      decision = "escalate"
   elif (
      budget_over
      or bool(duplication.get("violation", False))
      or policy_severity == "deny"
      or risk_level == "high"
   ):
      decision = "deny"
   else:
      decision = "approve"

   rationale = _build_rationale(request, budget, duplication, policy, risk, decision)
   return ProcurementRecommendation(
      request_id=request.request_id,
      decision=decision,
      rationale=rationale,
   )


_configured_model = os.getenv("PROCUREMENT_AGENT_MODEL")
if not _configured_model:
   _configured_model = (
      "anthropic:claude-3-5-haiku-latest" if os.getenv("ANTHROPIC_API_KEY") else "test"
   )

agent: Agent[None, ProcurementRecommendation] = Agent(
   model=_configured_model,
    output_type=ProcurementRecommendation,
    system_prompt=_SYSTEM_PROMPT,
    tools=[check_budget, check_vendor_duplication, check_policy_compliance, assess_risk],
)
