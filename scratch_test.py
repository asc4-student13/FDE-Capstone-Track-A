# scratch_test.py: delete before Session 4

import asyncio

from agent import agent
from data.loader import load_requests
from models import PurchaseRequest


def _request_by_id(request_id: str) -> PurchaseRequest:
    requests = load_requests()
    payload = next((item for item in requests if item.get("request_id") == request_id), None)
    if payload is None:
        raise ValueError(f"Request {request_id} not found in mock_data/requests.json")
    return PurchaseRequest.model_validate(payload)


async def _run_case(request_id: str, expected_decision: str) -> None:
    req = _request_by_id(request_id)
    prompt = (
        "Evaluate this purchase request using all registered tools and return a "
        "ProcurementRecommendation.\n\n"
        f"PurchaseRequest:\n{req.model_dump_json(indent=2)}"
    )

    result = await agent.run(prompt)
    recommendation = result.data
    rationale = recommendation.rationale.strip()

    print(f"{request_id}: decision={recommendation.decision}")
    print(f"{request_id}: rationale={recommendation.rationale}\n")

    if recommendation.decision != expected_decision:
        raise AssertionError(
            f"{request_id} expected {expected_decision}, got {recommendation.decision}"
        )
    if not rationale:
        raise AssertionError(f"{request_id} returned an empty rationale")


async def main() -> None:
    # Approve case
    await _run_case("REQ-001", "approve")

    # Deny case (POL-004 catering prohibition)
    await _run_case("REQ-009", "deny")

    # Escalate case: compliance-flagged vendor (risk path)
    await _run_case("REQ-011", "escalate")

    # Escalate case: near-director-threshold amount path
    await _run_case("REQ-014", "escalate")

    print("All manual agent checks passed.")


if __name__ == "__main__":
    asyncio.run(main())
