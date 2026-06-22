## ADDED Requirements

### Requirement: Vendor duplication check enforces single-source restrictions
The vendor duplication check SHALL evaluate whether a request above the single-source threshold violates contracted-vendor restrictions for covered categories.

#### Scenario: Single-source threshold not reached
- **WHEN** request amount is at or below the configured single-source threshold
- **THEN** the tool reports no single-source violation

#### Scenario: Conflicting active contracted vendors exist above threshold
- **WHEN** request amount exceeds the single-source threshold and active contracted vendors exist in the same category other than the requested vendor
- **THEN** the tool reports a violation with conflicting vendor identifiers

### Requirement: Duplication check explains result context
The tool SHALL include human-readable reason text describing why a violation was or was not triggered.

#### Scenario: No conflicts found
- **WHEN** no active contracted alternatives exist for the category above threshold
- **THEN** the tool reports no violation and explains that no conflicting active contract vendors were found
