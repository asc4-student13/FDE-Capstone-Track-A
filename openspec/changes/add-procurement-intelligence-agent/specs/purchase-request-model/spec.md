## ADDED Requirements

### Requirement: Purchase request contract validation
The system MUST validate purchase request inputs using a typed PurchaseRequest model before
tool execution begins.

The model MUST include these fields from mock_data/requests.json:
- request_id
- requestor
- cost_center_id
- vendor_name
- vendor_id
- category
- item_description
- quantity
- unit_price
- total_amount

The model MUST NOT require dataset-only annotation fields expected_outcome or outcome_reason.

#### Scenario: Missing required field fails validation
- **WHEN** one of the required request fields is absent
- **THEN** model validation MUST fail and no tool call MUST execute

#### Scenario: Invalid quantity is rejected
- **WHEN** quantity is less than or equal to zero
- **THEN** request validation MUST fail and processing MUST stop

### Requirement: Numeric field validator behavior
quantity MUST be greater than zero. unit_price and total_amount MUST be greater than zero.
The model SHOULD validate that total_amount equals quantity multiplied by unit_price within a
small rounding tolerance to prevent malformed requests.

#### Scenario: Invalid amount is rejected
- **WHEN** unit_price or total_amount is less than or equal to zero
- **THEN** model validation MUST fail
