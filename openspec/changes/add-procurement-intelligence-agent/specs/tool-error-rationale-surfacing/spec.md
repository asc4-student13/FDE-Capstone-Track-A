## ADDED Requirements

### Requirement: Tool errors are surfaced and escalated
The system MUST treat tool execution errors as escalation conditions and MUST include the error
context in recommendation rationale output.

#### Scenario: Tool failure causes safe escalation
- **WHEN** any required tool returns an error condition
- **THEN** decision MUST be `escalate` and rationale MUST reference the error

### Requirement: Rationale includes error source context
When tool errors occur, rationale MUST identify which check failed (budget, duplication, policy,
or risk) to aid procurement officer triage.

#### Scenario: Error rationale names failed check
- **WHEN** a tool error is present
- **THEN** rationale MUST include both failure cause and affected check name
