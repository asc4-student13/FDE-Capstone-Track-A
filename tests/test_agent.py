"""Tests for Procurement Intelligence Agent error-escalation behavior."""

from __future__ import annotations

from unittest.mock import patch

from pydantic_ai.models.test import TestModel

from agent import agent


def test_agent_escalates_when_budget_data_loading_fails() -> None:
    """Budget loader FileNotFoundError yields escalate with failure rationale context."""
    request_payload = {
        "request_id": "REQ-ERR-001",
        "requestor": "Test User",
        "cost_center_id": "CC-001",
        "vendor_name": "BlueSky Cloud Solutions",
        "vendor_id": "V-002",
        "category": "software_licenses",
        "item_description": "Error path validation purchase",
        "quantity": 1,
        "unit_price": 100.0,
        "total_amount": 100.0,
    }

    # TestModel avoids live API calls while still executing tool-call steps.
    fake_model = TestModel(
        custom_output_args={
            "request_id": "REQ-ERR-001",
            "decision": "escalate",
            "rationale": "Escalated due to budget data loading failure in check_budget.",
        }
    )

    with patch(
        "data.loader.load_budgets",
        side_effect=FileNotFoundError("budgets.json missing"),
    ):
        with agent.override(model=fake_model):
            result = agent.run_sync(str(request_payload))

    recommendation = result.output
    assert recommendation.decision == "escalate"
    assert "budget" in recommendation.rationale.lower()
    assert "load" in recommendation.rationale.lower()

    # Ensure the patched loader failure was present in tool output during the run.
    run_messages = result.all_messages_json().decode("utf-8")
    assert "Budget data could not be loaded" in run_messages
    assert "budgets.json missing" in run_messages
