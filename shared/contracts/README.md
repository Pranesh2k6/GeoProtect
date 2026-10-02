# /shared/contracts

API contract definitions and JSON examples for all four service boundaries.

**Owner**: All team members (changes require entry in `docs/contract-change-tracker.md`).

## Files

- `contract-v0.1.md` — Full API contract with endpoints, fields, units, and rules.
- `examples/` — One JSON file per endpoint per scenario (success, failure, duplicate).

## How to Use

1. Read `contract-v0.1.md` for the full specification.
2. Use files in `examples/` as test fixtures or reference payloads.
3. Validate examples: `python3 shared/tools/validate_shared.py`
