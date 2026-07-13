#!/usr/bin/env python3
"""Deterministically validate registry contracts and registered paths."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry"
REQUIRED = {
    "architectural_boundaries.json": "architectural_boundaries",
    "investigations.json": "investigations",
    "terminology.json": "terminology",
    "classifications.json": "classifications",
    "protocol_versions.json": "protocol_versions",
    "retained_classifications.json": "retained_classifications",
    "cohort_conclusions.json": "cohort_conclusions",
    "candidate_invariants.json": "candidate_invariants",
}
B2 = "b2-governance-cohort"
B2_PROTOCOL = "protocol-v1"
RETAINED_TYPE = "CanonicalRetainedClassification"
COHORT_TYPE = "CanonicalCohortConclusion"
RESULTS_DIR = Path("investigations/b2-governance-cohort/results")
DECISION_RULE = "investigations/b2-governance-cohort/preregistration/i1_i5_registration.json#/deterministic_decision_rule/I5"
COHORT_RULE = f"{DECISION_RULE}/cohort_outcome"
PRECEDENCE = ["indeterminate", "violates", "supports"]


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def fail(message: str) -> None:
    raise SystemExit(message)


def require_path(relative: str, source: str) -> Path:
    path = ROOT / relative
    if not path.exists():
        fail(f"{source} references missing path: {relative}")
    return path


def require_json_pointer(ref: str, source: str) -> None:
    relative = ref.split("#", 1)[0]
    require_path(relative, source)


def require_object(data: Any, source: str) -> dict[str, Any]:
    if not isinstance(data, dict):
        fail(f"{source} must be a JSON object")
    return data


def validate_b2_i1_i5_registration() -> None:
    relative = "investigations/b2-governance-cohort/preregistration/i1_i5_registration.json"
    path = ROOT / relative
    if not path.exists():
        fail(f"missing B2 I1-I5 registration object: {relative}")
    data = require_object(load_json(path), relative)
    required_fields = ["investigation_id", "protocol_version", "candidate_invariant", "admitted_evidence_rule", "cohort_rule", "measurement_vector", "deterministic_decision_rule", "registration_status", "unresolved_fields", "provenance_references"]
    for field in required_fields:
        if field not in data:
            fail(f"{relative} missing required field: {field}")
    if data["investigation_id"] != B2:
        fail(f"{relative} has invalid investigation_id: {data['investigation_id']}")
    protocol_version = data["protocol_version"]
    versions_data = load_json(REGISTRY / "protocol_versions.json")
    versions = versions_data.get("protocol_versions", []) if isinstance(versions_data, dict) else []
    if protocol_version not in {item.get("id") for item in versions if isinstance(item, dict)}:
        fail(f"{relative} has invalid protocol_version: {protocol_version}")
    decision_rule = data["deterministic_decision_rule"]
    if not isinstance(decision_rule, dict) or decision_rule.get("deterministic") is not True:
        fail(f"{relative} must declare a deterministic decision rule")
    for field in ["per_system_classification", "cohort_outcome", "precedence"]:
        if not decision_rule.get(field):
            fail(f"{relative} deterministic decision rule missing: {field}")
    unresolved = data["unresolved_fields"]
    if not isinstance(unresolved, list):
        fail(f"{relative} unresolved_fields must be a list")
    for item in unresolved:
        if not isinstance(item, dict) or item.get("value") != "UNRESOLVED" or not item.get("field") or not item.get("reason"):
            fail(f"{relative} unresolved field entries require field, reason, and explicit UNRESOLVED value")
    provenance = data["provenance_references"]
    if not isinstance(provenance, list) or not provenance:
        fail(f"{relative} provenance_references must be a non-empty list")
    for reference in provenance:
        if not isinstance(reference, str) or not reference:
            fail(f"{relative} provenance references must be non-empty strings")
        require_path(reference, relative)


def validate_retained_registry(entries: list[Any]) -> dict[str, dict[str, Any]]:
    seen_ids: Counter[str] = Counter()
    retained: dict[str, dict[str, Any]] = {}
    registered_paths: set[str] = set()
    for index, entry in enumerate(entries):
        source = f"registry/retained_classifications.json[{index}]"
        if not isinstance(entry, dict): fail(f"{source} must be an object")
        path_rel = str(entry.get("artifact_path", "")); registered_paths.add(path_rel)
        path = require_path(path_rel, source)
        artifact = require_object(load_json(path), path_rel)
        if artifact.get("object_type") != RETAINED_TYPE: fail(f"{path_rel} object_type mismatch: {artifact.get('object_type')}")
        rid = artifact.get("id")
        if not rid: fail(f"{path_rel} missing id")
        seen_ids[str(rid)] += 1
        if entry.get("retained_classification_id") and entry.get("retained_classification_id") != rid: fail(f"{source} retained_classification_id does not match artifact id")
        if entry.get("investigation_id") != artifact.get("investigation_id"): fail(f"{path_rel} investigation_id mismatch with registry")
        if artifact.get("investigation_id") != B2: fail(f"{path_rel} has unexpected investigation_id: {artifact.get('investigation_id')}")
        if entry.get("protocol_version") and entry.get("protocol_version") != artifact.get("protocol_version"): fail(f"{path_rel} protocol_version mismatch with registry")
        if artifact.get("protocol_version") != B2_PROTOCOL: fail(f"{path_rel} has unexpected protocol_version: {artifact.get('protocol_version')}")
        for key in ["input_dataset_ref", "input_analysis_ref", "decision_rule_ref"]:
            if not artifact.get(key): fail(f"{path_rel} missing {key}")
            require_json_pointer(str(artifact[key]), path_rel)
        if entry.get("decision_rule_ref") != artifact.get("decision_rule_ref"): fail(f"{path_rel} decision_rule_ref mismatch with registry")
        retained[str(rid)] = artifact
    duplicates = [rid for rid, count in seen_ids.items() if count > 1]
    if duplicates: fail(f"duplicate retained-classification IDs: {', '.join(sorted(duplicates))}")
    for path in sorted((ROOT / RESULTS_DIR).glob("*.retained-classification.json")):
        rel = str(path.relative_to(ROOT))
        if rel not in registered_paths: fail(f"orphaned canonical B2 result artifact: {rel}")
    return retained


def expected_outcome(classifications: list[dict[str, Any]]) -> tuple[str, list[str]]:
    by_class = {name: sorted(row["system_id"] for row in classifications if row.get("classification") == name) for name in PRECEDENCE}
    for name in PRECEDENCE:
        if by_class[name]: return name, by_class[name]
    fail("retained classification has no per-system classifications")


def validate_cohort_registry(entries: list[Any], retained: dict[str, dict[str, Any]]) -> None:
    seen_ids: Counter[str] = Counter(); registered_paths: set[str] = set()
    for index, entry in enumerate(entries):
        source = f"registry/cohort_conclusions.json[{index}]"
        if not isinstance(entry, dict): fail(f"{source} must be an object")
        path_rel = str(entry.get("artifact_path", "")); registered_paths.add(path_rel)
        path = require_path(path_rel, source)
        artifact = require_object(load_json(path), path_rel)
        if artifact.get("object_type") != COHORT_TYPE: fail(f"{path_rel} object_type mismatch: {artifact.get('object_type')}")
        cid = artifact.get("cohort_conclusion_id")
        if not cid: fail(f"{path_rel} missing cohort_conclusion_id")
        seen_ids[str(cid)] += 1
        if entry.get("cohort_conclusion_id") and entry.get("cohort_conclusion_id") != cid: fail(f"{source} cohort_conclusion_id does not match artifact")
        if entry.get("investigation_id") != artifact.get("investigation_id") or artifact.get("investigation_id") != B2: fail(f"{path_rel} investigation_id mismatch")
        if entry.get("protocol_version") and entry.get("protocol_version") != artifact.get("protocol_version"): fail(f"{path_rel} protocol_version mismatch with registry")
        if artifact.get("protocol_version") != B2_PROTOCOL: fail(f"{path_rel} has unexpected protocol_version: {artifact.get('protocol_version')}")
        refs = artifact.get("source_retained_classification_refs")
        ids = artifact.get("source_retained_classification_ids")
        if not isinstance(refs, list) or not refs: fail(f"{path_rel} missing source_retained_classification_refs")
        if not isinstance(ids, list) or not ids: fail(f"{path_rel} missing source_retained_classification_ids")
        for ref in refs: require_path(str(ref), path_rel)
        for rid in ids:
            if rid not in retained: fail(f"{path_rel} broken retained-classification reference: {rid}")
        if entry.get("source_retained_classification") and entry["source_retained_classification"] not in refs: fail(f"{path_rel} registry source_retained_classification not listed in artifact refs")
        src = retained[str(ids[0])]
        rows = src.get("per_system_classifications", [])
        if artifact.get("cohort_size") != len(rows) or artifact.get("cohort_size") != src.get("cohort_size"): fail(f"{path_rel} cohort_size mismatch")
        outcome, basis = expected_outcome(rows)
        det = artifact.get("deterministic_conclusion", {})
        if det.get("outcome") != outcome: fail(f"{path_rel} incorrect cohort outcome relative to I5 precedence")
        if sorted(det.get("basis_system_ids", [])) != basis: fail(f"{path_rel} incorrect basis_system_ids")
        if artifact.get("protocol_decision_rule_ref") != COHORT_RULE: fail(f"{path_rel} protocol_decision_rule_ref mismatch")
        require_json_pointer(str(artifact.get("protocol_decision_rule_ref", "")), path_rel)
    duplicates = [cid for cid, count in seen_ids.items() if count > 1]
    if duplicates: fail(f"duplicate cohort-conclusion IDs: {', '.join(sorted(duplicates))}")
    for path in sorted((ROOT / RESULTS_DIR).glob("*.cohort-conclusion.json")):
        rel = str(path.relative_to(ROOT))
        if rel not in registered_paths: fail(f"orphaned canonical B2 result artifact: {rel}")


def main() -> None:
    loaded: dict[str, Any] = {}
    for filename, key in REQUIRED.items():
        path = REGISTRY / filename
        if not path.exists(): fail(f"missing registry contract: registry/{filename}")
        data = load_json(path)
        if not isinstance(data, dict) or key not in data: fail(f"registry/{filename} missing top-level key: {key}")
        loaded[filename] = data
    for item in loaded["investigations.json"]["investigations"]:
        if not isinstance(item, dict): fail("investigation registry entries must be objects")
        require_path(str(item.get("path", "")), "registry/investigations.json")
    for item in loaded["protocol_versions.json"]["protocol_versions"]:
        if not isinstance(item, dict): fail("protocol registry entries must be objects")
        require_path(str(item.get("path", "")), "registry/protocol_versions.json")
    terminology = loaded["terminology.json"]
    if isinstance(terminology, dict) and terminology.get("authority"):
        require_path(str(terminology["authority"]), "registry/terminology.json")
    validate_b2_i1_i5_registration()
    retained = validate_retained_registry(loaded["retained_classifications.json"]["retained_classifications"])
    validate_cohort_registry(loaded["cohort_conclusions.json"]["cohort_conclusions"], retained)
    print("registry validation passed")

if __name__ == "__main__":
    main()
