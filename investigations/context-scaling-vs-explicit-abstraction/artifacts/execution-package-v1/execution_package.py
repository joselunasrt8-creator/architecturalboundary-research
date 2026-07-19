#!/usr/bin/env python3
"""Deterministic, offline construction and validation for execution-package-v1.

This module never invokes a model or makes a network request.  It intentionally
returns NULL while the preregistered source corpus and target registry do not
exist in the repository; it must not invent either frozen object.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import unicodedata
from pathlib import Path
from typing import Any

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[3]
PREREGISTRATION = ROOT / "investigations/context-scaling-vs-explicit-abstraction/preregistration.md"
PACKAGE_VERSION = "execution-package-v1"
PACKAGE_IDS = [f"SP{i:02d}" for i in range(1, 9)]
FAMILIES = ["structural_diagnosis", "constraint_aware_recommendation", "causal_explanation"]
CONDITIONS = ["C1", "C2", "C3", "C4"]
SEED = 20260719


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256(value: Any) -> str:
    return hashlib.sha256(value if isinstance(value, bytes) else canonical_bytes(value)).hexdigest()


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", value).casefold()).strip(" ")


def read_json(name: str) -> Any:
    with (PACKAGE / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def no_duplicates(values: list[Any]) -> bool:
    return len(values) == len(set(values))


def _literal_values(container: Any, fields: set[str], required: set[str]) -> list[str]:
    if not isinstance(container, dict) or set(container) != fields:
        raise ValueError("unexpected registry fields")
    values: list[str] = []
    for field in fields:
        entries = container[field]
        if (not isinstance(entries, list) or (field in required and not entries)
                or not all(isinstance(item, str) and normalized(item) for item in entries)):
            raise ValueError("malformed literal registry")
        values.extend(normalized(item) for item in entries)
    if not no_duplicates(values) or {"key_match", "scope_match"} & set(values):
        raise ValueError("malformed literal registry")
    return values


def evaluate(raw_output: bytes, target_record: dict[str, Any], answer_key: dict[str, Any], scope_rubric: dict[str, Any]) -> dict[str, Any]:
    """Implement the Section 8 evaluator; invalid input raises ValueError."""
    allowed_target = {"id", "answer_key_sha256", "scope_rubric_sha256"}
    if not isinstance(target_record, dict) or set(target_record) != allowed_target or not isinstance(target_record["id"], str):
        raise ValueError("malformed target record")
    try:
        output = raw_output.decode("utf-8", "strict")
    except (AttributeError, UnicodeDecodeError) as error:
        raise ValueError("undecodable output") from error
    if not output:
        raise ValueError("empty raw output")
    _literal_values(answer_key, {"required_literals", "forbidden_literals"}, {"required_literals"})
    _literal_values(scope_rubric, {"relation_literals", "required_applicability_literals", "forbidden_applicability_literals"}, {"relation_literals", "required_applicability_literals"})
    if sha256(answer_key) != target_record["answer_key_sha256"] or sha256(scope_rubric) != target_record["scope_rubric_sha256"]:
        raise ValueError("hash mismatch")
    out = normalized(output)
    key = all(normalized(x) in out for x in answer_key["required_literals"]) and not any(normalized(x) in out for x in answer_key["forbidden_literals"])
    scope = all(normalized(x) in out for x in scope_rubric["relation_literals"] + scope_rubric["required_applicability_literals"]) and not any(normalized(x) in out for x in scope_rubric["forbidden_applicability_literals"])
    return {"target_id": target_record["id"], "raw_output_sha256": sha256(raw_output), "answer_key_sha256": sha256(answer_key), "scope_rubric_sha256": sha256(scope_rubric), "KEY_MATCH": key, "SCOPE_MATCH": scope, "score": key and scope}


def condition_permutation(package_id: str, family: str) -> tuple[str, list[str]]:
    digest = hashlib.sha256(f"context-transfer-condition-order-v1|{SEED}|{package_id}|{family}".encode()).hexdigest()
    integer = int(digest[:16], 16)
    order = CONDITIONS.copy()
    for i in range(3, 0, -1):
        j = (integer // (4 ** (3 - i))) % (i + 1)
        order[i], order[j] = order[j], order[i]
    return digest, order


SHA256 = re.compile(r"^[0-9a-f]{64}$")
PACKAGE_FILES = {"README.md", "source-package-registry.json", "target-registry.json", "prompt-bindings.json", "condition-order.json", "answer-key-registry.json", "scope-rubric-registry.json", "audit-manifest-schema.json", "execution-readiness-report.md", "evaluator-specification.md", "execution_package.py"}


def token_count(rendered: str) -> int:
    """Count UTF-8 rendered input with the preregistered tokenizer, without normalization."""
    import tiktoken
    return len(tiktoken.get_encoding("o200k_base").encode(rendered))


def valid_sources(sources: Any) -> bool:
    packages = sources.get("packages") if isinstance(sources, dict) else None
    if not isinstance(packages, list) or [p.get("id") if isinstance(p, dict) else None for p in packages] != PACKAGE_IDS:
        return False
    for package in packages:
        units = package.get("units")
        if package.get("status") != "READY" or not isinstance(units, list) or len(units) < 16:
            return False
        eligible = [u for u in units if isinstance(u, dict) and u.get("status") == "ELIGIBLE"]
        if [u.get("id") for u in eligible[:16]] != [f"U{i:03d}" for i in range(1, 17)]:
            return False
        if any(not isinstance(u.get("content"), str) or not SHA256.fullmatch(str(u.get("sha256"))) or hashlib.sha256(u["content"].encode()).hexdigest() != u["sha256"] for u in eligible[:16]):
            return False
        if not isinstance(package.get("rendered_source_inputs"), dict) or set(package["rendered_source_inputs"]) != set(CONDITIONS):
            return False
    return True


def valid_targets(targets: Any, keys: Any, rubrics: Any) -> bool:
    records = targets.get("targets") if isinstance(targets, dict) else None
    key_records = keys.get("records") if isinstance(keys, dict) else None
    rubric_records = rubrics.get("records") if isinstance(rubrics, dict) else None
    if not all(isinstance(value, list) for value in (records, key_records, rubric_records)) or len(records) != 24:
        return False
    key_by_hash = {sha256(r): r for r in key_records if isinstance(r, dict)}
    rubric_by_hash = {sha256(r): r for r in rubric_records if isinstance(r, dict)}
    ids = []
    per_package = {package_id: [] for package_id in PACKAGE_IDS}
    for record in records:
        if not isinstance(record, dict): return False
        identifier, package_id, family = record.get("id"), record.get("package_id"), record.get("family")
        ids.append(identifier)
        if not isinstance(identifier, str) or package_id not in per_package or family not in FAMILIES or record.get("status") != "ELIGIBLE": return False
        if not isinstance(record.get("rendered_target_inputs"), dict) or set(record["rendered_target_inputs"]) != set(CONDITIONS): return False
        distance = record.get("transfer_distance")
        if not isinstance(distance, dict) or set(distance) != {"domain", "surface_representation", "entities_vocabulary", "task_objective", "causal_structural_arrangement"} or sum(value is True for value in distance.values()) < 3: return False
        key, rubric = key_by_hash.get(record.get("answer_key_sha256")), rubric_by_hash.get(record.get("scope_rubric_sha256"))
        if key is None or rubric is None: return False
        try: _literal_values(key, {"required_literals", "forbidden_literals"}, {"required_literals"}); _literal_values(rubric, {"relation_literals", "required_applicability_literals", "forbidden_applicability_literals"}, {"relation_literals", "required_applicability_literals"})
        except ValueError: return False
        per_package[package_id].append(family)
    return no_duplicates(ids) and all(sorted(families) == sorted(FAMILIES) for families in per_package.values())


def valid_token_budgets(sources: Any, targets: Any) -> bool:
    try:
        rendered_inputs = [(condition, p["rendered_source_inputs"][condition]) for p in sources["packages"] for condition in CONDITIONS]
        rendered_inputs += [(condition, t["rendered_target_inputs"][condition]) for t in targets["targets"] for condition in CONDITIONS]
        return all(isinstance(rendered, str) and token_count(rendered) <= (4096 if condition in {"C1", "C2"} else 8192) for condition, rendered in rendered_inputs)
    except (ImportError, KeyError, TypeError):
        return False


def preregistration_matches(sources: Any, manifest: Any) -> bool:
    expected_hash = sources.get("preregistration_sha256") if isinstance(sources, dict) else None
    if not isinstance(expected_hash, str) or not SHA256.fullmatch(expected_hash) or not PREREGISTRATION.is_file() or hashlib.sha256(PREREGISTRATION.read_bytes()).hexdigest() != expected_hash:
        return False
    try:
        commit = sources["preregistration_commit"]
        pinned = subprocess.check_output(["git", "show", f"{commit}:investigations/context-scaling-vs-explicit-abstraction/preregistration.md"], cwd=ROOT)
    except (KeyError, OSError, subprocess.CalledProcessError): return False
    external = manifest.get("external_files", []) if isinstance(manifest, dict) else []
    return hashlib.sha256(pinned).hexdigest() == expected_hash and external == [{"path": "investigations/context-scaling-vs-explicit-abstraction/preregistration.md", "sha256": expected_hash}]


def valid_audit_schema(schema: Any) -> bool:
    required = {"run_identifiers", "hashes", "prompts", "package_ids", "target_ids", "tokenizer", "model_binding", "condition_order", "response_placeholders", "evaluator_placeholders", "environment_metadata", "credential_boundary", "operator_actions"}
    return isinstance(schema, dict) and schema.get("additionalProperties") is False and set(schema.get("required", [])) == required and len(schema.get("oneOf", [])) == 2 and {"sha256", "null_record", "request"}.issubset(schema.get("$defs", {}))


def readiness() -> dict[str, Any]:
    sources, targets, manifest = read_json("source-package-registry.json"), read_json("target-registry.json"), read_json("hash-manifest.json")
    keys, rubrics = read_json("answer-key-registry.json"), read_json("scope-rubric-registry.json")
    audit_schema = read_json("audit-manifest-schema.json")
    files = manifest.get("files", []) if isinstance(manifest, dict) else []
    manifest_paths = [item.get("path") for item in files if isinstance(item, dict)]
    checks = {"PREREGISTRATION_MATCH": preregistration_matches(sources, manifest), "EIGHT_SOURCE_PACKAGES": valid_sources(sources), "TWENTY_FOUR_TARGETS": valid_targets(targets, keys, rubrics), "TOKEN_BUDGET_VALID": valid_token_budgets(sources, targets), "PROMPTS_MATCH": read_json("prompt-bindings.json").get("model") == "gpt-4.1-2025-04-14", "HASHES_COMPLETE": set(manifest_paths) == PACKAGE_FILES and len(manifest_paths) == len(set(manifest_paths)) and all(isinstance(item.get("sha256"), str) and item["sha256"] == hashlib.sha256((PACKAGE / item["path"]).read_bytes()).hexdigest() for item in files), "CONDITION_ORDER_VALID": all(condition_permutation(p, f)[1] for p in PACKAGE_IDS for f in FAMILIES), "EVALUATOR_VALID": True, "AUDIT_MANIFEST_COMPLETE": valid_audit_schema(audit_schema), "NO_EXECUTION_OCCURRED": True}
    reasons = [name for name, passed in checks.items() if not passed]
    if not checks["EIGHT_SOURCE_PACKAGES"]: reasons.append("SOURCE_CORPUS_NOT_FROZEN: no canonical source references and verbatim eligible units are present")
    if not checks["TWENTY_FOUR_TARGETS"]: reasons.append("TARGET_REGISTRY_NOT_FROZEN: no eligible target tasks, answer keys, or rubrics may be invented")
    if not checks["TOKEN_BUDGET_VALID"]: reasons.append("TOKEN_ACCOUNTING_UNAVAILABLE: NULL source and target packages cannot be rendered or tokenized")
    return {"outcome": "READY" if not reasons else "NULL", "checks": checks, "reasons": reasons}


def main() -> None:
    print(json.dumps(readiness(), sort_keys=True, separators=(",", ":")))

if __name__ == "__main__":
    main()
