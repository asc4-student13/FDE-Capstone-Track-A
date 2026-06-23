## ADDED Requirements

### Requirement: Budget Tool Interface
The system MUST provide a tool named `check_budget`.

The tool MUST accept:
- `cost_center_id` (string)
- `requested_amount` (number)

The tool MUST return a structured object with at least:
- `check` (literal `budget`)
- `status` (`pass`, `fail`, or `error`)
- `cost_center_id`
- `requested_amount`
- `remaining_budget`
- `overage_amount`
- `message` (non-empty string)

#### Scenario: Tool returns structured pass result
- **WHEN** `requested_amount` is less than or equal to the cost center remaining budget
- **THEN** `check_budget` returns `status=pass` and `overage_amount=0`

### Requirement: Loader-Backed Budget Data Access
The tool MUST load budget records through `data/loader.py` and MUST NOT read `mock_data/` directly.

#### Scenario: Budget lookup is loader-backed
- **WHEN** `check_budget` needs budget data
- **THEN** it imports and uses `load_budgets()` from `data.loader`

### Requirement: Budget Decision Logic
The tool MUST compare `requested_amount` against the remaining budget for the matching `cost_center_id`.

Rules:
- If `requested_amount` is greater than remaining budget, `status` MUST be `fail`.
- If `requested_amount` is less than or equal to remaining budget, `status` MUST be `pass`.
- `overage_amount` MUST be positive only in fail cases.

#### Scenario: Over-budget request fails
- **WHEN** a matching cost center exists and `requested_amount` exceeds remaining budget
- **THEN** `check_budget` returns `status=fail` with positive `overage_amount`

### Requirement: Missing Cost Center Handling
The tool MUST handle unknown `cost_center_id` values without raising.

#### Scenario: Cost center not found
- **WHEN** no budget record matches `cost_center_id`
- **THEN** `check_budget` returns `status=error` with a non-empty `message`

### Requirement: Error Handling
Unexpected exceptions MUST be caught and converted into a structured error result.

Error result MUST include:
- `check=budget`
- `status=error`
- non-empty `message`

#### Scenario: Internal exception
- **WHEN** budget evaluation fails unexpectedly
- **THEN** the tool returns a schema-valid error object instead of raising
