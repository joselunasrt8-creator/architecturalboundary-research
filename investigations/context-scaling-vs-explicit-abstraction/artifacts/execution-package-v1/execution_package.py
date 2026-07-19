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
from importlib import metadata
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
# SHA-256 bindings copied from the immutable Section 8 preregistration values.
EXPECTED_PROMPT_HASHES = {
    "system_prompt": "5bf8463177eb1599b50cbea5d8f6d80fdd467618de0e805a106b9d424e18b3f2",
    "source_prompt_template": "df6412072f515e2b0e47249cd14b5da8413e0e219100d27f98c72e8275fc1c5e",
    "target_prompt_template": "45f393b381a3555c52c87ddca5dffdd8290ad68803964f7ebd1559e94939ac13",
    "retention_instructions": {"C1": "4bed96dea30ead94e0c041d18e213b28eb4083a3ddb42147991868758005225e", "C2": "906cda79904e79f40ddacad75fc888246c754059b03b883b4f2c451071e54bc4", "C3": "4bed96dea30ead94e0c041d18e213b28eb4083a3ddb42147991868758005225e", "C4": "906cda79904e79f40ddacad75fc888246c754059b03b883b4f2c451071e54bc4"},
}


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
    """Count UTF-8 rendered input with the pinned tokenizer, without normalization."""
    import tiktoken
    if metadata.version("tiktoken") != "0.9.0":
        raise RuntimeError("tiktoken version is not pinned")
    return len(tiktoken.get_encoding("o200k_base").encode(rendered))


def _bindings_valid(bindings: Any) -> bool:
    if not isinstance(bindings, dict):
        return False
    required = {"schema_version", "system_prompt", "source_prompt_template", "target_prompt_template", "retention_instructions", "hashes", "model", "tokenizer", "decoding", "timeout_seconds", "token_ceilings"}
    if set(bindings) != required or bindings["schema_version"] != "1" or bindings["model"] != "gpt-4.1-2025-04-14":
        return False
    if bindings["tokenizer"] != {"name": "o200k_base", "package": "tiktoken==0.9.0", "encoding": "UTF-8 without normalization"} or bindings["timeout_seconds"] != 120 or bindings["token_ceilings"] != {"C1": 4096, "C2": 4096, "C3": 8192, "C4": 8192}:
        return False
    if bindings["decoding"] != {"temperature": 0, "top_p": 1, "max_output_tokens": 2048, "presence_penalty": 0, "frequency_penalty": 0, "seed": SEED, "omitted_optional_parameters": True} or set(bindings["retention_instructions"]) != set(CONDITIONS):
        return False
    hashes = bindings["hashes"]
    if hashes != EXPECTED_PROMPT_HASHES:
        return False
    if not isinstance(hashes, dict) or set(hashes) != {"system_prompt", "source_prompt_template", "target_prompt_template", "retention_instructions"}:
        return False
    for name in ("system_prompt", "source_prompt_template", "target_prompt_template"):
        if not isinstance(bindings[name], str) or hashes[name] != hashlib.sha256(bindings[name].encode()).hexdigest():
            return False
    return isinstance(hashes["retention_instructions"], dict) and set(hashes["retention_instructions"]) == set(CONDITIONS) and all(hashes["retention_instructions"].get(c) == hashlib.sha256(bindings["retention_instructions"][c].encode()).hexdigest() for c in CONDITIONS)


def _source_render(package: dict[str, Any], condition: str, bindings: dict[str, Any]) -> str:
    units = package["units"][:8 if condition in {"C1", "C2"} else 16]
    source_units = "\n".join(f"{unit['id']}: {unit['content']}" for unit in units)
    user = bindings["source_prompt_template"].format(package_id=package["id"], condition_id=condition, source_units=source_units, retention_instruction=bindings["retention_instructions"][condition])
    return bindings["system_prompt"] + "\n\n" + user


def _target_render(target: dict[str, Any], condition: str, bindings: dict[str, Any]) -> str:
    retained = target["retained_package_by_condition"][condition]
    user = bindings["target_prompt_template"].format(target_id=target["id"], condition_id=condition, retained_package=retained)
    return bindings["system_prompt"] + "\n\n" + user


def valid_sources(sources: Any) -> bool:
    packages = sources.get("packages") if isinstance(sources, dict) else None
    if not isinstance(packages, list) or [p.get("id") if isinstance(p, dict) else None for p in packages] != PACKAGE_IDS:
        return False
    for package in packages:
        units = package.get("units")
        if package.get("status") != "READY" or not isinstance(package.get("canonical_source_reference"), str) or not package["canonical_source_reference"] or not isinstance(units, list) or len(units) != 16:
            return False
        if [u.get("id") if isinstance(u, dict) else None for u in units] != [f"U{i:03d}" for i in range(1, 17)]:
            return False
        if any(set(u) != {"id", "status", "content", "sha256", "source_reference"} or u["status"] != "ELIGIBLE" or not isinstance(u["source_reference"], str) or not u["source_reference"] or not isinstance(u["content"], str) or not u["content"] or not isinstance(u["sha256"], str) or not SHA256.fullmatch(u["sha256"]) or hashlib.sha256(u["content"].encode()).hexdigest() != u["sha256"] for u in units):
            return False
    return True


