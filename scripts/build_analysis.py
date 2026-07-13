#!/usr/bin/env python3
"""Build and check the canonical B2 Analysis artifact.

This stage consumes only the canonical B2 comparative dataset and produces a
measurement-distribution analysis.  It intentionally does not apply retained
classification or cohort-conclusion outputs.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVESTIGATION_ID = "b2-governance-cohort"
PROTOCOL_VERSION = "protocol-v1"
ANALYSIS_ID = "analysis-b2-governance-cohort-i4-measurement-distribution"
SCHEMA_VERSION = "canonical-analysis-v1"
MEASUREMENTS = ("m_R", "m_L", "m_E", "m_RL", "m_LE")
DATASET_PATH = ROOT / "investigations" / INVESTIGATION_ID / "dataset" / "b2-governance-cohort-i4.dataset.json"
OUTPUT_PATH = ROOT / "investigations" / INVESTIGATION_ID / "analysis" / "b2-governance-cohort-i4.analysis.json"
SCHEMA_PATH = ROOT / "schemas" / "analysis.schema.json"
DATASET_SCHEMA_PATH = ROOT / "schemas" / "dataset.schema.json"

try:
    from jsonschema import Draft202012Validator
except ModuleNotFoundError:  # pragma: no cover
    sys.path.insert(0, str(ROOT))
    from tools.jsonschema_fallback import Draft202012Validator


def load_json(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise SystemExit(f"JSON object required: {path.relative_to(ROOT)}")
    return data


def validate_with_schema(data: dict[str, object], schema_path: Path, label: str) -> None:
    schema = load_json(schema_path)
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda error: list(error.path))
    if errors:
        detail = "; ".join(error.message for error in errors)
        raise SystemExit(f"{label} schema validation failed: {detail}")


def load_validated_dataset() -> dict[str, object]:
    dataset = load_json(DATASET_PATH)
    validate_with_schema(dataset, DATASET_SCHEMA_PATH, str(DATASET_PATH.relative_to(ROOT)))
    if dataset.get("object_type") != "ComparativeDataset":
        raise SystemExit("analysis input is not a ComparativeDataset")
    if dataset.get("investigation_id") != INVESTIGATION_ID or dataset.get("protocol_version") != PROTOCOL_VERSION:
        raise SystemExit("analysis input dataset identity does not match B2 protocol-v1")
    if dataset.get("row_ordering") != "system_id ascending":
        raise SystemExit("analysis input dataset row ordering is not canonical")
    return dataset


def verify_dataset(dataset: dict[str, object]) -> dict[str, object]:
    rows = dataset.get("rows")
    if not isinstance(rows, list):
        raise SystemExit("analysis input dataset rows must be a list")
    source_msr_ids = dataset.get("source_msr_ids")
    if not isinstance(source_msr_ids, list):
        raise SystemExit("analysis input dataset source_msr_ids must be a list")
    system_ids = [row.get("system_id") for row in rows if isinstance(row, dict)]
    msr_ids = [row.get("msr_id") for row in rows if isinstance(row, dict)]
    if len(system_ids) != len(rows) or len(msr_ids) != len(rows):
        raise SystemExit("analysis input dataset rows must be objects with system_id and msr_id")
    allowed_row_keys = {"system_id", "msr_id", *MEASUREMENTS, "lineage"}
    for row in rows:
        if not isinstance(row, dict):
            raise SystemExit("analysis input dataset row must be an object")
        extra = sorted(set(row) - allowed_row_keys)
        if extra:
            raise SystemExit(f"analysis input dataset row contains non-comparative field(s): {', '.join(extra)}")
        for measurement in MEASUREMENTS:
            if row.get(measurement) not in (0, 1, None):
                raise SystemExit(f"analysis input dataset has invalid measurement value for {measurement}")
    return {
        "object_type": dataset["object_type"],
        "schema_version": dataset["schema_version"],
        "cohort_size_matches_rows": dataset.get("cohort_size") == len(rows),
        "row_ordering_verified": system_ids == sorted(system_ids),
        "source_msr_ids_match_rows": source_msr_ids == msr_ids,
        "only_registered_measurement_fields": True,
    }


def build_analysis() -> dict[str, object]:
    dataset = load_validated_dataset()
    verification = verify_dataset(dataset)
    if not all(value is True for key, value in verification.items() if key.endswith(("rows", "verified", "fields")) or key == "source_msr_ids_match_rows"):
        raise SystemExit("analysis input dataset verification failed")
    rows = dataset["rows"]
    assert isinstance(rows, list)
    distributions = {measurement: {"observed_1": 0, "observed_0": 0, "missing": 0} for measurement in MEASUREMENTS}
    matrix = []
    for row in rows:
        assert isinstance(row, dict)
        measurements = {measurement: row[measurement] for measurement in MEASUREMENTS}
        for measurement, value in measurements.items():
            if value == 1:
                distributions[measurement]["observed_1"] += 1
            elif value == 0:
                distributions[measurement]["observed_0"] += 1
            else:
                distributions[measurement]["missing"] += 1
        matrix.append({
            "system_id": row["system_id"],
            "msr_id": row["msr_id"],
            "measurements": measurements,
            "lineage": row["lineage"],
        })
    return {
        "object_type": "CanonicalAnalysis",
        "schema_version": SCHEMA_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "investigation_id": INVESTIGATION_ID,
        "id": ANALYSIS_ID,
        "analysis_stage": "B2 Analysis",
        "input_dataset_ref": str(DATASET_PATH.relative_to(ROOT)),
        "measurement_vector_ref": dataset["measurement_vector_ref"],
        "cohort_size": dataset["cohort_size"],
        "row_ordering": dataset["row_ordering"],
        "measurement_fields": list(MEASUREMENTS),
        "dataset_verification": verification,
        "measurement_distributions": distributions,
        "system_measurement_matrix": matrix,
        "deferred_outputs": ["retained_classification", "cohort_conclusion"],
        "provenance": {
            "method": "ComparativeDataset -> deterministic measurement distribution analysis",
            "created_from": [str(DATASET_PATH.relative_to(ROOT))],
        },
        "generation": {
            "builder": "scripts/build_analysis.py",
            "mode": "deterministic-rebuild",
            "repository_root": ".",
        },
    }


def stable_bytes(data: dict[str, object]) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=False) + "\n").encode("utf-8")


def check_committed(expected: dict[str, object]) -> None:
    if not OUTPUT_PATH.exists():
        raise SystemExit(f"missing canonical analysis: {OUTPUT_PATH.relative_to(ROOT)}")
    committed_bytes = OUTPUT_PATH.read_bytes()
    committed = json.loads(committed_bytes)
    if not isinstance(committed, dict):
        raise SystemExit("committed analysis must be a JSON object")
    validate_with_schema(committed, SCHEMA_PATH, str(OUTPUT_PATH.relative_to(ROOT)))
    if committed != expected:
        raise SystemExit("committed analysis structure differs from deterministic dataset analysis")
    if committed_bytes != stable_bytes(expected):
        raise SystemExit("committed analysis bytes differ from deterministic rebuild")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate committed analysis freshness without writing")
    args = parser.parse_args()
    analysis = build_analysis()
    validate_with_schema(analysis, SCHEMA_PATH, "deterministic B2 analysis")
    if args.check:
        check_committed(analysis)
        print(f"canonical analysis fresh: {OUTPUT_PATH.relative_to(ROOT)}")
        return
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_bytes(stable_bytes(analysis))
    print(f"wrote {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
