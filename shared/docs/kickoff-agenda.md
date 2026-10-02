# Kickoff Agenda — 60 Minutes

> Use this agenda for the team kickoff meeting. Each decision references
> the specific file where the answer should be recorded.

---

## Pre-meeting (5 min)

All team members should have read:
- `shared/README.md` (2-minute orientation)
- `shared/docs/demo-scenario.md` (the scenario)
- `shared/docs/assumptions.md` (what needs confirmation)

---

## Part 1: Confirm the Demo Scenario (15 min)

| # | Decision | Who | Reference File |
|---|----------|-----|----------------|
| 1 | Are the **H3 cells** acceptable, or does Member 2 have an actual Basantpur block boundary GeoJSON? | Member 2 | `docs/demo-scenario.md`, assumption A6 |
| 2 | Can Member 2 extract the **real IMD rainfall** for Supaul on 2020-07-26 from `imdlib`? If so, does it change the tier? | Member 2 | `docs/assumptions.md`, A1 |
| 3 | Can Member 2 find the **real Basua gauge peak** from archived WRD Bihar FMIS bulletins? | Member 2 | `docs/assumptions.md`, A2 |
| 4 | Is **₹50,000 sum insured** realistic for Supaul kharif rice? Should we use a different figure? | Member 4 | `docs/assumptions.md`, A5 |
| 5 | Are the **payout percentages (25%, 60%, 100%)** acceptable or should they mirror a real RWBCIS term sheet? | Member 4 | `config/thresholds.yaml`, assumption A12 |

---

## Part 2: Confirm the Ledger Setup (15 min)

All questions from `docs/ledger-notes.md`:

| # | Decision | Who | Reference File |
|---|----------|-----|----------------|
| 6 | Is the **Drunix SDK** available? Is it a drop-in for Fabric Gateway Go SDK? | Member 3 | `docs/ledger-notes.md` |
| 7 | What **endorsement policy** should claims use? | Member 3 | `docs/ledger-notes.md` |
| 8 | Can we run a **local Drunix test network**, or use Fabric v2.5.x as dev stand-in? | Member 3 | `docs/ledger-notes.md` |
| 9 | Confirm the **ports** (7050, 7051, 5433) or provide replacements. | Member 3 | `docs/ports-and-tooling.md` |

---

## Part 3: Walk Through the Contract (15 min)

| # | Decision | Who | Reference File |
|---|----------|-----|----------------|
| 10 | Review `POST /api/v1/events`: is the **backend-generates-event_id** pattern acceptable? | All | `contracts/contract-v0.1.md` §1.1 |
| 11 | Review `POST /api/v1/verify`: does the **data_provenance** field work for Member 1's frontend? | Member 1 | `contracts/contract-v0.1.md` §2.1 |
| 12 | Review `POST /api/v1/claims`: are the **deterministic ID derivations** (SHA256) agreed? | Members 3, 4 | `contracts/contract-v0.1.md` §3.1 |
| 13 | Review the **tier test cases**: does the "all three signals must pass" rule work? | All | `docs/tier-test-cases.md` |

---

## Part 4: Tooling and Logistics (10 min)

| # | Decision | Who | Reference File |
|---|----------|-----|----------------|
| 14 | Adopt the **port map** or propose changes. | All | `docs/ports-and-tooling.md` |
| 15 | Copy **`.pre-commit-config.yaml`** and **`.gitignore`** from `config/` to repo root. | Member 4 | `config/pre-commit-config.yaml`, `config/gitignore-proposal` |
| 16 | Set up **linters**: Ruff (M2/M4), Biome (M1), golangci-lint (M3). | All | `docs/ports-and-tooling.md` |

---

## Part 5: Action Items and Parking Lot (5 min)

- Assign each open assumption from `docs/assumptions.md` a sprint task.
- Log any contract changes agreed upon in `docs/contract-change-tracker.md`.
- Set up the shared Git branch strategy.

---

## Post-meeting

Member 4 runs:
```bash
python3 shared/tools/validate_shared.py
```
to confirm everything is still consistent after any kickoff changes.
