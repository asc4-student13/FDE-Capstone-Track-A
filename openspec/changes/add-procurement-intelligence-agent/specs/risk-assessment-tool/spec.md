## ADDED Requirements

### Requirement: Risk Assessment Tool Interface
The system MUST provide a tool named `assess_risk`.

The tool MUST accept:
- `vendor_id`

The tool MAY also accept optional request context used to refine risk scoring, such as:
- `total_amount`
- `category`
- `cost_center_id`

The tool MUST return a structured object with at least:
- `check` (literal `risk_assessment`)
- `status` (`pass`, `escalate`, or `error`)
- `vendor_id`
- `compliance_flag` (boolean)
- `contract_status` (`active`, `expired`, `none`, or `unknown`)
- `risk_level` (`low`, `medium`, `high`, or `critical`)
- `risk_factors` (list)
- `message` (non-empty string)

#### Scenario: Structured risk profile is returned
- **WHEN** a known vendor is evaluated
- **THEN** the tool returns compliance flag status, contract status, and computed risk level

### Requirement: Risk Level Computation
The tool MUST compute `risk_level` from vendor profile state using deterministic rules.

Minimum required mapping:
- `critical`: vendor has `compliance_flag=true`
- `high`: `contract_status=expired` and no compliance flag
- `medium`: `contract_status=none` and no compliance flag
- `low`: `contract_status=active` and no compliance flag

The tool MAY raise risk level based on additional contextual factors (for example near-threshold spend), but MUST NOT lower the base level implied by compliance flag or contract status.

#### Scenario: Compliance flag sets critical risk
- **WHEN** vendor compliance flag is true
- **THEN** `risk_level=critical` and `status=escalate`

#### Scenario: Active contract and clean compliance yields low risk
- **WHEN** vendor has active contract and no compliance flag
- **THEN** `risk_level=low` and `status=pass`

### Requirement: Escalation Behavior
The tool MUST set `status=escalate` when risk profile requires human review.

Escalation triggers MUST include:
- `risk_level=critical`

The tool SHOULD escalate for `risk_level=high` and MAY escalate for `risk_level=medium` when optional context indicates elevated uncertainty.

#### Scenario: Expired-contract vendor escalates
- **WHEN** vendor contract is expired and no override exists
- **THEN** `risk_level=high` and `status=escalate`

### Requirement: Error Handling
Exceptions MUST be caught and converted into a structured error result.

Error result MUST include:
- `check=risk_assessment`
- `status=error`
- non-empty `message`

#### Scenario: Internal risk evaluation exception
- **WHEN** vendor lookup or scoring fails unexpectedly
- **THEN** the tool returns a schema-valid error object instead of raising
