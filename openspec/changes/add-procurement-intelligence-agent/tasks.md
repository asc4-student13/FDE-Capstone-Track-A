## 1. Models

- [ ] 1.1 Implement PurchaseRequest with all request input fields from mock_data/requests.json
- [ ] 1.2 Add numeric validators for quantity, unit_price, and total_amount
- [ ] 1.3 Implement ProcurementRecommendation with decision constrained to approve/deny/escalate
- [ ] 1.4 Enforce non-empty rationale validation

## 2. Data Loader

- [ ] 2.1 Implement loader functions for budgets, vendors, policies, and requests
- [ ] 2.2 Ensure no tool or agent module reads mock_data files directly
- [ ] 2.3 Ensure loader errors propagate in a way tools can surface in results

## 3. Budget Tool

- [ ] 3.1 Implement check_budget(cost_center_id, requested_amount)
- [ ] 3.2 Return within_budget, remaining_budget, requested_amount, overage, and cost_center_id
- [ ] 3.3 Return error context for missing cost center or data-load failures

## 4. Vendor Duplication Tool

- [ ] 4.1 Implement check_vendor_duplication(vendor_id, category, amount)
- [ ] 4.2 Apply POL-001 threshold and active-contract conflict logic
- [ ] 4.3 Return violation status, conflicting vendor details, and reason text
- [ ] 4.4 Return error context for data-load failures

## 5. Policy Compliance Tool

- [ ] 5.1 Implement check_policy_compliance(vendor_id, category, amount, quantity)
- [ ] 5.2 Encode deny/escalate policy triggers and return violation records
- [ ] 5.3 Return highest_severity and violation_count fields consistently
- [ ] 5.4 Return error context with safe escalation severity on data failures

## 6. Risk Assessment Tool

- [ ] 6.1 Implement assess_risk(vendor_id)
- [ ] 6.2 Map vendor state to low/medium/high/critical risk levels
- [ ] 6.3 Return required risk fields and error details for unknown or unavailable data

## 7. Agent Wiring and Decisioning

- [ ] 7.1 Construct Pydantic AI agent with output_type ProcurementRecommendation
- [ ] 7.2 Execute all four tools for each request before recommendation output
- [ ] 7.3 Implement strict decision priority escalate > deny > approve
- [ ] 7.4 Implement fallback: any tool error forces escalate and is included in rationale

## 8. Tests and Validation

- [ ] 8.1 Add unit tests for each tool primary success path
- [ ] 8.2 Add edge-case tests for budget overage, expired contract, compliance flag, and duplication
- [ ] 8.3 Add end-to-end tests for approve, deny, and escalate outcomes
- [ ] 8.4 Run openspec validate add-procurement-intelligence-agent
- [ ] 8.5 Run pytest tests/ -v --tb=short --junitxml=docs/test-results.xml