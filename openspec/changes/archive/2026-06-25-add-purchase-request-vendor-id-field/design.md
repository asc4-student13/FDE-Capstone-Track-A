## Context

The current `PurchaseRequest` schema validates request identity, requestor, cost center, vendor name, category, item details, quantity, pricing, and total amount, but omits `vendor_id`. In the mock request dataset, `vendor_id` is a first-class field and several checks (risk and vendor duplication) operate by vendor identifier. This mismatch weakens schema fidelity and can produce inconsistent call-site behavior.

## Goals / Non-Goals

**Goals:**
- Add `vendor_id` as a required typed field in `PurchaseRequest`.
- Keep `ProcurementRecommendation` unchanged.
- Update model-construction call sites and tests so the stricter schema validates consistently.
- Preserve current decision outcomes while improving input contract correctness.

**Non-Goals:**
- No changes to recommendation decision priority logic.
- No changes to mock data files.
- No introduction of new dependencies or runtime services.

## Decisions

1. Require `vendor_id: str` directly on `PurchaseRequest`.
- Rationale: It matches source data and removes ambiguity from identity-by-name matching.
- Alternative considered: infer vendor ID from `vendor_name` at runtime.
- Why rejected: inference is error-prone (name collisions/formatting drift) and violates explicit schema contracts.

2. Apply a strict model-contract update rather than optional/backward-compatible `vendor_id`.
- Rationale: OpenSpec requirements favor explicit validated fields; required input catches invalid payloads early.
- Alternative considered: `vendor_id: str | None = None` with fallback behavior.
- Why rejected: this prolongs inconsistent payload shapes and delays test alignment.

3. Update all PurchaseRequest construction paths in tests/examples in the same change.
- Rationale: prevents partial migration where schema changes but fixtures and examples fail.
- Alternative considered: phase updates across multiple changes.
- Why rejected: unnecessary churn for a small, bounded model correction.

## Risks / Trade-offs

- [Risk] Existing callers without `vendor_id` will fail validation immediately.
  - Mitigation: update all in-repo call sites and tests in this change; document stricter contract in rationale and tasks.
- [Risk] Dataset/name mismatches may remain in policy checks that compare `vendor_name`.
  - Mitigation: this change is model-alignment only; future change can normalize policy checks to also use `vendor_id` where appropriate.
- [Trade-off] Backward compatibility is reduced in favor of correctness.
  - Mitigation: controlled migration in one repository with updated tests.

## Migration Plan

1. Add required `vendor_id` field to `PurchaseRequest` in `models.py`.
2. Update tests and scripts that instantiate `PurchaseRequest` to include `vendor_id`.
3. Run targeted tests and scratch execution.
4. Run full test suite before review.

Rollback strategy:
- Revert this change set to restore prior schema if an external integration depends on the old payload shape.

## Open Questions

- Should policy compliance checks migrate to vendor-ID-first lookups in a follow-up change for consistency with risk/vendor-duplication checks?
