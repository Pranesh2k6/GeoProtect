# Research Notes

> Compiled 2026-10-02. Every item includes source URL, access date, and a
> one-line takeaway. Items marked **ASSUMPTION** could not be confirmed from an
> official primary source.

---

## 1 Demo Event Selection

### 1.1 Kerala Floods, August 2018

| Attribute | Detail |
|-----------|--------|
| **Dates** | 2018-08-08 to 2018-08-20 (peak 15–17 Aug) |
| **IMD rainfall** | 2,346.6 mm cumulative Jun 1 – Aug 19, 42% above normal; extreme daily spikes > 200 mm in mid-August. IMD gridded data available via `imdlib`. |
| **CWC gauge** | Pamba river gauges at Kallopara, Malakkara, Thumpamon; levels well above danger marks. Specific historical metre readings available only in CWC study report, not in a public real-time API archive. |
| **Sentinel-1** | Extensively mapped using GEE + Otsu thresholding; >94% accuracy reported (PLoS ONE). No Copernicus EMS EMSR activation found. ISRO/Bhuvan products available. |
| **Agricultural area** | Kuttanad region (below sea level rice paddies) — well-documented but unusual topography. |

- **Source**: CWC "Kerala Flood Study Report" via kerala.gov.in, accessed 2026-10-02.
- **Source**: Sentinel-1 mapping study, PLoS ONE, accessed 2026-10-02.
- **Takeaway**: Rich data but CWC gauge numbers require digging into archived PDF reports; Kuttanad's sub-sea-level geography is unusual for a "typical" parametric trigger.

### 1.2 Bihar Floods, July 2020

| Attribute | Detail |
|-----------|--------|
| **Dates** | 2020-07-10 to 2020-07-30 (multiple pulses through monsoon) |
| **IMD rainfall** | Bihar recorded 82% above normal in June 2020; extremely heavy rainfall (>204.5 mm/24 h) in Supaul, Darbhanga, Madhubani. IMD gridded data via `imdlib`; district-wise data via REST API. |
| **CWC gauge** | Kosi at Basua: Danger Level = **47.75 m**. Also Baltara (33.85 m) and Kursela (30.00 m). Rivers crossed danger levels for extended periods. |
| **Sentinel-1** | Widely used in academic studies (GEE-based); ~8.36 lakh ha inundated in Sep 2019 event. 2020 floods similarly mapped. No Copernicus EMS EMSR activation, but NRSC/ISRO flood maps available. |
| **Agricultural area** | Kosi basin floodplain in Supaul district — predominantly rice (kharif), maize. Classic flood-prone agricultural region. |

- **Source**: CWC/WRD Bihar, befiqr.in (Basua DL), accessed 2026-10-02.
- **Source**: IMD data patterns from academic studies and IMD API docs, accessed 2026-10-02.
- **Takeaway**: Best fit for demo — flat agricultural Gangetic plain, well-documented CWC gauge with published danger level, abundant Sentinel-1 mapping, and real paddy farming.

### 1.3 Assam Floods, July 2020

| Attribute | Detail |
|-----------|--------|
| **Dates** | 2020-07-01 to 2020-07-25 (multiple waves) |
| **IMD rainfall** | Excessive July 2020 rainfall across Assam. |
| **CWC gauge** | Brahmaputra at Dhubri: Danger Level = 28.62 m; levels exceeded during peak. |
| **Sentinel-1** | Multi-temporal mapping widely done; >95% accuracy; 85% of Kaziranga submerged. |
| **Agricultural area** | Widespread but Kaziranga/wildlife focus dominates reporting; less structured CWC data in public domain compared to Bihar. |

- **Source**: assam.gov.in flood bulletins, reliefweb.int, accessed 2026-10-02.
- **Takeaway**: Good data but Bihar is simpler for a hackathon demo — Assam's Brahmaputra is extremely wide, making village-scale polygon harder to scope.

### 1.4 Recommendation

**Selected event: Bihar Floods, July 2020 — Kosi basin near Supaul.**

