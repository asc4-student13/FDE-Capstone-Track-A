## Why

FedEx procurement officers process high request volume, and many requests are repetitive but still require careful policy and risk review. A structured pre-screening agent is needed now to improve consistency, reduce manual triage time, and surface escalations early without removing human decision authority.

## What Changes

- Add a Pydantic AI procurement agent that accepts a purchase request and returns a structured recommendation.
- Enforce structured output with decision constrained to `approve`, `deny`, or `escalate` and a non-empty rationale.
- Add Pydantic v2 models for validated input (`PurchaseRequest`) and output (`ProcurementRecommendation`).
- Add a data loader abstraction in `data/loader.py` so tools do not read `mock_data/` files directly.
- Add and wire four procurement checks as tools: budget, vendor duplication, policy compliance, and risk assessment.
- Define deterministic recommendation priority: escalate > deny > approve.
- Require tool errors to be captured and reflected in rationale, with safe handling rather than silent failure.

## Capabilities

### New Capabilities
- `procurement-agent-core`: Accepts purchase requests, executes all required checks, and emits structured procurement recommendations.
- `procurement-model-validation`: Defines and validates typed procurement request/recommendation models with decision constraints.
- `procurement-data-loader`: Provides centralized access to mock procurement datasets through loader functions.
- `procurement-budget-check`: Evaluates cost-center remaining budget against requested amount.
- `procurement-vendor-duplication-check`: Detects single-source/contracted-vendor conflicts for applicable categories.
- `procurement-policy-compliance-check`: Evaluates request data against procurement policy rules and forced outcomes.
- `procurement-risk-assessment-check`: Produces vendor risk level from contract and compliance attributes.
- `procurement-decision-priority`: Applies escalation-first decision ordering and error-aware recommendation behavior.

### Modified Capabilities
- None.

## Impact

- Affected code: `agent.py`, `models.py`, `data/loader.py`, `tools/`, and `tests/`.
- Affected behavior: request triage becomes policy/risk-aware and consistently structured for procurement officer review.
- Dependencies: Pydantic v2 and Pydantic AI become required runtime contracts for agent I/O and orchestration.
- Governance: recommendation rationale becomes a required decision artifact that references checks and tool-error context when present.