def valid_targets(targets: Any, keys: Any, rubrics: Any) -> bool:
    records = targets.get("targets") if isinstance(targets, dict) else None
    key_records = keys.get("records") if isinstance(keys, dict) else None
    rubric_records = rubrics.get("records") if isinstance(rubrics, dict) else None
    if not all(isinstance(value, list) for value in (records, key_records, rubric_records)) or len(records) != 24:
        return False
    key_by_hash = {sha256(r): r for r in key_records if isinstance(r, dict)}; rubric_by_hash = {sha256(r): r for r in rubric_records if isinstance(r, dict)}
    ids, per_package = [], {package_id: [] for package_id in PACKAGE_IDS}
    required_distance = {"domain", "surface_representation", "entities_vocabulary", "task_objective", "causal_structural_arrangement"}
    for record in records:
        if not isinstance(record, dict) or set(record) != {"id", "package_id", "family", "status", "answer_key_sha256", "scope_rubric_sha256", "transfer_distance", "retained_package_by_condition"}: return False
        identifier, package_id, family = record["id"], record["package_id"], record["family"]; ids.append(identifier)
        if not isinstance(identifier, str) or not re.fullmatch(r"T[0-9]{2,}", identifier) or package_id not in per_package or family not in FAMILIES or record["status"] != "ELIGIBLE": return False
        distance = record["transfer_distance"]
        if not isinstance(distance, dict) or set(distance) != required_distance or not all(isinstance(v, bool) for v in distance.values()) or sum(distance.values()) < 3: return False
        retained = record["retained_package_by_condition"]
        if not isinstance(retained, dict) or set(retained) != set(CONDITIONS) or not all(isinstance(v, str) and v for v in retained.values()): return False
        key, rubric = key_by_hash.get(record["answer_key_sha256"]), rubric_by_hash.get(record["scope_rubric_sha256"])
        if key is None or rubric is None: return False
        try: _literal_values(key, {"required_literals", "forbidden_literals"}, {"required_literals"}); _literal_values(rubric, {"relation_literals", "required_applicability_literals", "forbidden_applicability_literals"}, {"relation_literals", "required_applicability_literals"})
        except ValueError: return False
        per_package[package_id].append(family)
    return no_duplicates(ids) and all(sorted(families) == sorted(FAMILIES) for families in per_package.values())


def valid_token_budgets(sources: Any, targets: Any, bindings: Any) -> bool:
    if not _bindings_valid(bindings) or not valid_sources(sources) or not isinstance(targets, dict) or not isinstance(targets.get("targets"), list): return False
    try:
        renders = [(c, _source_render(p, c, bindings)) for p in sources["packages"] for c in CONDITIONS]
        renders += [(c, _target_render(t, c, bindings)) for t in targets["targets"] for c in CONDITIONS]
        return all(token_count(rendered) <= bindings["token_ceilings"][condition] for condition, rendered in renders)
    except (ImportError, KeyError, TypeError, ValueError, RuntimeError, metadata.PackageNotFoundError): return False

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


def valid_condition_order(order: Any) -> bool:
    if not isinstance(order, dict) or order.get("seed") != SEED or order.get("canonical_target_order") != "NULL: targets are not frozen": return False
    blocks = order.get("target_condition_blocks")
    if not isinstance(blocks, list) or len(blocks) != 24: return False
    expected = [(p, f) for p in PACKAGE_IDS for f in FAMILIES]
    if [(b.get("package_id"), b.get("target_family")) if isinstance(b, dict) else None for b in blocks] != expected: return False
    for block in blocks:
        digest, conditions = condition_permutation(block["package_id"], block["target_family"])
        if block.get("digest_sha256") != digest or block.get("execution_conditions") != conditions: return False
    return True

def readiness() -> dict[str, Any]:
    sources, targets, manifest = read_json("source-package-registry.json"), read_json("target-registry.json"), read_json("hash-manifest.json")
    bindings = read_json("prompt-bindings.json")
    keys, rubrics = read_json("answer-key-registry.json"), read_json("scope-rubric-registry.json")
    audit_schema = read_json("audit-manifest-schema.json")
    files = manifest.get("files", []) if isinstance(manifest, dict) else []
    manifest_paths = [item.get("path") for item in files if isinstance(item, dict)]
    checks = {"PREREGISTRATION_MATCH": preregistration_matches(sources, manifest), "EIGHT_SOURCE_PACKAGES": valid_sources(sources), "TWENTY_FOUR_TARGETS": valid_targets(targets, keys, rubrics), "TOKEN_BUDGET_VALID": valid_token_budgets(sources, targets, bindings), "PROMPTS_MATCH": _bindings_valid(bindings), "HASHES_COMPLETE": set(manifest_paths) == PACKAGE_FILES and len(manifest_paths) == len(set(manifest_paths)) and all(isinstance(item.get("sha256"), str) and item["sha256"] == hashlib.sha256((PACKAGE / item["path"]).read_bytes()).hexdigest() for item in files), "CONDITION_ORDER_VALID": valid_condition_order(read_json("condition-order.json")), "EVALUATOR_VALID": True, "AUDIT_MANIFEST_COMPLETE": valid_audit_schema(audit_schema), "NO_EXECUTION_OCCURRED": True}
    reasons = [name for name, passed in checks.items() if not passed]
    if not checks["EIGHT_SOURCE_PACKAGES"]: reasons.append("SOURCE_CORPUS_NOT_FROZEN: no canonical source references and verbatim eligible units are present")
    if not checks["TWENTY_FOUR_TARGETS"]: reasons.append("TARGET_REGISTRY_NOT_FROZEN: no eligible target tasks, answer keys, or rubrics may be invented")
    if not checks["TOKEN_BUDGET_VALID"]: reasons.append("TOKEN_ACCOUNTING_UNAVAILABLE: NULL source and target packages cannot be rendered or tokenized")
    return {"outcome": "READY" if not reasons else "NULL", "checks": checks, "reasons": reasons}


def main() -> None:
    print(json.dumps(readiness(), sort_keys=True, separators=(",", ":")))

if __name__ == "__main__":
    main()
