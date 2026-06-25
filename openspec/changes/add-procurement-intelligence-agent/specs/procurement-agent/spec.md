## ADDED Requirements

### Requirement: Agent input and output contracts use typed models
The agent SHALL accept a validated PurchaseRequest input and SHALL return a ProcurementRecommendation output, both defined in models.py.

#### Scenario: Valid typed request is processed
- **WHEN** a PurchaseRequest with all required fields is provided
- **THEN** the agent evaluates the request and returns a ProcurementRecommendation

#### Scenario: Output decision and rationale satisfy model constraints
- **WHEN** the agent produces a recommendation
- **THEN** decision is one of approve, deny, or escalate and rationale is non-empty

### Requirement: Agent invokes all four procurement tools per evaluation
The agent SHALL use all four tools during each request evaluation: check_budget, check_vendor_duplication, check_policy_compliance, and assess_risk.

#### Scenario: Four-tool orchestration is executed
- **WHEN** a request is evaluated
- **THEN** the agent calls budget, vendor duplication, policy compliance, and risk assessment checks before finalizing output

### Requirement: Decision priority is deterministic across concurrent signals
The agent SHALL apply decision precedence in this order: escalate, then deny, then approve.

#### Scenario: Escalation and denial signals both occur
- **WHEN** at least one check indicates escalation and at least one check indicates denial
- **THEN** the final decision is escalate

#### Scenario: Denial signal occurs without escalation signal
- **WHEN** one or more checks indicate denial and no checks indicate escalation
- **THEN** the final decision is deny

#### Scenario: No escalation or denial signals occur
- **WHEN** all checks complete without escalation or denial triggers
- **THEN** the final decision is approve

### Requirement: Tool and data failures are handled conservatively
The agent SHALL treat any tool failure or explicit tool error output as a safety condition, include the failure context in rationale, and choose escalate.

#### Scenario: One required tool fails or returns explicit error
- **WHEN** any required tool raises an exception or returns an error field
- **THEN** the recommendation decision is escalate and rationale includes the tool failure context

### Requirement: System prompt enforces procedural and governance constraints
The agent system prompt SHALL require complete four-check execution, strict decision precedence, explicit rationale quality requirements, and conservative handling of incomplete data.

#### Scenario: Prompt-guided decision formation
- **WHEN** the agent forms a recommendation
- **THEN** the system prompt instructions enforce all of the following constraints:
  - all four tools are run for each request
  - decision precedence is escalate before deny before approve
  - rationale cites the checks and evidence that drove the decision
  - tool/data errors are surfaced and force escalation
