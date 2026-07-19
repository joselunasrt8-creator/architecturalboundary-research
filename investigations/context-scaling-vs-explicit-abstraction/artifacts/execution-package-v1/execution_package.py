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
    "Return the source-specific answer, then exactly one line ABSTRACTION:, then the abstraction containing "
    "principle, applicability conditions, limitations/failure cases, source-unit provenance for every material "
    "claim, and reuse instructions."
)
EXPECTED_BINDINGS = {
    "schema_version": "1",
    "endpoint": "https://api.openai.com/v1/responses",
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
    return {name: (package_dir / name).read_bytes() for name in PACKAGE_FILES | {"hash-manifest.json"}}


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


def bindings_valid(bindings: Any) -> bool:
    return bindings == EXPECTED_BINDINGS


def _source_render(package: dict[str, Any], condition: str, bindings: dict[str, Any]) -> str:
    units = package["units"][: 8 if condition in {"C1", "C2"} else 16]
    unit_text = "\n".join(f"{unit['id']}: {unit['content']}" for unit in units)
    user = bindings["source_prompt_template"].format(
        package_id=package["id"],
        condition_id=condition,
        source_units=unit_text,
        retention_instruction=bindings["retention_instructions"][condition],
    )
    return bindings["system_prompt"] + "\n\n" + user


def _retained_package(artifact: dict[str, Any], condition: str) -> str:
    lines = ["SOURCE RESPONSE:", artifact["source_response"], "CITATION IDENTIFIERS:"]
    lines.extend(artifact["citation_identifiers"])
    lines.append("RETAINED OBJECTS:")
    for item in artifact["retained_objects"]:
        lines.extend((f"{item['id']}:", item["content"]))
    if condition in {"C2", "C4"}:
        lines.extend(("ABSTRACTION ARTIFACT:", artifact["abstraction_artifact"]))
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
        unit_sequences: set[tuple[str, ...]] = set()
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
            if len({unit["content"] for unit in units}) != 16 or len({unit["sha256"] for unit in units}) != 16:
                return False
            if len({unit["source_reference"] for unit in units}) != 16:
                return False
            if package["source_hashes"] != [unit["sha256"] for unit in units]:
                return False
            sequence = tuple(package["source_hashes"])
            if sequence in unit_sequences:
                return False
            unit_sequences.add(sequence)
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
    "retained_package_accounting",
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
            accounting = target["retained_package_accounting"]
            if not closed(accounting, set(CONDITIONS)):
                return False
            for condition in CONDITIONS:
                entry = accounting[condition]
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
                if not closed(entry, fields) or not valid_hash(entry["retention_instruction_sha256"]) or not valid_hash(
                    entry["target_prompt_sha256"]
                ) or not valid_hash(entry["rendered_package_sha256"]):
                    return False
                if not integer(entry["token_count"]) or entry["token_ceiling"] != TOKEN_CEILINGS[condition]:
                    return False
                if any(entry[name] is not False for name in ("truncation", "compression", "substitution")):
                    return False
            body = {key_name: value for key_name, value in target.items() if key_name != "target_record_hash"}
            if not valid_hash(target["target_record_hash"]) or sha256(body) != target["target_record_hash"]:
                return False
        return used_keys == set(key_by_hash) and used_rubrics == set(rubric_by_hash)
    except (KeyError, TypeError, ValueError):
        return False


STAGE1_FIELDS = {
    "source_response",
    "source_response_sha256",
    "abstraction_artifact",
    "abstraction_artifact_sha256",
    "citation_identifiers",
    "retained_objects",
}


def valid_stage1_outputs(stage1: Any) -> bool:
    try:
        if not closed(stage1, set(PACKAGE_IDS)):
            return False
        for package in PACKAGE_IDS:
            if not closed(stage1[package], set(CONDITIONS)):
                return False
            for condition in CONDITIONS:
                artifact = stage1[package][condition]
                if not closed(artifact, STAGE1_FIELDS) or not isinstance(artifact["source_response"], str) or not artifact[
                    "source_response"
                ]:
                    return False
                if hashlib.sha256(artifact["source_response"].encode()).hexdigest() != artifact["source_response_sha256"]:
                    return False
                citations = artifact["citation_identifiers"]
                if not isinstance(citations, list) or not citations or not all(isinstance(item, str) and item for item in citations):
                    return False
                if len(citations) != len(set(citations)):
                    return False
                retained = artifact["retained_objects"]
                if not isinstance(retained, list) or not all(
                    closed(item, {"id", "content", "sha256"})
                    and isinstance(item["id"], str)
                    and item["id"]
                    and isinstance(item["content"], str)
                    and item["content"]
                    and hashlib.sha256(item["content"].encode()).hexdigest() == item["sha256"]
                    for item in retained
                ):
                    return False
                abstraction = artifact["abstraction_artifact"]
                abstraction_hash = artifact["abstraction_artifact_sha256"]
                if condition in {"C1", "C3"}:
                    if abstraction is not None or abstraction_hash is not None or retained:
                        return False
                else:
                    if not isinstance(abstraction, str) or not abstraction or hashlib.sha256(abstraction.encode()).hexdigest() != abstraction_hash:
                        return False
                    if len(retained) != 1 or retained[0]["content"] != abstraction or retained[0]["sha256"] != abstraction_hash:
                        return False
        return True
    except (KeyError, TypeError):
        return False


def valid_token_budgets(
    sources: Any,
    targets: Any,
    keys: Any,
    rubrics: Any,
    bindings: Any,
    counter: Callable[[str], int] = token_count,
) -> bool:
    """Reproduce every stored source/target count and enforce all four ceilings."""
    if not valid_sources(sources, bindings, counter) or not valid_targets(targets, keys, rubrics):
        return False
    stage1 = targets.get("stage1_outputs") if isinstance(targets, dict) else None
    if not valid_stage1_outputs(stage1):
        return False
    try:
        for package in sources["packages"]:
            for condition in CONDITIONS:
                count = counter(_source_render(package, condition, bindings))
                if count != package["token_accounting"]["condition_counts"][condition] or count > TOKEN_CEILINGS[condition]:
                    return False
        for target in targets["targets"]:
            for condition in CONDITIONS:
                rendered = _target_render(target, condition, bindings, stage1)
                count = counter(rendered)
                accounting = target["retained_package_accounting"][condition]
                if count != accounting["token_count"] or count > TOKEN_CEILINGS[condition]:
                    return False
                if sha256(rendered.encode()) != accounting["rendered_package_sha256"]:
                    return False
                if hashlib.sha256(target["target_prompt"].encode()).hexdigest() != accounting["target_prompt_sha256"]:
                    return False
                instruction = bindings["retention_instructions"][condition]
                if hashlib.sha256(instruction.encode()).hexdigest() != accounting["retention_instruction_sha256"]:
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


def hashes_complete(manifest: Any, files: Mapping[str, bytes], preregistration_bytes: bytes) -> bool:
    try:
        if not closed(manifest, {"schema_version", "algorithm", "files", "external_files"}):
            return False
        if manifest["schema_version"] != "1" or manifest["algorithm"] != "sha256":
            return False
        records = manifest["files"]
        if not isinstance(records, list):
            return False
        paths = [item.get("path") if isinstance(item, dict) else None for item in records]
        if set(paths) != PACKAGE_FILES or len(paths) != len(set(paths)) or set(files) != PACKAGE_FILES | {"hash-manifest.json"}:
            return False
        if not all(
            closed(item, {"path", "sha256"})
            and valid_hash(item["sha256"])
            and sha256(files[item["path"]]) == item["sha256"]
            for item in records
        ):
            return False
        return manifest["external_files"] == [{"path": PREREGISTRATION_PATH, "sha256": sha256(preregistration_bytes)}]
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
        }:
            return False
        if set(schema["$defs"]) < {"sha256", "pre_execution", "source_execution", "target_execution"}:
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


