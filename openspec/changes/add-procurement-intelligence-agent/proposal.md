## Why

The procurement assistant needs a deterministic, testable recommendation contract for pre-screening purchase requests before human approval. This change is needed now to align Session 2 and Session 3 implementation with a single source of truth for model schema, tool behavior, and decision precedence.

## What Changes

- Introduce a Pydantic AI procurement agent that returns structured recommendations with `decision` and `rationale`.
- Define `PurchaseRequest` and `ProcurementRecommendation` as Pydantic v2 models with strict validation for required fields and numeric constraints.
- Route all data access through `data/loader.py`; do not read `mock_data/` directly from agent or tools.
- Define and enforce contracts for four tools: `check_budget`, `check_vendor_duplication`, `check_policy_compliance`, and `assess_risk`.
- Establish deterministic decision priority: escalate > deny > approve.
- Require tool failures to be caught and represented in rationale text so failures are visible to reviewers.
- Exclude non-capstone concerns (deployment, UI, authentication/authorization, persistent storage).

## Capabilities

### New Capabilities
- `procurement-intelligence-agent`: Structured procurement recommendation capability that validates request input/output, executes the four domain checks, and maps results to approve/deny/escalate with deterministic precedence.

### Modified Capabilities
- None.

## Impact

- Affected code:
  - `solutions/models.py`
  - `solutions/data/loader.py`
  - `solutions/tools/budget.py`
  - `solutions/tools/vendor_duplication.py`
  - `solutions/tools/policy_compliance.py`
  - `solutions/tools/risk_assessment.py`
  - `solutions/agent.py`
  - `solutions/tests/*.py`
- APIs/contracts:
  - Pydantic model schema becomes the runtime LLM output contract via `output_type`.
  - Tool return shapes and error semantics become explicit and testable.
- Dependencies:
  - Uses existing Pydantic v2 and Pydantic AI stack from project environment.
- Systems:
  - No infrastructure, deployment, or data-store changes.