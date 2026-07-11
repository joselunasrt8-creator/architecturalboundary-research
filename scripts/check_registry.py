#!/usr/bin/env python3
"""Deterministically validate registry contracts and registered paths."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry"
REQUIRED = {
    "architectural_boundaries.json": "architectural_boundaries",
    "investigations.json": "investigations",
    "terminology.json": "terminology",
    "classifications.json": "classifications",
    "protocol_versions.json": "protocol_versions",
    "retained_classifications.json": "retained_classifications",
    "candidate_invariants.json": "candidate_invariants",
}


def load_json(path: Path) -> object:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def require_path(relative: str, source: str) -> None:
    if not (ROOT / relative).exists():
        raise SystemExit(f"{source} references missing path: {relative}")


def validate_b2_i1_i5_registration() -> None:
    relative = "investigations/b2-governance-cohort/preregistration/i1_i5_registration.json"
    path = ROOT / relative
    if not path.exists():
        raise SystemExit(f"missing B2 I1-I5 registration object: {relative}")
    data = load_json(path)
    if not isinstance(data, dict):
        raise SystemExit(f"{relative} must be a JSON object")

    required_fields = [
        "investigation_id",
        "protocol_version",
        "candidate_invariant",
        "admitted_evidence_rule",
        "cohort_rule",
        "measurement_vector",
        "deterministic_decision_rule",
        "registration_status",
        "unresolved_fields",
        "provenance_references",
    ]
    for field in required_fields:
        if field not in data:
            raise SystemExit(f"{relative} missing required field: {field}")

    if data["investigation_id"] != "b2-governance-cohort":
        raise SystemExit(f"{relative} has invalid investigation_id: {data['investigation_id']}")

    protocol_version = data["protocol_version"]
    versions_data = load_json(REGISTRY / "protocol_versions.json")
    versions = versions_data.get("protocol_versions", []) if isinstance(versions_data, dict) else []
    valid_versions = {item.get("id") for item in versions if isinstance(item, dict)}
    if protocol_version not in valid_versions:
        raise SystemExit(f"{relative} has invalid protocol_version: {protocol_version}")

    decision_rule = data["deterministic_decision_rule"]
    if not isinstance(decision_rule, dict) or decision_rule.get("deterministic") is not True:
        raise SystemExit(f"{relative} must declare a deterministic decision rule")
    for field in ["per_system_classification", "cohort_outcome", "precedence"]:
        if not decision_rule.get(field):
            raise SystemExit(f"{relative} deterministic decision rule missing: {field}")

    unresolved = data["unresolved_fields"]
    if not isinstance(unresolved, list):
        raise SystemExit(f"{relative} unresolved_fields must be a list")
    for item in unresolved:
        if not isinstance(item, dict):
            raise SystemExit(f"{relative} unresolved field entries must be objects")
        if item.get("value") != "UNRESOLVED":
            raise SystemExit(f"{relative} unresolved field lacks explicit UNRESOLVED value")
        if not item.get("field") or not item.get("reason"):
            raise SystemExit(f"{relative} unresolved field entries require field and reason")

    provenance = data["provenance_references"]
    if not isinstance(provenance, list) or not provenance:
        raise SystemExit(f"{relative} provenance_references must be a non-empty list")
    for reference in provenance:
        if not isinstance(reference, str) or not reference:
            raise SystemExit(f"{relative} provenance references must be non-empty strings")
        require_path(reference, relative)


def main() -> None:
    loaded: dict[str, object] = {}
    for filename, key in REQUIRED.items():
        path = REGISTRY / filename
        if not path.exists():
            raise SystemExit(f"missing registry contract: registry/{filename}")
        data = load_json(path)
        if not isinstance(data, dict) or key not in data:
            raise SystemExit(f"registry/{filename} missing top-level key: {key}")
        loaded[filename] = data

    investigations = loaded["investigations.json"]["investigations"]  # type: ignore[index]
    if not isinstance(investigations, list):
        raise SystemExit("registry/investigations.json investigations must be a list")
    for item in investigations:
        if not isinstance(item, dict):
            raise SystemExit("investigation registry entries must be objects")
        require_path(str(item.get("path", "")), "registry/investigations.json")

    versions = loaded["protocol_versions.json"]["protocol_versions"]  # type: ignore[index]
    if not isinstance(versions, list):
        raise SystemExit("registry/protocol_versions.json protocol_versions must be a list")
    for item in versions:
        if not isinstance(item, dict):
            raise SystemExit("protocol registry entries must be objects")
        require_path(str(item.get("path", "")), "registry/protocol_versions.json")

    terminology = loaded["terminology.json"]
    if isinstance(terminology, dict) and terminology.get("authority"):
        require_path(str(terminology["authority"]), "registry/terminology.json")

    validate_b2_i1_i5_registration()

    print("registry validation passed")


if __name__ == "__main__":
    main()