def _parse_time(value: Any) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")) if isinstance(value, str) else None
    except ValueError:
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
    """Validate audit lineage, budgets, inventories, chronology, order, and scores."""
    try:
        run = record["run_identifiers"]
        state = run["execution_state"]
        if state == "PRE_EXECUTION_NULL":
            return all(isinstance(value, dict) and value.get("status") == "NULL" for key, value in record.items() if key != "run_identifiers")
        binding = record["model_binding"]
        request = binding["request"]
        hashes = record["hashes"]
        response = record["response"]
        accounting = record["token_accounting"]
        start, end = _parse_time(binding["started_at"]), _parse_time(binding["ended_at"])
        if not start or not end or end < start or (end - start).total_seconds() > 120:
            return False
        if hashes["request_sha256"] != request["request_sha256"] or hashes["raw_response_sha256"] != response["raw_response_sha256"]:
            return False
        if record["credential_boundary"] != {"request_count": 1, "retry": False}:
            return False
        if accounting["tokenizer"] != "tiktoken==0.9.0/o200k_base" or accounting["token_ceiling"] != TOKEN_CEILINGS[run["condition_id"]]:
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
        if not integer(position, minimum=1) or position > 4 or record["condition_order"]["condition_id"] != run["condition_id"]:
            return False
        if state == "SOURCE_EXECUTION_BOUND":
            if run["invocation"] != "source" or run["target_id"] is not None or run["target_family"] is not None or record["evaluator"] is not None:
                return False
            if position != CONDITIONS.index(run["condition_id"]) + 1:
                return False
            package = next((item for item in sources.get("packages", []) if item.get("id") == run["package_id"]), None)
            if package is None:
                return False
            expected_units = package["units"][: 8 if run["condition_id"] in {"C1", "C2"} else 16]
            if accounting["supplied_source_unit_ids"] != [item["id"] for item in expected_units]:
                return False
            if accounting["supplied_source_unit_hashes"] != [item["sha256"] for item in expected_units]:
                return False
            rendered = _source_render(package, run["condition_id"], bindings)
            return (
                hashes["package_sha256"] == package["package_hash"] == accounting["package_record_sha256"]
                and accounting["target_record_sha256"] == "0" * 64
                and accounting["rendered_input_sha256"] == sha256(rendered.encode())
                and accounting["token_count"] == token_count(rendered)
                and accounting["source_prompt_sha256"] == EXPECTED_BINDINGS["hashes"]["source_prompt_template"]
                and accounting["target_prompt_sha256"] == "0" * 64
            )
        if state != "TARGET_EXECUTION_BOUND" or run["invocation"] != "target" or not isinstance(raw_output, bytes):
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
        if block is None or block["execution_conditions"][position - 1] != run["condition_id"]:
            return False
        key_records = _registry_records(keys, "key")
        rubric_records = _registry_records(rubrics, "rubric")
        if key_records is None or rubric_records is None:
            return False
        key = next((item for item in key_records if sha256(item) == target["answer_key_sha256"]), None)
        rubric = next((item for item in rubric_records if sha256(item) == target["scope_rubric_sha256"]), None)
        if key is None or rubric is None:
            return False
        expected = evaluate(
            raw_output,
            {"id": target["id"], "answer_key_sha256": target["answer_key_sha256"], "scope_rubric_sha256": target["scope_rubric_sha256"]},
            key,
            rubric,
        )
        package = next((item for item in sources.get("packages", []) if item.get("id") == run["package_id"]), None)
        if package is None or not bindings_valid(bindings) or not valid_stage1_outputs(targets.get("stage1_outputs")):
            return False
        rendered = _target_render(target, run["condition_id"], bindings, targets["stage1_outputs"])
        return (
            record["evaluator"] == expected
            and response["raw_response_sha256"] == sha256(raw_output)
            and hashes["package_sha256"] == package["package_hash"] == accounting["package_record_sha256"]
            and target["target_record_hash"] == accounting["target_record_sha256"]
            and accounting["rendered_input_sha256"] == sha256(rendered.encode())
            and accounting["token_count"] == token_count(rendered)
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
    return set(files) == PACKAGE_FILES | {"hash-manifest.json"} and not any(forbidden.search(name) for name in files)


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


CHECK_NAMES = (
    "PREREGISTRATION_MATCH",
    "EIGHT_SOURCE_PACKAGES",
    "TWENTY_FOUR_TARGETS",
    "TOKEN_BUDGET_VALID",
    "PROMPTS_MATCH",
    "HASHES_COMPLETE",
    "CONDITION_ORDER_VALID",
    "EVALUATOR_VALID",
    "AUDIT_MANIFEST_COMPLETE",
    "NO_EXECUTION_OCCURRED",
    "INVOCATION_BOUNDARY_VALID",
)


def readiness_from_bytes(
    files: Mapping[str, bytes],
    preregistration_bytes: bytes,
    pinned_preregistration_bytes: bytes,
    *,
    commit_is_merged: bool,
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
        checks = {
            "PREREGISTRATION_MATCH": preregistration_matches(
                sources,
                manifest,
                preregistration_bytes,
                pinned_preregistration_bytes,
                commit_is_merged=commit_is_merged,
            ),
            "EIGHT_SOURCE_PACKAGES": valid_sources(sources, bindings, counter),
            "TWENTY_FOUR_TARGETS": valid_targets(targets, keys, rubrics),
            "TOKEN_BUDGET_VALID": valid_token_budgets(sources, targets, keys, rubrics, bindings, counter),
            "PROMPTS_MATCH": bindings_valid(bindings),
            "HASHES_COMPLETE": hashes_complete(manifest, files, preregistration_bytes),
            "CONDITION_ORDER_VALID": valid_condition_order(order, targets),
            "EVALUATOR_VALID": evaluator_valid(manifest, files),
            "AUDIT_MANIFEST_COMPLETE": valid_audit_schema(audit_schema),
            "NO_EXECUTION_OCCURRED": no_execution_occurred(files),
            "INVOCATION_BOUNDARY_VALID": invocation_boundary_valid(files),
        }
    except (KeyError, TypeError, ValueError, json.JSONDecodeError, UnicodeDecodeError):
        checks = {name: False for name in CHECK_NAMES}
    reasons = [f"READINESS_{name}_FAILED" for name, passed in checks.items() if not passed]
    return {"outcome": "READY" if all(checks.values()) else "NULL", "checks": checks, "reasons": reasons}


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


def readiness() -> dict[str, Any]:
    try:
        pinned, merged = _pinned_preregistration()
        return readiness_from_bytes(
            package_bytes(),
            PREREGISTRATION.read_bytes(),
            pinned,
            commit_is_merged=merged,
        )
    except OSError:
        checks = {name: False for name in CHECK_NAMES}
        return {
            "outcome": "NULL",
            "checks": checks,
            "reasons": [f"READINESS_{name}_FAILED" for name in CHECK_NAMES],
        }


def main() -> None:
    print(json.dumps(readiness(), sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
