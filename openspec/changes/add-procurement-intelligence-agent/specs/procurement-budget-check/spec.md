## ADDED Requirements

### Requirement: Budget check validates remaining cost-center capacity
The budget check tool SHALL compare requested total amount to the cost center remaining budget and return whether the request is within budget, including overage amount when exceeded.

#### Scenario: Request fits remaining budget
- **WHEN** requested amount is less than or equal to remaining budget for the cost center
- **THEN** the tool reports within-budget true and overage zero

#### Scenario: Request exceeds remaining budget
- **WHEN** requested amount is greater than remaining budget for the cost center
- **THEN** the tool reports within-budget false and includes positive overage amount

### Requirement: Unknown cost center produces explicit budget-check error
The budget check SHALL return a structured error signal when the provided cost center does not exist in budget data.

#### Scenario: Cost center not found
- **WHEN** the request references an unknown cost center identifier
- **THEN** the tool returns an error field describing the missing cost center
