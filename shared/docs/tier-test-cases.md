# Tier Test Cases

> 8 boundary test cases for the tier determination logic.
> All thresholds come from `config/thresholds.yaml`.
> All three signals (rainfall, gauge, inundation) must be met for a tier.
> The highest tier for which ALL three triggers are met is assigned.
> If no tier is met, result is `trigger_not_met`.

---

## Signal Disagreement Rule

**Rule**: All three signals must independently satisfy a tier's thresholds
for that tier to be assigned. If signals disagree (e.g., rainfall qualifies
for tier_2 but gauge only qualifies for tier_1), the **lowest qualifying
tier** is assigned — i.e., the highest tier for which ALL three signals pass.

---

## Reference Thresholds

| Tier | Rainfall (mm/24h) | Gauge | Inundation (%) |
|------|-------------------|-------|----------------|
| tier_1 | ≥ 115.6 | ≥ Warning Level | ≥ 10 |
| tier_2 | ≥ 204.5 | ≥ Danger Level | ≥ 30 |
| tier_3 | ≥ 204.5 | ≥ HFL | ≥ 60 |

Demo gauge values: WL = 46.50 m, DL = 47.75 m, HFL = 49.24 m.

---

## Test Cases

### TC-01: Exactly at tier_1 thresholds (boundary)

| Signal | Value | Meets tier_1? | Meets tier_2? |
|--------|-------|---------------|---------------|
| Rainfall | 115.6 mm | ✅ (= 115.6) | ❌ (< 204.5) |
| Gauge | 46.50 m | ✅ (= WL) | ❌ (< DL) |
| Inundation | 10% | ✅ (= 10) | ❌ (< 30) |

**Expected**: `tier_1`, payout **25%**.

---

### TC-02: Just below tier_1 on one signal

| Signal | Value | Meets tier_1? |
|--------|-------|---------------|
| Rainfall | 115.5 mm | ❌ (< 115.6) |
| Gauge | 46.50 m | ✅ |
| Inundation | 10% | ✅ |

**Expected**: `trigger_not_met`. No tier assigned, no payout.

---

### TC-03: Exactly at tier_2 thresholds (boundary)

| Signal | Value | Meets tier_1? | Meets tier_2? | Meets tier_3? |
|--------|-------|---------------|---------------|---------------|
| Rainfall | 204.5 mm | ✅ | ✅ (= 204.5) | ✅ |
| Gauge | 47.75 m | ✅ | ✅ (= DL) | ❌ (< HFL) |
| Inundation | 30% | ✅ | ✅ (= 30) | ❌ (< 60) |

**Expected**: `tier_2`, payout **60%**.

---

### TC-04: Exactly at tier_3 thresholds (boundary)

| Signal | Value | Meets tier_1? | Meets tier_2? | Meets tier_3? |
|--------|-------|---------------|---------------|---------------|
| Rainfall | 204.5 mm | ✅ | ✅ | ✅ |
| Gauge | 49.24 m | ✅ | ✅ | ✅ (= HFL) |
| Inundation | 60% | ✅ | ✅ | ✅ (= 60) |

**Expected**: `tier_3`, payout **100%**.

---

### TC-05: Signals disagree — rainfall high, gauge low

| Signal | Value | Meets tier_1? | Meets tier_2? |
|--------|-------|---------------|---------------|
| Rainfall | 250 mm | ✅ | ✅ |
| Gauge | 46.00 m | ❌ (< WL) | ❌ |
| Inundation | 50% | ✅ | ✅ |

**Expected**: `trigger_not_met`. Gauge does not even meet tier_1.

---

### TC-06: Signals disagree — gauge at tier_2, but inundation only at tier_1

| Signal | Value | Meets tier_1? | Meets tier_2? |
|--------|-------|---------------|---------------|
| Rainfall | 220 mm | ✅ | ✅ |
| Gauge | 48.00 m | ✅ | ✅ (≥ DL) |
| Inundation | 20% | ✅ | ❌ (< 30) |

**Expected**: `tier_1`, payout **25%**. All three meet tier_1 but inundation
fails tier_2.

---

### TC-07: One signal completely missing (null)

| Signal | Value | Notes |
|--------|-------|-------|
| Rainfall | 230 mm | Available |
| Gauge | null | Data missing from CWC |
| Inundation | 45% | Available |

**Expected**: Verification returns `"success": false`,
`"reason_code": "data_missing"`. No tier assigned. Rationale: all three
signals are required; a null signal cannot satisfy any threshold.

---

### TC-08: Demo scenario values (regression test)

| Signal | Value | Meets tier_1? | Meets tier_2? | Meets tier_3? |
|--------|-------|---------------|---------------|---------------|
| Rainfall | 230 mm | ✅ | ✅ | ✅ |
| Gauge | 48.50 m | ✅ | ✅ (≥ DL) | ❌ (< 49.24 HFL) |
| Inundation | 45% | ✅ | ✅ (≥ 30) | ❌ (< 60) |

**Expected**: `tier_2`, payout **60%**. This is the demo scenario from
`docs/demo-scenario.md`. Sum insured ₹50,000 → payout ₹30,000/farmer.
