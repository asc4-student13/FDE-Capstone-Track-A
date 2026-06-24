"""Tests for root procurement agent configuration and wrapper behavior."""

from __future__ import annotations

import agent as agent_module
from agent import recommend_procurement_action
from data import loader
from data.loader import load_requests
from models import ProcurementRecommendation


def _request_by_id(request_id: str) -> dict[str, object]:
    requests = load_requests()
    match = next((item for item in requests if item.get("request_id") == request_id), None)
    if match is None:
        raise AssertionError(f"Request {request_id} was not found in mock data.")
    return match


def test_system_prompt_declares_required_priority() -> None:
    """System prompt should explicitly enforce escalate > deny > approve."""
    assert "escalate > deny > approve" in agent_module._SYSTEM_PROMPT


def test_agent_registers_four_tools() -> None:
    """Agent definition should register all four procurement tools."""
    function_toolset = getattr(agent_module.agent, "_function_toolset", None)
    assert function_toolset is not None

    tools_map = getattr(function_toolset, "tools", None)
    assert isinstance(tools_map, dict)
    assert set(tools_map.keys()) == {
        "check_budget",
        "check_vendor_duplication",
        "check_policy_compliance",
        "assess_risk",
    }


def test_recommend_procurement_action_uses_agent_result(monkeypatch) -> None:
    """Wrapper should return typed recommendation data from agent run result."""

    class _FakeResult:
        def __init__(self, data: ProcurementRecommendation) -> None:
            self.data = data

    def _fake_run_sync(_prompt: str) -> _FakeResult:
        return _FakeResult(
            ProcurementRecommendation(
                decision="approve",
                rationale="All checks passed with no policy or risk findings.",
            )
        )

    monkeypatch.setattr(agent_module.agent, "run_sync", _fake_run_sync)

    recommendation = recommend_procurement_action(_request_by_id("REQ-003"))
    assert recommendation.decision == "approve"
    assert recommendation.rationale.strip()


def test_recommend_procurement_action_escalates_on_runtime_error(monkeypatch) -> None:
    """Wrapper should return schema-valid escalation when runtime execution fails."""

    def _fake_run_sync(_prompt: str):
        raise RuntimeError("simulated model outage")

    monkeypatch.setattr(agent_module.agent, "run_sync", _fake_run_sync)

    recommendation = recommend_procurement_action(_request_by_id("REQ-003"))
    assert recommendation.decision == "escalate"
    assert "simulated model outage" in recommendation.rationale


def test_recommendation_escalates_when_budget_data_file_missing(monkeypatch) -> None:
    """Patching load_budgets failure should produce escalate with error rationale."""

    def _raise_file_not_found() -> list[object]:
        raise FileNotFoundError("budgets.json missing")

    monkeypatch.setattr(loader, "load_budgets", _raise_file_not_found)

    recommendation = recommend_procurement_action(_request_by_id("REQ-003"))

    assert recommendation.decision == "escalate"
    assert recommendation.rationale.strip()
    assert "loading failure" in recommendation.rationale.lower()
    assert "budget" in recommendation.rationale.lower()
