#!/usr/bin/env python3
"""Deterministic Option B selector over explicit candidate-review records.

This module does not scan the repository and does not construct source packages.
The following milestone must obtain the pinned git tree, unitize candidates, and
provide review records to this selector.
"""
from __future__ import annotations

import fnmatch
import hashlib
import json
import re
import unicodedata
from importlib import metadata
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable


HERE = Path(__file__).resolve().parent
PROTOCOL_PATH = HERE / "source-selection-freeze.json"
ROOT = HERE.parents[3]
PROMPT_BINDINGS_PATH = (
    ROOT
    / "investigations/context-scaling-vs-explicit-abstraction/artifacts/execution-package-v1"
    / "prompt-bindings.json"
)
PACKAGE_IDS = [f"SP{index:02d}" for index in range(1, 9)]
CONDITIONS = ["C1", "C2", "C3", "C4"]
UNIT_IDS = [f"U{index:03d}" for index in range(1, 17)]
PROVENANCE_FIELDS = {
    "authorship_classification",
    "authorship_evidence",
    "generated",
    "provenance_clear",
    "derived_from",
}
LEAKAGE_FIELDS = {
    "contains_target_tasks",
    "contains_answer_keys",
    "contains_scope_rubrics",
    "contains_prior_experiment_outputs",
    "contains_experiment_specific_instructions",
    "selected_after_target_performance",
}
CANDIDATE_FIELDS = {
    "path",
    "commit",
    "stable_locator",
    "content_utf8",
    "blob_sha256",
    "document_role",
    "provenance",
    "units",
    "token_accounting",
    "leakage",
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_bytes())


def load_protocol() -> dict[str, Any]:
    return load_json(PROTOCOL_PATH)


def load_bindings() -> dict[str, Any]:
    return load_json(PROMPT_BINDINGS_PATH)


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def closed(value: Any, fields: set[str]) -> bool:
    return isinstance(value, dict) and set(value) == fields


def normalize_path(path: str) -> str:
    if not isinstance(path, str) or not path or path.startswith(("/", "\\")) or "\\" in path:
        raise ValueError("path must be repository-relative POSIX text")
    parts = PurePosixPath(path).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise ValueError("path traversal is prohibited")
    return unicodedata.normalize("NFKC", path)


def path_allowed(path: str, protocol: dict[str, Any]) -> bool:
    try:
        normalized_path = normalize_path(path)
        boundary = protocol["corpus_boundary"]
        if not any(normalized_path.startswith(prefix) for prefix in boundary["allowed_path_prefixes"]):
            return False
        if any(normalized_path.startswith(prefix) for prefix in boundary["excluded_path_prefixes"]):
            return False
        parts = PurePosixPath(normalized_path).parts
        if any(part in set(boundary["excluded_directory_names"]) for part in parts[:-1]):
            return False
        if any(fnmatch.fnmatchcase(parts[-1], pattern) for pattern in boundary["excluded_filename_patterns"]):
            return False
        return PurePosixPath(normalized_path).suffix in boundary["candidate_file_extensions"]
    except (KeyError, TypeError, ValueError):
        return False


def discover_candidate_paths(repository_paths: Iterable[str], protocol: dict[str, Any]) -> list[str]:
    """Filter a pinned git-tree path listing without consulting the working tree."""
    unique = {path for path in repository_paths if path_allowed(path, protocol)}
    return sorted(unique, key=lambda path: (normalize_path(path), path.encode("utf-8")))


