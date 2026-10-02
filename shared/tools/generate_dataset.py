#!/usr/bin/env python3
"""
generate_dataset.py — Generate reproducible sample data for GeoProtect demo.

Uses a fixed random seed so output is deterministic. Produces:
  - sample-data/farmers.csv
  - sample-data/policies.csv
  - sample-data/edge_cases.csv
  - sample-data/scenario_manifest.json

Run from repo root:
  python3 shared/tools/generate_dataset.py
"""

import csv
import json
import os
import random

# ---------- constants ----------
SEED = 42
random.seed(SEED)

SHARED_DIR = os.path.join(os.path.dirname(__file__), "..")
OUT_DIR = os.path.join(SHARED_DIR, "sample-data")

EVENT_ID = "EVT-b20f7c01"
EVENT_DATE = "2020-07-26T00:00:00Z"
H3_RESOLUTION = 8
PAYOUT_PERCENT = 60
SUM_INSURED = 50000
PAYOUT_PER_FARMER = int(SUM_INSURED * PAYOUT_PERCENT / 100)  # 30000

# Affected H3 cells (from demo-scenario.md)
AFFECTED_CELLS = [
    "883c1ea285fffff",
    "883c1ea28dfffff",
    "883c1ea2a9fffff",
    "883c1ea2e1fffff",
    "883c1ea2e3fffff",
    "883c1ea2e7fffff",
    "883c1ea2ebfffff",
    "883c1ea05bfffff",
    "883c1ea281fffff",
    "883c1ea287fffff",
]

# Non-affected cells (decoys)
NON_AFFECTED_CELLS = [
    "883c1ea051fffff",
    "883c1ea053fffff",
    "883c1ea059fffff",
    "883c1ea213fffff",
    "883c1ea217fffff",
    "883c1ea233fffff",
    "883c1ea23bfffff",
    "883c1ea283fffff",
]

# Crops realistic for kharif season in Supaul, Bihar
KHARIF_CROPS = ["rice", "maize", "jute"]  # kharif season

# ---------- 12 target farmers ----------
TARGET_FARMERS = [
    {"farmer_id": "FRM-00a1b2c3", "h3_cell": "883c1ea2e3fffff", "policy_id": "POL-aa010001"},
    {"farmer_id": "FRM-00a1b2c4", "h3_cell": "883c1ea2e3fffff", "policy_id": "POL-aa010002"},
    {"farmer_id": "FRM-00a1b2c5", "h3_cell": "883c1ea2e1fffff", "policy_id": "POL-aa010003"},
    {"farmer_id": "FRM-00a1b2c6", "h3_cell": "883c1ea2e7fffff", "policy_id": "POL-aa010004"},
    {"farmer_id": "FRM-00a1b2c7", "h3_cell": "883c1ea2ebfffff", "policy_id": "POL-aa010005"},
    {"farmer_id": "FRM-00a1b2c8", "h3_cell": "883c1ea285fffff", "policy_id": "POL-aa010006"},
    {"farmer_id": "FRM-00a1b2c9", "h3_cell": "883c1ea28dfffff", "policy_id": "POL-aa010007"},
    {"farmer_id": "FRM-00a1b2ca", "h3_cell": "883c1ea2a9fffff", "policy_id": "POL-aa010008"},
    {"farmer_id": "FRM-00a1b2cb", "h3_cell": "883c1ea05bfffff", "policy_id": "POL-aa010009"},
    {"farmer_id": "FRM-00a1b2cc", "h3_cell": "883c1ea281fffff", "policy_id": "POL-aa010010"},
    {"farmer_id": "FRM-00a1b2cd", "h3_cell": "883c1ea287fffff", "policy_id": "POL-aa010011"},
    {"farmer_id": "FRM-00a1b2ce", "h3_cell": "883c1ea2e1fffff", "policy_id": "POL-aa010012"},
]