Justification:
1. Published CWC danger level at Basua (47.75 m) gives a concrete trigger threshold.
2. IMD data confirms extremely heavy rainfall (>204.5 mm/24 h) for the region.
3. Sentinel-1 flood mapping studies are abundant; methodology well-established.
4. Supaul district has a flat agricultural floodplain (kharif rice, maize) ideal for a parametric insurance demo.
5. Data is available from Indian sources (NRSC/ISRO, IMD, CWC/WRD Bihar) without depending on Copernicus EMS activation.

**Selected area**: Basantpur block, Supaul district, Bihar (name only — no exact coordinates stored beyond H3 cells).

---

## 2 Trigger Thresholds

### 2.1 IMD Rainfall Classification (24 h)

| Category | Range (mm / 24 h) |
|----------|-------------------|
| Heavy Rainfall | 64.5 – 115.5 |
| Very Heavy Rainfall | 115.6 – 204.4 |
| Extremely Heavy Rainfall | ≥ 204.5 |

Measurement period ends at 08:30 IST. Other categories: Very Light (trace–2.4), Light (2.5–15.5), Moderate (15.6–64.4).

- **Source**: imd.gov.in official classification, accessed 2026-10-02.

### 2.2 CWC Flood Level Convention

| Category | Condition | Colour |
|----------|-----------|--------|
| Normal | Below Warning Level | — |
| Above Normal | At or above Warning Level, below Danger Level | Yellow |
| Severe | At or above Danger Level, below HFL | Orange |
| Extreme | At or above Highest Flood Level (HFL) | Red |

- **Source**: cwc.gov.in flood forecasting definitions, accessed 2026-10-02.
- **Takeaway**: Warning and Danger levels are station-specific; HFL is the historical maximum ever recorded at a station.

### 2.3 Indian Crop Insurance Schemes — Parametric Triggers

| Scheme | Mechanism | Flood relevance |
|--------|-----------|-----------------|
| **PMFBY** | Yield-based (Area Approach + CCEs); localized calamity (incl. inundation) assessed per-farm by joint committee within 72 h. | Flood claims are "localized calamity" — individual farm assessment. |
| **RWBCIS** | Weather indices: payout triggered when recorded weather crosses pre-defined thresholds at notified stations. No field inspection for weather triggers. | Conceptual match for our parametric model. |

Key design borrowings:
- RWBCIS's "deemed loss" concept: if trigger breached, all insured farmers in the Reference Unit Area are eligible.
- PMFBY's 72-hour intimation window is a reasonable SLA upper bound.
- Payout percentages in RWBCIS are defined per Term Sheet per district per crop — typically 25%, 50%, 75%, 100% of sum insured based on severity.

- **Source**: PMFBY/RWBCIS operational guidelines (pmfby.gov.in), accessed 2026-10-02.
- **Takeaway**: Our three-tier model (25%, 60%, 100%) is a reasonable simplification inspired by RWBCIS term sheet practices.

### 2.4 Proposed Three-Tier Model

| Tier | Trigger Rule | Payout % |
|------|-------------|----------|
| **tier_1** (Moderate) | Rainfall ≥ 115.6 mm/24 h (Very Heavy) AND gauge ≥ Warning Level AND satellite confirms ≥ 10% inundation | 25% |
| **tier_2** (Severe) | Rainfall ≥ 204.5 mm/24 h (Extremely Heavy) AND gauge ≥ Danger Level AND satellite confirms ≥ 30% inundation | 60% |
| **tier_3** (Extreme) | Rainfall ≥ 204.5 mm/24 h AND gauge ≥ HFL AND satellite confirms ≥ 60% inundation | 100% |

All three signals (rainfall, gauge, satellite) must be met simultaneously. Any two alone are insufficient.

---

## 3 H3 Resolution

### 3.1 Resolution Comparison

| Resolution | Avg Hex Area (km²) | Avg Edge Length (km) |
|------------|--------------------|-----------------------|
| 7 | 5.161 | 1.221 |
| 8 | 0.737 | 0.461 |
| 9 | 0.105 | 0.174 |

