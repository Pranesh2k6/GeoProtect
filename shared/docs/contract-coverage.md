# Contract Coverage

> One row per endpoint. Columns show which example files exist.
> Every cell is either a filename (must exist in `contracts/examples/`)
> or `n/a — <reason>`.

---

## Failure Reason Applicability Rules

| Failure Reason | Where Resolved | Notes |
|----------------|---------------|-------|
| `validation_error` | At any boundary | Request body fails schema validation |
| `not_found` | Boundary 1 only | Resource lookup by ID |
| `data_missing` | Boundary 2 only | Verification data incomplete |
| `service_unavailable` | Boundaries 3, 4 | Ledger or payment rail unreachable |
| `duplicate_attempt` | Boundaries 3, 4 | Idempotent create returns `duplicate: true` in success |
| `trigger_not_met` | Boundary 2 only | Signals do not meet any tier |
| `policy_inactive` | Backend filters | Never reaches gateway (resolved before Boundary 3) |
| `policy_expired` | Backend filters | Never reaches gateway (resolved before Boundary 3) |
| `farmer_outside_cells` | Backend filters | Never reaches gateway (resolved before Boundary 3) |

---

## Full Coverage Table

| # | Boundary | Method + Path | Success | `validation_error` | `not_found` | `data_missing` | `service_unavailable` | `trigger_not_met` | `policy_inactive` | `policy_expired` | `farmer_outside_cells` |
|---|----------|--------------|---------|-------------------|-------------|----------------|----------------------|-------------------|------------------|-----------------|----------------------|
| 1 | 1: FE→BE | POST /api/v1/events | `post_event_response_success.json` | `post_event_response_failure.json` | n/a — create op | n/a — not a data query | n/a — no upstream | n/a — not a verify op | n/a — no policy check | n/a — no policy check | n/a — no cell check |
| 2 | 1: FE→BE | GET /api/v1/events/{id} | inline in contract | n/a — GET has no body | `get_event_response_not_found.json` | n/a — not a data query | n/a — no upstream | n/a — not a verify op | n/a — no policy check | n/a — no policy check | n/a — no cell check |
| 3 | 1: FE→BE | GET /api/v1/events/{id}/claims | inline in contract | n/a — GET has no body | `get_event_response_not_found.json` (reuse) | n/a — not a data query | n/a — no upstream | n/a — not a verify op | n/a — no policy check | n/a — no policy check | n/a — no cell check |
| 4 | 1: FE→BE | GET /api/v1/farmers | inline in contract | n/a — GET has no body | n/a — returns [] | n/a — not a data query | n/a — no upstream | n/a — not a verify op | n/a — no policy check | n/a — no policy check | n/a — no cell check |
| 5 | 2: BE→DM | POST /api/v1/verify | `post_verify_response_success.json` | n/a — internal call | n/a — event exists by this point | `post_verify_response_failure.json` | n/a — DM is co-located | `post_verify_response_trigger_not_met.json` | n/a — no policy check | n/a — no policy check | n/a — no cell check |
| 6 | 2: BE→DM | GET /api/v1/flood-extent/{id} | GeoJSON inline | n/a — GET has no body | n/a — implies event exists | n/a — covered by verify | n/a — DM is co-located | n/a — not a verify op | n/a — no policy check | n/a — no policy check | n/a — no cell check |
| 7 | 3: BE→GW | POST /api/v1/claims | `post_claim_response_success.json` | n/a — internal call | n/a — claim is created | n/a — not a data query | `post_claim_response_failure.json` | n/a — tier decided before claims | n/a — backend filters | n/a — backend filters | n/a — backend filters |
| 8 | 3: BE→GW | GET /api/v1/claims/{id} | inline in contract | n/a — GET has no body | n/a — claim exists by this point | n/a — not a data query | n/a — read from local state | n/a — not a verify op | n/a — no policy check | n/a — no policy check | n/a — no cell check |
| 9 | 3: BE→GW | PUT /api/v1/claims/{id}/status | inline in contract | n/a — internal call | n/a — claim exists by this point | n/a — not a data query | n/a — write after create | n/a — not a verify op | n/a — no policy check | n/a — no policy check | n/a — no cell check |
| 10 | 4: BE→PAY | POST /api/v1/payouts | `post_payout_response_success.json` | n/a — internal call | n/a — payout is created | n/a — not a data query | `post_payout_response_failure.json` | n/a — not a verify op | n/a — no policy check | n/a — no policy check | n/a — no cell check |

---

## Duplicate Handling (Not a Failure)

Duplicates return `"success": true` with `"duplicate": true`. They are
**success** responses, not failures:

| Boundary | Duplicate Example |
|----------|-------------------|
| 3: POST /api/v1/claims | `post_claim_response_duplicate.json` |
| 4: POST /api/v1/payouts | inline in contract |
| 1: POST /api/v1/events | handled via `"duplicate": true` in success response |

---

## Request Examples

| Boundary | Request Example |
|----------|----------------|
| 1: POST /api/v1/events | `post_event_request.json` |
| 2: POST /api/v1/verify | `post_verify_request.json` |
| 3: POST /api/v1/claims | `post_claim_request.json` |
| 4: POST /api/v1/payouts | `post_payout_request.json` |

---

## File Inventory (15 example files)

| # | Filename | Exists |
|---|---------|--------|
| 1 | `get_event_response_not_found.json` | ✅ |
| 2 | `post_claim_request.json` | ✅ |
| 3 | `post_claim_response_duplicate.json` | ✅ |
| 4 | `post_claim_response_failure.json` | ✅ |
| 5 | `post_claim_response_success.json` | ✅ |
| 6 | `post_event_request.json` | ✅ |
| 7 | `post_event_response_failure.json` | ✅ |
| 8 | `post_event_response_success.json` | ✅ |
| 9 | `post_payout_request.json` | ✅ |
| 10 | `post_payout_response_failure.json` | ✅ |
| 11 | `post_payout_response_success.json` | ✅ |
| 12 | `post_verify_request.json` | ✅ |
| 13 | `post_verify_response_failure.json` | ✅ |
| 14 | `post_verify_response_success.json` | ✅ |
| 15 | `post_verify_response_trigger_not_met.json` | ✅ |
