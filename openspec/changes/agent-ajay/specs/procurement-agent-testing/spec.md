## ADDED Requirements

### Requirement: Mock-data-only automated testing
The system SHALL provide automated tests for tool behavior and end-to-end recommendation
outcomes using mock data without external network dependency.

#### Scenario: Validate primary decision paths
- **WHEN** tests are executed against representative requests
- **THEN** approve, deny, and escalate outcomes MUST each be covered by at least one passing test