- **Source**: h3geo.org/docs/core-library/restable (official H3 documentation), accessed 2026-10-02.

### 3.2 Recommendation: Resolution 8

- **Area**: ~0.74 km² per cell — a good match for village-scale work (Indian villages typically cover 1–5 km²; 2–6 cells per village).
- **Edge length**: ~461 m — fine enough for meaningful flood polygon overlap.
- **Cell count**: A typical village-scale flood polygon (5–10 km²) would produce ~7–14 cells at resolution 8.
- Resolution 7 is too coarse (5 km² = one cell per village, no spatial discrimination).
- Resolution 9 is too fine (0.1 km² = 50+ cells per village, heavy processing for no benefit in a parametric scheme).

### 3.3 H3 v3 → v4 API Changes

| Operation | v3 (Python) | v4 (Python, h3-py ≥ 4.0) |
|-----------|-------------|---------------------------|
| lat/lng → cell | `h3.geo_to_h3(lat, lng, res)` | `h3.latlng_to_cell(lat, lng, res)` |
| polygon → cells | `h3.polyfill(geojson, res)` | `h3.polygon_to_cells(h3shape, res)` |
| cell → boundary | `h3.h3_to_geo_boundary(cell)` | `h3.cell_to_boundary(cell)` |
| cell → center | `h3.h3_to_geo(cell)` | `h3.cell_to_latlng(cell)` |
| validity check | `h3.h3_is_valid(cell)` | `h3.is_valid_cell(cell)` |

**Pinned versions:**
- Python: `h3==4.1.0` (h3-py, PyPI)
- JavaScript: `h3-js@4.2.1` (npm; note: the npm package `h3` is an unrelated HTTP framework)

- **Source**: h3geo.org migration guide; PyPI h3 4.1.0; npm h3-js, accessed 2026-10-02.

---

## 4 Data-Source Facts (Member 2)

### 4.1 IMD Rainfall Data

| Type | Format | Access | Notes |
|------|--------|--------|-------|
| Gridded (0.25° × 0.25°) | `.GRD` binary / NetCDF | `pip install imdlib`; `imd.get_data('rain', start, end)` | Bulk download; xarray output; free for research. |
| District-wise | JSON | REST API `https://api.imd.gov.in/api/v1/districtrainfall` | May require registration / IP whitelisting. |
| Station (historical) | PDF / web tables | Manual download from mausam.imd.gov.in | Restricted; formal request via IMD Data Service Portal. |

**For the demo scenario**: Use gridded data via `imdlib` for the Supaul district area. Prepare a static JSON file with the 24 h rainfall reading for the event date. **Manual download is needed**; the prepared scenario files should be built offline by Member 2.

- **Source**: imdlib docs (readthedocs.io), IMD API portal (api.imd.gov.in), accessed 2026-10-02.

### 4.2 CWC River Gauge Data

| Source | Format | Access |
|--------|--------|--------|
| National Water Data Portal (NWDP) | JSON / CSV via API | https://nwdp.nwic.gov.in — hourly telemetry |
| India-WRIS | JSON API + spatial layers | https://indiawris.gov.in/swagger-ui/ |
| FloodWatch India app | Mobile only | Real-time alerts |
| WRD Bihar (FMIS) | Web portal | https://fmiscwrdbihar.gov.in/ — archived bulletins |

**For the demo scenario**: Extract Basua gauge reading from archived FMIS bulletins or the CWC study report. Prepare a static JSON with gauge reading (m), warning level, danger level, HFL. **Manual download needed**.

- **Source**: nwic.gov.in, cwc.gov.in, fmiscwrdbihar.gov.in, accessed 2026-10-02.

### 4.3 Sentinel-1 Flood Mapping

**Core methodology:**
1. Pre-process SAR: thermal noise removal, radiometric calibration, terrain correction, speckle filtering.
2. Change detection: compare pre-flood (baseline) VV/VH backscatter with post-flood image.
3. Thresholding: Otsu's method (automatic, non-parametric) to classify flooded/non-flooded pixels.
4. Export: Binary flood mask → vector polygons → GeoJSON.

