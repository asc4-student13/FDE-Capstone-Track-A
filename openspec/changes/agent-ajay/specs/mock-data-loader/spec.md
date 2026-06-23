## ADDED Requirements

### Requirement: Centralized mock data access
The system SHALL load reference datasets through a single loader module rather than direct
JSON reads in tools or agent orchestration code.

#### Scenario: Tool requests budget data
- **WHEN** a budget check is executed
- **THEN** budget records MUST be retrieved via the loader interface