def normalized_document(content: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", content).casefold()).strip(" ")


def word_tokens(content: str) -> list[str]:
    return re.findall(r"\w+", normalized_document(content), flags=re.UNICODE)


def shingles(content: str, size: int) -> set[tuple[str, ...]]:
    words = word_tokens(content)
    return {tuple(words[index : index + size]) for index in range(max(0, len(words) - size + 1))}


def substantial_overlap(first: str, second: str, protocol: dict[str, Any]) -> bool:
    duplicate = protocol["eligibility"]["duplicate_detection"]
    size = duplicate["shingle_size_words"]
    left, right = shingles(first, size), shingles(second, size)
    if not left or not right:
        return False
    intersection = len(left & right)
    jaccard = intersection / len(left | right)
    containment = intersection / min(len(left), len(right))
    return jaccard >= float(duplicate["substantial_overlap_jaccard_threshold"]) or containment >= float(
        duplicate["substantial_overlap_containment_threshold"]
    )


def token_count(text: str) -> int:
    import tiktoken

    if metadata.version("tiktoken") != "0.9.0":
        raise RuntimeError("tokenizer version mismatch")
    return len(tiktoken.get_encoding("o200k_base").encode(text))


def render_candidate_source(
    candidate: dict[str, Any], package_id: str, condition: str, bindings: dict[str, Any]
) -> str:
    units = candidate["units"][: 8 if condition in {"C1", "C2"} else 16]
    unit_text = "\n".join(f"{unit['id']}: {unit['content']}" for unit in units)
    user = bindings["source_prompt_template"].format(
        package_id=package_id,
        condition_id=condition,
        source_units=unit_text,
        retention_instruction=bindings["retention_instructions"][condition],
    )
    return bindings["system_prompt"] + "\n\n" + user


def candidate_token_counts(
    candidate: dict[str, Any],
    bindings: dict[str, Any],
    counter: Callable[[str], int] = token_count,
) -> dict[str, int]:
    return {
        condition: max(
            counter(render_candidate_source(candidate, package_id, condition, bindings)) for package_id in PACKAGE_IDS
        )
        for condition in CONDITIONS
    }


def _unit_errors(candidate: dict[str, Any], protocol: dict[str, Any]) -> list[str]:
    units = candidate.get("units")
    content = candidate.get("content_utf8")
    minimum_words = protocol["eligibility"]["substantive_content"]["meaningful_unit_minimum_word_tokens"]
    if not isinstance(units, list) or len(units) < 16 or not isinstance(content, str):
        return ["INSUFFICIENT_MEANINGFUL_UNITS"]
    raw = content.encode("utf-8")
    meaningful = 0
    previous_end = 0
    for index, unit in enumerate(units, start=1):
        if not closed(unit, {"id", "start_byte", "end_byte", "content", "sha256"}):
            return ["MALFORMED_UNIT_RECORD"]
        expected_id = f"U{index:03d}"
        start, end = unit["start_byte"], unit["end_byte"]
        if (
            unit["id"] != expected_id
            or not isinstance(start, int)
            or isinstance(start, bool)
            or not isinstance(end, int)
            or isinstance(end, bool)
            or start < previous_end
            or end <= start
            or end > len(raw)
        ):
            return ["NONDETERMINISTIC_UNIT_BOUNDARY"]
        unit_bytes = unit["content"].encode("utf-8") if isinstance(unit["content"], str) else b""
        if raw[start:end] != unit_bytes or sha256(unit_bytes) != unit["sha256"]:
            return ["NONVERBATIM_OR_HASH_MISMATCHED_UNIT"]
        meaningful += len(word_tokens(unit["content"])) >= minimum_words
        previous_end = end
    return [] if meaningful >= 16 else ["INSUFFICIENT_MEANINGFUL_UNITS"]


def candidate_errors(
    candidate: Any,
    protocol: dict[str, Any],
    bindings: dict[str, Any],
    counter: Callable[[str], int] = token_count,
) -> list[str]:
    if not closed(candidate, CANDIDATE_FIELDS):
        return ["MALFORMED_CANDIDATE_RECORD"]
    errors: list[str] = []
    path = candidate["path"]
    repository = protocol["repository"]
    if not path_allowed(path, protocol):
        errors.append("OUTSIDE_FROZEN_CORPUS")
    if candidate["commit"] != repository["commit"]:
        errors.append("COMMIT_BINDING_MISMATCH")
    content = candidate["content_utf8"]
    if not isinstance(content, str) or sha256(content.encode("utf-8")) != candidate["blob_sha256"]:
        errors.append("DOCUMENT_HASH_MISMATCH")
    locator = protocol["eligibility"]["stable_binding"]["stable_locator_template"].format(
        commit=repository["commit"], path=path
    )
    if candidate["stable_locator"] != locator:
        errors.append("STABLE_LOCATOR_MISMATCH")
    provenance = candidate["provenance"]
    if not closed(provenance, PROVENANCE_FIELDS):
        errors.append("MALFORMED_PROVENANCE")
    elif (
        provenance["authorship_classification"] != "HUMAN_AUTHORED"
        or not isinstance(provenance["authorship_evidence"], list)
        or not provenance["authorship_evidence"]
        or not all(isinstance(item, str) and item.strip() for item in provenance["authorship_evidence"])
        or provenance["generated"] is not False
        or provenance["provenance_clear"] is not True
        or provenance["derived_from"] != []
    ):
        errors.append("INELIGIBLE_PROVENANCE")
    if candidate["document_role"] != "SUBSTANTIVE_SOURCE":
        errors.append("INSUBSTANTIAL_OR_INDEX_ONLY_DOCUMENT")
    if not isinstance(content, str) or len(word_tokens(content)) < protocol["eligibility"]["substantive_content"][
        "minimum_unicode_word_tokens"
    ]:
        errors.append("INSUFFICIENT_SUBSTANTIVE_CONTENT")
    errors.extend(_unit_errors(candidate, protocol))
    leakage = candidate["leakage"]
    if not closed(leakage, LEAKAGE_FIELDS) or any(value is not False for value in leakage.values()):
        errors.append("EXPERIMENT_LEAKAGE")
    accounting = candidate["token_accounting"]
    accounting_fields = {
        "tokenizer_name",
        "tokenizer_package",
        "condition_counts",
        "truncation",
        "compression",
        "substitution",
    }
    budget = protocol["eligibility"]["source_budget"]
    if not closed(accounting, accounting_fields):
        errors.append("MALFORMED_TOKEN_ACCOUNTING")
    else:
        try:
            reproduced = candidate_token_counts(candidate, bindings, counter)
            counts = accounting["condition_counts"]
            if (
                accounting["tokenizer_name"] != budget["tokenizer_name"]
                or accounting["tokenizer_package"] != budget["tokenizer_package"]
                or set(counts) != set(CONDITIONS)
                or any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in counts.values())
                or counts != reproduced
                or any(counts[condition] > budget["ceilings"][condition] for condition in CONDITIONS)
                or any(accounting[name] is not False for name in ("truncation", "compression", "substitution"))
            ):
                errors.append("SOURCE_BUDGET_INELIGIBLE")
        except (KeyError, TypeError, RuntimeError):
            errors.append("SOURCE_BUDGET_INELIGIBLE")
    return errors


