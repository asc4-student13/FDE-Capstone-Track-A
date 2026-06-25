## Purpose
Define and validate the typed data contract for procurement request and recommendation models.

## Requirements

### Requirement: Purchase request model enforces typed procurement fields
The system SHALL define a PurchaseRequest model with typed required fields for request identity,
requester, cost center, vendor name, vendor identifier, category, item details, quantity,
unit price, and total amount.

#### Scenario: Valid request is accepted by model
- **WHEN** all required fields are present, including `vendor_id`, with valid positive numeric values
- **THEN** the PurchaseRequest model validates successfully

#### Scenario: Missing vendor identifier is rejected
- **WHEN** a purchase request is submitted without `vendor_id`
- **THEN** model validation fails and reports `vendor_id` as required