**Polarisation**: VV is more sensitive to water surface; VH better in vegetated areas. Use both or VH for agricultural floodplains.

**Simplest prepared evidence format**: A GeoJSON `FeatureCollection` containing:
- One `Polygon` feature for the flood extent
- Properties: `event_date`, `satellite` ("Sentinel-1A"), `polarisation` ("VH"), `method` ("otsu_change_detection"), `confidence` (float 0–1), `source` ("prepared_scenario")

**Tools**: Google Earth Engine (cloud-based, free) or ESA SNAP (desktop).

- **Source**: Sentinel-1 SAR flood mapping best practices, GEE documentation, accessed 2026-10-02.

---

## 5 Blockchain Facts (Member 3)

### 5.1 Drunix

**Drunix is a real platform.** It is an open-source, enterprise-grade, permissioned blockchain launched by the **National Payments Corporation of India (NPCI)** in June 2026. It is an enhanced fork of Hyperledger Fabric with backward compatibility to Fabric v2.5.x.

Key architectural features relevant to GeoProtect:
- **Split peer roles**: Endorsement peers (Lite Peers) and commit peers scale independently.
- **YugabyteDB SQL state store**: Supports SQL-based ledger state queries.
- **Stateless validation**: Decoupled into a scalable service.
- **Shared transient store**: Reduces network calls for private data.
- **Permissioned**: Only approved organisations can participate.

Chaincode is written in Go (same as Hyperledger Fabric). The gateway pattern follows the Fabric Gateway SDK.

- **Source**: simplileap.com, zebpay.com, vajiramandravi.com (Drunix coverage), accessed 2026-10-02.
- **Takeaway**: Drunix is confirmed. Our contract is Drunix-specific (not ledger-agnostic). Chaincode in Go, gateway in Go, YugabyteDB for state.

### 5.2 Gateway Pattern and Idempotency

- **Deterministic claim ID**: `claim_id = SHA256(event_id + farmer_id)` truncated to a hex prefix. This ensures the same event + farmer always produces the same claim ID. If the gateway receives a duplicate creation request, it returns the existing claim with `"duplicate": true`.
- **Never on-chain**: Names, phone numbers, Aadhaar, bank account numbers, exact coordinates. Only pseudonymous `farmer_id`, `policy_id`, hashes, and status enums.
- **Private data collections**: KYC details and bank info go in Fabric/Drunix private data collections with retention policies, not in the public ledger state.

---

## 6 Tooling

### 6.1 Formatter + Linter per Language

| Language | Tool | Version | Notes |
|----------|------|---------|-------|
| Python | Ruff (lint + format) | `0.16.10` | Replaces Black + Flake8 + isort |
| TypeScript / React | Biome (lint + format) | `2.5.15` | Replaces ESLint + Prettier |
| Go | golangci-lint | `2.14.0` | Standard Go linter runner |
| YAML / Markdown | Prettier | `3.5.3` | ASSUMPTION: version; check latest |

### 6.2 Pre-commit Configuration

Recommend `pre-commit` framework (https://pre-commit.com) with hooks for:
- `ruff` (Python)
- `biome` (TypeScript)
- `golangci-lint` (Go)
- `prettier` (YAML, Markdown)
- `check-json` / `check-yaml` (from `pre-commit-hooks`)
- `detect-secrets` (for accidentally committed credentials)

### 6.3 Port Map

| Service | Port | Owner |
|---------|------|-------|
| Frontend (React dev server) | 3000 | Member 1 |
| Backend API (FastAPI) | 8000 | Member 4 |
| Data Module (Python) | 8100 | Member 2 |
| Blockchain Gateway (Go) | 8200 | Member 3 |
| Mock Payment Adapter | 8300 | Member 4 |
| PostgreSQL | 5432 | Member 4 |
| YugabyteDB (YSQL) | 5433 | Member 3 |
| Drunix Peer | 7051 | Member 3 |
| Drunix Orderer | 7050 | Member 3 |

- **Source**: Convention based on Fabric defaults and common dev ports; port numbers are ASSUMPTION, to be confirmed by team.
