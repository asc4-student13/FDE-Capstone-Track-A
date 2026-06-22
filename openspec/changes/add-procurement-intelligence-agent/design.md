## Context

The procurement workflow needs an advisory pre-screening agent that evaluates purchase requests consistently before human review. The project already provides mock procurement datasets and expects strict schema validation, deterministic recommendation semantics, and transparent rationale. Constraints include using Pydantic v2 models, using Pydantic AI structured output, routing all mock data access through data/loader.py, and executing exactly four checks for every request.

Stakeholders are procurement officers (primary consumers), engineering maintainers of tools/models/tests, and governance reviewers who require traceable rationale and safe behavior when data/tools fail.

## Goals / Non-Goals

**Goals:**
- Produce structured recommendations with decision constrained to approve, deny, or escalate.
- Guarantee a non-empty rationale that names the checks and policy context driving the decision.
- Run all four checks for each request: budget, vendor duplication, policy compliance, and risk assessment.
- Apply deterministic decision priority: escalate first, then deny, then approve.
- Surface tool/data errors explicitly in rationale and route uncertain outcomes to escalation.

**Non-Goals:**
- Replacing final human procurement approval authority.
- Modifying source fixtures in mock_data/.
- Building a live external procurement integration.
- Expanding to additional policy domains beyond provided mock policy set.

## Decisions

1. Use strongly typed request and recommendation models as the agent I/O contract.
Rationale: Validation at system boundaries prevents malformed requests and constrains outputs to allowed decisions.
Alternative considered: untyped dict payloads. Rejected due to weaker validation and lower explainability.

2. Centralize data access through data/loader.py for budgets, vendors, policies, and requests.
Rationale: This enforces a single source of loading behavior, simplifies test isolation, and honors repository constraints against direct tool access to mock_data files.
Alternative considered: each tool reads JSON directly. Rejected for duplication and policy non-compliance.

3. Model each procurement check as a dedicated tool function and require all tools to run on every request.
Rationale: Independent tool outputs improve traceability and ensure rationale can reference complete evidence instead of short-circuiting.
Alternative considered: stop after first decisive violation. Rejected because it hides relevant context from procurement officers.

4. Apply recommendation precedence escalate > deny > approve.
Rationale: Escalation-first handling is safer for compliance uncertainty, critical risk, and data/tool failures. Deny applies for confirmed blocking violations when no higher-priority escalation condition exists. Approve is only valid when all checks pass.
Alternative considered: deny-before-escalate. Rejected because escalation-worthy risk could be incorrectly flattened into denial without expert review.

5. Encode policy and risk outcomes as structured signals consumed by decision logic.
Rationale: Policy rules and risk levels should return machine-readable indicators (for example forced decision and severity) to avoid brittle natural-language parsing.
Alternative considered: free-text only tool responses. Rejected due to ambiguity and difficult testability.

6. Treat tool failures as explicit safety events.
Rationale: Missing or unavailable data must not produce silent approval. Error context is surfaced in rationale and recommendation escalates for human triage.
Alternative considered: default deny on any tool error. Rejected because escalation preserves workflow continuity while signaling uncertainty.

## Risks / Trade-offs

- Risk: Over-escalation may increase reviewer workload near policy thresholds.
  Mitigation: Keep escalation triggers explicit, test threshold boundaries, and document rationale expectations.

- Risk: Policy interpretation drift between tools and system prompt.
  Mitigation: Encode policy IDs and forced outcomes in tool outputs and verify behavior with scenario-based tests.

- Risk: Inconsistent rationale quality from model generation.
  Mitigation: Require rationale content constraints and include test assertions for non-empty, check-referenced explanations.

- Risk: Data schema mismatch between loader and tools.
  Mitigation: Use typed loader outputs and defensive error handling paths that escalate with context.

- Trade-off: Running all checks per request adds compute overhead.
  Mitigation: Acceptable for this project scale and justified by better transparency and governance.

## Migration Plan

- Add validated data models and loader functions.
- Implement four procurement tools with stable result contracts and error paths.
- Wire tools into the Pydantic AI agent with structured output_type configuration.
- Apply decision-priority logic and rationale constraints in agent guidance and tests.
- Validate behavior against representative approve, deny, and escalate requests.
- Prepare rollback by reverting new agent/tool/model wiring while retaining dataset fixtures unchanged.

## Open Questions

- Should near-threshold escalation be fixed at 5 percent below director threshold or configurable per policy?
- Should manager-threshold non-compliance force escalate or deny when explicit approval metadata is absent?
- How should unknown vendor IDs be classified relative to high-risk versus escalation-first handling?
