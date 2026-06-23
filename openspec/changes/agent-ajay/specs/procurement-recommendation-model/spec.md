## ADDED Requirements

### Requirement: Recommendation decision constraint
The system SHALL return recommendations whose decision value is exactly one of
`approve`, `deny`, or `escalate`.

#### Scenario: Enforce allowed decision values
- **WHEN** the agent produces a recommendation
- **THEN** the decision MUST match one of the three allowed values

### Requirement: Non-empty recommendation rationale
The system SHALL include a non-empty rationale string for every recommendation.

#### Scenario: Prevent blank rationales
- **WHEN** a recommendation is generated
- **THEN** the rationale MUST contain non-whitespace content
