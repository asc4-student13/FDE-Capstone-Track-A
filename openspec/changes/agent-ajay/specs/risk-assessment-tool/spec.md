## ADDED Requirements

### Requirement: Vendor risk classification
The system SHALL classify vendor risk using contract status and compliance flag context,
including support for low, medium, high, and critical outcomes.

#### Scenario: Escalate flagged compliance vendors
- **WHEN** vendor compliance flag is active
- **THEN** the risk assessment MUST return critical risk classification