# ---------- edge case definitions ----------
EDGE_CASES = [
    # Inactive policies inside affected cells
    {
        "farmer_id": "FRM-00d1e2f9", "h3_cell": "883c1ea2e3fffff",
        "policy_id": "POL-bb020001", "status": "inactive",
        "edge_type": "inactive_policy_in_affected_cell",
    },
    {
        "farmer_id": "FRM-00d1e2fa", "h3_cell": "883c1ea2e7fffff",
        "policy_id": "POL-bb020002", "status": "inactive",
        "edge_type": "inactive_policy_in_affected_cell",
    },
    # Expired policies inside affected cells
    {
        "farmer_id": "FRM-00d1e2fb", "h3_cell": "883c1ea2e1fffff",
        "policy_id": "POL-bb020003", "status": "expired",
        "end_date": "2020-06-30",
        "edge_type": "expired_policy_in_affected_cell",
    },
    {
        "farmer_id": "FRM-00d1e2fc", "h3_cell": "883c1ea285fffff",
        "policy_id": "POL-bb020004", "status": "expired",
        "end_date": "2020-07-15",
        "edge_type": "expired_policy_in_affected_cell",
    },
    # Duplicate attempt (farmer already in targets)
    {
        "farmer_id": "FRM-00a1b2c3", "h3_cell": "883c1ea2e3fffff",
        "policy_id": "POL-aa010001", "status": "active",
        "edge_type": "duplicate_claim_attempt",
    },
]


def make_farmer_row(farmer_id, h3_cell, crop=None, land_area_ha=None):
    """Create a farmer CSV row."""
    if crop is None:
        crop = random.choice(KHARIF_CROPS)
    if land_area_ha is None:
        land_area_ha = round(random.uniform(0.5, 3.0), 2)
    return {
        "farmer_id": farmer_id,
        "h3_cell": h3_cell,
        "crop": crop,
        "land_area_ha": land_area_ha,
    }


def make_policy_row(policy_id, farmer_id, status="active",
                    sum_insured=SUM_INSURED,
                    start_date="2020-06-01", end_date="2020-11-30"):
    """Create a policy CSV row."""
    return {
        "policy_id": policy_id,
        "farmer_id": farmer_id,
        "status": status,
        "sum_insured": sum_insured,
        "start_date": start_date,
        "end_date": end_date,
    }


