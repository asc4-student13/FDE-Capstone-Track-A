## ADDED Requirements

### Requirement: Agent evaluates purchase requests with four-check orchestration
The procurement agent SHALL accept a validated purchase request, execute budget, vendor duplication, policy compliance, and risk assessment checks for every request, and return a structured recommendation.

#### Scenario: Agent performs complete check set
- **WHEN** a valid purchase request is submitted to the agent
- **THEN** the agent runs all four checks before producing the recommendation

### Requirement: Recommendation includes constrained decision and rationale
The agent output SHALL include request_id, a decision constrained to approve, deny, or escalate, and a non-empty rationale explaining the checks that drove the recommendation.

#### Scenario: Structured recommendation is returned
- **WHEN** the agent finishes evaluating a request
- **THEN** it returns a recommendation object with constrained decision and non-empty rationale text

### Requirement: Tool docstrings define explicit invocation timing
Each procurement tool function SHALL include docstring guidance that explicitly states when the tool should be called by the agent.

#### Scenario: Tool guidance is unambiguous
- **WHEN** a developer reviews a procurement tool function docstring
- **THEN** the docstring clearly states the invocation timing (for example, call for every purchase request)
