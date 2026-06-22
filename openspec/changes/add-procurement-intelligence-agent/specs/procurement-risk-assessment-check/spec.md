## ADDED Requirements

### Requirement: Risk assessment computes vendor risk level from contract and compliance state
The risk assessment tool SHALL return low, medium, high, or critical risk levels based on vendor compliance flag and contract status.

#### Scenario: Compliance-flagged vendor is critical risk
- **WHEN** vendor compliance flag is true
- **THEN** the tool returns risk level critical with escalation-oriented summary text

#### Scenario: Expired contract vendor is high risk
- **WHEN** vendor contract status is expired and no compliance flag is active
- **THEN** the tool returns risk level high

#### Scenario: No-contract vendor is medium risk
- **WHEN** vendor contract status is none and no compliance flag is active
- **THEN** the tool returns risk level medium

#### Scenario: Active compliant vendor is low risk
- **WHEN** vendor has active contract status and no compliance flag
- **THEN** the tool returns risk level low

### Requirement: Unknown vendor is surfaced as risk-check error context
The tool SHALL return explicit error context when a vendor cannot be found in the vendor dataset.

#### Scenario: Vendor id missing from reference data
- **WHEN** the request vendor id is not present in vendor records
- **THEN** the tool returns an error field and non-low risk classification
