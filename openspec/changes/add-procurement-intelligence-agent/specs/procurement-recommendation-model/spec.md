## ADDED Requirements

### Requirement: Recommendation decision constraint
The system MUST output ProcurementRecommendation.decision as exactly one of:
- approve
- deny
- escalate

#### Scenario: Decision outside allowed literals is rejected
- **WHEN** the recommendation decision is not one of the three allowed values
- **THEN** output validation MUST fail

### Requirement: Recommendation rationale is non-empty
The system MUST include a rationale string with each recommendation and rationale MUST be non-empty
after whitespace stripping.

#### Scenario: Blank rationale is rejected
- **WHEN** rationale is empty or whitespace
- **THEN** output validation MUST fail

#### Scenario: Request identifier is echoed in output
- **WHEN** a recommendation is produced for a request
- **THEN** recommendation.request_id MUST equal input request_id
