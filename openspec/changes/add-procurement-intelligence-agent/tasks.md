## 1. Models and Validation

- [x] 1.1 Define or refine `PurchaseRequest` in `solutions/models.py` to represent every field from `mock_data/requests.json` with Pydantic v2 validators.
- [x] 1.2 Define or refine `ProcurementRecommendation` in `solutions/models.py` with `decision` constrained to `approve|deny|escalate` and non-empty `rationale`.
- [x] 1.3 Add or update model tests to verify numeric validation, enum constraints, and rationale non-empty enforcement.

## 2. Data Loader

- [x] 2.1 Verify `solutions/data/loader.py` exposes the budgets, vendors, and policies data needed by all tools.
- [x] 2.2 Refactor any direct fixture file reads in agent/tools to call loader functions only.
- [x] 2.3 Add loader-focused tests or fixtures to confirm stable joins by `cost_center_id`, `vendor_id`, and category.

## 3. Tool Contracts

- [x] 3.1 Implement/normalize `check_budget` contract in `solutions/tools/budget.py` including pass/fail/error and overage details.
- [ ] 3.2 Implement/normalize `check_vendor_duplication` contract in `solutions/tools/vendor_duplication.py` for single-source checks.
- [ ] 3.3 Implement/normalize `check_policy_compliance` contract in `solutions/tools/policy_compliance.py` for policy-trigger mapping.
- [ ] 3.4 Implement/normalize `assess_risk` contract in `solutions/tools/risk_assessment.py` for compliance flag and threshold risk escalation.
- [ ] 3.5 Ensure each tool catches internal exceptions and returns structured error output.

## 4. Agent Orchestration

- [ ] 4.1 Wire all four tools in `solutions/agent.py` so every recommendation evaluates budget, duplication, policy, and risk.
- [ ] 4.2 Implement decision precedence `escalate > deny > approve` when aggregating tool outcomes.
- [ ] 4.3 Implement fallback behavior so tool errors produce schema-valid output and are reflected in rationale.

## 5. Outcome Coverage Tests

- [ ] 5.1 Add or update tests for representative `approve` outcomes from sample requests.
- [ ] 5.2 Add or update tests for representative `deny` outcomes (budget overage, expired contract, prohibited category, single-source violation).
- [ ] 5.3 Add or update tests for representative `escalate` outcomes (compliance flag, threshold/near-threshold, conflict cases).
- [ ] 5.4 Add a test that simulates a tool failure and verifies fallback `escalate` with explanatory rationale.

## 6. Spec and Change Validation

- [ ] 6.1 Run `openspec validate add-procurement-intelligence-agent` and resolve any errors.
- [ ] 6.2 Run `openspec list` to confirm the change remains active.
- [ ] 6.3 Keep checklist state updated as implementation tasks are completed in Sessions 2 and 3.