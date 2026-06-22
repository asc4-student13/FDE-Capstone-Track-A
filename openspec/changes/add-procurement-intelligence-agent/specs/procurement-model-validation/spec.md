## ADDED Requirements

### Requirement: Purchase request model enforces typed procurement fields
The system SHALL define a PurchaseRequest model with typed required fields for request identity, requester, cost center, vendor, category, item details, quantity, unit price, and total amount.

#### Scenario: Valid request is accepted by model
- **WHEN** all required fields are present with valid positive numeric values
- **THEN** the PurchaseRequest model validates successfully

### Requirement: Recommendation model constrains decision outcomes
The system SHALL define a ProcurementRecommendation model that restricts decision values to approve, deny, or escalate and requires non-empty rationale text.

#### Scenario: Invalid decision is rejected
- **WHEN** a recommendation is produced with a decision outside approve, deny, or escalate
- **THEN** model validation fails

#### Scenario: Blank rationale is rejected
- **WHEN** a recommendation rationale is empty or whitespace-only
- **THEN** model validation fails
