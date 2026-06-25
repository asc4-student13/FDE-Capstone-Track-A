## ADDED Requirements

### Requirement: Agent escalates when tool returns error result
The agent system prompt MUST instruct the model that if any tool returns an error result, the
final recommendation MUST be `escalate`, and the rationale MUST explicitly reference the tool
error.

#### Scenario: Tool error is present during recommendation
- **WHEN** the model receives tool output indicating an error result
- **THEN** the model returns recommendation `escalate`
- **THEN** the rationale text references the tool error condition

### Requirement: Budget load failure is covered by regression test
The test suite MUST include a case that patches `data.loader.load_budgets` to raise
`FileNotFoundError` and verifies the agent response is `escalate` with rationale mentioning the
budget data loading failure.

#### Scenario: Patched budget loader failure
- **WHEN** `data.loader.load_budgets` is patched to raise `FileNotFoundError`
- **THEN** running the agent returns recommendation `escalate`
- **THEN** the rationale includes language indicating data loading failed
