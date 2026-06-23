## Why

FedEx procurement analysts currently spend significant time on routine requests that can be
evaluated using deterministic policy and risk checks. A Procurement Intelligence Agent is needed
to pre-screen requests, produce consistent recommendations, and surface rationale so analysts can
focus on complex or high-value exceptions.

This capstone scope is limited to mock-data pre-screening logic and structured recommendations.
It excludes deployment, UI, authentication, and persistent storage.

## What Changes

- Add a Pydantic AI procurement agent that returns a structured recommendation for each request.
- Add strict input/output model validation using Pydantic v2 models.
- Enforce recommendation decision values to one of `approve`, `deny`, or `escalate` and require
  non-empty rationale.
- Require data access through `data/loader.py` only; no direct reads from `mock_data/` in tools.
- Add four tool checks in `tools/`: budget, vendor duplication, policy compliance, and risk.
- Apply decision priority `escalate > deny > approve`.
- Require tool errors to be captured and reflected in rationale output.

## Capabilities

### New Capabilities
- `purchase-request-model`: Validate procurement request input schema and numeric constraints.
- `procurement-recommendation-model`: Enforce typed output with constrained decision and required
  rationale.
- `mock-data-loader-access`: Centralize mock data reads through `data/loader.py`.
- `procurement-check-tools`: Execute budget, duplication, policy, and risk checks in `tools/`.
- `procurement-agent-decisioning`: Orchestrate checks and apply decision priority rules.
- `tool-error-rationale-surfacing`: Escalate safely on tool errors and include error context in
  rationale.

### Modified Capabilities
- None.

## Impact

- Affected code: `agent.py`, `models.py`, `data/loader.py`, `tools/`, and `tests/`.
- Architectural impact: consolidates domain checks into explicit tools with deterministic priority.
- Process impact: improves explainability and consistency of advisory outcomes for procurement
  officers.

## Risks and Assumptions

- Risk: policy interpretation drift between sample expected outcomes and tool logic.
  Mitigation: encode policy thresholds in tests and document precedence decisions.
- Risk: overuse of escalation can reduce analyst efficiency.
  Mitigation: keep deny/escalate triggers explicit and rationale specific to policy/check results.
- Assumption: all domain evaluation uses mock data loaded through `data/loader.py` during capstone.