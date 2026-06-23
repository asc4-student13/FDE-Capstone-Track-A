## 1. Models and Contracts

- [x] 1.1 Implement purchase request schema validation with positive numeric constraints
- [x] 1.2 Implement recommendation schema enforcing `approve|deny|escalate` decisions
- [x] 1.3 Enforce non-empty rationale validation on all recommendation outputs

## 2. Data and Tooling

- [x] 2.1 Implement centralized loader functions for budgets, vendors, policies, and requests
- [x] 2.2 Implement budget check tool with overage and missing-cost-center handling
- [x] 2.3 Implement vendor duplication tool for high-value single-source violations
- [x] 2.4 Implement policy compliance tool with violation severity outputs
- [x] 2.5 Implement risk assessment tool with low/medium/high/critical outcomes

## 3. Agent Orchestration

- [x] 3.1 Wire all four tools into the procurement agent runtime
- [x] 3.2 Implement decision priority and escalation-on-error behavior
- [x] 3.3 Ensure recommendation rationale references checks that drove the outcome

## 4. Testing and Validation

- [x] 4.1 Add unit tests for each tool success path and representative edge case
- [x] 4.2 Add end-to-end tests covering approve, deny, and escalate outcomes
- [x] 4.3 Run OpenSpec validation and address any change-level validation findings
- [x] 4.4 Run pytest with junit output for RAPID review evidence
