## ADDED Requirements

### Requirement: Policy compliance check evaluates rule-based forced outcomes
The policy compliance check SHALL evaluate request attributes against procurement policies and return a violations list with policy identifiers and forced decision signals.

#### Scenario: Prohibited category is denied
- **WHEN** request category is catering
- **THEN** the tool returns a violation for the catering prohibition policy with forced decision deny

#### Scenario: Compliance-flagged vendor requires escalation
- **WHEN** the vendor has an active compliance flag
- **THEN** the tool returns a violation that forces escalation for legal/compliance review

#### Scenario: Director threshold requires escalation
- **WHEN** request amount is at or above the director approval threshold
- **THEN** the tool returns a violation that forces escalation

### Requirement: Policy check reports highest severity
The tool SHALL return an aggregate highest severity indicator of escalate, deny, or none based on generated violations.

#### Scenario: Mixed violations include escalation
- **WHEN** at least one policy violation forces escalation
- **THEN** highest severity is reported as escalate
