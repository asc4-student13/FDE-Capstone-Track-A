## ADDED Requirements

### Requirement: Purchase request schema validation
The system SHALL validate purchase request input fields before any tool is invoked.
Required fields MUST include request identifiers, cost center, vendor details, category,
quantity, unit price, and total amount. Quantity and monetary fields MUST be greater than zero.

#### Scenario: Reject invalid numeric values
- **WHEN** a request contains quantity, unit price, or total amount less than or equal to zero
- **THEN** the request validation MUST fail and processing MUST not continue
