## ADDED Requirements

### Requirement: Policy Compliance Tool Interface
The system MUST provide a tool named `check_policy_compliance`.

The tool MUST accept a purchase request object with fields required to evaluate policy conditions, including at least:
- `request_id`
- `cost_center_id`
- `vendor_id`
- `category`
- `quantity`
- `total_amount`

The tool MUST return a structured object with at least:
- `check` (literal `policy_compliance`)
- `status` (`pass`, `fail`, `escalate`, or `error`)
- `violations` (list)
- `triggered_policy_ids` (list)
- `message` (non-empty string)

Each `violations` item MUST include:
- `policy_id`
- `rule_description`
- `forced_decision` (`deny` or `escalate`)

#### Scenario: No policy violations
- **WHEN** no policy is triggered for a request
- **THEN** the tool returns `status=pass` and an empty `violations` list

### Requirement: Evaluate All Eight Policies
The tool MUST evaluate all policies in `mock_data/policies.json` through loader-backed policy data and apply them deterministically:
- POL-001 Single-Source Restriction
- POL-002 Manager Approval Threshold
- POL-003 Director Approval Threshold
- POL-004 Prohibited Category Catering
- POL-005 Expired Contract Vendor
- POL-006 Compliance-Flagged Vendor Hold
- POL-007 Staffing Vendor Single-Source
- POL-008 Budget Overage Prohibition

The tool MUST emit violation entries for every triggered policy in the request.

#### Scenario: Multiple policies trigger together
- **WHEN** a request violates more than one policy
- **THEN** all triggered policies are represented in `violations` and `triggered_policy_ids`

### Requirement: Forced-Decision Mapping
The tool MUST map policy triggers to forced decisions as follows:
- `deny`: POL-001, POL-004, POL-005, POL-007, POL-008
- `escalate`: POL-003, POL-006

POL-002 is a non-compliance/process control and MUST be represented as:
- a violation entry with `policy_id=POL-002`
- `forced_decision=escalate` when approval evidence is missing

Aggregate status mapping:
1. If any triggered policy has `forced_decision=escalate`, tool `status` MUST be `escalate`.
2. Else if any triggered policy has `forced_decision=deny`, tool `status` MUST be `fail`.
3. Else tool `status` MUST be `pass`.

#### Scenario: Director threshold forces escalation
- **WHEN** `total_amount` is 50000 or more
- **THEN** a POL-003 violation is included with `forced_decision=escalate` and tool `status=escalate`

#### Scenario: Prohibited category forces denial
- **WHEN** category is `catering`
- **THEN** a POL-004 violation is included with `forced_decision=deny` and tool `status=fail`

### Requirement: Error Handling
Exceptions MUST be caught and converted into a structured error result.

Error result MUST include:
- `check=policy_compliance`
- `status=error`
- non-empty `message`

#### Scenario: Internal evaluation exception
- **WHEN** policy evaluation fails unexpectedly
- **THEN** the tool returns a schema-valid error object instead of raising
