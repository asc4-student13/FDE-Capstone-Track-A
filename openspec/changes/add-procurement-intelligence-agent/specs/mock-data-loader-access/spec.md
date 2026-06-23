## ADDED Requirements

### Requirement: Loader-only mock data access
The system MUST load mock domain data through data/loader.py and MUST NOT read mock_data/
files directly from agent or tool modules.

The loader MUST provide explicit functions for budgets, vendors, policies, and requests data.
If a required mock file is missing, the loader MUST raise a file-related error that calling tools
can catch and surface.

#### Scenario: Tool obtains dataset through loader
- **WHEN** a tool requires budgets, vendors, policies, or requests data
- **THEN** the tool MUST call a loader function instead of direct file I/O

#### Scenario: Missing mock file propagates as tool-visible error
- **WHEN** a referenced mock data file does not exist
- **THEN** loader behavior MUST allow tool logic to produce an explicit error result
