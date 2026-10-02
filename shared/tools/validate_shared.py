#!/usr/bin/env python3
"""
validate_shared.py — Validate all /shared deliverables for consistency.

Usage:
  python3 shared/tools/validate_shared.py           # normal validation
  python3 shared/tools/validate_shared.py --self-test  # run mutation self-tests

Checks:
  1.  H3 cell validity and resolution
  2.  Exactly 12 affected farmers with active policies
  3.  Payout arithmetic
  4.  Enum values in examples match vocabulary.md
  5.  JSON examples parse
  6.  JSON examples validate against contract-defined schemas
  7.  No personal data / coordinates
  8.  ID format validation
  9.  Provenance labels: exist and valid for rainfall, gauge, HFL, WL
  10. Policy date coverage
  11. Threshold consistency with demo-scenario.md
  12. Change tracker exists and is non-empty
  13. Contract-coverage.md references only files that exist
  14. Every tracker entry references files that exist
"""

import csv
import json
import os
import re
import shutil
import sys
import tempfile

import h3
import yaml

SHARED = os.path.join(os.path.dirname(__file__), "..")
PASS = 0
FAIL = 0


def check(label, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {label}")
    else:
        FAIL += 1
        print(f"  ❌ {label}: {detail}")
    return condition


def load_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def load_json(path):
    with open(path) as f:
        return json.load(f)


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


# ---- JSON Schema definitions for each example type ----
# These schemas validate the STRUCTURE of each example, not just that it parses.

EXAMPLE_SCHEMAS = {
    "post_event_request.json": {
        "type": "object",
        "required": ["event_date", "region_name", "h3_cells"],
        "properties": {
            "event_date": {"type": "string"},
            "region_name": {"type": "string"},
            "h3_cells": {"type": "array", "items": {"type": "string"}},
        },
        "additionalProperties": False,
    },
    "post_event_response_success.json": {
        "type": "object",
        "required": ["success", "event_id", "stage", "duplicate"],
        "properties": {
            "success": {"type": "boolean", "const": True},
            "event_id": {"type": "string", "pattern": "^EVT-[0-9a-f]{8}$"},
            "stage": {"type": "string"},
            "duplicate": {"type": "boolean"},
        },
    },
    "post_event_response_failure.json": {
        "type": "object",
        "required": ["success", "reason_code", "message"],
        "properties": {
            "success": {"type": "boolean", "const": False},
            "reason_code": {"type": "string"},
            "message": {"type": "string"},
        },
    },
    "get_event_response_not_found.json": {
        "type": "object",
        "required": ["success", "reason_code", "message"],
        "properties": {
            "success": {"type": "boolean", "const": False},
            "reason_code": {"type": "string", "const": "not_found"},
            "message": {"type": "string"},
        },
    },
    "post_verify_request.json": {
        "type": "object",
        "required": ["event_id", "event_date", "h3_cells"],
        "properties": {
            "event_id": {"type": "string", "pattern": "^EVT-[0-9a-f]{8}$"},
            "event_date": {"type": "string"},
            "h3_cells": {"type": "array", "items": {"type": "string"}},
        },
    },
    "post_verify_response_success.json": {
        "type": "object",
        "required": [
            "success", "event_id", "rainfall_mm", "rainfall_class",
            "gauge_station", "gauge_level_m", "warning_level_m",
            "danger_level_m", "highest_flood_level_m", "inundation_pct",
            "confidence", "tier", "verified_at", "data_provenance",
        ],
        "properties": {
            "success": {"type": "boolean", "const": True},
            "event_id": {"type": "string"},
            "rainfall_mm": {"type": "number"},
            "rainfall_class": {"type": "string"},
            "gauge_station": {"type": "string"},
            "gauge_level_m": {"type": "number"},
            "warning_level_m": {"type": "number"},
            "danger_level_m": {"type": "number"},
            "highest_flood_level_m": {"type": "number"},
            "inundation_pct": {"type": "number"},
            "confidence": {"type": "number"},
            "tier": {"type": "string"},
            "verified_at": {"type": "string"},
            "data_provenance": {"type": "object"},
        },
    },
    "post_verify_response_failure.json": {
        "type": "object",
        "required": ["success", "event_id", "reason_code", "message"],
        "properties": {
            "success": {"type": "boolean", "const": False},
            "event_id": {"type": "string"},
            "reason_code": {"type": "string"},
            "message": {"type": "string"},
        },
    },
    "post_verify_response_trigger_not_met.json": {
        "type": "object",
        "required": ["success", "event_id", "reason_code", "message"],
        "properties": {
            "success": {"type": "boolean", "const": False},
            "event_id": {"type": "string"},
            "reason_code": {"type": "string", "const": "trigger_not_met"},
            "message": {"type": "string"},
        },
    },
    "post_claim_request.json": {
        "type": "object",
        "required": [
            "claim_id", "event_id", "farmer_id", "policy_id",
            "tier", "payout_amount_inr", "sum_insured_inr", "payout_percent",
        ],
        "properties": {
            "claim_id": {"type": "string", "pattern": "^CLM-[0-9a-f]{16}$"},
            "event_id": {"type": "string"},
            "farmer_id": {"type": "string"},
            "policy_id": {"type": "string"},
            "tier": {"type": "string"},
            "payout_amount_inr": {"type": "integer"},
            "sum_insured_inr": {"type": "integer"},
            "payout_percent": {"type": "integer"},
        },
    },
    "post_claim_response_success.json": {
        "type": "object",
        "required": ["success", "claim_id", "status", "duplicate", "created_at"],
        "properties": {
            "success": {"type": "boolean", "const": True},
            "claim_id": {"type": "string"},
            "status": {"type": "string", "const": "created"},
            "duplicate": {"type": "boolean", "const": False},
            "created_at": {"type": "string"},
        },
    },
    "post_claim_response_duplicate.json": {
        "type": "object",
        "required": ["success", "claim_id", "status", "duplicate", "created_at"],
        "properties": {
            "success": {"type": "boolean", "const": True},
            "claim_id": {"type": "string"},
            "status": {"type": "string"},
            "duplicate": {"type": "boolean", "const": True},
            "created_at": {"type": "string"},
        },
    },
    "post_claim_response_failure.json": {
        "type": "object",
        "required": ["success", "reason_code", "message"],
        "properties": {
            "success": {"type": "boolean", "const": False},
            "reason_code": {"type": "string"},
            "message": {"type": "string"},
        },
    },
    "post_payout_request.json": {
        "type": "object",
        "required": ["payout_id", "claim_id", "event_id", "farmer_id", "amount_inr"],
        "properties": {
            "payout_id": {"type": "string", "pattern": "^PAY-[0-9a-f]{16}$"},
            "claim_id": {"type": "string"},
            "event_id": {"type": "string"},
            "farmer_id": {"type": "string"},
            "amount_inr": {"type": "integer"},
        },
    },
    "post_payout_response_success.json": {
        "type": "object",
        "required": ["success", "payout_id", "status", "duplicate", "submitted_at"],
        "properties": {
            "success": {"type": "boolean", "const": True},
            "payout_id": {"type": "string"},
            "status": {"type": "string", "const": "submitted"},
            "duplicate": {"type": "boolean", "const": False},
            "submitted_at": {"type": "string"},
        },
    },
    "post_payout_response_failure.json": {
        "type": "object",
        "required": ["success", "reason_code", "message"],
        "properties": {
            "success": {"type": "boolean", "const": False},
            "reason_code": {"type": "string"},
            "message": {"type": "string"},
        },
    },
}


def run_checks(shared_dir):
    """Run all validation checks. Returns (pass_count, fail_count)."""
    global PASS, FAIL, SHARED
    SHARED = shared_dir
    PASS = 0
    FAIL = 0

    print("=" * 60)
    print("GeoProtect /shared Validator v0.1.2")
    print("=" * 60)

    # ---------- load data ----------
    farmers = load_csv(os.path.join(SHARED, "sample-data", "farmers.csv"))
    policies = load_csv(os.path.join(SHARED, "sample-data", "policies.csv"))
    manifest = load_json(os.path.join(SHARED, "sample-data", "scenario_manifest.json"))
    thresholds = load_yaml(os.path.join(SHARED, "config", "thresholds.yaml"))
    schema = load_json(os.path.join(SHARED, "config", "thresholds.schema.json"))

    affected_cells = set(manifest["affected_h3_cells"])
    event_date = manifest["event_date"][:10]  # "2020-07-26"
    examples_dir = os.path.join(SHARED, "contracts", "examples")

    # ---------- 1. H3 cell validity ----------
    print("\n[1] H3 Cell Validity")
    all_h3_cells = set()
    for row in farmers:
        all_h3_cells.add(row["h3_cell"])
    for cell in manifest["affected_h3_cells"]:
        all_h3_cells.add(cell)

    all_valid = True
    all_res8 = True
    for cell in sorted(all_h3_cells):
        if not h3.is_valid_cell(cell):
            all_valid = False
            check(f"Cell {cell} valid", False, "Not a valid H3 cell")
        elif h3.get_resolution(cell) != 8:
            all_res8 = False
            check(f"Cell {cell} resolution", False,
                  f"Resolution {h3.get_resolution(cell)}, expected 8")

    check("All H3 cells are valid", all_valid)
    check("All H3 cells are resolution 8", all_res8)

    # ---------- 2. Exactly 12 affected farmers ----------
    print("\n[2] Affected Farmer Count")
    policy_map = {}
    for p in policies:
        policy_map.setdefault(p["farmer_id"], []).append(p)

    affected_active = set()
    for f in farmers:
        farmer_policies = policy_map.get(f["farmer_id"], [])
        for p in farmer_policies:
            if (f["h3_cell"] in affected_cells
                and p["status"] == "active"
                and p["end_date"] >= event_date):
                affected_active.add(f["farmer_id"])

    check("Exactly 12 affected farmers with active policies",
          len(affected_active) == 12,
          f"Found {len(affected_active)}: {sorted(affected_active)}")

    # ---------- 3. Payout arithmetic ----------
    print("\n[3] Payout Arithmetic")
    tier = manifest["tier"]
    tier_config = thresholds["tiers"][tier]
    payout_pct = tier_config["payout_percent"]
    sum_insured = manifest["sum_insured_inr"]
    expected_per_farmer = int(sum_insured * payout_pct / 100)
    expected_total = 12 * expected_per_farmer

    check("Tier is tier_2", tier == "tier_2", f"Got {tier}")
    check("Payout percent is 60%", payout_pct == 60, f"Got {payout_pct}")
    check(f"Payout per farmer = ₹{expected_per_farmer}",
          manifest["payout_per_farmer_inr"] == expected_per_farmer,
          f"Manifest says {manifest['payout_per_farmer_inr']}")
    check(f"Total payout = ₹{expected_total}",
          manifest["total_payout_inr"] == expected_total,
          f"Manifest says {manifest['total_payout_inr']}")

    for fid in sorted(affected_active):
        found_50k = any(
            int(p["sum_insured"]) == sum_insured
            for p in policy_map.get(fid, [])
            if p["status"] == "active"
        )
        check(f"  {fid} has policy with sum_insured = {sum_insured}",
              found_50k,
              f"Policies: {[p['sum_insured'] for p in policy_map.get(fid, [])]}")

    # ---------- 4. Enum values in examples ----------
    print("\n[4] Enum Values in Contract Examples")
    vocab_path = os.path.join(SHARED, "docs", "vocabulary.md")
    with open(vocab_path) as f:
        vocab_text = f.read()

    vocab_values = set(re.findall(r"`([a-z][a-z0-9_]*)`", vocab_text))

    enum_fields = {"stage", "tier", "status", "reason_code", "rainfall_class"}

    for fn in sorted(os.listdir(examples_dir)):
        if not fn.endswith(".json"):
            continue
        filepath = os.path.join(examples_dir, fn)
        try:
            data = load_json(filepath)
        except json.JSONDecodeError as e:
            check(f"{fn} parses as JSON", False, str(e))
            continue

        for key in enum_fields:
            if key in data and data[key] is not None:
                val = data[key]
                check(f"{fn}: {key}={val} in vocabulary",
                      val in vocab_values,
                      f"'{val}' not found in vocabulary.md")

    # ---------- 5. JSON examples parse ----------
    print("\n[5] JSON Examples Parse")
    for fn in sorted(os.listdir(examples_dir)):
        if not fn.endswith(".json"):
            continue
        filepath = os.path.join(examples_dir, fn)
        try:
            load_json(filepath)
            check(f"{fn} valid JSON", True)
        except json.JSONDecodeError as e:
            check(f"{fn} valid JSON", False, str(e))

    # Validate thresholds against schema
    try:
        import jsonschema
        jsonschema.validate(thresholds, schema)
        check("thresholds.yaml validates against schema", True)
    except jsonschema.ValidationError as e:
        check("thresholds.yaml validates against schema", False, str(e.message))
    except ImportError:
        check("jsonschema available", False, "pip install jsonschema")

    # ---------- 6. JSON examples validate against contract schemas ----------
    print("\n[6] JSON Examples Validate Against Contract Schemas")
    try:
        import jsonschema
        for fn in sorted(os.listdir(examples_dir)):
            if not fn.endswith(".json"):
                continue
            if fn not in EXAMPLE_SCHEMAS:
                check(f"{fn} has a schema defined", False,
                      "No schema in EXAMPLE_SCHEMAS")
                continue
            filepath = os.path.join(examples_dir, fn)
            try:
                data = load_json(filepath)
                jsonschema.validate(data, EXAMPLE_SCHEMAS[fn])
                check(f"{fn} validates against schema", True)
            except jsonschema.ValidationError as e:
                check(f"{fn} validates against schema", False, e.message)
            except json.JSONDecodeError as e:
                check(f"{fn} validates against schema", False, f"JSON error: {e}")
    except ImportError:
        check("jsonschema available for example validation", False,
              "pip install jsonschema")

    # ---------- 7. No personal data or coordinates ----------
    print("\n[7] No Personal Data or Coordinates")
    personal_patterns = [
        (r"\b\d{12}\b", "Aadhaar-like 12-digit number"),
        (r"\b\d{10}\b", "Phone-like 10-digit number"),
        (r"\b[A-Z]{5}\d{4}[A-Z]\b", "PAN-like pattern"),
        (r"\blatitude\b", "latitude field"),
        (r"\blongitude\b", "longitude field"),
        (r'"lat"\s*:', "lat JSON key"),
        (r'"lng"\s*:', "lng JSON key"),
        (r'"lon"\s*:', "lon JSON key"),
    ]

    files_to_scan = []
    for dirpath, dirnames, filenames in os.walk(SHARED):
        if ".git" in dirpath:
            continue
        for fn in filenames:
            if fn.endswith((".csv", ".json", ".yaml", ".yml", ".md")):
                files_to_scan.append(os.path.join(dirpath, fn))

    pii_found = False
    for filepath in files_to_scan:
        with open(filepath) as f:
            try:
                content = f.read()
            except UnicodeDecodeError:
                continue
        for pattern, desc in personal_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                if desc.startswith("Aadhaar") or desc.startswith("Phone"):
                    real_matches = [m for m in matches
                                   if not re.search(r"[a-fA-F]", m)]
                    if not real_matches:
                        continue
                relpath = os.path.relpath(filepath, SHARED)
                check(f"{relpath}: no {desc}", False,
                      f"Found {len(matches)} match(es)")
                pii_found = True

    if not pii_found:
        check("No personal data patterns found in any file", True)

    # ---------- 8. ID format validation ----------
    print("\n[8] ID Format Validation")
    id_regexes = {
        "event_id": r"^EVT-[0-9a-f]{8}$",
        "farmer_id": r"^FRM-[0-9a-f]{8}$",
        "policy_id": r"^POL-[0-9a-f]{8}$",
        "claim_id": r"^CLM-[0-9a-f]{16}$",
        "payout_id": r"^PAY-[0-9a-f]{16}$",
    }

    for f in farmers:
        check(f"farmer_id {f['farmer_id']} format",
              re.match(id_regexes["farmer_id"], f["farmer_id"]) is not None,
              f"Does not match {id_regexes['farmer_id']}")

    for p in policies:
        check(f"policy_id {p['policy_id']} format",
              re.match(id_regexes["policy_id"], p["policy_id"]) is not None,
              f"Does not match {id_regexes['policy_id']}")

    check(f"event_id {manifest['event_id']} format",
          re.match(id_regexes["event_id"], manifest["event_id"]) is not None)

    for fn in sorted(os.listdir(examples_dir)):
        if not fn.endswith(".json"):
            continue
        data = load_json(os.path.join(examples_dir, fn))
        for key, pattern in id_regexes.items():
            if key in data and data[key] is not None:
                check(f"{fn}: {key} format",
                      re.match(pattern, data[key]) is not None,
                      f"'{data[key]}' vs {pattern}")

    # ---------- 9. Provenance labels ----------
    print("\n[9] Provenance Labels")
    valid_provenance = {
        "verified", "verified_secondary",
        "demo_calibrated", "demo_exaggerated",
        "unverified",
    }

    required_prov_fields = [
        "rainfall_mm", "gauge_level_m", "highest_flood_level_m",
        "warning_level_m",
    ]

    if "data_provenance" in manifest:
        dp = manifest["data_provenance"]
        check("Manifest has data_provenance", True)
        for field, label in dp.items():
            check(f"  {field} provenance = {label} is valid",
                  label in valid_provenance,
                  f"Expected one of {valid_provenance}")
        for rp in required_prov_fields:
            check(f"  Provenance for {rp} present",
                  rp in dp,
                  "Missing from data_provenance")
    else:
        check("Manifest has data_provenance", False, "Missing data_provenance field")

    # Also check verify response example has data_provenance
    verify_path = os.path.join(examples_dir, "post_verify_response_success.json")
    if os.path.exists(verify_path):
        verify_data = load_json(verify_path)
        if "data_provenance" in verify_data:
            vdp = verify_data["data_provenance"]
            check("Verify response has data_provenance", True)
            for rp in required_prov_fields:
                check(f"  Verify response provenance for {rp} present",
                      rp in vdp, "Missing from verify response data_provenance")
            for field, label in vdp.items():
                check(f"  Verify {field} = {label} is valid",
                      label in valid_provenance,
                      f"Expected one of {valid_provenance}")
        else:
            check("Verify response has data_provenance", False,
                  "Missing data_provenance in verify response")

    # ---------- 10. Policy date coverage ----------
    print("\n[10] Policy Date Coverage")
    for p in policies:
        fid = p["farmer_id"]
        farmer_cell = None
        for f in farmers:
            if f["farmer_id"] == fid:
                farmer_cell = f["h3_cell"]
                break

        if farmer_cell in affected_cells:
            if p["status"] == "active":
                check(f"  {p['policy_id']} active, brackets event date",
                      p["start_date"] <= event_date <= p["end_date"],
                      f"start={p['start_date']}, end={p['end_date']}, event={event_date}")
            elif p["status"] == "expired":
                check(f"  {p['policy_id']} expired, end_date before event",
                      p["end_date"] < event_date,
                      f"end={p['end_date']} should be < {event_date}")

    # ---------- 11. Threshold consistency ----------
    print("\n[11] Threshold Consistency with Demo Scenario")
    demo_path = os.path.join(SHARED, "docs", "demo-scenario.md")
    if os.path.exists(demo_path):
        with open(demo_path) as f:
            demo_text = f.read()
        hfl_yaml = thresholds["demo_gauge"]["highest_flood_level_m"]
        check(f"HFL {hfl_yaml} appears in demo-scenario.md",
              str(hfl_yaml) in demo_text,
              f"thresholds.yaml has {hfl_yaml} but not found in demo-scenario.md")
        dl_yaml = thresholds["demo_gauge"]["danger_level_m"]
        check(f"DL {dl_yaml} appears in demo-scenario.md",
              str(dl_yaml) in demo_text,
              f"thresholds.yaml has {dl_yaml} but not found in demo-scenario.md")

    # ---------- 12. Change tracker ----------
    print("\n[12] Change Tracker")
    tracker_path = os.path.join(SHARED, "docs", "contract-change-tracker.md")
    if os.path.exists(tracker_path):
        with open(tracker_path) as f:
            tracker_text = f.read()
        check("Change tracker exists and is non-empty",
              len(tracker_text) > 100)

        # Check that every file path mentioned in backticks exists
        mentioned_files = re.findall(
            r"`((?:config|contracts|docs|sample-data|tools)/[^`]+)`",
            tracker_text)
        for mf in mentioned_files:
            full_path = os.path.join(SHARED, mf)
            exists = os.path.exists(full_path) or os.path.isdir(full_path)
            # Skip directory references ending in /
            if mf.endswith("/"):
                exists = os.path.isdir(full_path.rstrip("/"))
            check(f"  Tracker ref exists: {mf}", exists,
                  f"File not found: {full_path}")
    else:
        check("Change tracker exists", False, "File not found")

    # ---------- 13. Contract-coverage file references ----------
    print("\n[13] Contract-Coverage File References")
    coverage_path = os.path.join(SHARED, "docs", "contract-coverage.md")
    if os.path.exists(coverage_path):
        with open(coverage_path) as f:
            coverage_text = f.read()
        check("Contract-coverage.md exists", True)

        # Extract all .json filenames referenced in backticks
        referenced_files = set(re.findall(r"`([a-z_]+\.json)`", coverage_text))
        for rf in sorted(referenced_files):
            filepath = os.path.join(examples_dir, rf)
            check(f"  Coverage ref exists: {rf}",
                  os.path.exists(filepath),
                  f"Referenced in contract-coverage.md but not found in examples/")

        # Also verify every example file on disk is mentioned
        for fn in sorted(os.listdir(examples_dir)):
            if not fn.endswith(".json"):
                continue
            check(f"  Example {fn} mentioned in coverage",
                  fn in coverage_text,
                  f"File exists but not referenced in contract-coverage.md")
    else:
        check("Contract-coverage.md exists", False, "File not found")

    # ---------- summary ----------
    print("\n" + "=" * 60)
    total = PASS + FAIL
    print(f"Results: {PASS}/{total} passed, {FAIL} failed")
    print("=" * 60)

    return PASS, FAIL


# ============================================================
# SELF-TEST MODE
# ============================================================

def run_self_test():
    """Apply deliberate breakages and verify the validator catches each."""
    print("\n" + "=" * 60)
    print("SELF-TEST MODE: Applying deliberate breakages")
    print("=" * 60)

    original_shared = os.path.join(os.path.dirname(__file__), "..")
    caught = 0
    missed = 0
    total_tests = 0

    def run_mutant(name, mutate_fn):
        nonlocal caught, missed, total_tests
        total_tests += 1
        tmpdir = tempfile.mkdtemp(prefix="geoprotect_selftest_")
        tmp_shared = os.path.join(tmpdir, "shared")
        try:
            shutil.copytree(original_shared, tmp_shared)
            mutate_fn(tmp_shared)
            old_stdout = sys.stdout
            sys.stdout = open(os.devnull, "w")
            try:
                _, fails = run_checks(tmp_shared)
            finally:
                sys.stdout.close()
                sys.stdout = old_stdout
            if fails > 0:
                caught += 1
                print(f"  ✅ CAUGHT: {name} ({fails} failure(s) detected)")
            else:
                missed += 1
                print(f"  ❌ MISSED: {name} (validator passed when it should fail)")
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    # --- Breakage 1: H3 cell at resolution 9 ---
    def break_h3_res9(shared):
        fp = os.path.join(shared, "sample-data", "farmers.csv")
        rows = load_csv(fp)
        rows[0]["h3_cell"] = "893c1ea2e37ffff"  # res 9 cell
        with open(fp, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    run_mutant("H3 cell at resolution 9", break_h3_res9)

    # --- Breakage 2: 13 affected farmers instead of 12 ---
    def break_13_farmers(shared):
        fp = os.path.join(shared, "sample-data", "farmers.csv")
        rows = load_csv(fp)
        rows.append({"farmer_id": "FRM-00ffffff", "h3_cell": "883c1ea2e3fffff",
                      "crop": "rice", "land_area_ha": "1.5"})
        with open(fp, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        pp = os.path.join(shared, "sample-data", "policies.csv")
        prows = load_csv(pp)
        prows.append({"policy_id": "POL-ff999999", "farmer_id": "FRM-00ffffff",
                       "status": "active", "sum_insured": "50000",
                       "start_date": "2020-06-01", "end_date": "2020-11-30"})
        with open(pp, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(prows[0].keys()))
            writer.writeheader()
            writer.writerows(prows)
    run_mutant("13 affected farmers instead of 12", break_13_farmers)

    # --- Breakage 3: Payout arithmetic off by 1 rupee ---
    def break_payout(shared):
        fp = os.path.join(shared, "sample-data", "scenario_manifest.json")
        m = load_json(fp)
        m["total_payout_inr"] = m["total_payout_inr"] + 1
        with open(fp, "w") as f:
            json.dump(m, f, indent=2)
    run_mutant("Total payout arithmetic off by 1 rupee", break_payout)

    # --- Breakage 4: Enum value not in vocabulary ---
    def break_bad_enum(shared):
        fp = os.path.join(shared, "contracts", "examples",
                          "post_event_response_success.json")
        d = load_json(fp)
        d["stage"] = "nonexistent_stage"
        with open(fp, "w") as f:
            json.dump(d, f, indent=2)
    run_mutant("Enum value not in vocabulary.md", break_bad_enum)

    # --- Breakage 5: Malformed farmer_id ---
    def break_farmer_id(shared):
        fp = os.path.join(shared, "sample-data", "farmers.csv")
        rows = load_csv(fp)
        rows[0]["farmer_id"] = "FARMER-INVALID"
        with open(fp, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    run_mutant("Malformed farmer_id", break_farmer_id)

    # --- Breakage 6: Latitude/longitude in CSV ---
    def break_add_coords(shared):
        fp = os.path.join(shared, "sample-data", "farmers.csv")
        with open(fp, "a") as f:
            f.write('\nFRM-00aabbcc,883c1ea2e3fffff,rice,1.5,"lat": 26.12')
    run_mutant("Latitude/longitude pair in CSV", break_add_coords)

    # --- Breakage 7: Phone number in doc ---
    def break_add_phone(shared):
        fp = os.path.join(shared, "docs", "demo-scenario.md")
        with open(fp, "a") as f:
            f.write("\nContact: 9876543210\n")
    run_mutant("Phone number in doc", break_add_phone)

    # --- Breakage 8: Threshold HFL mismatch ---
    def break_hfl_mismatch(shared):
        fp = os.path.join(shared, "config", "thresholds.yaml")
        t = load_yaml(fp)
        t["demo_gauge"]["highest_flood_level_m"] = 50.00
        with open(fp, "w") as f:
            yaml.dump(t, f)
    run_mutant("Threshold HFL disagrees with demo-scenario.md", break_hfl_mismatch)

    # --- Breakage 9: Active policy end_date before event ---
    def break_policy_dates(shared):
        fp = os.path.join(shared, "sample-data", "policies.csv")
        rows = load_csv(fp)
        for r in rows:
            if r["status"] == "active" and r["farmer_id"] == "FRM-00a1b2c3":
                r["end_date"] = "2020-07-01"
                break
        with open(fp, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    run_mutant("Active policy end_date before event date", break_policy_dates)

    # --- Breakage 10: Missing provenance in manifest ---
    def break_provenance(shared):
        fp = os.path.join(shared, "sample-data", "scenario_manifest.json")
        m = load_json(fp)
        del m["data_provenance"]
        with open(fp, "w") as f:
            json.dump(m, f, indent=2)
    run_mutant("Missing data_provenance in manifest", break_provenance)

    # --- Breakage 11: Delete a failure example referenced by coverage ---
    def break_delete_example(shared):
        fp = os.path.join(shared, "contracts", "examples",
                          "post_verify_response_failure.json")
        os.remove(fp)
    run_mutant("Delete failure example referenced by coverage", break_delete_example)

    # --- Breakage 12: Example fails JSON Schema validation ---
    def break_schema_violation(shared):
        fp = os.path.join(shared, "contracts", "examples",
                          "post_claim_response_success.json")
        d = load_json(fp)
        d["success"] = False  # should be True per schema
        with open(fp, "w") as f:
            json.dump(d, f, indent=2)
    run_mutant("Example fails contract JSON Schema", break_schema_violation)

    # --- Breakage 13: Invalid provenance label ---
    def break_bad_provenance(shared):
        fp = os.path.join(shared, "sample-data", "scenario_manifest.json")
        m = load_json(fp)
        m["data_provenance"]["rainfall_mm"] = "made_up_label"
        with open(fp, "w") as f:
            json.dump(m, f, indent=2)
    run_mutant("Invalid provenance label in manifest", break_bad_provenance)

    # --- Breakage 14: Tracker references non-existent file ---
    def break_tracker_ref(shared):
        fp = os.path.join(shared, "docs", "contract-change-tracker.md")
        with open(fp) as f:
            text = f.read()
        text += "\n| CHG-999 | 2026-10-02 | Test | Added `config/nonexistent.yaml` | `config/nonexistent.yaml` | ☐ | ☐ | ☐ | ☐ |\n"
        with open(fp, "w") as f:
            f.write(text)
    run_mutant("Tracker references non-existent file", break_tracker_ref)

    # --- Summary ---
    print(f"\n{'=' * 60}")
    print(f"Self-test results: {caught}/{total_tests} breakages caught, "
          f"{missed} missed")
    print(f"{'=' * 60}")

    return missed


def main():
    if "--self-test" in sys.argv:
        shared_dir = os.path.join(os.path.dirname(__file__), "..")
        p, f = run_checks(shared_dir)
        missed = run_self_test()
        return 0 if (f == 0 and missed == 0) else 1
    else:
        shared_dir = os.path.join(os.path.dirname(__file__), "..")
        _, f = run_checks(shared_dir)
        return 0 if f == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
