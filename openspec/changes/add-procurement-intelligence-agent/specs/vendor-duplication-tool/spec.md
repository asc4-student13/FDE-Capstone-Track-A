## ADDED Requirements

### Requirement: Vendor Duplication Tool Interface
The system MUST provide a tool named `check_vendor_duplication`.

The tool MUST accept:
- `vendor_id`
- `category`
- `total_amount`

The tool MUST return a structured object with at least:
- `check` (literal `vendor_duplication`)
- `status` (`pass`, `fail`, or `error`)
- `triggered_policy_ids` (list)
- `conflicting_vendor_ids` (list)
- `conflicting_contracts` (list of contract detail objects)
- `is_requested_vendor_contracted` (boolean)
- `message` (non-empty string)

#### Scenario: Tool returns structured pass result
- **WHEN** the requested vendor is contracted for the category, or no conflicting contracted vendor exists
- **THEN** `check_vendor_duplication` returns `status=pass` and empty conflict lists

### Requirement: Single-Source Conflict Detection
The tool MUST detect whether FedEx has one or more active contracts with other vendors in the same category.

For each conflicting vendor, output MUST include:
- `vendor_id`
- `vendor_name`
- `contract_id`
- `contract_status`

The requested vendor itself MUST NOT be listed as a conflict.

#### Scenario: Conflicting contracted vendors are returned
- **WHEN** the requested vendor is not contracted and other active contracted vendors exist in the same category
- **THEN** the tool returns those alternatives in `conflicting_vendor_ids` and `conflicting_contracts`

### Requirement: POL-001 Threshold Denial Trigger
The tool MUST enforce POL-001 single-source behavior based on the policy threshold amount.

Rules:
- If `total_amount` is greater than POL-001 `threshold_amount` and category is affected by POL-001, and the requested vendor is not contracted while contracted alternatives exist, `status` MUST be `fail`.
- In this case, output MUST include `POL-001` in `triggered_policy_ids`.
- If amount is at or below threshold, tool SHOULD report conflicts but MUST NOT fail only because of POL-001 threshold logic.

#### Scenario: Above-threshold non-contracted vendor fails
- **WHEN** amount exceeds POL-001 threshold and contracted alternatives exist for the category
- **THEN** the tool returns `status=fail` with `POL-001` and conflict details

### Requirement: Error Handling
Exceptions MUST be caught and converted into a structured error result.

Error result MUST include:
- `check=vendor_duplication`
- `status=error`
- non-empty `message`

#### Scenario: Internal tool exception
- **WHEN** data lookup or evaluation fails unexpectedly
- **THEN** the tool returns a schema-valid error object instead of raising
