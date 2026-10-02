# Demo Scenario — Single Source of Truth

> This document defines the ONE scenario used for the hackathon demo.
> Every number here must match thresholds.yaml, the CSVs, and the contract
> examples. If you change a number, change it everywhere.
>
> **Provenance labels**: VERIFIED = confirmed from primary official source;
> VERIFIED (secondary) = confirmed from an aggregator/news source citing
> official data but primary PDF not opened; DEMO-CALIBRATED = not a real
> reading but chosen to sit realistically inside a documented range;
> DEMO-EXAGGERATED = deliberately set above the documented range to
> reach a specific tier; UNVERIFIED = no source found.

---

## Event

| Field | Value |
|-------|-------|
| **Event ID** | `EVT-b20f7c01` |
| **Event name** | Bihar Kosi Floods, July 2020 |
| **Event date** | `2020-07-26T00:00:00Z` |
| **Region** | Basantpur block, Supaul district, Bihar |
| **H3 resolution** | 8 |

---

## Verification Signals

### IMD Rainfall

| Field | Value | Provenance | Source |
|-------|-------|------------|--------|
| 24 h rainfall | **230 mm** | DEMO-EXAGGERATED | IMD reports "heavy to very heavy" rainfall for Supaul in July 2020 (real range 64.5–204.4 mm). **230 mm is above the real range** and above the "Extremely Heavy" threshold (204.5 mm), chosen deliberately to reach tier_2. A real Kosi-type flood may have only "very heavy" local rainfall because the flood is upstream-driven from Nepal. See A1. |
| Classification | `extremely_heavy` | DEMO-EXAGGERATED | Follows from the 230 mm value. Real event was "heavy to very heavy". |

### CWC River Gauge — Basua Station (Kosi)

| Field | Value | Provenance | Source |
|-------|-------|------------|--------|
| Warning Level | **46.50 m** | UNVERIFIED | CWC publishes DL and HFL for Basua but warning level not found in public sources. See A11. |
| Danger Level | **47.75 m** | VERIFIED (secondary) | CWC/WRD Bihar data via befiqr.in (aggregator). Primary CWC PDF bulletin not directly opened. |
| HFL | **49.24 m** | VERIFIED (secondary) | Recorded in 2017. CWC/WRD Bihar data via befiqr.in (aggregator). Primary CWC PDF bulletin not directly opened. |
| Observed gauge reading | **48.50 m** | DEMO-CALIBRATED | Kosi at Basua crossed DL (47.75 m) in July 2020 but stayed below HFL (49.24 m). 48.50 m sits realistically in the Severe range. See A2. |
| CWC category | Severe (above DL, below HFL) | VERIFIED | CWC convention confirmed from cwc.gov.in. |

### Sentinel-1 Satellite Inundation

| Field | Value | Provenance | Source |
|-------|-------|------------|--------|
| Inundation fraction | **45%** of polygon area | DEMO-CALIBRATED | No actual Sentinel-1 analysis performed. 45% is realistic for a severe Kosi basin flood. See A4. |
| Method | Otsu change detection on VH backscatter | VERIFIED | Standard methodology documented in literature. |
| Confidence | 0.92 | DEMO-CALIBRATED | Reasonable for agricultural floodplain. |

---

## Tier Determination

Checking against thresholds.yaml:

| Check | tier_1 (≥115.6 mm, ≥WL, ≥10%) | tier_2 (≥204.5 mm, ≥DL, ≥30%) | tier_3 (≥204.5 mm, ≥HFL, ≥60%) |
|-------|------|------|------|
| Rainfall 230 mm | ✅ | ✅ | ✅ |
| Gauge 48.50 m vs WL/DL/HFL | ✅ (≥46.50) | ✅ (≥47.75) | ❌ (48.50 < 49.24) |
| Inundation 45% | ✅ (≥10%) | ✅ (≥30%) | ❌ (45% < 60%) |

**Result**: **tier_2** — Payout = **60%** of sum insured.

