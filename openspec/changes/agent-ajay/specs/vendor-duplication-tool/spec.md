## ADDED Requirements

### Requirement: Single-source violation detection
The system SHALL detect vendor duplication risk for high-value requests where policy requires
using an existing active contracted vendor in the same category.

#### Scenario: Flag high-value duplication breach
- **WHEN** request amount exceeds the single-source threshold and another active vendor exists
- **THEN** the check MUST return a violation with conflicting vendor identifiers
