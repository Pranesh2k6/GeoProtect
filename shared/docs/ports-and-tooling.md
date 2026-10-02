# Ports and Tooling

> Fixed port assignments and recommended toolchain for all GeoProtect services.

---

## Port Map

| Service | Port | Owner | Protocol | Notes |
|---------|------|-------|----------|-------|
| Frontend (React dev server) | 3000 | Member 1 | HTTP | Vite/CRA dev server |
| Backend API (FastAPI) | 8000 | Member 4 | HTTP | Single public API |
| Data Module (Python) | 8100 | Member 2 | HTTP | Internal only |
| Blockchain Gateway (Go) | 8200 | Member 3 | HTTP | Internal only |
| Mock Payment Adapter | 8300 | Member 4 | HTTP | Internal only |
| PostgreSQL | 5432 | Member 4 | TCP | Farmer/policy DB |
| YugabyteDB (YSQL) | 5433 | Member 3 | TCP | Drunix SQL state |
| Drunix Orderer | 7050 | Member 3 | gRPC | Fabric-compatible |
| Drunix Peer | 7051 | Member 3 | gRPC | Fabric-compatible |

> **Out of scope (deferred)**: Kafka, Kubernetes, Vault, MinIO.

---

## Toolchain

### Formatter + Linter

| Language | Tool | Pinned Version | Install |
|----------|------|----------------|---------|
| Python | Ruff | `0.16.10` | `pip install ruff==0.16.10` |
| TypeScript / React | Biome | `2.5.15` | `npx @biomejs/biome@2.5.15` |
| Go | golangci-lint | `2.14.0` | `go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.14.0` |
| YAML / Markdown | Prettier | `3.5.3` | `npx prettier@3.5.3` |

### Pre-commit Configuration

Install: `pip install pre-commit && pre-commit install`

Recommended `.pre-commit-config.yaml` (place in repo root):

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: check-json
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.16.10
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.5.3
    hooks:
      - id: prettier
        types_or: [yaml, markdown]

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
```

> **Note**: Biome and golangci-lint are best run via their own CI steps or
> local scripts rather than pre-commit hooks due to binary dependencies.
> Members 1 and 3 should add equivalent checks to their service-level
> scripts.

### Shared Python Dependencies

See `shared/tools/requirements.txt` for the Python tools used in `/shared`.
