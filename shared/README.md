# /shared

Shared configuration, contracts, sample data, documentation, and tools for the
GeoProtect parametric flood-insurance platform. **This folder is the single
source of truth** that all four team members build against.

**No application code lives here.** Only documentation, data, configuration,
and small helper scripts.

**Current version**: v0.1.1 (see `docs/contract-change-tracker.md`).

---

## Quick Orientation (2 minutes)

1. **What are we building?** — Read `docs/demo-scenario.md`. One flood event,
   12 farmers, tier_2, ₹30,000/farmer, ₹360,000 total.
2. **What are the APIs?** — Read `contracts/contract-v0.1.md`. Four boundaries,
   10 endpoints.
3. **What do I code against?** — Your sample data is in `sample-data/`, your
   config is in `config/thresholds.yaml`, your enums are in `docs/vocabulary.md`.
4. **What's unconfirmed?** — Read `docs/assumptions.md` (12 items, 3 resolved).
5. **What about the blockchain?** — Read `docs/ledger-notes.md` (Member 3).

---

## Contents

| Path | What it is | Owner |
|------|-----------|-------|
| [`contracts/`](contracts/) | API contract v0.1.1 and 15 JSON example files | All |
| [`sample-data/`](sample-data/) | Generated CSVs (35 farmers, 36 policies, 15 edge cases) and scenario manifest | M4 (gen), M2 (scenario) |
| [`docs/`](docs/) | Demo scenario, conventions, vocabulary, research, assumptions, tier tests, coverage, ledger notes, kickoff agenda, ports, change tracker | All |
| [`config/`](config/) | Thresholds (YAML + schema), `.env.template` files, `.gitignore` proposal, `.pre-commit-config.yaml` | All |
| [`tools/`](tools/) | Dataset generator and validator (with self-test mode) | All |

---

## Quick Start

```bash
# Install dependencies
pip install h3==4.1.0 pyyaml jsonschema

# Generate sample data (deterministic, seed=42)
python3 shared/tools/generate_dataset.py

# Validate everything is consistent
python3 shared/tools/validate_shared.py

# Run mutation self-tests (proves the validator has teeth)
python3 shared/tools/validate_shared.py --self-test
```

---

## Key Files

- **`docs/demo-scenario.md`** — THE scenario with provenance labels.
- **`contracts/contract-v0.1.md`** — Four API boundaries (v0.1.1).
- **`docs/vocabulary.md`** — All valid enums. If it's not here, it's invalid.
- **`config/thresholds.yaml`** — Trigger rules with IMD/CWC citations.
- **`docs/assumptions.md`** — 12 assumptions with provenance labels.
- **`docs/tier-test-cases.md`** — 8 boundary test cases for tier logic.
- **`docs/ledger-notes.md`** — Drunix questions for Member 3.
- **`docs/kickoff-agenda.md`** — 60-minute kickoff with decisions mapped to files.

---

## Rules

1. Every number must be identical across all files that reference it.
2. Changes to the contract go through `docs/contract-change-tracker.md`.
3. No personal data (names, phones, Aadhaar, coordinates) anywhere in `/shared`.
4. Run `validate_shared.py` after any edit — it must pass clean.
5. DEMO-CALIBRATED values must never be presented as real measurements.

---

## Out of Scope

Kafka, Kubernetes, Vault, MinIO — deferred for all team members.
