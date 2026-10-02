# Vocabulary

> Closed lists of enumerated values used across all GeoProtect services.
> All values are `snake_case` lowercase. Any value not in this file is invalid.

---

## Event Stages

| Value | Meaning |
|-------|---------|
| `detected` | Raw signals received; event created by backend. |
| `verifying` | Data module is verifying signals (rainfall, gauge, satellite). |
| `verified` | All three signals confirmed; tier assigned. |
| `matching` | Backend is matching insured farmers to affected H3 cells. |
| `processing` | Claims are being created on the ledger and payouts initiated. |
| `completed` | All claims processed and payouts submitted. |
| `failed` | Verification or processing failed; see rejection reason. |

---

## Tiers

> **Naming note**: Tier labels deliberately avoid "Severe" and "Extreme"
> which are CWC flood-situation classifications. Our tiers are:
> moderate / major / catastrophic.
>
> **Signal primacy**: For upstream-driven floods (e.g., Kosi, where water
> originates in the Nepal catchment), the **gauge** is the primary signal —
> local rainfall may be only "heavy" or "very heavy" even during a major
> flood. The current tier rules require ALL three signals to pass, which
> means a Kosi-type upstream flood with only 180 mm local rainfall
> (below 204.5 mm) **cannot reach tier_2** under these rules. This is a
> known limitation; the team should discuss a "gauge-primary" override
> mode at kickoff (see `docs/kickoff-agenda.md`).

| Value | Label | Meaning |
|-------|-------|---------|
| `tier_1` | Moderate Flood | 25% payout of sum insured. |
| `tier_2` | Major Flood | 60% payout of sum insured. |
| `tier_3` | Catastrophic Flood | 100% payout of sum insured. |

---

## Claim Statuses

| Value | Meaning |
|-------|---------|
| `created` | Claim record created on the ledger. |
| `approved` | Claim passed all validation checks. |
| `rejected` | Claim rejected; see `reason_code`. |
| `payout_pending` | Payout instruction sent to payment adapter. |
| `payout_completed` | Payment confirmed settled. |
| `payout_failed` | Payment attempt failed; may be retried. |

---

## Payout Statuses

| Value | Meaning |
|-------|---------|
| `created` | Payout record created. |
| `submitted` | Payout instruction submitted to payment rail. |
| `settled` | Funds confirmed delivered. |
| `failed` | Payment failed (bank error, timeout, etc.). |
| `retried` | Failed payout retried automatically. |

---

## Rejection Reasons

| Value | Meaning |
|-------|---------|
| `trigger_not_met` | Flood signals did not meet the required tier threshold. |
| `policy_inactive` | Farmer's policy is not in `active` status. |
| `policy_expired` | Policy end_date is before the event date. |
| `farmer_outside_cells` | Farmer's H3 cell is not in the affected cell list. |
| `duplicate_attempt` | A claim for this event + farmer already exists. |
| `data_missing` | Required verification data is incomplete or unavailable. |
| `service_unavailable` | An upstream service (data module, gateway, payment) is unreachable. |
| `kyc_not_verified` | Farmer's KYC status is not verified. |

---

## Policy Statuses

| Value | Meaning |
|-------|---------|
| `active` | Policy is current and valid. |
| `inactive` | Policy has been deactivated (non-payment, opt-out). |
| `expired` | Policy end_date has passed. |

---

## Error Codes

| Code | HTTP Status | Meaning |
|------|------------|---------|
| `validation_error` | 400 | Request body failed schema validation. |
| `not_found` | 404 | Requested resource does not exist. |
| `conflict` | 409 | Idempotency conflict (duplicate detected, original returned). |
| `upstream_timeout` | 504 | An upstream dependency did not respond in time. |
| `internal_error` | 500 | Unexpected server error. |
| `service_unavailable` | 503 | A required service is temporarily unavailable. |

---

## IMD Rainfall Classes

| Value | Meaning |
|-------|---------|
| `very_light` | Trace – 2.4 mm / 24 h. |
| `light` | 2.5 – 15.5 mm / 24 h. |
| `moderate` | 15.6 – 64.4 mm / 24 h. |
| `heavy` | 64.5 – 115.5 mm / 24 h. |
| `very_heavy` | 115.6 – 204.4 mm / 24 h. |
| `extremely_heavy` | ≥ 204.5 mm / 24 h. |

---

## Data Provenance Labels

> Used in the `data_provenance` field of verification responses.
> Frontend must display these on the evidence panel.

| Value | Meaning |
|-------|---------|
| `verified` | Value confirmed from a **primary** official source (e.g., CWC PDF bulletin, IMD station data). |
| `verified_secondary` | Value confirmed from a secondary/aggregator source (e.g., befiqr.in, news reports citing official data). Primary source not directly opened. |
| `demo_calibrated` | Not a real measurement; chosen to sit realistically inside a documented range. Must never be presented as real data. |
| `demo_exaggerated` | Not a real measurement; **deliberately set above the documented range** to reach a specific tier for demonstration purposes. Must never be presented as real data. |
| `unverified` | No authoritative source found; treat with caution. |
