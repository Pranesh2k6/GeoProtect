# /shared/tools

Helper scripts for generating and validating shared data.

**Owner**: All team members.

## Scripts

| Script | Purpose |
|--------|---------|
| `generate_dataset.py` | Generate deterministic sample data (seed=42). |
| `validate_shared.py` | Validate all shared deliverables for consistency. |

## Setup

```bash
pip install -r shared/tools/requirements.txt
```

## Usage

```bash
# Generate data
python3 shared/tools/generate_dataset.py

# Validate everything
python3 shared/tools/validate_shared.py
```
