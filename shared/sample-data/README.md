# /shared/sample-data

Generated sample data for the GeoProtect demo scenario.

**Owner**: Member 4 (generator), Member 2 (scenario files listed in manifest).

## Files

- `farmers.csv` — 34 pseudonymous farmers with H3 cell, crop, and land area.
- `policies.csv` — 34 policies linked to farmers (active, inactive, expired).
- `edge_cases.csv` — 13 edge cases with expected results.
- `scenario_manifest.json` — Manifest listing the prepared files Member 2 must create.

## Regeneration

All files are deterministically generated with seed 42:

```bash
python3 shared/tools/generate_dataset.py
```

**Do not edit these files by hand.** Modify the generator script instead.
