#!/usr/bin/env python3
"""Deterministic, offline validation for execution-package-v1.

The module contains no model invocation path.  It validates immutable package
bytes and fails closed: missing or malformed inputs produce NULL, never implied
authority to execute.
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
import unicodedata
from datetime import datetime
from importlib import metadata
from pathlib import Path
from typing import Any, Callable, Mapping

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[3]
PREREGISTRATION_PATH = "investigations/context-scaling-vs-explicit-abstraction/preregistration.md"
PREREGISTRATION = ROOT / PREREGISTRATION_PATH
PREREGISTRATION_COMMIT = "aed5ff895d3afb0a03b819bc5112327b479b8905"
PREREGISTRATION_SHA256 = "8e793c7fb68c8efc0e9fb2602214231f783e79e93f7bc10fc5ed9153b3b4cd23"
PACKAGE_VERSION = "execution-package-v1"
PACKAGE_IDS = [f"SP{i:02d}" for i in range(1, 9)]
UNIT_IDS = [f"U{i:03d}" for i in range(1, 17)]
TARGET_IDS = [f"T{i:02d}" for i in range(1, 25)]
FAMILIES = ["structural_diagnosis", "constraint_aware_recommendation", "causal_explanation"]
CONDITIONS = ["C1", "C2", "C3", "C4"]
SEED = 20260719
TOKEN_CEILINGS = {"C1": 4096, "C2": 4096, "C3": 8192, "C4": 8192}
SHA256 = re.compile(r"^[0-9a-f]{64}$")

SYSTEM_PROMPT = (
    "You are a careful research assistant. Follow the user message exactly. Do not use tools, "
    "browse, retrieve, or rely on information not supplied in this conversation. Return only the requested answer."
)
SOURCE_PROMPT = (
    "SOURCE PACKAGE {package_id}; CONDITION {condition_id}. Source units, in order: {source_units}. "
    "Produce the source-specific answer. {retention_instruction}"
)
TARGET_PROMPT = (
    "TARGET {target_id}; CONDITION {condition_id}. Retained package: {retained_package}. Solve the target. "
    "State the conclusion and a concise justification. Do not use tools, retrieval, or outside knowledge."
)
CONTEXT_INSTRUCTION = "Return only the source-specific answer; do not create or state any reusable abstraction."
ABSTRACTION_INSTRUCTION = (
    "Return the source-specific answer, then exactly one line ABSTRACTION:, then one canonical JSON object with "
    "exactly artifact_id, principle, applicability_conditions, limitations, source_unit_provenance, and "
    "reuse_instructions. Provenance entries must contain unit_id, unit_sha256, and claims for every material claim."
)
EXPECTED_BINDINGS = {
    "schema_version": "1",
    "endpoint": "https://api.openai.com/v1/responses",
    "scorer_image_sha256": None,
    "system_prompt": SYSTEM_PROMPT,
    "source_prompt_template": SOURCE_PROMPT,
    "target_prompt_template": TARGET_PROMPT,
    "retention_instructions": {
        "C1": CONTEXT_INSTRUCTION,
        "C2": ABSTRACTION_INSTRUCTION,
        "C3": CONTEXT_INSTRUCTION,
        "C4": ABSTRACTION_INSTRUCTION,
    },
    "hashes": {
        "system_prompt": hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest(),
        "source_prompt_template": hashlib.sha256(SOURCE_PROMPT.encode()).hexdigest(),
        "target_prompt_template": hashlib.sha256(TARGET_PROMPT.encode()).hexdigest(),
        "retention_instructions": {
            "C1": hashlib.sha256(CONTEXT_INSTRUCTION.encode()).hexdigest(),
            "C2": hashlib.sha256(ABSTRACTION_INSTRUCTION.encode()).hexdigest(),
            "C3": hashlib.sha256(CONTEXT_INSTRUCTION.encode()).hexdigest(),
            "C4": hashlib.sha256(ABSTRACTION_INSTRUCTION.encode()).hexdigest(),
        },
    },
    "model": "gpt-4.1-2025-04-14",
    "tokenizer": {"name": "o200k_base", "package": "tiktoken==0.9.0", "encoding": "UTF-8 without normalization"},
    "decoding": {
        "temperature": 0,
        "top_p": 1,
        "max_output_tokens": 2048,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "seed": SEED,
        "omitted_optional_parameters": True,
    },
    "timeout_seconds": 120,
    "token_ceilings": TOKEN_CEILINGS,
}
PACKAGE_FILES = {
    "README.md",
    "source-package-registry.json",
    "target-registry.json",
    "prompt-bindings.json",
    "condition-order.json",
    "answer-key-registry.json",
    "scope-rubric-registry.json",
    "audit-manifest-schema.json",
    "execution-readiness-report.md",
    "evaluator-specification.md",
    "execution_package.py",
}
MANIFEST_NAME = "hash-manifest.json"
MANIFEST_ANCHOR_NAME = "hash-manifest-anchor-v2.json"
JSON_INPUTS = {
    "source-package-registry.json",
    "target-registry.json",
    "prompt-bindings.json",
    "condition-order.json",
    "answer-key-registry.json",
    "scope-rubric-registry.json",
    "audit-manifest-schema.json",
    "hash-manifest.json",
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256(value: Any) -> str:
    return hashlib.sha256(value if isinstance(value, bytes) else canonical_bytes(value)).hexdigest()


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", value).casefold()).strip(" ")


def valid_hash(value: Any) -> bool:
    return isinstance(value, str) and SHA256.fullmatch(value) is not None


def closed(value: Any, fields: set[str]) -> bool:
    return isinstance(value, dict) and set(value) == fields


def integer(value: Any, *, minimum: int = 0) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= minimum


def read_json(name: str) -> Any:
    return json.loads((PACKAGE / name).read_bytes())


def package_bytes(package_dir: Path = PACKAGE) -> dict[str, bytes]:
    names = PACKAGE_FILES | {MANIFEST_NAME, MANIFEST_ANCHOR_NAME}
    return {name: (package_dir / name).read_bytes() for name in names}


def _literal_list(value: Any, *, nonempty: bool) -> list[str]:
    if not isinstance(value, list) or (nonempty and not value):
        raise ValueError("malformed literal registry")
    if not all(isinstance(item, str) and normalized(item) for item in value):
        raise ValueError("malformed literal registry")
    result = [normalized(item) for item in value]
    if len(result) != len(set(result)) or {"key_match", "scope_match"} & set(result):
        raise ValueError("malformed literal registry")
    return result


def validate_literal_registries(answer_key: Any, scope_rubric: Any) -> None:
    if not closed(answer_key, {"required_literals", "forbidden_literals"}) or not closed(
        scope_rubric,
        {"relation_literals", "required_applicability_literals", "forbidden_applicability_literals"},
    ):
        raise ValueError("malformed literal registry")
    required = set(_literal_list(answer_key["required_literals"], nonempty=True))
    forbidden = set(_literal_list(answer_key["forbidden_literals"], nonempty=False))
    relations = set(_literal_list(scope_rubric["relation_literals"], nonempty=True))
    applicable = set(_literal_list(scope_rubric["required_applicability_literals"], nonempty=True))
    inapplicable = set(_literal_list(scope_rubric["forbidden_applicability_literals"], nonempty=False))
    positives = required | relations | applicable
    negatives = forbidden | inapplicable
    if required & forbidden or applicable & inapplicable or relations & inapplicable or positives & negatives:
        raise ValueError("normalized literal conflict")


def evaluate(
    raw_output: bytes,
    target_record: dict[str, Any],
    answer_key: dict[str, Any],
    scope_rubric: dict[str, Any],
) -> dict[str, Any]:
    """Run the frozen offline evaluator; malformed registries raise ValueError."""
    if not closed(target_record, {"id", "answer_key_sha256", "scope_rubric_sha256"}):
        raise ValueError("malformed target record")
    if not isinstance(target_record["id"], str) or not valid_hash(target_record["answer_key_sha256"]) or not valid_hash(
        target_record["scope_rubric_sha256"]
    ):
        raise ValueError("malformed target record")
    try:
        text = raw_output.decode("utf-8", "strict")
    except (AttributeError, UnicodeDecodeError) as error:
        raise ValueError("undecodable output") from error
    if not text:
        raise ValueError("empty raw output")
    validate_literal_registries(answer_key, scope_rubric)
    if sha256(answer_key) != target_record["answer_key_sha256"] or sha256(scope_rubric) != target_record[
        "scope_rubric_sha256"
    ]:
        raise ValueError("hash mismatch")
    output = normalized(text)
    key_match = all(normalized(item) in output for item in answer_key["required_literals"]) and not any(
        normalized(item) in output for item in answer_key["forbidden_literals"]
    )
    scope_match = all(
        normalized(item) in output
        for item in scope_rubric["relation_literals"] + scope_rubric["required_applicability_literals"]
    ) and not any(normalized(item) in output for item in scope_rubric["forbidden_applicability_literals"])
    return {
        "target_id": target_record["id"],
        "raw_output_sha256": sha256(raw_output),
        "answer_key_sha256": sha256(answer_key),
        "scope_rubric_sha256": sha256(scope_rubric),
        "KEY_MATCH": key_match,
        "SCOPE_MATCH": scope_match,
        "score": key_match and scope_match,
    }


def condition_permutation(package_id: str, family: str) -> tuple[str, str, int, list[str]]:
    digest_input = f"context-transfer-condition-order-v1|{SEED}|{package_id}|{family}"
    digest = hashlib.sha256(digest_input.encode()).hexdigest()
    integer_value = int.from_bytes(bytes.fromhex(digest[:16]), byteorder="big", signed=False)
    order = CONDITIONS.copy()
    for index in range(3, 0, -1):
        swap = (integer_value // (4 ** (3 - index))) % (index + 1)
        order[index], order[swap] = order[swap], order[index]
    return digest_input, digest, integer_value, order


def bindings_valid(bindings: Any, *, require_scorer: bool = False) -> bool:
    if not isinstance(bindings, dict):
        return False
    expected = dict(EXPECTED_BINDINGS)
    scorer = bindings.get("scorer_image_sha256")
    expected["scorer_image_sha256"] = scorer
    if bindings != expected:
        return False
    return valid_hash(scorer) if require_scorer else scorer is None or valid_hash(scorer)


def _source_user_prompt(package: dict[str, Any], condition: str, bindings: dict[str, Any]) -> str:
    units = package["units"][: 8 if condition in {"C1", "C2"} else 16]
    unit_text = "\n".join(f"{unit['id']}: {unit['content']}" for unit in units)
    return bindings["source_prompt_template"].format(
        package_id=package["id"],
        condition_id=condition,
        source_units=unit_text,
        retention_instruction=bindings["retention_instructions"][condition],
    )


def _source_render(package: dict[str, Any], condition: str, bindings: dict[str, Any]) -> str:
    return bindings["system_prompt"] + "\n\n" + _source_user_prompt(package, condition, bindings)


def _retained_package(artifact: dict[str, Any], condition: str) -> str:
    lines = ["SOURCE RESPONSE:", artifact["source_response"], "CITATION IDENTIFIERS:"]
    lines.extend(artifact["citation_identifiers"])
    lines.append("RETAINED OBJECTS:")
    if condition in {"C2", "C4"}:
        abstraction = artifact["abstraction_artifact"]
        lines.extend((f"ABSTRACTION ARTIFACT {abstraction['artifact_id']}:", abstraction["canonical_serialization"]))
    return "\n".join(lines)


def _target_render(
    target: dict[str, Any], condition: str, bindings: dict[str, Any], stage1_outputs: dict[str, Any]
) -> str:
    artifact = stage1_outputs[target["package_id"]][condition]
    retained = _retained_package(artifact, condition)
    user = bindings["target_prompt_template"].format(
        target_id=target["id"], condition_id=condition, retained_package=retained
    )
    return bindings["system_prompt"] + "\n\n" + user + "\n\nTARGET TASK:\n" + target["target_prompt"]


def _target_user_prompt(
    target: dict[str, Any], condition: str, bindings: dict[str, Any], stage1_outputs: dict[str, Any]
) -> str:
    rendered = _target_render(target, condition, bindings, stage1_outputs)
    prefix = bindings["system_prompt"] + "\n\n"
    if not rendered.startswith(prefix):
        raise ValueError("target render does not contain the frozen system prompt")
    return rendered[len(prefix) :]


def canonical_source_request(
    package: dict[str, Any], condition: str, bindings: dict[str, Any]
) -> dict[str, Any]:
    units = package["units"][: 8 if condition in {"C1", "C2"} else 16]
    return {
        "endpoint": bindings["endpoint"],
        "system_prompt": bindings["system_prompt"],
        "rendered_user_prompt": _source_user_prompt(package, condition, bindings),
        "supplied_inputs": [
            {"kind": "source_unit", "identifier": unit["id"], "sha256": unit["sha256"], "content": unit["content"]}
            for unit in units
        ],
        "model": bindings["model"],
        "decoding": bindings["decoding"],
        "tools": [],
        "tool_choice": "none",
    }


def canonical_target_request(
    target: dict[str, Any], condition: str, bindings: dict[str, Any], stage1_outputs: dict[str, Any]
) -> dict[str, Any]:
    artifact = stage1_outputs[target["package_id"]][condition]
    supplied = [
        {
            "kind": "source_response",
            "identifier": f"{target['package_id']}:{condition}:source_response",
            "sha256": artifact["source_response_sha256"],
            "content": artifact["source_response"],
        }
    ]
    supplied.extend(
        {
            "kind": "citation_identifier",
            "identifier": citation,
            "sha256": sha256(citation.encode()),
            "content": citation,
        }
        for citation in artifact["citation_identifiers"]
    )
    if condition in {"C2", "C4"}:
        abstraction = artifact["abstraction_artifact"]
        supplied.append(
            {
                "kind": "retained_object",
                "identifier": abstraction["artifact_id"],
                "sha256": abstraction["sha256"],
                "content": abstraction["canonical_serialization"],
            }
        )
    return {
        "endpoint": bindings["endpoint"],
        "system_prompt": bindings["system_prompt"],
        "rendered_user_prompt": _target_user_prompt(target, condition, bindings, stage1_outputs),
        "supplied_inputs": supplied,
        "model": bindings["model"],
        "decoding": bindings["decoding"],
        "tools": [],
        "tool_choice": "none",
    }


def token_count(text: str) -> int:
    import tiktoken

    if metadata.version("tiktoken") != "0.9.0":
        raise RuntimeError("tokenizer version mismatch")
    return len(tiktoken.get_encoding("o200k_base").encode(text))


SOURCE_FIELDS = {
    "id",
    "status",
    "canonical_source_reference",
    "immutable_locator",
    "document_order",
    "unit_boundary_method",
    "unit_boundary_version",
    "units",
    "source_hashes",
    "package_hash",
    "duplicate_decisions",
    "exclusion_decisions",
    "duplicate_eligible_content_absent",
    "subsets",
    "token_accounting",
    "provenance",
}
UNIT_FIELDS = {"id", "status", "content", "sha256", "source_reference"}


def valid_sources(
    registry: Any,
    bindings: Any,
    counter: Callable[[str], int] = token_count,
) -> bool:
    try:
        top = {
            "schema_version",
            "package_version",
            "preregistration_path",
            "preregistration_commit",
            "preregistration_sha256",
            "unitization",
            "packages",
        }
        if not closed(registry, top) or registry["schema_version"] != "1" or registry["package_version"] != PACKAGE_VERSION:
            return False
        if not bindings_valid(bindings) or not isinstance(registry["unitization"], str) or not registry["unitization"]:
            return False
        packages = registry["packages"]
        if not isinstance(packages, list) or [item.get("id") if isinstance(item, dict) else None for item in packages] != PACKAGE_IDS:
            return False
        source_references: set[str] = set()
        immutable_locators: set[str] = set()
        global_verbatim_hashes: set[str] = set()
        global_normalized_hashes: set[str] = set()
        for package in packages:
            if not closed(package, SOURCE_FIELDS) or package["status"] != "READY" or package["duplicate_eligible_content_absent"] is not True:
                return False
            strings = (
                "canonical_source_reference",
                "immutable_locator",
                "document_order",
                "unit_boundary_method",
                "unit_boundary_version",
            )
            if not all(isinstance(package[field], str) and package[field] for field in strings):
                return False
            if package["canonical_source_reference"] in source_references or package["immutable_locator"] in immutable_locators:
                return False
            source_references.add(package["canonical_source_reference"])
            immutable_locators.add(package["immutable_locator"])
            if not isinstance(package["duplicate_decisions"], list) or not isinstance(package["exclusion_decisions"], list):
                return False
            units = package["units"]
            if not isinstance(units, list) or [unit.get("id") if isinstance(unit, dict) else None for unit in units] != UNIT_IDS:
                return False
            for unit in units:
                if not closed(unit, UNIT_FIELDS) or unit["status"] != "ELIGIBLE":
                    return False
                if not isinstance(unit["content"], str) or not unit["content"] or not isinstance(unit["source_reference"], str) or not unit[
                    "source_reference"
                ]:
                    return False
                if not valid_hash(unit["sha256"]) or hashlib.sha256(unit["content"].encode()).hexdigest() != unit["sha256"]:
                    return False
                normalized_content = normalized(unit["content"])
                if not normalized_content:
                    return False
                normalized_hash = sha256(normalized_content.encode())
                if unit["sha256"] in global_verbatim_hashes or normalized_hash in global_normalized_hashes:
                    return False
                global_verbatim_hashes.add(unit["sha256"])
                global_normalized_hashes.add(normalized_hash)
            if len({unit["content"] for unit in units}) != 16 or len({unit["sha256"] for unit in units}) != 16:
                return False
            if len({unit["source_reference"] for unit in units}) != 16:
                return False
            if package["source_hashes"] != [unit["sha256"] for unit in units]:
                return False
            if package["subsets"] != {"N=8": UNIT_IDS[:8], "M=16": UNIT_IDS}:
                return False
            accounting = package["token_accounting"]
            accounting_fields = {
                "tokenizer",
                "package",
                "condition_counts",
                "condition_ceilings",
                "truncation",
                "compression",
                "substitution",
            }
            if not closed(accounting, accounting_fields) or accounting["tokenizer"] != "o200k_base" or accounting["package"] != "tiktoken==0.9.0":
                return False
            if accounting["condition_ceilings"] != TOKEN_CEILINGS or any(
                accounting[name] is not False for name in ("truncation", "compression", "substitution")
            ):
                return False
            counts = accounting["condition_counts"]
            if not closed(counts, set(CONDITIONS)) or not all(integer(counts[condition]) for condition in CONDITIONS):
                return False
            for condition in CONDITIONS:
                if counts[condition] != counter(_source_render(package, condition, bindings)):
                    return False
            package_body = {key: value for key, value in package.items() if key != "package_hash"}
            if not valid_hash(package["package_hash"]) or sha256(package_body) != package["package_hash"]:
                return False
        return True
    except Exception:
        return False


def _registry_records(registry: Any, kind: str) -> list[dict[str, Any]] | None:
    fields = {"schema_version", "package_version", "status", "reason", "records"}
    if not closed(registry, fields) or registry["schema_version"] != "1" or registry["package_version"] != PACKAGE_VERSION:
        return None
    if registry["status"] != "READY" or not isinstance(registry["reason"], str) or not registry["reason"]:
        return None
    records = registry["records"]
    if not isinstance(records, list) or len(records) != 24 or not all(isinstance(item, dict) for item in records):
        return None
    expected = {"required_literals", "forbidden_literals"} if kind == "key" else {
        "relation_literals",
        "required_applicability_literals",
        "forbidden_applicability_literals",
    }
    if any(set(item) != expected for item in records):
        return None
    return records


TARGET_FIELDS = {
    "id",
    "package_id",
    "family",
    "status",
    "target_prompt",
    "answer_key_sha256",
    "scope_rubric_sha256",
    "required_literals",
    "forbidden_literals",
    "relation_literals",
    "applicability_literals",
    "transfer_distance",
    "overlap_checks",
    "eligibility_rationale",
    "eligibility_determination",
    "target_record_hash",
}


def valid_targets(registry: Any, key_registry: Any, rubric_registry: Any) -> bool:
    try:
        top = {
            "schema_version",
            "package_version",
            "selection_rule",
            "expected_target_count",
            "targets",
            "stage1_outputs",
            "source_execution_audits",
            "target_package_accounting",
            "status",
            "reason",
        }
        if not closed(registry, top) or registry["schema_version"] != "1" or registry["package_version"] != PACKAGE_VERSION:
            return False
        targets = registry["targets"]
        if registry["expected_target_count"] != 24 or registry["status"] != "READY" or not isinstance(registry["selection_rule"], str):
            return False
        if not isinstance(registry["reason"], str) or not registry["reason"] or not isinstance(targets, list) or len(targets) != 24:
            return False
        keys = _registry_records(key_registry, "key")
        rubrics = _registry_records(rubric_registry, "rubric")
        if keys is None or rubrics is None:
            return False
        key_by_hash = {sha256(item): item for item in keys}
        rubric_by_hash = {sha256(item): item for item in rubrics}
        if len(key_by_hash) != 24 or len(rubric_by_hash) != 24:
            return False
        expected_pairs = [(package, family) for package in PACKAGE_IDS for family in FAMILIES]
        actual_ids = [item.get("id") if isinstance(item, dict) else None for item in targets]
        actual_pairs = [
            (item.get("package_id"), item.get("family")) if isinstance(item, dict) else (None, None) for item in targets
        ]
        if actual_ids != TARGET_IDS or actual_pairs != expected_pairs:
            return False
        used_keys: set[str] = set()
        used_rubrics: set[str] = set()
        for target in targets:
            if not closed(target, TARGET_FIELDS) or target["status"] != "ELIGIBLE" or target["eligibility_determination"] != "ELIGIBLE":
                return False
            if not isinstance(target["target_prompt"], str) or not target["target_prompt"] or not isinstance(
                target["eligibility_rationale"], str
            ) or not target["eligibility_rationale"]:
                return False
            if not valid_hash(target["answer_key_sha256"]) or not valid_hash(target["scope_rubric_sha256"]):
                return False
            if target["answer_key_sha256"] not in key_by_hash or target["scope_rubric_sha256"] not in rubric_by_hash:
                return False
            used_keys.add(target["answer_key_sha256"])
            used_rubrics.add(target["scope_rubric_sha256"])
            key = key_by_hash[target["answer_key_sha256"]]
            rubric = rubric_by_hash[target["scope_rubric_sha256"]]
            validate_literal_registries(key, rubric)
            if target["required_literals"] != key["required_literals"] or target["forbidden_literals"] != key["forbidden_literals"]:
                return False
            if target["relation_literals"] != rubric["relation_literals"] or target["applicability_literals"] != rubric[
                "required_applicability_literals"
            ]:
                return False
            distance = target["transfer_distance"]
            distance_fields = {"domain", "surface_representation", "entities_vocabulary", "task_objective", "causal_structural_arrangement"}
            if not closed(distance, distance_fields) or not all(isinstance(value, bool) for value in distance.values()) or sum(distance.values()) < 3:
                return False
            checks = target["overlap_checks"]
            if not closed(checks, {"no_source_overlap", "no_answer_leakage", "no_rubric_leakage"}) or not all(
                value is True for value in checks.values()
            ):
                return False
            body = {key_name: value for key_name, value in target.items() if key_name != "target_record_hash"}
            if not valid_hash(target["target_record_hash"]) or sha256(body) != target["target_record_hash"]:
                return False
        return used_keys == set(key_by_hash) and used_rubrics == set(rubric_by_hash)
    except (KeyError, TypeError, ValueError):
        return False


STAGE1_FIELDS = {
    "package_id",
    "condition_id",
    "source_audit_id",
    "source_audit_binding_sha256",
    "raw_response_sha256",
    "retained_raw_response_utf8",
    "immutable_artifact_reference",
    "source_response",
    "source_response_sha256",
    "abstraction_artifact",
    "abstraction_artifact_sha256",
    "citation_identifiers",
    "retained_objects",
    "stage1_output_hash",
}


ABSTRACTION_CORE_FIELDS = {
    "artifact_id",
    "principle",
    "applicability_conditions",
    "limitations",
    "source_unit_provenance",
    "reuse_instructions",
}
ABSTRACTION_FIELDS = ABSTRACTION_CORE_FIELDS | {"canonical_serialization", "sha256"}
ABSTRACTION_CLAIMS = {"principle", "applicability_conditions", "limitations", "reuse_instructions"}


def structured_abstraction(serialized: str, package: dict[str, Any], condition: str) -> dict[str, Any]:
    """Parse the exact canonical C2/C4 artifact and bind every provenance item to supplied units."""
    if condition not in {"C2", "C4"} or not isinstance(serialized, str) or not serialized:
        raise ValueError("missing abstraction artifact")
    core = json.loads(serialized)
    if not closed(core, ABSTRACTION_CORE_FIELDS) or canonical_bytes(core).decode("utf-8") != serialized:
        raise ValueError("abstraction is not canonical JSON")
    if core["artifact_id"] != f"A-{package['id']}-{condition}":
        raise ValueError("invalid abstraction identifier")
    if not all(isinstance(core[name], str) and core[name].strip() for name in ("principle", "reuse_instructions")):
        raise ValueError("empty abstraction text")
    for name in ("applicability_conditions", "limitations"):
        values = core[name]
        if not isinstance(values, list) or not values or not all(isinstance(value, str) and value.strip() for value in values):
            raise ValueError("empty abstraction list")
    supplied = package["units"][: 8 if condition == "C2" else 16]
    supplied_hashes = {unit["id"]: unit["sha256"] for unit in supplied}
    provenance = core["source_unit_provenance"]
    if not isinstance(provenance, list) or not provenance:
        raise ValueError("missing abstraction provenance")
    seen_units: set[str] = set()
    covered_claims: set[str] = set()
    for item in provenance:
        if not closed(item, {"unit_id", "unit_sha256", "claims"}):
            raise ValueError("malformed abstraction provenance")
        unit_id = item["unit_id"]
        claims = item["claims"]
        if unit_id in seen_units or supplied_hashes.get(unit_id) != item["unit_sha256"]:
            raise ValueError("unbound abstraction provenance")
        if not isinstance(claims, list) or not claims or not all(claim in ABSTRACTION_CLAIMS for claim in claims):
            raise ValueError("invalid abstraction claim provenance")
        if len(claims) != len(set(claims)):
            raise ValueError("duplicate abstraction claim provenance")
        seen_units.add(unit_id)
        covered_claims.update(claims)
    if covered_claims != ABSTRACTION_CLAIMS:
        raise ValueError("incomplete abstraction claim provenance")
    return {
        **core,
        "canonical_serialization": serialized,
        "sha256": sha256(serialized.encode("utf-8")),
    }


def source_audit_binding_hash(record: Any) -> str:
    """Hash a source audit with the reciprocal Stage-1 hash slot canonically nulled."""
    if not isinstance(record, dict):
        raise ValueError("malformed source audit")
    normalized_record = json.loads(canonical_bytes(record))
    normalized_record["response"]["stage1_output_hash"] = None
    return sha256(normalized_record)


def _stage1_raw_bytes(artifact: Any, raw_artifacts: Mapping[str, bytes] | None = None) -> bytes | None:
    try:
        response = {
            "retained_raw_response_utf8": artifact["retained_raw_response_utf8"],
            "immutable_artifact_reference": artifact["immutable_artifact_reference"],
        }
        reference = response["immutable_artifact_reference"]
        supplied = None
        if isinstance(reference, dict) and raw_artifacts is not None:
            supplied = raw_artifacts.get(reference.get("path"))
        return _retained_response_bytes(response, supplied)
    except (KeyError, TypeError):
        return None


def valid_stage1_output_record(
    artifact: Any,
    package: dict[str, Any],
    condition: str,
    raw_artifacts: Mapping[str, bytes] | None = None,
) -> bool:
    try:
        if condition not in CONDITIONS:
            return False
        if (
            not closed(artifact, STAGE1_FIELDS)
            or artifact["package_id"] != package["id"]
            or artifact["condition_id"] != condition
            or not isinstance(artifact["source_audit_id"], str)
            or not artifact["source_audit_id"]
            or not valid_hash(artifact["source_audit_binding_sha256"])
            or not isinstance(artifact["source_response"], str)
            or not artifact["source_response"]
        ):
            return False
        raw = _stage1_raw_bytes(artifact, raw_artifacts)
        if raw is None or sha256(raw) != artifact["raw_response_sha256"]:
            return False
        parsed_response, parsed_abstraction = parse_source_response(raw, condition)
        if parsed_response != artifact["source_response"]:
            return False
        if hashlib.sha256(artifact["source_response"].encode()).hexdigest() != artifact["source_response_sha256"]:
            return False
        citations = artifact["citation_identifiers"]
        if not isinstance(citations, list) or not citations or not all(isinstance(item, str) and item for item in citations):
            return False
        if len(citations) != len(set(citations)):
            return False
        supplied_ids = {unit["id"] for unit in package["units"][: 8 if condition in {"C1", "C2"} else 16]}
        if not all(item.startswith(f"{package['id']}:") and item.split(":", 1)[1] in supplied_ids for item in citations):
            return False
        retained = artifact["retained_objects"]
        if not isinstance(retained, list):
            return False
        abstraction = artifact["abstraction_artifact"]
        abstraction_hash = artifact["abstraction_artifact_sha256"]
        if condition in {"C1", "C3"}:
            if parsed_abstraction is not None or abstraction is not None or abstraction_hash is not None or retained:
                return False
        else:
            expected_abstraction = structured_abstraction(parsed_abstraction, package, condition)
            if abstraction != expected_abstraction or abstraction_hash != expected_abstraction["sha256"]:
                return False
            expected_reference = {
                "id": expected_abstraction["artifact_id"],
                "kind": "abstraction_artifact",
                "sha256": expected_abstraction["sha256"],
            }
            if retained != [expected_reference]:
                return False
        body = {key: value for key, value in artifact.items() if key != "stage1_output_hash"}
        return (
            valid_hash(artifact["stage1_output_hash"])
            and sha256(body) == artifact["stage1_output_hash"]
        )
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return False


def valid_stage1_outputs(
    stage1: Any,
    audits: Any,
    sources: Any,
    targets: Any,
    order: Any,
    audit_schema: Any,
    bindings: Any,
    raw_artifacts: Mapping[str, bytes] | None = None,
) -> bool:
    try:
        from jsonschema import Draft202012Validator, FormatChecker

        if not closed(stage1, set(PACKAGE_IDS)) or not isinstance(audits, list) or len(audits) != 32:
            return False
        audit_by_id = {
            item.get("run_identifiers", {}).get("audit_id"): item for item in audits if isinstance(item, dict)
        }
        expected_audit_ids = {f"source-{package}-{condition}" for package in PACKAGE_IDS for condition in CONDITIONS}
        if set(audit_by_id) != expected_audit_ids or len(audit_by_id) != len(audits):
            return False
        validator = Draft202012Validator(audit_schema, format_checker=FormatChecker())
        for package in PACKAGE_IDS:
            if not closed(stage1[package], set(CONDITIONS)):
                return False
            source_package = next(item for item in sources["packages"] if item["id"] == package)
            for condition in CONDITIONS:
                artifact = stage1[package][condition]
                audit = audit_by_id.get(artifact.get("source_audit_id")) if isinstance(artifact, dict) else None
                raw = _stage1_raw_bytes(artifact, raw_artifacts)
                if (
                    audit is None
                    or list(validator.iter_errors(audit))
                    or not valid_stage1_output_record(artifact, source_package, condition, raw_artifacts)
                    or source_audit_binding_hash(audit) != artifact["source_audit_binding_sha256"]
                    or not semantic_audit_valid(
                        audit,
                        order,
                        sources=sources,
                        targets=targets,
                        raw_output=raw,
                        bindings=bindings,
                    )
                ):
                    return False
        return True
    except (KeyError, StopIteration, TypeError, ValueError):
        return False


def valid_source_budgets(
    sources: Any,
    bindings: Any,
    counter: Callable[[str], int] = token_count,
) -> bool:
    """Reproduce source request counts without requiring future Stage-1 outputs."""
    if not valid_sources(sources, bindings, counter):
        return False
    try:
        for package in sources["packages"]:
            for condition in CONDITIONS:
                count = counter(_source_render(package, condition, bindings))
                if count != package["token_accounting"]["condition_counts"][condition] or count > TOKEN_CEILINGS[condition]:
                    return False
        return True
    except Exception:
        return False


def valid_target_budgets(
    sources: Any,
    targets: Any,
    keys: Any,
    rubrics: Any,
    bindings: Any,
    order: Any,
    audit_schema: Any,
    counter: Callable[[str], int] = token_count,
) -> bool:
    """Validate retained Stage-1 artifacts and all rendered target request budgets."""
    if not valid_targets(targets, keys, rubrics) or not bindings_valid(bindings, require_scorer=True):
        return False
    stage1 = targets.get("stage1_outputs") if isinstance(targets, dict) else None
    accounting = targets.get("target_package_accounting") if isinstance(targets, dict) else None
    if not valid_stage1_outputs(
        stage1,
        targets.get("source_execution_audits"),
        sources,
        targets,
        order,
        audit_schema,
        bindings,
    ) or not closed(accounting, set(TARGET_IDS)):
        return False
    try:
        for target in targets["targets"]:
            target_accounting = accounting[target["id"]]
            if not closed(target_accounting, set(CONDITIONS)):
                return False
            for condition in CONDITIONS:
                rendered = _target_render(target, condition, bindings, stage1)
                count = counter(rendered)
                entry = target_accounting[condition]
                fields = {
                    "retention_instruction_sha256",
                    "target_prompt_sha256",
                    "rendered_package_sha256",
                    "token_count",
                    "token_ceiling",
                    "truncation",
                    "compression",
                    "substitution",
                }
                if not closed(entry, fields) or not valid_hash(entry["retention_instruction_sha256"]):
                    return False
                if not valid_hash(entry["target_prompt_sha256"]) or not valid_hash(entry["rendered_package_sha256"]):
                    return False
                if not integer(entry["token_count"]) or entry["token_ceiling"] != TOKEN_CEILINGS[condition]:
                    return False
                if any(entry[name] is not False for name in ("truncation", "compression", "substitution")):
                    return False
                if count != entry["token_count"] or count > TOKEN_CEILINGS[condition]:
                    return False
                if sha256(rendered.encode()) != entry["rendered_package_sha256"]:
                    return False
                if hashlib.sha256(target["target_prompt"].encode()).hexdigest() != entry["target_prompt_sha256"]:
                    return False
                instruction = bindings["retention_instructions"][condition]
                if hashlib.sha256(instruction.encode()).hexdigest() != entry["retention_instruction_sha256"]:
                    return False
        return True
    except Exception:
        return False


def preregistration_matches(
    sources: Any,
    manifest: Any,
    current_bytes: bytes,
    pinned_bytes: bytes,
    *,
    commit_is_merged: bool,
) -> bool:
    try:
        external = manifest["external_files"]
        return (
            commit_is_merged
            and sources["preregistration_path"] == PREREGISTRATION_PATH
            and sources["preregistration_commit"] == PREREGISTRATION_COMMIT
            and sources["preregistration_sha256"] == PREREGISTRATION_SHA256
            and sha256(current_bytes) == PREREGISTRATION_SHA256
            and sha256(pinned_bytes) == PREREGISTRATION_SHA256
            and current_bytes == pinned_bytes
            and external == [{"path": PREREGISTRATION_PATH, "sha256": PREREGISTRATION_SHA256}]
        )
    except (KeyError, TypeError):
        return False


def canonical_analysis_order(targets: Any) -> list[dict[str, str]] | None:
    if not isinstance(targets, dict) or not isinstance(targets.get("targets"), list):
        return None
    by_pair = {
        (item.get("package_id"), item.get("family")): item.get("id")
        for item in targets["targets"]
        if isinstance(item, dict)
    }
    if set(by_pair) != {(package, family) for package in PACKAGE_IDS for family in FAMILIES}:
        return None
    return [
        {"package_id": package, "target_family": family, "target_id": by_pair[(package, family)], "condition_id": condition}
        for package in PACKAGE_IDS
        for family in FAMILIES
        for condition in CONDITIONS
    ]


def valid_condition_order(order: Any, targets: Any = None) -> bool:
    try:
        fields = {
            "schema_version",
            "seed",
            "canonical_source_order",
            "canonical_target_order",
            "target_condition_blocks",
            "verification_hash",
            "status",
        }
        if not closed(order, fields) or order["schema_version"] != "1" or order["seed"] != SEED:
            return False
        source_order = [{"package_id": package, "condition_id": condition} for package in PACKAGE_IDS for condition in CONDITIONS]
        if order["canonical_source_order"] != source_order:
            return False
        expected_analysis = canonical_analysis_order(targets)
        if expected_analysis is None or order["canonical_target_order"] != expected_analysis:
            return False
        blocks = order["target_condition_blocks"]
        expected_pairs = [(package, family) for package in PACKAGE_IDS for family in FAMILIES]
        if not isinstance(blocks, list) or [
            (item.get("package_id"), item.get("target_family")) if isinstance(item, dict) else (None, None) for item in blocks
        ] != expected_pairs:
            return False
        for block in blocks:
            if not closed(block, {"package_id", "target_family", "digest_sha256", "execution_conditions"}):
                return False
            digest_input, digest, integer_value, permutation = condition_permutation(block["package_id"], block["target_family"])
            if digest_input != f"context-transfer-condition-order-v1|{SEED}|{block['package_id']}|{block['target_family']}":
                return False
            if int(digest[:16], 16) != integer_value or block["digest_sha256"] != digest:
                return False
            if block["execution_conditions"] != permutation or sorted(permutation) != CONDITIONS or len(set(permutation)) != 4:
                return False
        return valid_hash(order["verification_hash"]) and order["verification_hash"] == sha256(blocks) and order["status"] == "READY"
    except (KeyError, TypeError, ValueError):
        return False


def manifest_anchor_valid(
    anchor: Any,
    manifest_bytes: bytes,
    evidence: Any,
) -> bool:
    """Bind current artifacts to the manifest at the exact commit frozen by the external anchor."""
    try:
        fields = {"schema_version", "algorithm", "manifest_path", "manifest_sha256", "manifest_commit"}
        return (
            closed(anchor, fields)
            and anchor["schema_version"] == "1"
            and anchor["algorithm"] == "sha256"
            and anchor["manifest_path"] == MANIFEST_NAME
            and valid_hash(anchor["manifest_sha256"])
            and re.fullmatch(r"[0-9a-f]{40}", anchor["manifest_commit"]) is not None
            and closed(
                evidence,
                {
                    "introduction_commit",
                    "frozen_anchor_bytes",
                    "anchored_commit",
                    "anchored_manifest_bytes",
                    "introduction_is_ancestor",
                    "anchored_commit_exists",
                    "anchored_commit_is_ancestor",
                    "manifest_found_at_anchor_commit",
                },
            )
            and evidence["introduction_is_ancestor"] is True
            and evidence["anchored_commit_exists"] is True
            and evidence["anchored_commit_is_ancestor"] is True
            and evidence["manifest_found_at_anchor_commit"] is True
            and re.fullmatch(r"[0-9a-f]{40}", evidence["introduction_commit"]) is not None
            and anchor["manifest_commit"] == evidence["anchored_commit"]
            and anchor["manifest_commit"] != evidence["introduction_commit"]
            and evidence["frozen_anchor_bytes"] == canonical_bytes(anchor) + b"\n"
            and evidence["anchored_manifest_bytes"] == manifest_bytes
            and sha256(evidence["anchored_manifest_bytes"]) == anchor["manifest_sha256"]
            and sha256(manifest_bytes) == anchor["manifest_sha256"]
        )
    except (KeyError, TypeError):
        return False


def hashes_complete(
    manifest: Any,
    files: Mapping[str, bytes],
    preregistration_bytes: bytes,
    anchor_evidence: Any,
) -> bool:
    try:
        if not closed(manifest, {"schema_version", "algorithm", "files", "external_files"}):
            return False
        if manifest["schema_version"] != "1" or manifest["algorithm"] != "sha256":
            return False
        records = manifest["files"]
        if not isinstance(records, list):
            return False
        paths = [item.get("path") if isinstance(item, dict) else None for item in records]
        expected_files = PACKAGE_FILES | {MANIFEST_NAME, MANIFEST_ANCHOR_NAME}
        if set(paths) != PACKAGE_FILES or len(paths) != len(set(paths)) or set(files) != expected_files:
            return False
        if not all(
            closed(item, {"path", "sha256"})
            and valid_hash(item["sha256"])
            and sha256(files[item["path"]]) == item["sha256"]
            for item in records
        ):
            return False
        anchor = json.loads(files[MANIFEST_ANCHOR_NAME])
        return (
            manifest["external_files"] == [{"path": PREREGISTRATION_PATH, "sha256": sha256(preregistration_bytes)}]
            and manifest_anchor_valid(anchor, files[MANIFEST_NAME], anchor_evidence)
        )
    except (KeyError, TypeError):
        return False


def valid_audit_schema(schema: Any) -> bool:
    try:
        from jsonschema import Draft202012Validator, FormatChecker

        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema, format_checker=FormatChecker())
        if not closed(schema, {"$schema", "type", "additionalProperties", "oneOf", "properties", "$defs"}):
            return False
        if schema["type"] != "object" or schema["additionalProperties"] is not False:
            return False
        if set(schema["properties"]) != {
            "run_identifiers",
            "hashes",
            "token_accounting",
            "model_binding",
            "response",
            "evaluator",
            "condition_order",
            "credential_boundary",
            "operator_actions",
            "scorer_image_sha256",
        }:
            return False
        if set(schema["$defs"]) < {
            "sha256",
            "canonical_request",
            "abstraction_artifact",
            "abstraction_provenance",
            "response",
            "pre_execution",
            "source_execution",
            "target_execution",
        }:
            return False
        stack = [schema]
        while stack:
            item = stack.pop()
            if isinstance(item, dict):
                if item.get("type") == "object" and "properties" in item and item.get("additionalProperties") is not False:
                    return False
                if "pattern" in item and item.get("type") != "string":
                    return False
                stack.extend(item.values())
            elif isinstance(item, list):
                stack.extend(item)
        return True
    except Exception:
        return False


def source_audit_capable(schema: Any) -> bool:
    try:
        if not valid_audit_schema(schema):
            return False
        source = schema["$defs"]["source_execution"]
        response_required = set(schema["$defs"]["response"]["required"])
        request_required = set(schema["$defs"]["canonical_request"]["required"])
        return (
            "scorer_image_sha256" in source["required"]
            and {
                "raw_response_sha256",
                "parsed_final_response",
                "parsed_final_response_sha256",
                "abstraction_artifact",
                "abstraction_artifact_sha256",
                "stage1_output_hash",
            }
            <= response_required
            and {
                "endpoint",
                "system_prompt",
                "rendered_user_prompt",
                "supplied_inputs",
                "model",
                "decoding",
                "tools",
                "tool_choice",
            }
            <= request_required
        )
    except (KeyError, TypeError):
        return False


def target_audit_capable(schema: Any) -> bool:
    try:
        return source_audit_capable(schema) and "scorer_image_sha256" in schema["$defs"]["target_execution"]["required"]
    except (KeyError, TypeError):
        return False


def _parse_time(value: Any) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")) if isinstance(value, str) else None
    except ValueError:
        return None


def parse_source_response(raw_response: bytes, condition: str) -> tuple[str, str | None]:
    try:
        text = raw_response.decode("utf-8", "strict")
    except (AttributeError, UnicodeDecodeError) as error:
        raise ValueError("undecodable source response") from error
    if not text:
        raise ValueError("empty source response")
    delimiter = "\nABSTRACTION:\n"
    if condition in {"C1", "C3"}:
        if delimiter in text:
            raise ValueError("context-only response contains abstraction delimiter")
        return text, None
    if condition not in {"C2", "C4"} or text.count(delimiter) != 1:
        raise ValueError("malformed abstraction delimiter")
    final_response, abstraction = text.split(delimiter)
    if not final_response or not abstraction:
        raise ValueError("empty parsed source object")
    return final_response, abstraction


def _retained_response_bytes(response: Any, supplied_bytes: bytes | None) -> bytes | None:
    try:
        inline = response["retained_raw_response_utf8"]
        reference = response["immutable_artifact_reference"]
        if isinstance(inline, str) and reference is None:
            raw = inline.encode("utf-8")
            return raw if supplied_bytes is None or supplied_bytes == raw else None
        if inline is None and closed(reference, {"path", "sha256"}) and isinstance(supplied_bytes, bytes):
            return supplied_bytes if valid_hash(reference["sha256"]) and sha256(supplied_bytes) == reference["sha256"] else None
        return None
    except (KeyError, TypeError):
        return None


def semantic_audit_valid(
    record: Any,
    order: Any,
    *,
    sources: Any = None,
    targets: Any = None,
    keys: Any = None,
    rubrics: Any = None,
    raw_output: bytes | None = None,
    bindings: Any = EXPECTED_BINDINGS,
) -> bool:
    """Validate canonical requests, retained responses, lineage, order, budgets, and scores."""
    try:
        run = record["run_identifiers"]
        state = run["execution_state"]
        if state == "PRE_EXECUTION_NULL":
            return all(
                isinstance(value, dict) and value.get("status") == "NULL"
                for key, value in record.items()
                if key != "run_identifiers"
            )
        if not bindings_valid(bindings, require_scorer=True):
            return False
        if record["scorer_image_sha256"] != bindings["scorer_image_sha256"] or not valid_hash(record["scorer_image_sha256"]):
            return False
        binding = record["model_binding"]
        request = binding["request"]
        hashes = record["hashes"]
        response = record["response"]
        accounting = record["token_accounting"]
        start, end = _parse_time(binding["started_at"]), _parse_time(binding["ended_at"])
        if not start or not end or end < start or (end - start).total_seconds() > bindings["timeout_seconds"]:
            return False
        request_hash = sha256(request)
        if hashes["request_sha256"] != binding["request_sha256"] or request_hash != binding["request_sha256"]:
            return False
        retained_bytes = _retained_response_bytes(response, raw_output)
        if retained_bytes is None or sha256(retained_bytes) != response["raw_response_sha256"]:
            return False
        if hashes["raw_response_sha256"] != response["raw_response_sha256"]:
            return False
        if hashlib.sha256(response["parsed_final_response"].encode()).hexdigest() != response["parsed_final_response_sha256"]:
            return False
        if record["credential_boundary"] != {"request_count": 1, "retry": False}:
            return False
        condition = run["condition_id"]
        if accounting["tokenizer"] != "tiktoken==0.9.0/o200k_base" or accounting["token_ceiling"] != TOKEN_CEILINGS[condition]:
            return False
        if not integer(accounting["token_count"]) or accounting["token_count"] > accounting["token_ceiling"] or accounting["budget_result"] is not True:
            return False
        actions = record["operator_actions"]
        times = [_parse_time(action["recorded_at"]) for action in actions]
        names = [action["action"] for action in actions]
        if not all(times) or times != sorted(times) or names.count("request") != 1:
            return False
        if not {"request", "response_retained", "offline_evaluation"} <= set(names):
            return False
        if not names.index("request") < names.index("response_retained") < names.index("offline_evaluation"):
            return False
        position = record["condition_order"]["position"]
        if not integer(position, minimum=1) or position > 4 or record["condition_order"]["condition_id"] != condition:
            return False
        package = next((item for item in sources.get("packages", []) if item.get("id") == run["package_id"]), None)
        if package is None:
            return False
        if state == "SOURCE_EXECUTION_BOUND":
            if run["invocation"] != "source" or run["target_id"] is not None or run["target_family"] is not None or record["evaluator"] is not None:
                return False
            if position != CONDITIONS.index(condition) + 1:
                return False
            expected_units = package["units"][: 8 if condition in {"C1", "C2"} else 16]
            if accounting["supplied_source_unit_ids"] != [item["id"] for item in expected_units]:
                return False
            if accounting["supplied_source_unit_hashes"] != [item["sha256"] for item in expected_units]:
                return False
            expected_request = canonical_source_request(package, condition, bindings)
            if request != expected_request:
                return False
            rendered = _source_render(package, condition, bindings)
            final_response, abstraction = parse_source_response(retained_bytes, condition)
            stage1 = targets.get("stage1_outputs")
            artifact = stage1.get(run["package_id"], {}).get(condition) if isinstance(stage1, dict) else None
            artifact_reference = artifact.get("immutable_artifact_reference") if isinstance(artifact, dict) else None
            artifact_raw = (
                {artifact_reference["path"]: retained_bytes}
                if isinstance(artifact_reference, dict) and isinstance(artifact_reference.get("path"), str)
                else None
            )
            if not valid_stage1_output_record(artifact, package, condition, artifact_raw):
                return False
            expected_abstraction = structured_abstraction(abstraction, package, condition) if abstraction is not None else None
            return (
                artifact["package_id"] == run["package_id"]
                and artifact["condition_id"] == condition
                and artifact["source_audit_id"] == run["audit_id"]
                and artifact["source_audit_binding_sha256"] == source_audit_binding_hash(record)
                and artifact["retained_raw_response_utf8"] == response["retained_raw_response_utf8"]
                and artifact["immutable_artifact_reference"] == response["immutable_artifact_reference"]
                and response["parsed_final_response"] == final_response == artifact["source_response"]
                and response["parsed_final_response_sha256"] == artifact["source_response_sha256"]
                and response["abstraction_artifact"] == expected_abstraction == artifact["abstraction_artifact"]
                and response["abstraction_artifact_sha256"] == artifact["abstraction_artifact_sha256"]
                and response["stage1_output_hash"] == artifact["stage1_output_hash"]
                and response["raw_response_sha256"] == artifact["raw_response_sha256"]
                and hashes["package_sha256"] == package["package_hash"] == accounting["package_record_sha256"]
                and accounting["target_record_sha256"] == "0" * 64
                and accounting["rendered_input_sha256"] == sha256(rendered.encode())
                and accounting["token_count"] == token_count(rendered)
                and accounting["source_prompt_sha256"] == EXPECTED_BINDINGS["hashes"]["source_prompt_template"]
                and accounting["target_prompt_sha256"] == "0" * 64
            )
        if state != "TARGET_EXECUTION_BOUND" or run["invocation"] != "target":
            return False
        target = next((item for item in targets.get("targets", []) if item.get("id") == run["target_id"]), None)
        if target is None or target["package_id"] != run["package_id"] or target["family"] != run["target_family"]:
            return False
        block = next(
            (
                item
                for item in order["target_condition_blocks"]
                if item["package_id"] == run["package_id"] and item["target_family"] == run["target_family"]
            ),
            None,
        )
        if block is None or block["execution_conditions"][position - 1] != condition:
            return False
        stage1_artifact = targets.get("stage1_outputs", {}).get(run["package_id"], {}).get(condition)
        if not valid_stage1_output_record(stage1_artifact, package, condition):
            return False
        expected_request = canonical_target_request(target, condition, bindings, targets["stage1_outputs"])
        if request != expected_request:
            return False
        key_records = _registry_records(keys, "key")
        rubric_records = _registry_records(rubrics, "rubric")
        if key_records is None or rubric_records is None:
            return False
        key = next((item for item in key_records if sha256(item) == target["answer_key_sha256"]), None)
        rubric = next((item for item in rubric_records if sha256(item) == target["scope_rubric_sha256"]), None)
        if key is None or rubric is None:
            return False
        expected_evaluator = evaluate(
            retained_bytes,
            {"id": target["id"], "answer_key_sha256": target["answer_key_sha256"], "scope_rubric_sha256": target["scope_rubric_sha256"]},
            key,
            rubric,
        )
        rendered = _target_render(target, condition, bindings, targets["stage1_outputs"])
        target_accounting = targets["target_package_accounting"][target["id"]][condition]
        return (
            record["evaluator"] == expected_evaluator
            and response["parsed_final_response"] == retained_bytes.decode("utf-8", "strict")
            and response["abstraction_artifact"] is None
            and response["abstraction_artifact_sha256"] is None
            and response["stage1_output_hash"] is None
            and hashes["package_sha256"] == package["package_hash"] == accounting["package_record_sha256"]
            and target["target_record_hash"] == accounting["target_record_sha256"]
            and accounting["rendered_input_sha256"] == sha256(rendered.encode()) == target_accounting["rendered_package_sha256"]
            and accounting["token_count"] == token_count(rendered) == target_accounting["token_count"]
            and accounting["source_prompt_sha256"] == EXPECTED_BINDINGS["hashes"]["source_prompt_template"]
            and accounting["target_prompt_sha256"] == EXPECTED_BINDINGS["hashes"]["target_prompt_template"]
            and accounting["supplied_source_unit_ids"] == []
            and accounting["supplied_source_unit_hashes"] == []
        )
    except Exception:
        return False


def evaluator_valid(manifest: Any, files: Mapping[str, bytes]) -> bool:
    try:
        record = next(item for item in manifest["files"] if item["path"] == "execution_package.py")
        key = {"required_literals": ["yes"], "forbidden_literals": ["no"]}
        rubric = {
            "relation_literals": ["relation"],
            "required_applicability_literals": ["applicable"],
            "forbidden_applicability_literals": [],
        }
        target = {"id": "T01", "answer_key_sha256": sha256(key), "scope_rubric_sha256": sha256(rubric)}
        return (
            record["sha256"] == sha256(files["execution_package.py"])
            and evaluate(b"yes relation applicable", target, key, rubric)["score"] is True
            and evaluate(b"no relation applicable", target, key, rubric)["score"] is False
        )
    except (KeyError, StopIteration, TypeError, ValueError):
        return False


def no_execution_occurred(files: Mapping[str, bytes]) -> bool:
    forbidden = re.compile(r"(^|[-_])(raw[-_]?output|model[-_]?output|execution[-_]?evidence|audit[-_]?record)([-_.]|$)", re.I)
    return set(files) == PACKAGE_FILES | {MANIFEST_NAME, MANIFEST_ANCHOR_NAME} and not any(
        forbidden.search(name) for name in files
    )


def invocation_boundary_valid(files: Mapping[str, bytes]) -> bool:
    """Require validator-only Python with no model/network client imports or calls."""
    try:
        tree = ast.parse(files["execution_package.py"].decode("utf-8"))
        forbidden_imports = {"openai", "requests", "httpx", "urllib", "socket", "aiohttp"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import) and any(item.name.split(".")[0] in forbidden_imports for item in node.names):
                return False
            if isinstance(node, ast.ImportFrom) and node.module and node.module.split(".")[0] in forbidden_imports:
                return False
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and re.search(r"invoke|execute_model|send_request", node.name):
                return False
        return True
    except (KeyError, UnicodeDecodeError, SyntaxError):
        return False


SOURCE_CHECK_NAMES = (
    "PREREGISTRATION_MATCH",
    "EIGHT_SOURCE_PACKAGES",
    "TARGET_ROSTER_VALID",
    "SOURCE_INPUT_BUDGET_VALID",
    "PROMPTS_MATCH",
    "SCORER_IMAGE_BOUND",
    "HASHES_COMPLETE",
    "CONDITION_ORDER_VALID",
    "EVALUATOR_VALID",
    "AUDIT_MANIFEST_COMPLETE",
    "SOURCE_AUDIT_CAPABLE",
    "NO_EXECUTION_OCCURRED",
    "INVOCATION_BOUNDARY_VALID",
)
TARGET_CHECK_NAMES = (
    "STAGE1_OUTPUTS_VALID",
    "TARGET_PACKAGE_BUDGET_VALID",
    "TARGET_AUDIT_CAPABLE",
)
CHECK_NAMES = SOURCE_CHECK_NAMES + TARGET_CHECK_NAMES + ("SOURCE_STAGE_READY", "TARGET_STAGE_READY")


def readiness_from_bytes(
    files: Mapping[str, bytes],
    preregistration_bytes: bytes,
    pinned_preregistration_bytes: bytes,
    *,
    commit_is_merged: bool,
    anchor_evidence: Any,
    counter: Callable[[str], int] = token_count,
) -> dict[str, Any]:
    try:
        parsed = {name: json.loads(files[name]) for name in JSON_INPUTS}
        sources = parsed["source-package-registry.json"]
        targets = parsed["target-registry.json"]
        bindings = parsed["prompt-bindings.json"]
        keys = parsed["answer-key-registry.json"]
        rubrics = parsed["scope-rubric-registry.json"]
        manifest = parsed["hash-manifest.json"]
        order = parsed["condition-order.json"]
        audit_schema = parsed["audit-manifest-schema.json"]
        source_checks = {
            "PREREGISTRATION_MATCH": preregistration_matches(
                sources,
                manifest,
                preregistration_bytes,
                pinned_preregistration_bytes,
                commit_is_merged=commit_is_merged,
            ),
            "EIGHT_SOURCE_PACKAGES": valid_sources(sources, bindings, counter),
            "TARGET_ROSTER_VALID": valid_targets(targets, keys, rubrics),
            "SOURCE_INPUT_BUDGET_VALID": valid_source_budgets(sources, bindings, counter),
            "PROMPTS_MATCH": bindings_valid(bindings),
            "SCORER_IMAGE_BOUND": bindings_valid(bindings, require_scorer=True),
            "HASHES_COMPLETE": hashes_complete(manifest, files, preregistration_bytes, anchor_evidence),
            "CONDITION_ORDER_VALID": valid_condition_order(order, targets),
            "EVALUATOR_VALID": evaluator_valid(manifest, files),
            "AUDIT_MANIFEST_COMPLETE": valid_audit_schema(audit_schema),
            "SOURCE_AUDIT_CAPABLE": source_audit_capable(audit_schema),
            "NO_EXECUTION_OCCURRED": no_execution_occurred(files),
            "INVOCATION_BOUNDARY_VALID": invocation_boundary_valid(files),
        }
        source_ready = all(source_checks.values())
        target_checks = {
            "STAGE1_OUTPUTS_VALID": valid_stage1_outputs(
                targets.get("stage1_outputs"),
                targets.get("source_execution_audits"),
                sources,
                targets,
                order,
                audit_schema,
                bindings,
            ),
            "TARGET_PACKAGE_BUDGET_VALID": valid_target_budgets(
                sources, targets, keys, rubrics, bindings, order, audit_schema, counter
            ),
            "TARGET_AUDIT_CAPABLE": target_audit_capable(audit_schema),
        }
        target_ready = source_ready and all(target_checks.values())
        checks = {
            **source_checks,
            **target_checks,
            "SOURCE_STAGE_READY": source_ready,
            "TARGET_STAGE_READY": target_ready,
        }
    except (KeyError, TypeError, ValueError, json.JSONDecodeError, UnicodeDecodeError):
        checks = {name: False for name in CHECK_NAMES}
        source_ready = False
        target_ready = False
    reasons = [f"READINESS_{name}_FAILED" for name, passed in checks.items() if not passed]
    return {
        "outcome": "READY" if target_ready else "NULL",
        "source_stage": "READY" if source_ready else "NULL",
        "target_stage": "READY" if target_ready else "NULL",
        "checks": checks,
        "reasons": reasons,
    }


def _pinned_preregistration() -> tuple[bytes, bool]:
    try:
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", PREREGISTRATION_COMMIT, "origin/main"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        pinned = subprocess.check_output(["git", "show", f"{PREREGISTRATION_COMMIT}:{PREREGISTRATION_PATH}"], cwd=ROOT)
        return pinned, True
    except (OSError, subprocess.CalledProcessError):
        return b"", False


def _manifest_anchor_evidence() -> dict[str, Any]:
    package_relative = PACKAGE.relative_to(ROOT).as_posix()
    anchor_path = f"{package_relative}/{MANIFEST_ANCHOR_NAME}"
    manifest_path = f"{package_relative}/{MANIFEST_NAME}"
    empty = {
        "introduction_commit": "",
        "frozen_anchor_bytes": b"",
        "anchored_commit": "",
        "anchored_manifest_bytes": b"",
        "introduction_is_ancestor": False,
        "anchored_commit_exists": False,
        "anchored_commit_is_ancestor": False,
        "manifest_found_at_anchor_commit": False,
    }
    try:
        additions = subprocess.check_output(
            ["git", "log", "--diff-filter=A", "--format=%H", "--", anchor_path], cwd=ROOT, text=True
        ).splitlines()
        if len(additions) != 1:
            return empty
        introduction = additions[0]
        frozen_anchor_bytes = subprocess.check_output(["git", "show", f"{introduction}:{anchor_path}"], cwd=ROOT)
        frozen_anchor = json.loads(frozen_anchor_bytes)
        anchored_commit = frozen_anchor["manifest_commit"]
        anchored_manifest_path = f"{package_relative}/{frozen_anchor['manifest_path']}"
        subprocess.run(
            ["git", "cat-file", "-e", f"{anchored_commit}^{{commit}}"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", introduction, "HEAD"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", anchored_commit, "HEAD"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        anchored_manifest_bytes = subprocess.check_output(
            ["git", "show", f"{anchored_commit}:{anchored_manifest_path}"], cwd=ROOT
        )
        return {
            "introduction_commit": introduction,
            "frozen_anchor_bytes": frozen_anchor_bytes,
            "anchored_commit": anchored_commit,
            "anchored_manifest_bytes": anchored_manifest_bytes,
            "introduction_is_ancestor": True,
            "anchored_commit_exists": True,
            "anchored_commit_is_ancestor": True,
            "manifest_found_at_anchor_commit": True,
        }
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError):
        return empty


def readiness() -> dict[str, Any]:
    try:
        pinned, merged = _pinned_preregistration()
        return readiness_from_bytes(
            package_bytes(),
            PREREGISTRATION.read_bytes(),
            pinned,
            commit_is_merged=merged,
            anchor_evidence=_manifest_anchor_evidence(),
        )
    except OSError:
        checks = {name: False for name in CHECK_NAMES}
        return {
            "outcome": "NULL",
            "source_stage": "NULL",
            "target_stage": "NULL",
            "checks": checks,
            "reasons": [f"READINESS_{name}_FAILED" for name in CHECK_NAMES],
        }


def main() -> None:
    print(json.dumps(readiness(), sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
