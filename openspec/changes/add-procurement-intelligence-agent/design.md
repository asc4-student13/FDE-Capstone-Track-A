## Context

The project introduces a procurement pre-screening agent that recommends `approve`, `deny`, or `escalate` for purchase requests. Domain fixtures in `mock_data/` define expected outcomes and policy triggers, but implementation is constrained to read data through `data/loader.py`. The capstone requires Pydantic v2 model validation for both request inputs and recommendation outputs, plus explicit contracts for four domain tools.

## Goals / Non-Goals

**Goals:**
- Implement deterministic recommendation behavior with explicit precedence: escalate > deny > approve.
- Enforce strict input/output schema validation through Pydantic models.
- Keep tool behavior observable through structured return objects and rationale text.
- Preserve continuity when tools fail by degrading safely instead of crashing.

**Non-Goals:**
- No UI, web service, or deployment pipeline changes.
- No authentication/authorization features.
- No persistent storage or database schema work.
- No direct reads of fixture files from agent/tool code.

## Decisions

1. Decision: Use Pydantic models as runtime contracts for both request and response.
- Rationale: The lab explicitly relies on structured output constraints; schema enforcement guarantees typed outcomes.
- Alternative considered: Plain dict validation in business logic.
- Why rejected: Weaker guarantees and less explicit runtime contract.

2. Decision: Centralize data access through `data/loader.py`.
- Rationale: Matches capstone requirement and prevents data-source coupling.
- Alternative considered: Each tool opens fixture JSON files directly.
- Why rejected: Violates architecture constraint and duplicates parsing logic.

3. Decision: Keep each tool independently responsible for one check domain and a stable return shape.
- Rationale: Improves testability and deterministic aggregation.
- Alternative considered: One large policy engine function.
- Why rejected: Harder to test failures and reason about partial results.

4. Decision: Apply strict precedence `escalate > deny > approve` at aggregation time.
- Rationale: Matches session instructions and resolves conflicts consistently.
- Alternative considered: `deny > escalate > approve`.
- Why rejected: Conflicts with required capstone behavior and escalation-first governance stance.

5. Decision: Convert tool exceptions to structured error results and default final decision to `escalate`.
- Rationale: Keeps responses schema-valid and safe under partial failure.
- Alternative considered: Propagate exception and fail run.
- Why rejected: Produces unstable UX and violates required error reflection in rationale.

6. Decision: Treat manager threshold (10,000-49,999.99) as compliance metadata unless combined with explicit violation.
- Rationale: Sample data includes approvals in this range; auto-denial would contradict fixtures.
- Alternative considered: deny all requests in range without explicit approval evidence.
- Why rejected: Inconsistent with provided expected outcomes.

## Risks / Trade-offs

- [Policy interpretation drift] -> Mitigation: encode policy IDs in tool outputs and reference them in rationale and tests.
- [Ambiguous fixture case REQ-015] -> Mitigation: enforce deterministic fallback logic (prefer escalate under uncertainty).
- [Duplicated threshold constants across tools] -> Mitigation: source threshold values from loader policy data rather than hard-coding.
- [Overly strict validators reject realistic data] -> Mitigation: constrain only clearly invalid states (empty IDs, non-positive amounts) and test edge fixtures.

## Migration Plan

1. Add or refine model contracts in `solutions/models.py`.
2. Verify/extend loader APIs in `solutions/data/loader.py` for all tool needs.
3. Implement/normalize contracts for each tool under `solutions/tools/`.
4. Wire tool calls and aggregation logic in `solutions/agent.py`.
5. Update or add tests in `solutions/tests/` to cover approve/deny/escalate paths and tool-error fallback.
6. Run `openspec validate add-procurement-intelligence-agent` to confirm artifacts stay valid during implementation planning.

Rollback strategy:
- Revert agent wiring to previous deterministic baseline while retaining tests and spec artifacts for future iteration.

## Open Questions

- Should near-threshold escalation tolerance be fixed at 5% or configurable?
- Should policy compliance own budget overage evaluation, or should budget remain authoritative with policy only annotating?
- For ambiguous cases with no explicit violation, should fallback be always escalate or configurable by environment?