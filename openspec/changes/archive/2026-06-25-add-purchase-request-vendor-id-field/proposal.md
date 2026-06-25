## Why

The `PurchaseRequest` model is missing `vendor_id`, even though request records in `mock_data/requests.json` include it and downstream checks rely on vendor identity. This mismatch creates validation inconsistencies and forces callers to infer vendor identity indirectly.

## What Changes

- Add required `vendor_id` to the `PurchaseRequest` model so request validation matches mock data fields.
- Update model-related tests and request construction sites to include `vendor_id` where `PurchaseRequest` instances are created.
- Align examples and scratch execution paths with the updated model contract.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `procurement-model-validation`: Update the purchase request schema requirement to explicitly require `vendor_id` as a typed required field.

## Impact

- Affected code: `models.py`, tests that construct `PurchaseRequest`, and local execution examples such as `scratch_test.py`.
- API/model contract: `PurchaseRequest` becomes stricter by requiring `vendor_id`.
- Dependencies/systems: No new external dependencies; impacts validation and call-site compatibility only.
