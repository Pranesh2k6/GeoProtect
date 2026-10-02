# Conventions

> Binding conventions for all GeoProtect services. Any deviation must go
> through contract-change-tracker.md.

---

## Date, Time, Currency

| Convention | Rule |
|------------|------|
| **Timezone** | All timestamps are UTC, ISO 8601 format: `YYYY-MM-DDTHH:MM:SSZ`. |
| **Currency** | Indian Rupees (INR), whole units only (no paise). Field name: `amount_inr`. |
| **Rainfall** | Millimetres per 24 hours. Field name: `rainfall_mm`. |
| **Gauge reading** | Metres above datum. Field name: `gauge_level_m`. |

---

## H3 Resolution

- **Resolution**: 8 (avg hex area ≈ 0.74 km², edge ≈ 461 m).
- **Library versions**: Python `h3==4.1.0`, JavaScript `h3-js@4.2.1`.
- All H3 cell IDs are stored as 15-character lowercase hex strings (e.g., `883c1ea2e3fffff`).

---

## ID Formats

All IDs are generated once and never changed. The `event_id` is created by the
backend when an event is first detected and is immutable throughout the
event's lifecycle.

| Entity | Prefix | Format | Regex | Example |
|--------|--------|--------|-------|---------|
| Event | `EVT-` | `EVT-` + 8 hex chars | `^EVT-[0-9a-f]{8}$` | `EVT-a1b2c3d4` |
| Farmer | `FRM-` | `FRM-` + 8 hex chars | `^FRM-[0-9a-f]{8}$` | `FRM-00112233` |
| Policy | `POL-` | `POL-` + 8 hex chars | `^POL-[0-9a-f]{8}$` | `POL-aabb0011` |
| Claim | `CLM-` | `CLM-` + 16 hex chars | `^CLM-[0-9a-f]{16}$` | `CLM-a1b2c3d400112233` |
| Payout | `PAY-` | `PAY-` + 16 hex chars | `^PAY-[0-9a-f]{16}$` | `PAY-f0e1d2c3b4a59687` |

### Claim ID derivation

The claim ID is deterministic:

```
claim_id = "CLM-" + SHA256(event_id + "|" + farmer_id)[:16]
```

This ensures idempotency — the same event + farmer always produces the same
claim ID. If a claim already exists with that ID, the system returns the
existing claim with `"duplicate": true`.

### Payout ID derivation

```
payout_id = "PAY-" + SHA256(claim_id + "|" + "payout")[:16]
```

---

## General API Rules

1. Every response contains `"success": true|false`.
2. On failure, the response also contains `"reason_code"` (from vocabulary.md)
   and a human-readable `"message"`.
3. Every request and response that relates to an event carries `"event_id"`.
4. Creating operations are **idempotent**: a repeat returns the original result
   with `"duplicate": true` and creates nothing new.
5. Unknown extra fields in requests are silently ignored.
6. **No personal data on the ledger**: no names, phone numbers, Aadhaar,
   bank details, or exact coordinates.
