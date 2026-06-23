## ADDED Requirements

### Requirement: Four mandatory procurement checks
The system MUST execute four checks for each request using tools in tools/:
- check_budget
- check_vendor_duplication
- check_policy_compliance
- assess_risk

#### Scenario: Request triggers all tool calls
- **WHEN** a valid purchase request is evaluated
- **THEN** all four checks MUST run before final recommendation output

### Requirement: Budget tool contract
Tool name MUST be check_budget and tool inputs MUST be:
- cost_center_id (string)
- requested_amount (number)

The return shape MUST include:
- within_budget (bool)
- cost_center_id (string)
- remaining_budget (number)
- requested_amount (number)
- overage (number)

On data-access or lookup failure, return shape MUST include error (string).

#### Scenario: Budget overage response shape
- **WHEN** requested_amount exceeds remaining budget
- **THEN** within_budget MUST be false and overage MUST be greater than zero

### Requirement: Vendor duplication tool contract
Tool name MUST be check_vendor_duplication and tool inputs MUST be:
- vendor_id (string)
- category (string)
- amount (number)

The return shape MUST include:
- violation (bool)
- vendor_id (string)
- category (string)
- amount (number)
- conflicting_vendor_ids (list of strings)
- conflicting_vendor_names (list of strings)
- reason (string)

On data-access failure, return shape MUST include error (string).

#### Scenario: POL-001 violation is surfaced
- **WHEN** amount exceeds configured threshold and active vendors exist in same category
- **THEN** violation MUST be true and conflicting vendor lists MUST be populated

### Requirement: Policy compliance tool contract
Tool name MUST be check_policy_compliance and tool inputs MUST be:
- vendor_id (string)
- category (string)
- amount (number)
- quantity (integer)

The return shape MUST include:
- violations (list of objects with policy_id, rule_description, forced_decision)
- violation_count (integer)
- highest_severity (string: none, deny, or escalate)

On data-access failure, return shape MUST include error (string) and highest_severity MUST
indicate safe escalation behavior.

#### Scenario: Multiple policy hits resolve to highest severity
- **WHEN** both deny and escalate policy violations are present
- **THEN** highest_severity MUST be escalate

### Requirement: Risk assessment tool contract
Tool name MUST be assess_risk and tool input MUST be:
- vendor_id (string)

The return shape MUST include:
- vendor_id (string)
- vendor_name (string)
- compliance_flag (bool)
- compliance_notes (string)
- contract_status (string)
- risk_level (string: low, medium, high, critical)
- risk_summary (string)

On vendor lookup or data-access failure, return shape MUST include error (string).

#### Scenario: Compliance flagged vendor becomes critical
- **WHEN** vendor compliance_flag is true
- **THEN** risk_level MUST be critical
