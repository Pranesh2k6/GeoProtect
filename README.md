# GeoProtect

**Parametric Micro-Insurance and Automated Relief Ledger on Drunix**

## The Problem

A flood doesn't wait for a survey. For a smallholder farmer, the loss is instant, but help is not. Traditional micro-insurance relies on manual damage assessments and paperwork, so payouts take weeks or months. Small policies are also costly to process, so insurers struggle to serve this group well. Even PMFBY, India's flagship crop insurance, still sees settlement delays, because data has to move between states, insurers and banks.

In that gap, families are left without cash when they need it most, and many turn to high-interest debt.

## Our Solution

GeoProtect is a parametric flood-relief network on NPCI's Drunix. Every policy carries a clear, measurable trigger. When independent data sources confirm the trigger over a farmer's registered land, a claim is created and paid automatically to the farmer's bank account through an NPCI-compatible payment rail. No claim form. No damage survey. The farmer gets an SMS or voice alert in their own language.

GeoProtect is built as a fast first-response layer that sits beside yield-based schemes like PMFBY. It puts emergency cash in farmers' hands in the first days after a flood. It does not replace cover for crop loss.

## How It Works

1. **Register.** Farmers, KYC status and policies are onboarded through a Farmer Registry / Authorised KYC Service. Aadhaar appears only as a KYC mechanism; the application never queries it directly. Each farm's location is stored as a small map-cell ID (H3 grid), not as exact coordinates.

2. **Verify.** Independent data providers send signed evidence to Drunix: (a) rainfall and weather data, (b) Sentinel-1 radar flood mapping, which sees through monsoon cloud, and (c) river-gauge or disaster-authority confirmation. A Drunix endorsement policy requires a quorum, before the event is marked verified. No single AI output or data source can release money. Images and raw datasets stay off-chain; the ledger holds the event ID, polygon hash, data hashes, confidence score and trigger parameters.

3. **Match.** The verified flood polygon is converted off-chain into a list of map cells. A plain SQL query on Drunix's SQL state store returns the active policies in those cells. If chaincode-level SQL is not practical in the prototype, the match runs off-chain and only the eligibility list and its hash are committed.

4. **Pay.** Chaincode checks policy status, trigger threshold and eligibility, creates the claim, and sends a payout instruction to the NPCI payment adapter. Payout status (created, submitted, settled, failed, retried) is tracked on the ledger, and each payout is idempotent so no farmer is paid twice.

5. **Prove.** Policies, disaster events, claims and payouts form a tamper-resistant audit trail that the insurer, bank, data providers and government can all inspect.

## The Drunix Edge

- **Built for the surge.** One regional flood can create thousands of claims in minutes. Drunix splits endorsing peers (Lite Peers) from committing peers and runs validation as a stateless service, so each layer scales on its own.

- **SQL state store.** SQL-backed on-chain state (YugabyteDB) lets us run structured queries across disasters, policies and eligibility without key-value workarounds.

- **Private data, fewer network calls.** Identity, bank and claim details stay in private data collections between authorised organisations. Drunix's shared transient store cuts the network calls this needs.

- **Shared truth across organisations.** The insurer, bank, data providers and a government body each run a node. Quorum endorsement makes the disaster record a shared fact, not one party's word.

- **Fabric-compatible.** Drunix is backwards compatible with Hyperledger Fabric v2.5.x, so existing chaincode and tooling carry over.

## Privacy and Compliance

- **Minimal ledger.** Only pseudonymous farmer IDs, hashes and status go on-chain. No names, bank details or exact coordinates.

- **DPDP-ready design.** Personal data sits in private collections with retention limits, built for India's DPDP Act, whose core duties apply from 13 May 2027.

- **Human safety net.** An appeals queue lets a farmer challenge a missed trigger, so automation never has the last word.
