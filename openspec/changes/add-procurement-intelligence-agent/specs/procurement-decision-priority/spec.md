## ADDED Requirements

### Requirement: Recommendation priority is escalate before deny before approve
The decision policy SHALL evaluate check outcomes using strict priority where escalate takes precedence over deny, and deny takes precedence over approve.

#### Scenario: Escalation and denial signals both present
- **WHEN** one or more checks produce escalation conditions and one or more checks also produce denial conditions
- **THEN** final recommendation decision is escalate

#### Scenario: Denial signal without escalation
- **WHEN** one or more checks produce denial conditions and no check produces escalation conditions
- **THEN** final recommendation decision is deny

#### Scenario: No escalation or denial conditions
- **WHEN** all checks complete without escalation or denial conditions
- **THEN** final recommendation decision is approve

### Requirement: Tool failures are reflected and handled conservatively
If any required check fails or returns explicit error context, the recommendation logic MUST include the failure in rationale and SHALL choose escalate.

#### Scenario: Data unavailable in one tool
- **WHEN** a tool returns an error due to unavailable reference data
- **THEN** final decision is escalate and rationale includes the tool failure context
