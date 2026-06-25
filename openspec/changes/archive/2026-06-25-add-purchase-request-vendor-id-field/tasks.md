## 1. Model Contract Update

- [x] 1.1 Add required `vendor_id: str` to `PurchaseRequest` in `models.py`
- [x] 1.2 Ensure `PurchaseRequest` field list and ordering align with request payload semantics

## 2. Call-Site Alignment

- [x] 2.1 Update all in-repo `PurchaseRequest(...)` construction paths to include `vendor_id`
- [x] 2.2 Update scratch/example execution scripts that instantiate `PurchaseRequest`

## 3. Tests and Verification

- [x] 3.1 Update or add model/policy tests to validate missing `vendor_id` fails schema validation
- [x] 3.2 Run targeted tests for impacted modules and confirm pass
- [x] 3.3 Run full test suite and capture results for review
