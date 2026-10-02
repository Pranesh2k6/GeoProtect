# API Contract v0.1.1

> Baseline contract for GeoProtect. Four service boundaries.
> All conventions from `docs/conventions.md` apply. All enums from
> `docs/vocabulary.md`. JSON examples are in `contracts/examples/`.
> Ledger-specific configuration is in `docs/ledger-notes.md`.

---

## Global Rules

1. Every response has `"success": true|false`.
2. On failure: add `"reason_code"` (vocabulary.md) and `"message"` (human-readable string).
3. Every request/response carries `"event_id"` when applicable.
4. Create operations are **idempotent**: a repeat returns the original with `"duplicate": true`.
5. Unknown extra fields in requests are silently ignored.
6. No personal data (names, phones, Aadhaar, bank details, coordinates) flows to the gateway. See `docs/ledger-notes.md` for the exact field list.
7. The `event_id` is generated **exactly once by the backend** when it first receives the trigger from the frontend. The frontend sends the trigger request WITHOUT an event_id; the backend creates one and returns it. No other service may mint event IDs.

---

## Event ID Lifecycle

```
Frontend → POST /api/v1/events (no event_id in request)
  Backend generates event_id = "EVT-" + 8 random hex chars
  Backend stores event, returns event_id to frontend
  Backend → POST /api/v1/verify (passes event_id)
  Backend → POST /api/v1/claims (passes event_id, per farmer)
  Backend → POST /api/v1/payouts (passes event_id, per claim)
```

## Deterministic ID Derivation

- **claim_id**: `CLM-` + hex(SHA256(`event_id` + `|` + `farmer_id`))[:16]
- **payout_id**: `PAY-` + hex(SHA256(`claim_id` + `|` + `"payout"`))[:16]
- These are computed by the backend before calling downstream services.

---

## Boundary 1: Frontend → Backend

### 1.1 POST /api/v1/events

**Purpose**: Trigger detection of a new flood event. Backend generates event_id.

Request body:

| Field | Type | In | Required | Description |
|-------|------|-----|----------|-------------|
| `event_date` | string | body | yes | ISO 8601 UTC timestamp. |
| `region_name` | string | body | yes | Human-readable region (e.g., "Basantpur block, Supaul"). |
| `h3_cells` | string[] | body | yes | List of affected H3 cell IDs at resolution 8. |

**Response (success)**:

| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | `true` |
| `event_id` | string | Backend-generated event ID (regex: `^EVT-[0-9a-f]{8}$`). |
| `stage` | string | Current event stage (vocabulary.md). |
| `duplicate` | bool | `true` if a matching event already existed (same date + region + cells). |

**Response (failure)**:

| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | `false` |
| `reason_code` | string | Error code from vocabulary.md. |
| `message` | string | Human-readable error. |

### 1.2 GET /api/v1/events/{event_id}

**Purpose**: Get full event status including verification, tier, claims summary.

**Response (success)**:

| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | `true` |
| `event_id` | string | The event ID. |
| `event_date` | string | ISO 8601 UTC. |
| `region_name` | string | Region name. |
| `stage` | string | Current event stage. |
| `tier` | string\|null | Assigned tier or null if not yet verified. |
| `h3_cells` | string[] | Affected cells. |
| `verification` | object | `{ rainfall_mm, gauge_level_m, inundation_pct, verified_at }` |
| `claims_summary` | object | `{ total, approved, rejected, payout_pending, payout_completed }` |
| `total_payout_inr` | int | Total payout amount in whole INR. |

**Response (failure)**: `{ "success": false, "reason_code": "not_found", "message": "..." }`

### 1.3 GET /api/v1/events/{event_id}/claims

**Purpose**: List all claims for an event.

**Response (success)**:

| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | `true` |
| `event_id` | string | The event ID. |
| `claims` | array | List of claim objects (see below). |

Each claim object:

| Field | Type | Description |
|-------|------|-------------|
| `claim_id` | string | Deterministic claim ID. |
| `farmer_id` | string | Pseudonymous farmer ID. |
| `policy_id` | string | Policy ID. |
| `status` | string | Claim status (vocabulary.md). |
| `payout_amount_inr` | int | Payout in whole INR. |
| `reason_code` | string\|null | Rejection reason if rejected. |

### 1.4 GET /api/v1/farmers

**Purpose**: List farmers with optional filters.

Query params: `h3_cell` (filter by cell), `policy_status` (filter by status).

**Response**: `{ "success": true, "farmers": [...] }`

---

## Boundary 2: Backend → Data Module

### 2.1 POST /api/v1/verify

**Purpose**: Request verification of a flood event using all three signals.

| Field | Type | In | Required | Description |
|-------|------|-----|----------|-------------|
| `event_id` | string | body | yes | Event ID (from backend). |
| `event_date` | string | body | yes | ISO 8601 UTC. |
| `h3_cells` | string[] | body | yes | Affected H3 cells. |

**Response (success)**:

