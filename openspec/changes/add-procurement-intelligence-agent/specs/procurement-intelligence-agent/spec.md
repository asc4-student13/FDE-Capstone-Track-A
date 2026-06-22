## ADDED Requirements

### Requirement: Purchase Request Input Schema
The system MUST define a Pydantic v2 model named `PurchaseRequest` that represents every field present in `mock_data/requests.json`: `request_id`, `requestor`, `cost_center_id`, `vendor_name`, `vendor_id`, `category`, `item_description`, `quantity`, `unit_price`, `total_amount`, `expected_outcome`, and `outcome_reason`.

Numeric and text validation MUST be applied as follows:
- `quantity` MUST be greater than 0.
- `unit_price` MUST be greater than 0.
- `total_amount` MUST be greater than 0.
- `request_id`, `requestor`, `cost_center_id`, `vendor_name`, `vendor_id`, `category`, and `item_description` MUST be non-empty strings.
- `expected_outcome` MAY be optional at runtime, but if provided it MUST be one of `approve`, `deny`, `escalate`, or `ambiguous`.
- `outcome_reason` MAY be optional at runtime, but if provided it MUST be a non-empty string.

The model SHOULD include a consistency validator that checks `total_amount` approximately equals `quantity * unit_price` when all three values are provided.

#### Scenario: Valid purchase request payload is accepted
- **WHEN** a request includes all required business fields with valid positive numeric values and non-empty identifiers
- **THEN** `PurchaseRequest` validation succeeds and yields a typed object

#### Scenario: Invalid numeric values are rejected
- **WHEN** `quantity`, `unit_price`, or `total_amount` is zero or negative
- **THEN** `PurchaseRequest` validation fails with field-specific validation errors

### Requirement: Structured Recommendation Output Contract
The system MUST define a Pydantic v2 model named `ProcurementRecommendation` used as the agent `output_type`.

The model MUST enforce:
- `decision` is required and constrained to exactly one of `approve`, `deny`, or `escalate`.
- `rationale` is required and MUST be a non-empty string after trimming whitespace.

#### Scenario: Agent returns valid structured output
- **WHEN** the LLM response is parsed into `ProcurementRecommendation`
- **THEN** parsing succeeds only if `decision` is in the allowed set and `rationale` is non-empty

#### Scenario: Invalid decision token is rejected
- **WHEN** the LLM produces a decision outside `approve|deny|escalate`
- **THEN** output validation fails and the run is treated as invalid

### Requirement: Data Access Through Loader Only
The agent and tools MUST read procurement domain data through `data/loader.py` and MUST NOT read files under `mock_data/` directly.

#### Scenario: Tool requests domain data
- **WHEN** any tool needs budgets, vendors, policies, or request context
- **THEN** it obtains data via loader functions rather than opening files directly

### Requirement: Budget Tool Contract
The system MUST provide a tool named `check_budget`.

Contract:
- Inputs MUST include `cost_center_id` and `total_amount`.
- Output MUST include at least: `check` (literal `budget`), `status` (`pass` or `fail`), `remaining_budget`, `overage_amount`, and `message`.
- `status` MUST be `fail` when `total_amount` exceeds remaining budget.

Error behavior:
- Exceptions MUST be caught and converted into a structured result with `status` = `error` and a non-empty `message`.

#### Scenario: Request exceeds remaining budget
- **WHEN** `total_amount` is greater than the remaining budget for the given cost center
- **THEN** `check_budget` returns `status=fail` with positive `overage_amount`

### Requirement: Vendor Duplication Tool Contract
The system MUST provide a tool named `check_vendor_duplication`.

Contract:
- Inputs MUST include `vendor_id`, `category`, and `total_amount`.
- Output MUST include at least: `check` (literal `vendor_duplication`), `status` (`pass` or `fail`), `active_contract_vendors`, `is_requested_vendor_contracted`, and `message`.
- The tool MUST evaluate single-source restrictions for categories with active contracts and thresholds consistent with policy definitions.

Error behavior:
- Exceptions MUST be caught and converted into a structured result with `status` = `error` and a non-empty `message`.

#### Scenario: Non-contracted vendor selected above single-source threshold
- **WHEN** request amount is above the single-source threshold in a category that has active contracted vendors and the requested vendor is not one of them
- **THEN** `check_vendor_duplication` returns `status=fail` and identifies contracted alternatives

### Requirement: Policy Compliance Tool Contract
The system MUST provide a tool named `check_policy_compliance`.

Contract:
- Inputs MUST include request fields needed for policy evaluation, including at least `category`, `vendor_id`, `total_amount`, and `quantity`.
- Output MUST include at least: `check` (literal `policy_compliance`), `status` (`pass`, `fail`, or `escalate`), `triggered_policies`, and `message`.
- The tool MUST evaluate policy triggers including prohibited category, expired contract vendor, manager/director thresholds, staffing single-source rule, and budget overage prohibition where policy evaluation is centralized.

Error behavior:
- Exceptions MUST be caught and converted into a structured result with `status` = `error` and a non-empty `message`.

#### Scenario: Prohibited category policy triggers denial
- **WHEN** category is `catering`
- **THEN** `check_policy_compliance` returns `status=fail` and includes `POL-004` in `triggered_policies`

#### Scenario: Director threshold policy triggers escalation
- **WHEN** `total_amount` is greater than or equal to 50000
- **THEN** `check_policy_compliance` returns `status=escalate` and includes `POL-003` in `triggered_policies`

### Requirement: Risk Assessment Tool Contract
The system MUST provide a tool named `assess_risk`.

Contract:
- Inputs MUST include at least `vendor_id`, `total_amount`, and budget context needed for near-threshold/tight-budget risk decisions.
- Output MUST include at least: `check` (literal `risk_assessment`), `status` (`pass` or `escalate`), `risk_factors`, and `message`.
- The tool MUST escalate when vendor `compliance_flag` is true.
- The tool SHOULD escalate near-threshold amounts close to the director threshold and MAY include configurable tolerance.

Error behavior:
- Exceptions MUST be caught and converted into a structured result with `status` = `error` and a non-empty `message`.

#### Scenario: Compliance-flagged vendor triggers escalation
- **WHEN** the requested vendor has `compliance_flag=true`
- **THEN** `assess_risk` returns `status=escalate` and includes the compliance factor in `risk_factors`

### Requirement: Decision Mapping and Precedence
The agent MUST call all four tools and map aggregated results to a single structured recommendation.

Decision mapping MUST follow strict precedence:
1. If any check returns `escalate`, final `decision` MUST be `escalate`.
2. Else if any check returns `fail`, final `decision` MUST be `deny`.
3. Else final `decision` MUST be `approve`.

The agent MUST produce a non-empty rationale summarizing triggered checks and policies.

#### Scenario: Escalation overrides denial
- **WHEN** one check returns `fail` and another returns `escalate`
- **THEN** final recommendation decision is `escalate`

#### Scenario: Approval only when all checks pass
- **WHEN** all checks return `pass`
- **THEN** final recommendation decision is `approve`

### Requirement: Error-to-Rationale Fallback Behavior
Tool invocation errors MUST NOT crash the recommendation flow.

The agent MUST:
- catch tool errors,
- include error details in rationale text,
- choose a safe deterministic fallback decision.

The fallback policy MUST default to `escalate` when one or more checks return `error`.

#### Scenario: A tool raises an exception
- **WHEN** any tool execution fails unexpectedly
- **THEN** the final response remains schema-valid and includes the failure context in `rationale` with `decision=escalate`
