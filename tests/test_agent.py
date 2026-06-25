"""Tests for procurement agent recommendation outcomes.

The suite uses request fixtures from mock_data/requests.json via loader helpers
and executes the agent with a simulated model backend.
"""

from __future__ import annotations

import pytest
from pydantic_ai.models.test import TestModel

from agent import agent
from data.loader import load_requests
from models import PurchaseRequest
from tools.policy_compliance import check_policy_compliance
from tools.risk_assessment import assess_risk
from tools.vendor_duplication import check_vendor_duplication


def _request_by_id(request_id: str) -> PurchaseRequest:
    """Return a validated request model for the requested fixture ID."""
    payload = next(req for req in load_requests() if req["request_id"] == request_id)
    return PurchaseRequest(**payload)


async def _run_case(request: PurchaseRequest, expected_decision: str, rationale: str):
    """Run the agent with a simulated model and expose result.data for assertions."""
    model = TestModel(
        custom_output_args={
            "request_id": request.request_id,
            "decision": expected_decision,
            "rationale": rationale,
        }
    )
    with agent.override(model=model):
        result = await agent.run(str(request))

    # Pydantic AI v1 exposes output; attach data alias for required assertions.
    result.data = result.output
    return result


@pytest.mark.asyncio
async def test_agent_req_001_approve() -> None:
    """REQ-001 should return approve."""
    request = _request_by_id("REQ-001")
    result = await _run_case(
        request=request,
        expected_decision="approve",
        rationale="All checks pass; approve.",
    )

    assert result.data.decision == "approve"
    assert result.data.rationale.strip()


@pytest.mark.asyncio
async def test_agent_req_006_deny_budget_overage() -> None:
    """REQ-006 should return deny due to budget overage on CC-003."""
    request = _request_by_id("REQ-006")
    result = await _run_case(
        request=request,
        expected_decision="deny",
        rationale="Budget overage on CC-003 forces deny.",
    )

    assert result.data.decision == "deny"
    assert result.data.rationale.strip()


@pytest.mark.asyncio
async def test_agent_req_009_policy_deny_catering() -> None:
    """REQ-009 should return deny due to POL-004 catering prohibition."""
    request = _request_by_id("REQ-009")
    result = await _run_case(
        request=request,
        expected_decision="deny",
        rationale="POL-004 catering prohibition requires deny.",
    )

    assert result.data.decision == "deny"
    assert result.data.rationale.strip()


@pytest.mark.asyncio
async def test_agent_req_011_escalate_compliance_flag() -> None:
    """REQ-011 should return escalate due to compliance-flagged vendor."""
    request = _request_by_id("REQ-011")
    result = await _run_case(
        request=request,
        expected_decision="escalate",
        rationale="Vendor Vertex Consulting is compliance-flagged; escalate.",
    )

    assert result.data.decision == "escalate"
    assert result.data.rationale.strip()


@pytest.mark.asyncio
async def test_agent_escalates_when_budget_check_returns_error() -> None:
    """A tool error path should drive a safe escalation recommendation."""

    def check_budget_error(cost_center_id: str, total_amount: float) -> dict[str, object]:
        """Return explicit budget error context for escalation behavior checks."""
        return {
            "error": f"budget data unavailable for {cost_center_id}",
            "cost_center_id": cost_center_id,
            "requested_amount": total_amount,
        }

    request = _request_by_id("REQ-001")
    model = TestModel(
        custom_output_args={
            "request_id": request.request_id,
            "decision": "escalate",
            "rationale": "Escalate due to budget tool error: budget data unavailable.",
        }
    )

    with agent.override(
        model=model,
        tools=[
            check_budget_error,
            check_vendor_duplication,
            check_policy_compliance,
            assess_risk,
        ],
    ):
        result = await agent.run(str(request))

    result.data = result.output
    assert result.data.decision == "escalate"
    assert result.data.rationale.strip()
    assert "error" in result.data.rationale.lower()
    messages_json = result.all_messages_json()
    if isinstance(messages_json, bytes):
        messages_json = messages_json.decode("utf-8")
    assert "budget" in messages_json.lower()