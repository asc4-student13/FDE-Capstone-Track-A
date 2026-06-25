## Context

The procurement agent currently depends on tool calls that may raise runtime exceptions,
particularly during mock-data loading. The project requires deterministic recommendations
(`approve`, `deny`, `escalate`) and explicit rationale, but uncaught tool exceptions can bypass
that contract and produce unreliable behavior. This change standardizes tool-side error handling
and aligns agent prompt behavior to escalation semantics when tool errors occur.

Constraints:
- Do not add new tools or new Pydantic models.
- Keep implementation scoped to existing modules.
- In `agent.py`, only update the system prompt text.

## Goals / Non-Goals

**Goals:**
- Ensure each existing tool catches `FileNotFoundError`, `KeyError`, and generic `Exception`
  separately.
- Ensure tools return typed error results instead of raising for those failure paths.
- Ensure the agent system prompt explicitly instructs escalation with rationale that references
  tool errors.
- Add a regression test for budget data load failure that verifies escalate behavior.

**Non-Goals:**
- Introducing new tool modules.
- Introducing new output models or changing recommendation enum values.
- Refactoring unrelated agent orchestration logic.

## Decisions

1. Keep error-shape handling in existing tool result types.
Rationale: preserves current API and avoids introducing new models while still enabling typed
failure outputs.
Alternatives considered: adding a dedicated shared error model; rejected due to explicit scope
restriction against new models.

2. Handle three exception classes explicitly in each tool.
Rationale: `FileNotFoundError` and `KeyError` represent high-signal data-path failures and schema
mismatches, while generic `Exception` is needed as a safety net.
Alternatives considered: catching only base `Exception`; rejected because it loses failure intent
and weakens diagnostics.

3. Constrain agent-side change to system prompt only.
Rationale: aligns with requested scope and minimizes risk in core orchestration.
Alternatives considered: adding explicit runtime branch logic in `agent.py`; rejected because user
requested system-prompt-only changes there.

4. Validate behavior with a targeted patched-loader test.
Rationale: directly proves escalation when `load_budgets` fails and guards against regressions.
Alternatives considered: end-to-end fault injection across all tools; deferred to keep change
small and focused.

## Risks / Trade-offs

- [Risk] Tools may emit inconsistent error field wording across modules.
  -> Mitigation: keep error result content aligned to shared typed structures and require tests for
     key error-path behavior.
- [Risk] Prompt-only guidance could be weaker than hard-coded logic if model deviates.
  -> Mitigation: enforce with deterministic test asserting `escalate` and rationale content.
- [Risk] Catch-all exception handling can mask programming bugs.
  -> Mitigation: include exception details in typed error result rationale path for visibility.

## Migration Plan

1. Update existing tools to return typed error results for the three exception categories.
2. Update agent system prompt language to mandate escalation with error-referencing rationale.
3. Add and run regression tests.
4. If regressions occur, revert tool error-path edits and prompt text as a single change set.

## Open Questions

- Should future phases add per-tool error codes for finer-grained analytics, or keep message-only
  typed errors?
