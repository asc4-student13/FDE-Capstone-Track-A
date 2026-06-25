"""Pydantic AI procurement agent definition and invocation helpers."""

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
_ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


_SYSTEM_PROMPT = """
You are the FedEx Procurement Intelligence Agent.

You MUST evaluate each purchase request by calling ALL FOUR tools exactly once:
1) check_budget(cost_center_id, total_amount)
2) check_vendor_duplication(vendor_id, category, total_amount)
3) check_policy_compliance(request)
4) assess_risk(vendor_id, total_amount, category, cost_center_id)

Decision priority is strict and must always be applied in this order:
1. escalate
2. deny
3. approve
Explicit priority shorthand: escalate > deny > approve.

Decision mapping rules:
- If any check returns status=error, choose escalate.
- Else if any check returns status=escalate, choose escalate.
- Else if any check returns status=fail, choose deny.
- Else choose approve.

Rationale requirements:
- Use the following rationale template in complete sentences, 2 to 4 sentences total:
    1) Sentence 1: State the final recommendation (approve, deny, or escalate) and
         name the primary check(s) that drove it (budget, vendor_duplication,
         policy_compliance, risk_assessment).
    2) Sentence 2: Provide concrete evidence from tool output, including at least one
         of: policy ID(s), dollar amount(s), vendor name/ID, remaining budget, overage,
         risk level, or conflicting vendor details.
    3) Optional sentence(s): Add secondary triggered checks or additional context.
- Do not use bullet points or list formatting in rationale text.
- Never output vague text such as "policy issues" or "risk concerns" without specific details.

Error handling requirements:
- Do not ignore tool failures.
- If any tool returns status=error, reference that error in rationale and
    escalate the request.
- Surface tool errors in rationale and keep output schema-valid.
- Default to escalate on uncertainty or incomplete data.
""".strip()


agent: Agent[None, ProcurementRecommendation] = Agent(
    model=os.getenv("PROCUREMENT_AGENT_MODEL", "anthropic:claude-3-5-haiku-latest"),
    output_type=ProcurementRecommendation,
    system_prompt=_SYSTEM_PROMPT,
    tools=[
        check_budget,
        check_vendor_duplication,
        check_policy_compliance,
        assess_risk,
    ],
)


def _normalize_request(request: PurchaseRequest | dict[str, Any]) -> PurchaseRequest:
    """Normalize a dict or model input into a validated PurchaseRequest."""
    if isinstance(request, PurchaseRequest):
        return request
    return PurchaseRequest.model_validate(request)


def _decision_from_preflight(preflight_results: dict[str, dict[str, object]]) -> str:
    """Map tool statuses to a deterministic final decision.

    Priority order is escalate > deny > approve.
    """
    statuses = [str(result.get("status", "")).lower() for result in preflight_results.values()]
    if any(status in {"error", "escalate"} for status in statuses):
        return "escalate"
    if any(status == "fail" for status in statuses):
        return "deny"
    return "approve"


def recommend_procurement_action(
    request: PurchaseRequest | dict[str, Any],
) -> ProcurementRecommendation:
    """Run the configured Pydantic AI agent and return a typed recommendation.

    This wrapper keeps a schema-valid fallback behavior if runtime model/tool
    execution fails unexpectedly.
    """
    parsed_request = _normalize_request(request)

    preflight_results = {
        "budget": check_budget(parsed_request.cost_center_id, parsed_request.total_amount),
        "vendor_duplication": check_vendor_duplication(
            parsed_request.vendor_id,
            parsed_request.category,
            parsed_request.total_amount,
        ),
        "policy_compliance": check_policy_compliance(parsed_request),
        "risk_assessment": assess_risk(
            parsed_request.vendor_id,
            total_amount=parsed_request.total_amount,
            category=parsed_request.category,
            cost_center_id=parsed_request.cost_center_id,
        ),
    }

    error_messages: list[str] = []
    for check_name, result in preflight_results.items():
        if str(result.get("status", "")).lower() == "error":
            message = str(result.get("message", "Unknown error"))
            error_messages.append(f"{check_name}: {message}")

    if error_messages:
        return ProcurementRecommendation(
            decision="escalate",
            rationale=(
                "One or more tool checks failed; escalating for human review. "
                + " | ".join(error_messages)
            ),
        )

    user_prompt = (
        "Evaluate the following PurchaseRequest and return a procurement "
        "recommendation. You must call all four registered tools and apply the "
        "decision priority escalate > deny > approve.\n\n"
        f"PurchaseRequest JSON:\n{parsed_request.model_dump_json(indent=2)}"
    )

    try:
        result = agent.run_sync(user_prompt)
        recommendation = getattr(result, "data", None)
        if recommendation is None:
            recommendation = getattr(result, "output", None)
        if recommendation is None:
            raise RuntimeError("Agent run returned no structured output payload.")
        return recommendation
    except Exception as exc:
        fallback_decision = _decision_from_preflight(preflight_results)
        configured_model = os.getenv("PROCUREMENT_AGENT_MODEL", "anthropic:claude-3-5-haiku-latest")
        key_note = ""
        if configured_model.startswith("anthropic:") and not _ANTHROPIC_API_KEY:
            key_note = " ANTHROPIC_API_KEY is missing."
        elif configured_model.startswith("openai:") and not _OPENAI_API_KEY:
            key_note = " OPENAI_API_KEY is missing."

        checks_summary = ", ".join(
            f"{name}={result.get('status', 'unknown')}"
            for name, result in preflight_results.items()
        )

        return ProcurementRecommendation(
            decision=fallback_decision,
            rationale=(
                f"Recommendation is {fallback_decision} using deterministic tool-based fallback "
                "because model execution failed. "
                f"Request {parsed_request.request_id} for vendor {parsed_request.vendor_id} "
                f"at ${parsed_request.total_amount:,.2f} had local check statuses: "
                f"{checks_summary}. Runtime error context: {exc}.{key_note}"
            ),
        )