> **Note**: The tier outcome remains tier_2 after correcting HFL from 49.50
> to 49.24 m. The gauge reading (48.50 m) is still below HFL (49.24 m) and
> inundation (45%) is still below 60%, so tier_3 is not met.

> **Signal primacy for Kosi-type floods**: The Kosi is an upstream-driven
> flood system. Water originates in the Nepal catchment and arrives at Basua
> regardless of local rainfall. The **gauge is the primary signal**. In a
> real Kosi flood, local rainfall may be only "heavy" or "very heavy"
> (64.5–204.4 mm), which would **not** satisfy tier_2's rainfall threshold
> (≥204.5 mm). Our demo uses 230 mm (DEMO-EXAGGERATED) to demonstrate
> tier_2; in production, the team should discuss a "gauge-primary" override
> that allows the gauge and inundation signals to drive the tier without
> requiring extremely heavy local rainfall.

> **Warning level dependency**: tier_1 requires gauge ≥ Warning Level
> (46.50 m), which is UNVERIFIED. The demo scenario passes tier_1 trivially
> (gauge 48.50 m >> 46.50 m) so the UNVERIFIED WL does not affect the
> outcome. However, a near-boundary tier_1 test case would depend on this
> value. **No tier_2 or tier_3 rule depends on the warning level.**

---

## Affected H3 Cells

10 cells at resolution 8, representing the flood footprint in Basantpur block:

| # | H3 Cell ID | Valid | Resolution |
|---|-----------|-------|------------|
| 1 | `883c1ea285fffff` | ✅ | 8 |
| 2 | `883c1ea28dfffff` | ✅ | 8 |
| 3 | `883c1ea2a9fffff` | ✅ | 8 |
| 4 | `883c1ea2e1fffff` | ✅ | 8 |
| 5 | `883c1ea2e3fffff` | ✅ | 8 |
| 6 | `883c1ea2e7fffff` | ✅ | 8 |
| 7 | `883c1ea2ebfffff` | ✅ | 8 |
| 8 | `883c1ea05bfffff` | ✅ | 8 |
| 9 | `883c1ea281fffff` | ✅ | 8 |
| 10 | `883c1ea287fffff` | ✅ | 8 |

---

## Insured Farmers — Targets (12 affected)

Exactly **12 farmers** have active policies AND their H3 cell is in the
affected list above. They are distributed across the 10 cells:

| # | Farmer ID | H3 Cell | Policy ID | Status | Sum Insured (₹) |
|---|----------|---------|-----------|--------|-----------------|
| 1 | `FRM-00a1b2c3` | `883c1ea2e3fffff` | `POL-aa010001` | `active` | 50000 |
| 2 | `FRM-00a1b2c4` | `883c1ea2e3fffff` | `POL-aa010002` | `active` | 50000 |
| 3 | `FRM-00a1b2c5` | `883c1ea2e1fffff` | `POL-aa010003` | `active` | 50000 |
| 4 | `FRM-00a1b2c6` | `883c1ea2e7fffff` | `POL-aa010004` | `active` | 50000 |
| 5 | `FRM-00a1b2c7` | `883c1ea2ebfffff` | `POL-aa010005` | `active` | 50000 |
| 6 | `FRM-00a1b2c8` | `883c1ea285fffff` | `POL-aa010006` | `active` | 50000 |
| 7 | `FRM-00a1b2c9` | `883c1ea28dfffff` | `POL-aa010007` | `active` | 50000 |
| 8 | `FRM-00a1b2ca` | `883c1ea2a9fffff` | `POL-aa010008` | `active` | 50000 |
| 9 | `FRM-00a1b2cb` | `883c1ea05bfffff` | `POL-aa010009` | `active` | 50000 |
| 10 | `FRM-00a1b2cc` | `883c1ea281fffff` | `POL-aa010010` | `active` | 50000 |
| 11 | `FRM-00a1b2cd` | `883c1ea287fffff` | `POL-aa010011` | `active` | 50000 |
| 12 | `FRM-00a1b2ce` | `883c1ea2e1fffff` | `POL-aa010012` | `active` | 50000 |