def generate():
    os.makedirs(OUT_DIR, exist_ok=True)

    farmers = []
    policies = []
    edge_cases_out = []

    # 12 target farmers — active policies in affected cells
    for t in TARGET_FARMERS:
        farmers.append(make_farmer_row(t["farmer_id"], t["h3_cell"]))
        policies.append(make_policy_row(t["policy_id"], t["farmer_id"]))

    # Edge case farmers
    for ec in EDGE_CASES:
        if ec["edge_type"] == "duplicate_claim_attempt":
            # Already in farmers/policies list
            edge_cases_out.append({
                "farmer_id": ec["farmer_id"],
                "h3_cell": ec["h3_cell"],
                "policy_id": ec["policy_id"],
                "policy_status": ec["status"],
                "edge_type": ec["edge_type"],
                "expected_result": "Return existing claim with duplicate=true",
            })
            continue

        crop = random.choice(KHARIF_CROPS)
        farmers.append(make_farmer_row(ec["farmer_id"], ec["h3_cell"], crop))

        end_date = ec.get("end_date", "2020-11-30")
        policies.append(make_policy_row(
            ec["policy_id"], ec["farmer_id"],
            status=ec["status"],
            end_date=end_date,
        ))

        expected = {
            "inactive_policy_in_affected_cell": "Rejected: policy_inactive",
            "expired_policy_in_affected_cell": "Rejected: policy_expired",
        }
        edge_cases_out.append({
            "farmer_id": ec["farmer_id"],
            "h3_cell": ec["h3_cell"],
            "policy_id": ec["policy_id"],
            "policy_status": ec["status"],
            "edge_type": ec["edge_type"],
            "expected_result": expected.get(ec["edge_type"], ""),
        })

    # 8 decoy farmers — active policies outside affected cells
    for i, cell in enumerate(NON_AFFECTED_CELLS):
        fid = f"FRM-00d1e2f{i + 1}"
        pid = f"POL-cc03000{i + 1}"
        farmers.append(make_farmer_row(fid, cell))
        policies.append(make_policy_row(pid, fid))
        edge_cases_out.append({
            "farmer_id": fid,
            "h3_cell": cell,
            "policy_id": pid,
            "policy_status": "active",
            "edge_type": "active_policy_outside_affected_cells",
            "expected_result": "Rejected: farmer_outside_cells",
        })

    # --- NEW EDGE CASE: farmer with two policies (FRM-00a1b2c5 already
    # has POL-aa010003; add a second policy POL-ee050001 with different
    # sum_insured = 75000) ---
    policies.append(make_policy_row(
        "POL-ee050001", "FRM-00a1b2c5",
        status="active", sum_insured=75000,
    ))
    edge_cases_out.append({
        "farmer_id": "FRM-00a1b2c5",
        "h3_cell": "883c1ea2e1fffff",
        "policy_id": "POL-ee050001",
        "policy_status": "active",
        "edge_type": "farmer_with_two_policies",
        "expected_result": "Approved: one claim per policy, payout based on each policy's sum_insured",
    })

    # --- NEW EDGE CASE: outside farmer with different sum_insured ---
    fid_diff = "FRM-00ff0001"
    pid_diff = "POL-ff060001"
    farmers.append(make_farmer_row(fid_diff, "883c1ea283fffff"))
    policies.append(make_policy_row(
        pid_diff, fid_diff, sum_insured=35000,
    ))
    edge_cases_out.append({
        "farmer_id": fid_diff,
        "h3_cell": "883c1ea283fffff",
        "policy_id": pid_diff,
        "policy_status": "active",
        "edge_type": "different_sum_insured_outside_cells",
        "expected_result": "Rejected: farmer_outside_cells (sum_insured=35000 is irrelevant)",
    })

    # Additional non-affected farmers to pad dataset
    for i in range(10):
        fid = f"FRM-00ee00{i:02x}"
        pid = f"POL-dd04000{i}"
        cell = random.choice(NON_AFFECTED_CELLS)
        farmers.append(make_farmer_row(fid, cell))
        policies.append(make_policy_row(pid, fid))

    # Write farmers.csv
    farmers_path = os.path.join(OUT_DIR, "farmers.csv")
    with open(farmers_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["farmer_id", "h3_cell", "crop", "land_area_ha"])
        writer.writeheader()
        writer.writerows(farmers)
    print(f"✓ Wrote {len(farmers)} farmers to {farmers_path}")

    # Write policies.csv
    policies_path = os.path.join(OUT_DIR, "policies.csv")
    with open(policies_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["policy_id", "farmer_id", "status", "sum_insured", "start_date", "end_date"])
        writer.writeheader()
        writer.writerows(policies)
    print(f"✓ Wrote {len(policies)} policies to {policies_path}")

    # Write edge_cases.csv
    edge_path = os.path.join(OUT_DIR, "edge_cases.csv")
    with open(edge_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "farmer_id", "h3_cell", "policy_id", "policy_status",
            "edge_type", "expected_result",
        ])
        writer.writeheader()
        writer.writerows(edge_cases_out)
    print(f"✓ Wrote {len(edge_cases_out)} edge cases to {edge_path}")

    # Write scenario_manifest.json
    manifest = {
        "event_id": EVENT_ID,
        "event_date": EVENT_DATE,
        "region_name": "Basantpur block, Supaul",
        "h3_resolution": H3_RESOLUTION,
        "affected_h3_cells": AFFECTED_CELLS,
        "tier": "tier_2",
        "payout_percent": PAYOUT_PERCENT,
        "sum_insured_inr": SUM_INSURED,
        "payout_per_farmer_inr": PAYOUT_PER_FARMER,
        "affected_farmer_count": 12,
        "total_payout_inr": 12 * PAYOUT_PER_FARMER,
        "data_provenance": {
            "rainfall_mm": "demo_exaggerated",
            "gauge_level_m": "demo_calibrated",
            "inundation_pct": "demo_calibrated",
            "danger_level_m": "verified_secondary",
            "highest_flood_level_m": "verified_secondary",
            "warning_level_m": "unverified",
        },
        "prepared_files": [
            {
                "filename": "rainfall_evt_b20f7c01.json",
                "format": "JSON",
                "description": "24 h rainfall data for the event",
                "owner": "Member 2",
                "status": "pending",
            },
            {
                "filename": "gauge_evt_b20f7c01.json",
                "format": "JSON",
                "description": "Basua gauge reading and warning/danger/HFL levels",
                "owner": "Member 2",
                "status": "pending",
            },
            {
                "filename": "flood_extent_evt_b20f7c01.geojson",
                "format": "GeoJSON",
                "description": "Sentinel-1 derived flood polygon with metadata",
                "owner": "Member 2",
                "status": "pending",
            },
        ],
    }
    manifest_path = os.path.join(OUT_DIR, "scenario_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"✓ Wrote scenario manifest to {manifest_path}")

    print(f"\nSummary: {len(farmers)} farmers, {len(policies)} policies, "
          f"{len(edge_cases_out)} edge cases")


if __name__ == "__main__":
    generate()
