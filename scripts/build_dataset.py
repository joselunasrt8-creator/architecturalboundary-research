#!/usr/bin/env python3
"""Build and check the canonical B2 comparative dataset.

The dataset is a deterministic projection of the complete B2 MSR cohort.  It
contains only registered I4 measurement values plus repository-bounded lineage.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVESTIGATION_ID = "b2-governance-cohort"
PROTOCOL_VERSION = "protocol-v1"
DATASET_ID = "dataset-b2-governance-cohort-i4"
SCHEMA_VERSION = "canonical-dataset-v1"
COHORT_SIZE = 9
MEASUREMENTS = ("m_R", "m_L", "m_E", "m_RL", "m_LE")
REGISTRY_REF = "investigations/b2-governance-cohort/preregistration/i1_i5_registration.json#/measurement_vector/I4"
MSR_DIR = ROOT / "investigations" / INVESTIGATION_ID / "msr"
OUTPUT_PATH = ROOT / "investigations" / INVESTIGATION_ID / "dataset" / "b2-governance-cohort-i4.dataset.json"
SCHEMA_PATH = ROOT / "schemas" / "dataset.schema.json"

try:
    from jsonschema import Draft202012Validator
except ModuleNotFoundError:  # pragma: no cover - restricted local environments only
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


def load_validated_msr(path: Path) -> dict[str, object]:
    msr = load_json(path)
    validate_with_schema(msr, ROOT / "schemas" / "msr.schema.json", str(path.relative_to(ROOT)))
    if msr.get("object_type") != "MeasurementStudyRecord":
        raise SystemExit(f"not an MSR: {path.relative_to(ROOT)}")
    if msr.get("investigation_id") != INVESTIGATION_ID:
        raise SystemExit(f"MSR from unexpected investigation: {path.relative_to(ROOT)}")
    if msr.get("protocol_version") != PROTOCOL_VERSION:
        raise SystemExit(f"MSR protocol mismatch: {path.relative_to(ROOT)}")
    if msr.get("status") != "reference_execution":
        raise SystemExit(f"MSR is not canonical reference execution: {path.relative_to(ROOT)}")
    registry = msr.get("measurement_registry_ref")
    if not isinstance(registry, dict) or registry.get("measurement_vector_id") != "I4":
        raise SystemExit(f"MSR does not reference I4: {path.relative_to(ROOT)}")
    return msr


def project_row(msr: dict[str, object], path: Path) -> dict[str, object]:
    measurements = msr.get("measurements")
    if not isinstance(measurements, list):
        raise SystemExit(f"MSR measurements must be a list: {path.relative_to(ROOT)}")
    values: dict[str, object] = {}
    for entry in measurements:
        if not isinstance(entry, dict):
            raise SystemExit(f"MSR measurement must be an object: {path.relative_to(ROOT)}")
        mid = entry.get("measurement_id")
        if mid not in MEASUREMENTS:
            raise SystemExit(f"unknown measurement in {path.relative_to(ROOT)}: {mid}")
        if mid in values:
            raise SystemExit(f"duplicate measurement in {path.relative_to(ROOT)}: {mid}")
        values[str(mid)] = entry.get("value")
    if set(values) != set(MEASUREMENTS):
        raise SystemExit(f"MSR measurement set mismatch: {path.relative_to(ROOT)}")

    return {
        "system_id": msr["system_id"],
        "msr_id": msr["id"],
        **{name: values[name] for name in MEASUREMENTS},
        "lineage": {
            "msr_path": str(path.relative_to(ROOT)),
            "source_der_ids": msr["source_der_ids"],
            "measurement_registry_ref": REGISTRY_REF,
        },
    }


def build_dataset() -> dict[str, object]:
    paths = sorted(MSR_DIR.glob("*.msr.json"))
    if len(paths) != COHORT_SIZE:
        raise SystemExit(f"expected exactly {COHORT_SIZE} B2 MSRs, found {len(paths)}")

    rows: list[dict[str, object]] = []
    systems: dict[str, Path] = {}
    for path in paths:
        msr = load_validated_msr(path)
        system_id = msr.get("system_id")
        if not isinstance(system_id, str) or not system_id:
            raise SystemExit(f"MSR missing system_id: {path.relative_to(ROOT)}")
        if system_id in systems:
            first = systems[system_id].relative_to(ROOT)
            second = path.relative_to(ROOT)
            raise SystemExit(f"more than one canonical MSR exists for system {system_id}: {first}, {second}")
        systems[system_id] = path
        rows.append(project_row(msr, path))

    rows.sort(key=lambda row: str(row["system_id"]))
    source_msr_ids = [str(row["msr_id"]) for row in rows]
    msr_paths = [str(row["lineage"]["msr_path"]) for row in rows]  # type: ignore[index]
    created_from = [REGISTRY_REF.split("#", 1)[0], *msr_paths]
    return {
        "object_type": "ComparativeDataset",
        "schema_version": SCHEMA_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "investigation_id": INVESTIGATION_ID,
        "id": DATASET_ID,
        "measurement_vector_ref": REGISTRY_REF,
        "cohort_size": COHORT_SIZE,
        "row_ordering": "system_id ascending",
        "source_msr_ids": source_msr_ids,
        "rows": rows,
        "provenance": {
            "method": "MSR -> deterministic comparative projection",
            "created_from": created_from,
        },
        "generation": {
            "builder": "scripts/build_dataset.py",
            "mode": "deterministic-rebuild",
            "repository_root": ".",
        },
    }


def stable_bytes(data: dict[str, object]) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=False) + "\n").encode("utf-8")


def check_committed(expected: dict[str, object]) -> None:
    if not OUTPUT_PATH.exists():
        raise SystemExit(f"missing canonical dataset: {OUTPUT_PATH.relative_to(ROOT)}")
    committed_bytes = OUTPUT_PATH.read_bytes()
    try:
        committed = json.loads(committed_bytes)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"committed dataset is not valid JSON: {exc}") from exc
    if not isinstance(committed, dict):
        raise SystemExit("committed dataset must be a JSON object")
    validate_with_schema(committed, SCHEMA_PATH, str(OUTPUT_PATH.relative_to(ROOT)))
    if committed != expected:
        raise SystemExit("committed dataset structure differs from deterministic MSR projection")
    if committed_bytes != stable_bytes(expected):
        raise SystemExit("committed dataset bytes differ from deterministic rebuild")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate committed dataset freshness without writing")
    args = parser.parse_args()

    dataset = build_dataset()
    validate_with_schema(dataset, SCHEMA_PATH, "deterministic B2 dataset")
    if args.check:
        check_committed(dataset)
        print(f"canonical dataset fresh: {OUTPUT_PATH.relative_to(ROOT)}")
        return
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_bytes(stable_bytes(dataset))
    print(f"wrote {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
