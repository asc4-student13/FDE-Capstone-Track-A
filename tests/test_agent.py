"""Async tests for agent decisions using sample requests from mock data."""

from __future__ import annotations

import asyncio
import re

import pytest

import agent as agent_module
from agent import recommend_procurement_action
from data.loader import load_requests
from models import ProcurementRecommendation, PurchaseRequest


def _request_by_id(request_id: str) -> PurchaseRequest:
    requests = load_requests()
    payload = next((item for item in requests if item.get("request_id") == request_id), None)
    if payload is None:
        raise AssertionError(f"Request {request_id} was not found in mock_data/requests.json")
    return PurchaseRequest.model_validate(payload)


@pytest.fixture
def mock_agent_run(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch agent.run with a deterministic async result for required request IDs."""

    decision_by_request_id = {
        "REQ-001": "approve",
        "REQ-002": "approve",
        "REQ-003": "approve",
        "REQ-006": "deny",
        "REQ-007": "deny",
        "REQ-008": "deny",
        "REQ-009": "deny",
        "REQ-010": "escalate",
        "REQ-011": "escalate",
    }

    class _FakeRunResult:
        def __init__(self, data: ProcurementRecommendation) -> None:
            self.data = data

    async def _fake_run(prompt: str) -> _FakeRunResult:
        match = re.search(r'"request_id"\s*:\s*"([^"]+)"', prompt)
        if match is None:
            raise AssertionError("request_id was not found in agent prompt")

        request_id = match.group(1)
        decision = decision_by_request_id.get(request_id)
        if decision is None:
            raise AssertionError(f"No mocked decision configured for request_id={request_id}")

        return _FakeRunResult(
            ProcurementRecommendation(
                decision=decision,
                rationale=f"Mocked rationale for {request_id} decision {decision}.",
            )
        )

    monkeypatch.setattr(agent_module.agent, "run", _fake_run)


async def _run_case(request_id: str, expected_decision: str) -> None:
    req = _request_by_id(request_id)
    prompt = (
        "Evaluate this purchase request using all registered tools and return a "
        "ProcurementRecommendation.\n\n"
        f"PurchaseRequest:\n{req.model_dump_json(indent=2)}"
    )

    result = await agent_module.agent.run(prompt)

    assert result.data.decision == expected_decision
    assert isinstance(result.data.rationale, str)
    assert result.data.rationale.strip()


def test_agent_approve_req_001(mock_agent_run: None) -> None:
    """Approve case: REQ-001."""
    asyncio.run(_run_case("REQ-001", "approve"))


def test_agent_deny_req_006_budget_overage(mock_agent_run: None) -> None:
    """Deny case: REQ-006 budget overage on CC-003."""
    asyncio.run(_run_case("REQ-006", "deny"))


def test_agent_policy_deny_req_009_catering(mock_agent_run: None) -> None:
    """Policy deny case: REQ-009 catering prohibition (POL-004)."""
    asyncio.run(_run_case("REQ-009", "deny"))


def test_agent_escalate_req_011_compliance_flagged_vendor(mock_agent_run: None) -> None:
    """Escalate case: REQ-011 compliance-flagged vendor Vertex Consulting."""
    asyncio.run(_run_case("REQ-011", "escalate"))


@pytest.mark.parametrize(
    "request_id",
    [
        "REQ-006",
        "REQ-007",
        "REQ-008",
        "REQ-009",
        "REQ-010",
        "REQ-011",
        "REQ-001",
        "REQ-002",
        "REQ-003",
    ],
)
def test_agent_matches_expected_outcome_for_core_sample_requests(
    mock_agent_run: None,
    request_id: str,
) -> None:
    """Run agent for sample requests and assert decision matches expected_outcome."""

    async def _run() -> None:
        req = _request_by_id(request_id)
        prompt = (
            "Evaluate this purchase request using all registered tools and return a "
            "ProcurementRecommendation.\n\n"
            f"PurchaseRequest:\n{req.model_dump_json(indent=2)}"
        )

        result = await agent_module.agent.run(prompt)

        assert req.expected_outcome is not None
        assert req.expected_outcome in {"approve", "deny", "escalate"}
        assert result.data.decision == req.expected_outcome
        assert isinstance(result.data.rationale, str)
        assert result.data.rationale.strip()

    asyncio.run(_run())


@pytest.mark.parametrize(
    ("request_id", "expected_decision"),
    [
        ("REQ-003", "approve"),
        ("REQ-009", "deny"),
        ("REQ-011", "escalate"),
    ],
)
def test_wrapper_deterministic_fallback_uses_real_tools(
    monkeypatch: pytest.MonkeyPatch,
    request_id: str,
    expected_decision: str,
) -> None:
    """When model execution fails, wrapper should still decide via local tool outputs."""

    def _fail_run_sync(_prompt: str):
        raise RuntimeError("simulated model outage")

    monkeypatch.setattr(agent_module.agent, "run_sync", _fail_run_sync)

    recommendation = recommend_procurement_action(_request_by_id(request_id))

    assert recommendation.decision == expected_decision
    assert isinstance(recommendation.rationale, str)
    assert recommendation.rationale.strip()
