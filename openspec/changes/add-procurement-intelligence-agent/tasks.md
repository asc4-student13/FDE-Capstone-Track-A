## 1. Data Models and Loader

- [x] 1.1 Implement PurchaseRequest and ProcurementRecommendation Pydantic v2 models with typed fields and decision constraints.
- [x] 1.2 Add rationale non-empty validation on ProcurementRecommendation output.
- [x] 1.3 Implement data loader functions in data/loader.py for requests, vendors, policies, and budgets.
- [x] 1.4 Ensure tools consume loader functions and do not read mock_data files directly.

## 2. Tool Implementations

- [x] 2.1 Implement check_budget tool to evaluate remaining budget, overage, and missing cost center/data error paths.
- [x] 2.2 Implement check_vendor_duplication tool for single-source threshold logic and conflicting contracted vendors.
- [x] 2.3 Implement check_policy_compliance tool for policy violations, forced decision signals, and severity aggregation.
- [x] 2.4 Implement assess_risk tool for vendor risk classification and unknown-vendor handling.

## 3. Agent Wiring and Decision Logic

- [x] 3.1 Create the Pydantic AI procurement agent with output_type set to ProcurementRecommendation.
- [x] 3.2 Register all four tools and require complete four-check execution for every request.
- [x] 3.3 Implement recommendation precedence rules: escalate before deny before approve.
- [x] 3.4 Ensure tool error outcomes are surfaced in rationale and force escalation.

## 4. Testing and Verification

- [x] 4.1 Add unit tests for each tool primary success path and key edge cases.
- [x] 4.2 Add agent tests that demonstrate all three outcomes: approve, deny, and escalate.
- [x] 4.3 Add tests that verify rationale is non-empty and references decision-driving checks/policies.
- [x] 4.4 Add at least one partial-data/tool-failure test to verify safe escalation behavior.

## 5. Quality Gates and OpenSpec Validation

- [x] 5.1 Run openspec validate add-procurement-intelligence-agent and resolve any schema or artifact issues.
- [x] 5.2 Run pytest tests/ -v --tb=short --junitxml=docs/test-results.xml and confirm passing results.
- [ ] 5.3 Update go/no-go and review evidence artifacts as required for RAPID controls before review.
