## Why

Tool failures currently surface as exceptions rather than structured outcomes, making the agent
response inconsistent and hard to reason about. We need deterministic error handling now so the
agent can safely escalate requests with clear rationale when required data loading fails.

## What Changes

- Add a requirement that each existing tool catches `FileNotFoundError`, `KeyError`, and a generic
  `Exception` separately.
- Require tools to return typed error results for those failures instead of raising exceptions.
- Update the agent behavior contract so the system prompt instructs the model to reference tool
  errors in rationale and return `escalate` when a tool error occurs.
- Add a regression test that patches `data.loader.load_budgets` to raise `FileNotFoundError` and
  verifies the agent returns `escalate` with rationale mentioning data loading failure.
- Limit implementation scope to existing models and tools only; do not introduce new tools or
  Pydantic models.

## Capabilities

### New Capabilities
- `procurement-tool-error-results`: Standardized typed error handling for tool failures.
- `procurement-agent-error-escalation`: Agent prompt behavior that escalates and explains tool
  errors in rationale.

### Modified Capabilities
- None.

## Impact

- Affected code: `tools/budget.py`, `tools/policy_compliance.py`, `tools/risk_assessment.py`,
  `tools/vendor_duplication.py`, `agent.py`, and related tests.
- API/contract impact: Tool outputs become explicit typed error results on failure paths.
- Testing impact: Adds one focused agent test for data-loading `FileNotFoundError` escalation.
