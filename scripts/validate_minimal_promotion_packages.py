#!/usr/bin/env python3
"""Deterministically validate repository-local Minimal Promotion Packages."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas/minimal_promotion_package.schema.json"
PACKAGE_DIR = ROOT / "investigations/b2-governance-cohort/promotion-packages"
SUPPORTED_SCHEMA_VERSIONS = frozenset({"minimal-promotion-package-schema-v1"})
SHA256_METHOD = "repository file bytes without transformation"
PACKAGE_METHOD = (
    "RFC 8785-style deterministic JSON (UTF-8, sorted keys, compact separators) "
    "with package_content_digest.digest represented as an empty string to avoid a self-referential digest"
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
MUTABLE_PATH_PARTS = frozenset({".git", ".hg", ".svn", "workspace", "worktree", "tmp", "temp"})
NON_AUTHORITY_STATEMENT = (
    "Producer Proposal ≠ Consumer Decision. Evidence ≠ Formalization. Publication Readiness ≠ "
    "Formalization Eligibility. Indeterminate Evidence ≠ Supporting Evidence. This producer-owned package "
    "only identifies material for inspection; it neither authorizes promotion nor creates consumer authority, "
    "and raw evidence remains upstream in the referenced canonical artifacts."
)
OUTCOME_PURPOSES = {
    "supports": frozenset({"candidate_invariant_review", "bounded_formal_question", "vocabulary_alignment", "model_obligation"}),
    "indeterminate": frozenset({"indeterminate_evidence_review", "bounded_formal_question", "vocabulary_alignment", "model_obligation"}),
    "violates": frozenset({"counterexample_review", "bounded_formal_question"}),
}
REQUIRED_CLASSES = {
    "candidate_invariant_review": frozenset({"BOR", "SRF", "DER", "MSR", "Comparative Dataset", "Analysis", "Retained Classification", "Cohort Conclusion"}),
    "indeterminate_evidence_review": frozenset({"Analysis", "Retained Classification", "Cohort Conclusion"}),
    "counterexample_review": frozenset({"Cohort Conclusion"}),
}
EVIDENCE_FIELDS = {
    "supporting_evidence_summary": "supporting evidence",
    "indeterminate_evidence_summary": "indeterminate evidence",
    "negative_evidence_summary": "negative evidence",
    "missing_measurement_summary": "missing measurements",
    "known_limitations": "known limitations",
    "known_counterexamples": "known counterexamples",
}

try:
    from jsonschema import Draft202012Validator
except ModuleNotFoundError:  # pragma: no cover - restricted local environments only
    sys.path.insert(0, str(ROOT))
    from tools.jsonschema_fallback import Draft202012Validator


class PackageValidationError(ValueError):
    """A stable, user-facing package validation failure."""


def _fail(message: str) -> None:
    raise PackageValidationError(message)


def _json_path(parts: Iterable[Any]) -> str:
    return ".".join(str(part) for part in parts) or "<package>"


def _artifact_references(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        if "repository_relative_path" in value and "artifact_class" in value and "digest" in value:
            yield value
        for child in value.values():
            yield from _artifact_references(child)
    elif isinstance(value, list):
        for child in value:
            yield from _artifact_references(child)


def _validate_repository_path(raw: Any, field: str) -> Path:
    if not isinstance(raw, str) or not raw or "\\" in raw:
        _fail(f"{field}: path must be a non-empty POSIX repository-relative path")
    pure = PurePosixPath(raw)
    if pure.is_absolute() or re.match(r"^[A-Za-z]:", raw):
        _fail(f"{field}: absolute paths are prohibited: {raw}")
    if ".." in pure.parts:
        _fail(f"{field}: parent traversal is prohibited: {raw}")
    lowered = {part.lower() for part in pure.parts}
    if lowered & MUTABLE_PATH_PARTS or raw.startswith(("refs/heads/", "branches/")):
        _fail(f"{field}: mutable workspace path is prohibited: {raw}")
    resolved = (ROOT / pure).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError:
        _fail(f"{field}: path resolves outside the repository: {raw}")
    return resolved


def _validate_digest(digest: Any, field: str, *, package: bool = False) -> None:
    if not isinstance(digest, dict):
        _fail(f"{field}: digest must be an object")
    if digest.get("hash_algorithm") != "sha256":
        _fail(f"{field}.hash_algorithm: only sha256 is supported")
    if not isinstance(digest.get("digest"), str) or not SHA256_RE.fullmatch(digest["digest"]):
        _fail(f"{field}.digest: expected 64 lowercase hexadecimal SHA-256 characters")
    expected_method = PACKAGE_METHOD if package else SHA256_METHOD
    if digest.get("canonicalization_method") != expected_method:
        _fail(f"{field}.canonicalization_method: unsupported canonicalization method")


def canonical_package_digest(package: dict[str, Any]) -> str:
    """Return the documented self-reference-safe deterministic package digest."""
    canonical = copy.deepcopy(package)
    canonical["package_content_digest"]["digest"] = ""
    encoded = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_package(package: Any, *, root: Path = ROOT) -> None:
    """Validate one already-parsed package without mutation or external access."""
    if not isinstance(package, dict):
        _fail("<package>: package must be a JSON object")
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(package), key=lambda error: (list(error.absolute_path), error.message))
    if errors:
        error = errors[0]
        _fail(f"schema failure at {_json_path(error.absolute_path)}: {error.message}")

    if package["schema_version"] not in SUPPORTED_SCHEMA_VERSIONS:
        _fail(f"schema_version: unsupported schema version {package['schema_version']!r}")
    allowed = OUTCOME_PURPOSES[package["cohort_outcome"]]
    if package["package_purpose"] not in allowed:
        _fail(f"package_purpose: {package['package_purpose']!r} is incompatible with cohort_outcome {package['cohort_outcome']!r}")
    if package["hash_algorithm"] != "sha256":
        _fail("hash_algorithm: only sha256 is supported")

    for field, category in EVIDENCE_FIELDS.items():
        value = package[field]
        if isinstance(value, dict) and value.get("value") != "not_applicable" and value.get("category") != category:
            _fail(f"{field}.category: expected {category!r}")

    references = list(_artifact_references(package))
    for index, reference in enumerate(references):
        field = f"artifact_reference[{index}]"
        path = _validate_repository_path(reference["repository_relative_path"], f"{field}.repository_relative_path")
        _validate_digest(reference["digest"], f"{field}.digest")
        if not path.is_file():
            _fail(f"{field}.repository_relative_path: referenced artifact does not exist")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != reference["digest"]["digest"]:
            _fail(f"{field}.digest: artifact SHA-256 mismatch for {path.relative_to(root)}")

    required_classes = REQUIRED_CLASSES.get(package["package_purpose"], frozenset())
    present_required = {ref["artifact_class"] for ref in references if ref["required_for_purpose"]}
    missing = sorted(required_classes - present_required)
    if missing:
        _fail(f"required_for_purpose: missing required artifact class(es): {', '.join(missing)}")

    content_path = _validate_repository_path(package["package_content_reference"], "package_content_reference")
    expected_name = f"{package['package_id']}-{package['package_version']}.json"
    if content_path.name != expected_name:
        _fail("immutable identity: package_content_reference must match package_id and package_version")
    _validate_digest(package["package_content_digest"], "package_content_digest", package=True)
    actual_package_digest = canonical_package_digest(package)
    if package["package_content_digest"]["digest"] != actual_package_digest:
        _fail("package_content_digest.digest: package SHA-256 mismatch")
    if package["non_authority_statement"] != NON_AUTHORITY_STATEMENT:
        _fail("non_authority_statement: documented producer boundary statement is required")


def validate_path(path: Path) -> None:
    try:
        package = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        _fail(f"{path}: cannot read package JSON: {error}")
    validate_package(package)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="package paths (defaults to repository promotion packages)")
    args = parser.parse_args(argv)
    paths = args.paths or sorted(PACKAGE_DIR.glob("*.json"))
    if not paths:
        print("no Minimal Promotion Packages found", file=sys.stderr)
        return 1
    for path in paths:
        try:
            validate_path(path if path.is_absolute() else ROOT / path)
        except PackageValidationError as error:
            print(f"{path}: {error}", file=sys.stderr)
            return 1
        print(f"validated Minimal Promotion Package: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
