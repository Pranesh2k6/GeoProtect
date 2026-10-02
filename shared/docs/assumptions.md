# Assumptions

> Every assumption made during the initial shared setup. Each must be
> confirmed or replaced by the listed owner before the hackathon demo.
>
> **Provenance labels**: VERIFIED = confirmed from primary official source;
> VERIFIED (secondary) = confirmed from aggregator citing official data;
> DEMO-CALIBRATED = chosen realistically inside a documented range;
> DEMO-EXAGGERATED = deliberately set above the documented range;
> UNVERIFIED = no source found.

| # | Assumption | Provenance | Why | Owner | Deadline | Status |
|---|-----------|------------|-----|-------|----------|--------|
| A1 | **Demo rainfall value: 230 mm/24 h** for the Basantpur block event. IMD reports "heavy to very heavy" (64.5–204.4 mm) for Supaul district in July 2020 across multiple spells. **230 mm is above the real range** (above 204.5 mm "Extremely Heavy" threshold), chosen deliberately to reach tier_2. A real Kosi-type flood may not produce extremely heavy local rainfall because the flood is upstream-driven from the Nepal catchment. | DEMO-EXAGGERATED | Chosen to demonstrate a tier_2 scenario. If real rainfall was 180 mm (within "very heavy"), tier would drop to tier_1 under current rules. Team should discuss "gauge-primary" override at kickoff. | Member 2 | Before demo | ☐ Pending |
| A2 | **Demo gauge reading: 48.50 m** at Basua station (DL = 47.75 m). This is 0.75 m above the verified DL, placing the event in "above DL, below HFL". The Kosi at Basua did cross DL in July 2020 but the actual peak reading was not extracted from archived WRD Bihar FMIS bulletins. | DEMO-CALIBRATED | Sits realistically between DL (47.75 m, VERIFIED) and HFL (49.24 m, VERIFIED). Must not be presented as a real measurement. | Member 2 | Before demo | ☐ Pending |
| ~~A3~~ | ~~**Basua HFL is assumed to be 49.50 m.**~~ **RESOLVED**: HFL is **49.24 m**, recorded in 2017. Source: CWC/WRD Bihar data via befiqr.in (aggregator). Primary CWC PDF bulletin not directly opened. | VERIFIED (secondary) | No longer an assumption, but primary source not opened. befiqr.in is an aggregator that cites CWC/WRD Bihar data. | — | — | ✅ Verified (secondary) |
| A4 | **Satellite inundation of 45%** of the polygon area. This is a reasonable estimate for a severe Kosi basin flood but is not derived from an actual Sentinel-1 analysis. | DEMO-CALIBRATED | Sentinel-1 analysis not performed during setup. Must not be presented as a real measurement. | Member 2 | Before demo | ☐ Pending |
| A5 | **Sum insured per farmer: ₹50,000.** This is a round number inspired by PMFBY small/marginal farmer policy sizes but is not drawn from a specific scheme table for Supaul. | DEMO-CALIBRATED | Simplification for demo arithmetic. | Member 4 | Before demo | ☐ Pending |
| A6 | **H3 cells chosen via grid_disk around an approximate center point** for Basantpur block. The cells are geometrically valid at resolution 8 but may not perfectly overlap the actual Basantpur administrative boundary. | DEMO-CALIBRATED | Exact block boundary GeoJSON was not available during setup. | Member 2 | Before demo | ☐ Pending |
| A7 | **Port assignments** (see ports-and-tooling.md) are proposals. If any port conflicts with a team member's local environment, the team must agree on a replacement. | N/A | Standard convention, not hard requirement. | All | Sprint start | ☐ Pending |
| A8 | **Prettier version 3.5.3** for YAML/Markdown linting. Actual latest version may differ; verify before pinning in CI. | N/A | Version from web search; not confirmed on npmjs.com. | Member 1 | Sprint start | ☐ Pending |
| A9 | **Drunix blockchain compatibility.** Drunix is confirmed as an NPCI Fabric fork (June 2026), but no official SDK documentation or developer guide has been located. All chaincode/gateway assumptions are based on third-party coverage and may not hold. See `docs/ledger-notes.md` for full details and questions for Member 3. | UNVERIFIED | SDK docs not reviewed; third-party coverage only. | Member 3 | Sprint start | ☐ Pending |
| A10 | **Kharif rice and maize** are the representative crops for Supaul district. Verified from general knowledge of Bihar agriculture but not from a specific crop atlas or PMFBY notification. Jute is also included in the sample data as a kharif crop. | DEMO-CALIBRATED | Standard kharif crops for north Bihar alluvial plains. | Member 2 | Before demo | ☐ Pending |
| A11 | **Warning Level at Basua is assumed to be 46.50 m** (1.25 m below DL). CWC publishes DL and HFL for Basua but warning level was not found in any public source. | UNVERIFIED | Needed for tier_1 threshold check. | Member 2 | Before demo | ☐ Pending |
| A12 | **Payout percentages (25%, 60%, 100%)** are simplified from RWBCIS term sheet practices. Actual RWBCIS term sheets for Supaul/kharif rice may use different percentages. | DEMO-CALIBRATED | Reasonable simplification inspired by scheme design. | Member 4 | Before demo | ☐ Pending |
