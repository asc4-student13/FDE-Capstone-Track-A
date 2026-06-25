## 1. Tool Error Result Handling

- [x] 1.1 Update `tools/budget.py` to catch `FileNotFoundError`, `KeyError`, and `Exception` separately and return typed error results.
- [x] 1.2 Update `tools/policy_compliance.py` to catch `FileNotFoundError`, `KeyError`, and `Exception` separately and return typed error results.
- [x] 1.3 Update `tools/risk_assessment.py` to catch `FileNotFoundError`, `KeyError`, and `Exception` separately and return typed error results.
- [x] 1.4 Update `tools/vendor_duplication.py` to catch `FileNotFoundError`, `KeyError`, and `Exception` separately and return typed error results.

## 2. Agent Prompt Escalation Rule

- [x] 2.1 Edit only the system prompt text in `agent.py` to require escalation when any tool returns an error result.
- [x] 2.2 Ensure prompt wording requires rationale to explicitly reference tool errors.

## 3. Regression Test Coverage

- [x] 3.1 Add a test that patches `data.loader.load_budgets` to raise `FileNotFoundError` and verifies recommendation is `escalate`.
- [x] 3.2 Assert the same test checks rationale mentions budget/data loading failure.

## 4. Verification

- [x] 4.1 Run targeted tests for budget and agent behavior.
- [x] 4.2 Run full test suite and confirm no regressions.
