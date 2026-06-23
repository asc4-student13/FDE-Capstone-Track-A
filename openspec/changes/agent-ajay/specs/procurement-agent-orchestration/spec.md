## ADDED Requirements

### Requirement: Full-check recommendation orchestration
The system SHALL execute budget, vendor duplication, policy compliance, and risk checks for
every request before emitting a recommendation.

#### Scenario: Run all checks per request
- **WHEN** a valid purchase request is submitted
- **THEN** all four checks MUST be executed prior to final decision generation

### Requirement: Tool error escalation behavior
The system SHALL escalate a recommendation when any required check returns an error condition,
and the rationale MUST include the error context.

#### Scenario: Escalate on tool failure
- **WHEN** any tool call fails or returns explicit error data
- **THEN** recommendation decision MUST be `escalate` and rationale MUST reference the failure
