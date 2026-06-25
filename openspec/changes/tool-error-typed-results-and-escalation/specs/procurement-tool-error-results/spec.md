## ADDED Requirements

### Requirement: Tools return typed results for operational failures
Each existing procurement tool MUST catch `FileNotFoundError`, `KeyError`, and generic
`Exception` separately, and MUST return a typed error result object instead of raising these
exceptions.

#### Scenario: Budget data file missing
- **WHEN** budget checking invokes a data load that raises `FileNotFoundError`
- **THEN** the budget tool returns a typed error result describing the data loading failure
- **THEN** no exception is propagated to the agent caller

#### Scenario: Required data key missing
- **WHEN** a tool encounters `KeyError` while reading loaded records
- **THEN** the tool returns a typed error result that identifies missing-key failure semantics
- **THEN** no exception is propagated to the agent caller

#### Scenario: Unexpected runtime failure
- **WHEN** a tool encounters an unexpected `Exception`
- **THEN** the tool returns a typed error result containing generic failure context
- **THEN** no exception is propagated to the agent caller
