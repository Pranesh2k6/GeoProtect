# /shared/config

Configuration files for all GeoProtect services.

**Owner**: Member 4 (thresholds), All (env templates).

## Files

| File | Purpose |
|------|---------|
| `thresholds.yaml` | Trigger thresholds, tier rules, payout percentages with source citations. |
| `thresholds.schema.json` | JSON Schema for validating thresholds.yaml. |
| `backend.env.template` | Backend (FastAPI) environment variables. |
| `frontend.env.template` | Frontend (React) environment variables. |
| `data-module.env.template` | Data Module (Python) environment variables. |
| `blockchain.env.template` | Blockchain Gateway (Go) environment variables. |

## Usage

Copy the relevant `.env.template` to `.env` in your service directory and fill
in actual values. **Never commit `.env` files.**