---

## Payout Arithmetic

```
Tier:           tier_2
Payout %:       60%
Sum insured:    ₹50,000 per farmer
Payout/farmer:  ₹50,000 × 0.60 = ₹30,000
Affected:       12 farmers
Total payout:   12 × ₹30,000 = ₹360,000
```

| Item | Value |
|------|-------|
| Payout per farmer | **₹30,000** |
| Number of affected farmers | **12** |
| Total payout | **₹360,000** |

---

## Decoys (Non-Target Farmers)

### Farmers outside affected cells (should NOT receive payout)

| Farmer ID | H3 Cell | Policy Status | Why excluded |
|----------|---------|---------------|--------------|
| `FRM-00d1e2f1` | `883c1ea051fffff` | `active` | Cell not in affected list |
| `FRM-00d1e2f2` | `883c1ea053fffff` | `active` | Cell not in affected list |
| `FRM-00d1e2f3` | `883c1ea059fffff` | `active` | Cell not in affected list |
| `FRM-00d1e2f4` | `883c1ea213fffff` | `active` | Cell not in affected list |
| `FRM-00d1e2f5` | `883c1ea217fffff` | `active` | Cell not in affected list |
| `FRM-00d1e2f6` | `883c1ea233fffff` | `active` | Cell not in affected list |
| `FRM-00d1e2f7` | `883c1ea23bfffff` | `active` | Cell not in affected list |
| `FRM-00d1e2f8` | `883c1ea283fffff` | `active` | Cell not in affected list |

### Inactive policies inside affected cells

| Farmer ID | H3 Cell | Policy Status | Why excluded |
|----------|---------|---------------|--------------|
| `FRM-00d1e2f9` | `883c1ea2e3fffff` | `inactive` | Policy not active |
| `FRM-00d1e2fa` | `883c1ea2e7fffff` | `inactive` | Policy not active |

### Expired policies inside affected cells

| Farmer ID | H3 Cell | Policy Status | Policy End Date | Why excluded |
|----------|---------|---------------|-----------------|--------------|
| `FRM-00d1e2fb` | `883c1ea2e1fffff` | `expired` | `2020-06-30` | Policy expired before event |
| `FRM-00d1e2fc` | `883c1ea285fffff` | `expired` | `2020-07-15` | Policy expired before event |

### Duplicate attempt case

| Farmer ID | H3 Cell | Scenario |
|----------|---------|----------|
| `FRM-00a1b2c3` | `883c1ea2e3fffff` | Farmer #1 (already in targets). If a second claim creation is attempted for `EVT-b20f7c01` + `FRM-00a1b2c3`, the system must return the existing claim with `"duplicate": true`. First run: 12 claims created. Second run: 0 new claims, 12 duplicate responses. |

### Farmer with two policies (boundary test)

| Farmer ID | H3 Cell | Policies | Scenario |
|----------|---------|----------|----------|
| `FRM-00a1b2c5` | `883c1ea2e1fffff` | `POL-aa010003` (active), `POL-ee050001` (active, sum_insured=75000) | Farmer has two active policies. System must create one claim per policy. Both are valid. |

### Different sum insured (outside target set)

| Farmer ID | H3 Cell | Policy | Sum Insured | Scenario |
|----------|---------|--------|-------------|----------|
| `FRM-00ee0000` | `883c1ea233fffff` | `POL-dd040000` | ₹35,000 | Active policy outside affected cells with different sum insured. Rejected: farmer_outside_cells. |

---

## Scenario Manifest

Member 2 must prepare the following files (see `sample-data/scenario_manifest.json`):

| Filename | Format | Content |
|----------|--------|---------|
| `rainfall_evt_b20f7c01.json` | JSON | 24 h rainfall data for the event |
| `gauge_evt_b20f7c01.json` | JSON | Basua gauge reading and levels |
| `flood_extent_evt_b20f7c01.geojson` | GeoJSON | Sentinel-1 derived flood polygon |
