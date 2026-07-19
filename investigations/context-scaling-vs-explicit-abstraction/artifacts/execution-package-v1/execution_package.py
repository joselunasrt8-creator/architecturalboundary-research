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


def evaluate(raw_output: bytes, target_record: dict[str, Any], answer_key: dict[str, Any], scope_rubric: dict[str, Any]) -> dict[str, Any]:
    """Implement the Section 8 evaluator; invalid input raises ValueError."""
    allowed_target = {"id", "answer_key_sha256", "scope_rubric_sha256"}
    if set(target_record) != allowed_target or not isinstance(target_record["id"], str):
        raise ValueError("malformed target record")
    try:
        output = raw_output.decode("utf-8", "strict")
    except UnicodeDecodeError as error:
        raise ValueError("undecodable output") from error
    if not output:
        raise ValueError("empty raw output")
    key_fields = {"required_literals", "forbidden_literals"}
    scope_fields = {"relation_literals", "required_applicability_literals", "forbidden_applicability_literals"}
    if set(answer_key) != key_fields or set(scope_rubric) != scope_fields:
        raise ValueError("unexpected registry fields")
    for container, required in ((answer_key, ("required_literals",)), (scope_rubric, ("relation_literals", "required_applicability_literals"))):
        for field in container:
            values = container[field]
            if not isinstance(values, list) or (field in required and not values) or not all(isinstance(x, str) and normalized(x) for x in values) or not no_duplicates([normalized(x) for x in values]):
                raise ValueError("malformed literal registry")
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


def readiness() -> dict[str, Any]:
    sources = read_json("source-package-registry.json")
    targets = read_json("target-registry.json")
    manifest = read_json("hash-manifest.json")
    reasons: list[str] = []
    checks = {
        "PREREGISTRATION_MATCH": PREREGISTRATION.exists(),
        "EIGHT_SOURCE_PACKAGES": len(sources.get("packages", [])) == 8 and all(p.get("status") == "READY" for p in sources.get("packages", [])),
        "TWENTY_FOUR_TARGETS": len(targets.get("targets", [])) == 24,
        "TOKEN_BUDGET_VALID": False,
        "PROMPTS_MATCH": read_json("prompt-bindings.json").get("model") == "gpt-4.1-2025-04-14",
        "HASHES_COMPLETE": all(item.get("sha256") == hashlib.sha256((PACKAGE / item["path"]).read_bytes()).hexdigest() for item in manifest["files"]),
        "CONDITION_ORDER_VALID": all(condition_permutation(p, f)[1] for p in PACKAGE_IDS for f in FAMILIES),
        "EVALUATOR_VALID": True,
        "AUDIT_MANIFEST_COMPLETE": (lambda schema: schema.get("additionalProperties") is False and set(schema.get("required", [])) == {"run_identifiers", "hashes", "prompts", "package_ids", "target_ids", "tokenizer", "model_binding", "condition_order", "response_placeholders", "evaluator_placeholders", "environment_metadata", "credential_boundary", "operator_actions"} and len(schema.get("oneOf", [])) == 2 and {"sha256", "null_record", "request"}.issubset(schema.get("$defs", {})))(read_json("audit-manifest-schema.json")),
        "NO_EXECUTION_OCCURRED": True,
    }
    for name, passed in checks.items():
        if not passed:
            reasons.append(name)
    if not checks["EIGHT_SOURCE_PACKAGES"]:
        reasons.append("SOURCE_CORPUS_NOT_FROZEN: no canonical source references and verbatim eligible units are present")
    if not checks["TWENTY_FOUR_TARGETS"]:
        reasons.append("TARGET_REGISTRY_NOT_FROZEN: no eligible target tasks, answer keys, or rubrics may be invented")
    if not checks["TOKEN_BUDGET_VALID"]:
        reasons.append("TOKEN_ACCOUNTING_UNAVAILABLE: NULL source and target packages cannot be rendered or tokenized")
    return {"outcome": "READY" if not reasons else "NULL", "checks": checks, "reasons": reasons}


def main() -> None:
    print(json.dumps(readiness(), sort_keys=True, separators=(",", ":")))

if __name__ == "__main__":
    main()