def validate_protocol(protocol: Any) -> bool:
    try:
        return (
            protocol["schema_version"] == "1"
            and protocol["issue"] == 96
            and protocol["protocol_status"] == "READY"
            and protocol["selected_rule"] == "B"
            and re.fullmatch(r"[0-9a-f]{40}", protocol["repository"]["commit"]) is not None
            and protocol["candidate_ordering"]["rule"]
            == "normalized repository-relative path ascending; ties by original UTF-8 path bytes ascending"
            and protocol["selection"]["required_count"] == 8
            and protocol["selection"]["fewer_than_eight_result"] == "NULL"
            and protocol["selection"]["outside_corpus_substitution"] == "PROHIBITED"
            and protocol["selection"]["manual_substitution"] == "PROHIBITED"
            and protocol["selection"]["post_outcome_selection"] == "PROHIBITED"
            and protocol["selection_execution"]["status"] == "NOT_EXECUTED"
            and protocol["construction_status"] == "NOT_STARTED"
            and all(value == "NULL" for value in protocol["source_packages"].values())
        )
    except (KeyError, TypeError):
        return False


def select_candidates(
    candidates: list[dict[str, Any]],
    protocol: dict[str, Any],
    bindings: dict[str, Any],
    counter: Callable[[str], int] = token_count,
) -> dict[str, Any]:
    """Evaluate explicit records in canonical order and select the first eight eligible documents."""
    if not validate_protocol(protocol):
        raise ValueError("invalid frozen protocol")
    ordered = sorted(candidates, key=lambda item: (normalize_path(item.get("path", "")), item.get("path", "").encode()))
    reviewed: list[dict[str, Any]] = []
    eligible: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    for candidate in ordered:
        path = candidate.get("path", "")
        errors = candidate_errors(candidate, protocol, bindings, counter)
        if path in seen_paths:
            errors.append("DUPLICATE_PATH_RECORD")
        seen_paths.add(path)
        if not errors:
            candidate_normalized_hash = sha256(normalized_document(candidate["content_utf8"]).encode("utf-8"))
            for earlier in eligible:
                if candidate_normalized_hash == earlier["normalized_sha256"]:
                    errors.append("EXACT_DUPLICATE")
                    break
                if substantial_overlap(candidate["content_utf8"], earlier["candidate"]["content_utf8"], protocol):
                    errors.append("SUBSTANTIAL_DUPLICATE")
                    break
        reviewed.append({"path": path, "status": "ELIGIBLE" if not errors else "INELIGIBLE", "reasons": errors})
        if not errors:
            eligible.append(
                {
                    "candidate": candidate,
                    "normalized_sha256": sha256(normalized_document(candidate["content_utf8"]).encode("utf-8")),
                }
            )
            # Review the entire frozen corpus even after the selection quota is
            # reached.  The first eight remain selected, while the complete
            # ledger preserves every later eligibility determination.
    selected_paths = [item["candidate"]["path"] for item in eligible[:8]]
    ready = len(selected_paths) == 8
    assignments = {
        package_id: selected_paths[index] if ready else None for index, package_id in enumerate(PACKAGE_IDS)
    }
    return {
        "schema_version": "1",
        "corpus_commit": protocol["repository"]["commit"],
        "ordering_rule": protocol["candidate_ordering"]["rule"],
        "selection_result": "READY" if ready else "NULL",
        "reviewed_candidates": reviewed,
        "selected_paths": selected_paths if ready else [],
        "assignments": assignments,
        "construction_status": "NOT_STARTED",
    }


def selection_bytes(result: dict[str, Any]) -> bytes:
    return canonical_bytes(result) + b"\n"
