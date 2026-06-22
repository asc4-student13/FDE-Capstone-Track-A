## ADDED Requirements

### Requirement: Procurement data is loaded through centralized loader APIs
The system SHALL provide loader functions for budgets, vendors, policies, and sample requests, and tools SHALL use these loader functions rather than reading fixture files directly.

#### Scenario: Tool uses loader abstraction
- **WHEN** any procurement tool requires reference data
- **THEN** it retrieves data through data loader functions

### Requirement: Loader failures surface actionable errors
The loader and tool boundary SHALL surface data unavailability as explicit error context consumable by recommendation logic.

#### Scenario: Fixture load fails
- **WHEN** a referenced procurement data source cannot be loaded
- **THEN** the calling tool returns error context instead of silently continuing
