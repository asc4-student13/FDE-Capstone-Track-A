## ADDED Requirements

### Requirement: Budget sufficiency determination
The system SHALL evaluate whether a request amount fits within the selected cost center's
remaining budget and SHALL return overage when insufficient.

#### Scenario: Detect budget overage
- **WHEN** requested amount exceeds remaining budget
- **THEN** the result MUST indicate within_budget as false and include overage amount
