## Context

The procurement domain requires an advisory pre-screening step that is reliable, auditable, and
policy-aligned. The agent must produce typed recommendations while delegating domain logic to
explicit tool checks and using shared mock data loaded through `data/loader.py`.

## Goals / Non-Goals

**Goals:**
- Build a structured recommendation pipeline with constrained decisions and non-empty rationale.
- Keep tool responsibilities clear: budget, duplication, policy, and risk checks.
- Enforce deterministic decision precedence: escalate, then deny, then approve.
- Ensure tool failures become visible rationale signals and safe escalation outcomes.

**Non-Goals:**
- Automating final procurement approval authority.
- Integrating live external systems or production data sources.
- Changing mock data fixture content directly.

## Decisions

- Use Pydantic v2 models for input and output contracts.
Rationale: model validation creates deterministic boundaries and easier test assertions.

- Construct the agent with Pydantic AI and structured output contract.
Rationale: keeps orchestration compatible with AI-assisted reasoning while preserving schema safety.

- Keep business checks in tools and data access in loader only.
Rationale: enforces separation of concerns and prevents fixture coupling in agent logic.

- Apply strict decision priority (`escalate > deny > approve`).
Rationale: favors safe handling for compliance, policy, and data-quality uncertainty.

- Surface tool errors in rationale and force escalation.
Rationale: avoids silent failures and preserves explainability for procurement officers.

## Decision Priority Order

The recommendation engine applies strict precedence:
1. Escalate
2. Deny
3. Approve

Escalate always wins if any escalation condition is present, including policy escalation triggers,
critical risk, or tool/data errors.

## Tool Selection Logic

For each request, the agent runs all four tools:
- check_budget(cost_center_id, total_amount)
- check_vendor_duplication(vendor_id, category, total_amount)
- check_policy_compliance(vendor_id, category, total_amount, quantity)
- assess_risk(vendor_id)

The design intentionally avoids early exit so rationale can reflect all relevant check outcomes.

## Error Fallback Path

If any required tool returns an error, the agent takes a safe fallback path:
- set decision to escalate
- include error context in rationale
- preserve request_id and available check outputs for analyst review

This fallback prevents approvals under incomplete information.

## Risks / Trade-offs

- [Risk] Over-conservative escalation for borderline cases.
  -> Mitigation: include explicit rationale details and policy identifiers.

- [Risk] Divergence between sample expected outcomes and implemented policy interpretation.
  -> Mitigation: keep policy mapping explicit and validate with fixture-driven tests.

- [Risk] Regression if tools bypass loader and read mock data directly.
  -> Mitigation: enforce code review checks and tests around loader usage.

## Migration Plan

1. Define/verify models and loader contracts.
2. Implement or align tools with policy thresholds and vendor/budget semantics.
3. Wire agent orchestration with priority rules and error handling.
4. Run tests with junit capture and keep backout plan current.
5. Roll back by reverting to prior passing commit if recommendation quality regresses.

## Open Questions

- Should manager-threshold non-compliance (POL-002) influence recommendation decisions directly?
- Should ambiguous cases (like low-budget no-contract scenarios) default to approval or escalation?