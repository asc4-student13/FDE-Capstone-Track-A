# scratch_rationale_eval.py: temporary script for rationale quality checks

from __future__ import annotations

import re
from typing import Any

from agent import recommend_procurement_action
from data.loader import load_requests


_CHECK_KEYWORDS = [
    "budget",
    "vendor_duplication",
    "vendor duplication",
    "policy_compliance",
    "policy compliance",
    "risk_assessment",
    "risk assessment",
]


def _sentence_count(text: str) -> int:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return len([p for p in parts if p.strip()])


def _has_driver_check(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in _CHECK_KEYWORDS)


def _has_required_context(text: str, request: dict[str, Any]) -> bool:
    has_policy = bool(re.search(r"POL-\d{3}", text))
    has_amount = bool(re.search(r"\$\s?\d", text)) or bool(re.search(r"\b\d{3,}(?:\.\d+)?\b", text))
    vendor_id = str(request.get("vendor_id", ""))
    vendor_name = str(request.get("vendor_name", ""))
    has_vendor = (vendor_id and vendor_id in text) or (vendor_name and vendor_name in text)
    return has_policy or has_amount or has_vendor


def _no_bullets(text: str) -> bool:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return not any(line.startswith(("-", "*", "1.", "2.", "3.")) for line in lines)


def evaluate_rationale(request: dict[str, Any], rationale: str) -> list[str]:
    issues: list[str] = []
    sentence_count = _sentence_count(rationale)
    if sentence_count < 2 or sentence_count > 4:
        issues.append(f"Expected 2-4 sentences, found {sentence_count}")
    if not _has_driver_check(rationale):
        issues.append("Missing named driving check(s)")
    if not _has_required_context(rationale, request):
        issues.append("Missing amounts, vendor context, or policy IDs")
    if not _no_bullets(rationale):
        issues.append("Rationale contains bullet/list formatting")
    return issues


def main() -> None:
    requests = load_requests()
    failed = []

    for request in requests:
        request_id = str(request.get("request_id", ""))
        recommendation = recommend_procurement_action(request)
        rationale = recommendation.rationale.strip()
        issues = evaluate_rationale(request, rationale)

        print(f"{request_id}: decision={recommendation.decision}")
        print(f"{request_id}: rationale={rationale}")
        if issues:
            print(f"{request_id}: issues={issues}")
            failed.append((request_id, issues))
        print()

    print(f"Total requests evaluated: {len(requests)}")
    print(f"Requests failing template checks: {len(failed)}")
    if failed:
        print("Failed request IDs:")
        for request_id, issues in failed:
            print(f"- {request_id}: {issues}")


if __name__ == "__main__":
    main()