| Field | Type | Description | Units |
|-------|------|-------------|-------|
| `success` | bool | `true` | — |
| `event_id` | string | Event ID. | — |
| `rainfall_mm` | number | 24 h rainfall. | mm |
| `rainfall_class` | string | IMD classification (vocabulary.md). | — |
| `gauge_station` | string | Station name. | — |
| `gauge_level_m` | number | Observed water level. | metres |
| `warning_level_m` | number | Station warning level. | metres |
| `danger_level_m` | number | Station danger level. | metres |
| `highest_flood_level_m` | number | Station HFL. | metres |
| `inundation_pct` | number | Satellite flood fraction. | % (0–100) |
| `confidence` | number | Overall confidence score. | 0.0–1.0 |
| `tier` | string | Determined tier (vocabulary.md). | — |
| `verified_at` | string | Verification timestamp. | ISO 8601 UTC |
| `data_provenance` | object | Per-field provenance: `"verified"`, `"demo_calibrated"`, or `"unverified"`. Frontend must display this on the evidence panel. | — |

**Response (failure — data missing)**:

```json
{
  "success": false,
  "event_id": "EVT-b20f7c01",
  "reason_code": "data_missing",
  "message": "Gauge data not available for the requested date."
}
```

### 2.2 GET /api/v1/flood-extent/{event_id}

**Purpose**: Retrieve the flood polygon and metadata.

**Response**: GeoJSON FeatureCollection with properties including `event_id`, `inundation_pct`, `confidence`.

---

## Boundary 3: Backend → Blockchain Gateway

> **Note**: This boundary is ledger-agnostic. Ledger-specific configuration
> (channel names, SDK, ports) is in `docs/ledger-notes.md`.

### 3.1 POST /api/v1/claims

**Purpose**: Create a claim on the ledger. Idempotent.

| Field | Type | In | Required | Description |
|-------|------|-----|----------|-------------|
| `claim_id` | string | body | yes | Deterministic: `CLM-` + hex(SHA256(event_id \| farmer_id))[:16]. |
| `event_id` | string | body | yes | Event ID. |
| `farmer_id` | string | body | yes | Pseudonymous farmer ID. |
| `policy_id` | string | body | yes | Policy ID. |
| `tier` | string | body | yes | Tier from vocabulary.md. |
| `payout_amount_inr` | int | body | yes | Payout in whole INR. |
| `sum_insured_inr` | int | body | yes | Sum insured in whole INR. |
| `payout_percent` | int | body | yes | Payout percentage. |

**Response (success — new claim)**:

| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | `true` |
| `claim_id` | string | The claim ID. |
| `status` | string | `created` |
| `duplicate` | bool | `false` |
| `created_at` | string | ISO 8601 UTC. |
| `tx_reference` | string | Ledger transaction ID. |

**Response (success — duplicate)**:

| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | `true` |
| `claim_id` | string | The existing claim ID. |
| `status` | string | Current status of existing claim. |
| `duplicate` | bool | `true` |
| `created_at` | string | Original creation timestamp. |
| `tx_reference` | string | Original ledger transaction ID. |

**Response (failure)**:

```json
{
  "success": false,
  "reason_code": "service_unavailable",
  "message": "Ledger peer not reachable."
}
```

### 3.2 GET /api/v1/claims/{claim_id}

**Purpose**: Query claim status from the ledger.

**Response**: `{ "success": true, "claim_id": "...", "status": "...", "event_id": "...", "tx_reference": "...", ... }`

### 3.3 PUT /api/v1/claims/{claim_id}/status

**Purpose**: Update claim status (e.g., after payout).

| Field | Type | In | Required | Description |
|-------|------|-----|----------|-------------|
| `status` | string | body | yes | New status (vocabulary.md claim statuses). |
| `event_id` | string | body | yes | Event ID for traceability. |

**Response**: `{ "success": true, "claim_id": "...", "status": "...", "updated_at": "...", "tx_reference": "..." }`

---

## Boundary 4: Backend → Mock Payment Adapter

### 4.1 POST /api/v1/payouts

**Purpose**: Initiate a payout. Idempotent.

| Field | Type | In | Required | Description |
|-------|------|-----|----------|-------------|
| `payout_id` | string | body | yes | Deterministic: `PAY-` + hex(SHA256(claim_id \| "payout"))[:16]. |
| `claim_id` | string | body | yes | Associated claim ID. |
| `event_id` | string | body | yes | Event ID. |
| `farmer_id` | string | body | yes | Farmer ID. |
| `amount_inr` | int | body | yes | Payout amount in whole INR. |

**Response (success — new payout)**:

| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | `true` |
| `payout_id` | string | The payout ID. |
| `status` | string | `submitted` |
| `duplicate` | bool | `false` |
| `submitted_at` | string | ISO 8601 UTC. |

**Response (success — duplicate)**:

```json
{
  "success": true,
  "payout_id": "PAY-f0e1d2c3b4a59687",
  "status": "settled",
  "duplicate": true,
  "submitted_at": "2020-07-26T06:00:00Z"
}
```

**Response (failure)**:

```json
{
  "success": false,
  "reason_code": "service_unavailable",
  "message": "Payment rail timeout."
}
```

### 4.2 GET /api/v1/payouts/{payout_id}

**Purpose**: Check payout status.

**Response**: `{ "success": true, "payout_id": "...", "status": "...", "amount_inr": ..., ... }`
