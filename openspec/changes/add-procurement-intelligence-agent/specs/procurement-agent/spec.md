## ADDED Requirements

### Requirement: Agent Input and Output Types
The system MUST define an agent in `agent.py` that accepts a `PurchaseRequest` and returns a `ProcurementRecommendation`.

Input contract:
- Input type MUST be the `PurchaseRequest` model defined in `models.py`.
- If raw dict input is provided, it MUST be normalized/validated into `PurchaseRequest` before tool execution.

Output contract:
- Output type MUST be the `ProcurementRecommendation` model defined in `models.py`.
- `decision` MUST always be one of `approve`, `deny`, or `escalate`.
- `rationale` MUST be a non-empty string.

#### Scenario: Valid request returns schema-valid recommendation
- **WHEN** the agent receives a valid `PurchaseRequest`
- **THEN** it returns a `ProcurementRecommendation` with `decision in {approve, deny, escalate}` and non-empty `rationale`

#### Scenario: Invalid request payload fails validation safely
- **WHEN** input cannot be validated as `PurchaseRequest`
- **THEN** the agent MUST not crash and MUST return or surface a schema-safe escalation path per error policy

### Requirement: Mandatory Four-Tool Execution
The agent MUST invoke all four tools for every request evaluation:
- `check_budget` from `tools/budget.py`
- `check_vendor_duplication` from `tools/vendor_duplication.py`
- `check_policy_compliance` from `tools/policy_compliance.py`
- `assess_risk` from `tools/risk_assessment.py`

The agent MUST NOT short-circuit after the first triggered check; it MUST collect all check outcomes before final decision mapping.

#### Scenario: Multiple checks trigger together
- **WHEN** more than one tool returns non-pass outcomes
- **THEN** the agent still evaluates all four tools and includes combined evidence in rationale

### Requirement: Decision Priority Order
The agent MUST apply deterministic priority ordering when multiple checks fire.

Priority order:
1. `escalate`
2. `deny`
3. `approve`

Mapping rules:
- If any tool returns `status=error`, final decision MUST be `escalate`.
- Else if any tool returns `status=escalate`, final decision MUST be `escalate`.
- Else if any tool returns `status=fail`, final decision MUST be `deny`.
- Else final decision MUST be `approve`.

#### Scenario: Escalation overrides denial
- **WHEN** one tool returns `fail` and another returns `escalate`
- **THEN** final decision is `escalate`

#### Scenario: Error overrides all normal outcomes
- **WHEN** one or more tools return `error`
- **THEN** final decision is `escalate`

### Requirement: Error Handling and Fallback Behavior
The agent MUST treat tool failures as safety-critical and degrade predictably.

Behavior requirements:
- Tool exceptions MUST be caught (either in tool or by agent wrapper) and represented as structured error outcomes.
- Agent execution MUST remain alive when any single tool fails.
- Final output MUST remain schema-valid `ProcurementRecommendation`.
- Rationale MUST include which tool failed and the relevant error context.

#### Scenario: Single tool fails unexpectedly
- **WHEN** one tool throws or returns `status=error`
- **THEN** the agent returns `decision=escalate` with rationale that names the failed check

### Requirement: System Prompt Constraints
The system prompt used for the agent MUST constrain behavior to deterministic, policy-aligned recommendations.

The system prompt MUST:
- Instruct the model to evaluate procurement requests only within provided policy/tool results.
- Instruct the model to call all four tools exactly once per request evaluation flow.
- Declare the strict decision precedence `escalate > deny > approve`.
- Require rationale to reference specific checks and key evidence (for example policy IDs, overage amount, risk level, vendor conflict evidence).
- Require non-empty rationale and forbid vague responses.
- Forbid silent failure handling; errors must be surfaced in rationale and drive escalation.

#### Scenario: Prompt enforces evidence-based rationale
- **WHEN** the agent produces a recommendation
- **THEN** rationale includes specific check references rather than generic statements

#### Scenario: Prompt enforces deterministic precedence
- **WHEN** tool outcomes include conflicting statuses
- **THEN** the final decision follows `escalate > deny > approve` exactly
