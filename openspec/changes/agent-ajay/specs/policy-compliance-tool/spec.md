## ADDED Requirements

### Requirement: Policy violation evaluation
The system SHALL evaluate each request against procurement policy rules and SHALL emit
policy-specific violations with forced decision severity where applicable.

#### Scenario: Return explicit policy violations
- **WHEN** a request triggers one or more policy rules
- **THEN** each violation MUST include policy identifier and forced decision context
