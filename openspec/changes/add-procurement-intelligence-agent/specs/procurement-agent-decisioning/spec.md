## ADDED Requirements

### Requirement: Recommendation decision priority
The system MUST apply recommendation precedence in strict order: escalate, then deny, then
approve.

#### Scenario: Escalation overrides deny conditions
- **WHEN** escalate and deny conditions are both present
- **THEN** final recommendation decision MUST be `escalate`

### Requirement: Tool selection logic per request
For each valid request, the agent MUST call check_budget, check_vendor_duplication,
check_policy_compliance, and assess_risk before finalizing decision output.
The agent MUST NOT short-circuit after the first violation because rationale requires multi-check
context.

#### Scenario: Deny-only signal without escalation
- **WHEN** at least one deny condition exists and no escalation condition exists
- **THEN** final recommendation decision MUST be `deny`

#### Scenario: No violations produce approval
- **WHEN** no escalation or deny condition exists after all checks
- **THEN** final recommendation decision MUST be `approve`

### Requirement: Error fallback path
If any required tool returns an error, the agent MUST treat the request as incomplete information
and MUST return decision escalate.

#### Scenario: Tool error forces escalation
- **WHEN** one or more tool responses include an error field
- **THEN** final recommendation decision MUST be `escalate`
