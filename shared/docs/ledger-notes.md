# Ledger Notes — Member 3 to Confirm

> This document collects all Drunix / blockchain assumptions that were
> previously embedded in the contract and config. **Member 3 must confirm
> or correct every item here at kickoff.** The API contract itself
> (contract-v0.1.md) is now ledger-agnostic.

---

## What We Know (from public sources)

Drunix is an open-source, enterprise-grade, permissioned blockchain platform
launched by NPCI in June 2026. It is an enhanced fork of Hyperledger Fabric
with backward compatibility to Fabric v2.5.x.

- **Source**: simplileap.com, zebpay.com, opensourceforu.com (coverage articles),
  accessed 2026-10-02.
- **GitHub**: https://github.com/npci — NPCI's GitHub org; check for a
  "drunix" repo or SDK.
- **Related project**: Falcon (NPCI's Fabric network orchestrator).

Key architectural claims from coverage:
- Split peer roles: endorsement (Lite Peers) and commit peers.
- YugabyteDB SQL state store (replaces LevelDB/CouchDB).
- Stateless validation service.
- Shared transient store for private data.
- Go chaincode compatible with Fabric Chaincode Shim API.

**Caveat**: No authoritative SDK documentation or official Drunix developer
guide has been located. All of the above is from third-party coverage of the
June 2026 launch. Until Member 3 confirms, we treat Drunix as "probably
Fabric-compatible but not guaranteed."

---

## Assumptions Moved Here from Contract

| Item | Value Used | Status |
|------|-----------|--------|
| Chaincode language | Go | ASSUMPTION — Fabric-compatible but Drunix may differ |
| Channel name | `geoprotect-channel` | Placeholder — Member 3 to set |
| Chaincode name | `geoprotect-cc` | Placeholder — Member 3 to set |
| MSP ID | `Org1MSP` | Placeholder — Member 3 to set |
| Peer port | 7051 | Fabric default — may differ in Drunix |
| Orderer port | 7050 | Fabric default — may differ in Drunix |
| Gateway pattern | Fabric Gateway SDK for Go | ASSUMPTION |
| YugabyteDB port | 5433 | Standard YSQL port |
| Endorsement policy | Quorum of data providers | ASSUMPTION — needs chaincode design |
| Private data collections | For KYC, bank details | Fabric concept — confirm in Drunix |

---

## Questions for Member 3 at Kickoff

1. Is the Drunix SDK available? If so, where? Is it a drop-in replacement for `github.com/hyperledger/fabric-gateway`?
2. Does YugabyteDB replace CouchDB/LevelDB as the state store, or is it an additional query layer?
3. What endorsement policy should claims use? (e.g., "any 2 of 3 data providers" or "all org peers")
4. Does Drunix support the same Private Data Collection APIs as Fabric v2.5.x?
5. What is the correct peer/orderer addressing scheme? gRPC over TLS?
6. Are there any Drunix-specific chaincode APIs beyond the standard Fabric Shim?
7. Can we run a local Drunix test network for development, or should we use Fabric v2.5.x as a dev stand-in?
8. What transaction throughput should we design for? (e.g., 100 claims/minute for a regional flood)

---

## Fields That Cross the Ledger Boundary

Only these fields flow from the backend to the gateway (Boundary 3):

| Field | Type | On-chain? | Notes |
|-------|------|-----------|-------|
| `claim_id` | string | Yes | Deterministic hash, not personal |
| `event_id` | string | Yes | System-generated, not personal |
| `farmer_id` | string | Yes | Pseudonymous (`FRM-` prefix), not personal |
| `policy_id` | string | Yes | System reference, not personal |
| `tier` | string | Yes | Enum value |
| `payout_amount_inr` | int | Yes | Amount, not personal |
| `sum_insured_inr` | int | Yes | Amount, not personal |
| `payout_percent` | int | Yes | Derived from tier |
| `status` | string | Yes | Enum value |
| `tx_reference` | string | Yes (returned) | Ledger transaction ID |

**Never on-chain**: names, phone numbers, Aadhaar, bank account numbers,
exact coordinates, KYC documents.
