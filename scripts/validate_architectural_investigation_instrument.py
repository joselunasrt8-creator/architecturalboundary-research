#!/usr/bin/env python3
"""Validate only the mechanical identity boundary of Instrument v1 candidates."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_RELATIVE = Path("instrument/architectural-investigation/v1/instrument-manifest.json")
FREEZE_RECORD_RELATIVE = Path(
    "docs/reference-execution/v1.0/architectural-investigation-instrument-v1-freeze-record.md"
)
CANDIDATE2_MANIFEST_RELATIVE = Path(
    "instrument/architectural-investigation/v1/candidate-2/instrument-manifest.json"
)
ISSUE107_RECORD_RELATIVE = Path(
    "docs/reference-execution/v1.0/architectural-investigation-instrument-v1-readiness-review-issue-107.md"
)
ISSUE108_RECORD_RELATIVE = Path(
    "docs/reference-execution/v1.0/architectural-investigation-instrument-v1-readiness-adjudication-issue-108.md"
)
ISSUE108_CONTAINING_COMMIT = "0520a5deca3ad1e00cb74095ee74d0f7227d58c7"
ISSUE108_CONTAINING_TREE = "723a07778cd45a281535e6b305de1c91af050150"
EXPECTED_ARTIFACTS = {
    "instrument/architectural-investigation/v1/README.md",
    "instrument/architectural-investigation/v1/calibration-contract.md",
    "instrument/architectural-investigation/v1/compatibility-and-supersession.md",
    "instrument/architectural-investigation/v1/execution-record-contract.md",
    "instrument/architectural-investigation/v1/specification.md",
    "instrument/architectural-investigation/v1/unresolved-normative-gaps.md",
}
EXPECTED_CANONICAL_PATHS = {
    "instrument/architectural-investigation/v1/specification.md",
    "instrument/architectural-investigation/v1/execution-record-contract.md",
    "instrument/architectural-investigation/v1/calibration-contract.md",
    "instrument/architectural-investigation/v1/compatibility-and-supersession.md",
}
EXPECTED_GAPS = {f"AII-V1-GAP-{number:03d}" for number in range(1, 11)}
CANDIDATE2_RESOLVED_GAPS = {f"AII-V1-GAP-{number:03d}" for number in range(2, 8)}
CANDIDATE2_UNRESOLVED_GAPS = {
    "AII-V1-GAP-001",
    "AII-V1-GAP-008",
    "AII-V1-GAP-009",
    "AII-V1-GAP-010",
}
CANDIDATE2_EXPECTED_ARTIFACTS = {
    "instrument/architectural-investigation/v1/candidate-2/README.md",
    "instrument/architectural-investigation/v1/candidate-2/calibration/README.md",
    "instrument/architectural-investigation/v1/candidate-2/calibration/exemplar-mapping.md",
    "instrument/architectural-investigation/v1/candidate-2/calibration/fixture-v1.json",
    "instrument/architectural-investigation/v1/candidate-2/calibration/review-record.md",
    "instrument/architectural-investigation/v1/candidate-2/compatibility.md",
    "instrument/architectural-investigation/v1/candidate-2/conflict-precedence-and-supersession.md",
    "instrument/architectural-investigation/v1/candidate-2/evidence-and-authority.md",
    "instrument/architectural-investigation/v1/candidate-2/gap-resolution-register.md",
    "instrument/architectural-investigation/v1/candidate-2/legitimacy-crosswalk.md",
    "instrument/architectural-investigation/v1/candidate-2/maturity-and-transitions.md",
    "instrument/architectural-investigation/v1/candidate-2/readiness-and-binding.md",
}
CANDIDATE2_EXPECTED_CANONICAL_PATHS = {
    "instrument/architectural-investigation/v1/specification.md",
    "instrument/architectural-investigation/v1/execution-record-contract.md",
    "instrument/architectural-investigation/v1/candidate-2/evidence-and-authority.md",
    "instrument/architectural-investigation/v1/candidate-2/maturity-and-transitions.md",
    "instrument/architectural-investigation/v1/candidate-2/conflict-precedence-and-supersession.md",
    "instrument/architectural-investigation/v1/candidate-2/legitimacy-crosswalk.md",
    "instrument/architectural-investigation/v1/candidate-2/readiness-and-binding.md",
    "instrument/architectural-investigation/v1/candidate-2/compatibility.md",
}
EVIDENCE_CLASSES = {
    "NORMATIVE_SPECIFICATION", "NORMATIVE_BOUNDARY_DECLARATION", "PROCEDURAL_DOCUMENTATION",
    "DESCRIPTIVE_DOCUMENTATION", "IMPLEMENTATION_SOURCE", "MACHINE_VALIDATABLE_CONTRACT",
    "TEST_OR_FIXTURE", "WORKFLOW_CONFIGURATION", "EXECUTION_RECORD", "GENERATED_ARTIFACT",
    "REPOSITORY_METADATA", "HISTORICAL_RECORD", "EXTERNAL_PINNED_EVIDENCE",
    "DIRECT_OBSERVATION", "INFERENCE", "ABSENCE_OR_MISSING_EVIDENCE", "CONTRADICTORY_EVIDENCE",
}
AUTHORITY_CLASSES = {
    "DECLARED_CANONICAL", "NORMATIVE_SUPPORTING", "IMPLEMENTATION_AUTHORITATIVE",
    "WORKFLOW_AUTHORITATIVE", "REPOSITORY_STATUS_AUTHORITATIVE", "HISTORICAL_ONLY",
    "DESCRIPTIVE_ONLY", "EXTERNAL_RESOLVED", "EXTERNAL_UNRESOLVED",
    "NONAUTHORITATIVE_EXAMPLE", "UNKNOWN",
}
CLAIM_STATUSES = {
    "SUPPORTED", "SUPPORTED_WITH_LIMITATIONS", "CONTESTED", "INSUFFICIENT_EVIDENCE",
    "INFERENCE_ONLY", "WITHDRAWN", "INVALID",
}
MATURITY_TRACKS = {
    "CONCEPTUAL_METHOD", "DOCUMENTARY_SPECIFICATION", "OBSERVED_PRACTICE",
    "EXECUTABLE_IMPLEMENTATION", "TRANSFER_AND_REPRODUCTION",
}
PROMOTION_DISPOSITIONS = {
    "UNSUPPORTED", "OBSERVED_CANDIDATE", "PROVISIONAL", "PROMOTION_ELIGIBLE",
    "DEFERRED_PENDING_EVIDENCE", "REJECTED",
}
DETERMINATIONS = {
    "INSTRUMENT_V1_FROZEN_READY",
    "INSTRUMENT_V1_FREEZE_BLOCKED",
    "INSTRUMENT_SPECIFICATION_REVISION_REQUIRED",
}
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")


class InstrumentValidationError(ValueError):
    """Raised when the mechanically checkable identity contract fails."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git_blob_id(value: bytes) -> str:
    header = f"blob {len(value)}\0".encode("ascii")
    return hashlib.sha1(header + value).hexdigest()


def safe_repo_file(root: Path, raw: str) -> Path:
    pure = PurePosixPath(raw)
    if pure.is_absolute() or not pure.parts or ".." in pure.parts or "." in pure.parts:
        raise InstrumentValidationError(f"invalid repository-relative path: {raw}")
    path = root.joinpath(*pure.parts)
    if path.is_symlink() or not path.is_file():
        raise InstrumentValidationError(f"instrument path is not a regular file: {raw}")
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError as error:
        raise InstrumentValidationError(f"instrument path escapes repository: {raw}") from error
    return path


def aggregate_digest(artifacts: list[dict[str, str]]) -> str:
    ordered = sorted(artifacts, key=lambda item: item["path"])
    value = b"".join(
        item["path"].encode("utf-8") + b"\0" + item["sha256"].encode("ascii") + b"\n"
        for item in ordered
    )
    return sha256_bytes(value)


def require_full_hash(value: object, field: str, pattern: re.Pattern[str]) -> str:
    if not isinstance(value, str) or pattern.fullmatch(value) is None:
        raise InstrumentValidationError(f"{field} must be a lowercase full hash")
    return value


def validate_readiness_coherence(manifest: dict[str, object]) -> None:
    determination = manifest.get("readiness_determination")
    if determination not in DETERMINATIONS:
        raise InstrumentValidationError("unknown readiness determination")
    gaps = manifest.get("unresolved_gap_ids")
    if not isinstance(gaps, list) or len(gaps) != len(set(gaps)) or not set(gaps) <= EXPECTED_GAPS:
        raise InstrumentValidationError("unresolved gap inventory is invalid or duplicated")

    containing_commit = manifest.get("containing_commit")
    status = manifest.get("package_status")
    canonical_status = manifest.get("canonical_path_status")
    if determination == "INSTRUMENT_V1_FROZEN_READY":
        require_full_hash(containing_commit, "containing_commit", HEX40)
        if gaps:
            raise InstrumentValidationError("ready instrument cannot retain unresolved gaps")
        if status != "FROZEN" or canonical_status != "FROZEN":
            raise InstrumentValidationError("ready instrument must have frozen package and path status")
    else:
        if set(gaps) != EXPECTED_GAPS:
            raise InstrumentValidationError(
                "current unready candidate must preserve AII-V1-GAP-001 through -010 exactly once"
            )
        if containing_commit is not None:
            raise InstrumentValidationError("unready candidate must not claim a containing commit as frozen identity")
        if status != "UNFROZEN_CANDIDATE" or canonical_status != "PROPOSED_NOT_FROZEN":
            raise InstrumentValidationError("unready instrument must remain an unfrozen candidate")
    if manifest.get("audit_authorization") is not False:
        raise InstrumentValidationError("instrument manifest must not grant audit authorization")


def validate_content_identity(
    root: Path, manifest: dict[str, object], expected_artifacts: set[str]
) -> str:
    identity = manifest.get("content_identity")
    if not isinstance(identity, dict):
        raise InstrumentValidationError("content_identity must be an object")
    if identity.get("algorithm") != "sha256-path-nul-digest-lf-v1":
        raise InstrumentValidationError("unsupported content identity algorithm")
    artifacts = identity.get("artifacts")
    if not isinstance(artifacts, list) or not all(isinstance(item, dict) for item in artifacts):
        raise InstrumentValidationError("content identity artifacts must be objects")
    if artifacts != sorted(artifacts, key=lambda item: item.get("path", "")):
        raise InstrumentValidationError("content identity artifacts must be in lexical path order")
    paths = [item.get("path") for item in artifacts]
    if set(paths) != expected_artifacts or len(paths) != len(expected_artifacts):
        raise InstrumentValidationError("content identity artifact set is incomplete or duplicated")
    for item in artifacts:
        raw_path = item.get("path")
        digest = require_full_hash(item.get("sha256"), f"sha256 for {raw_path}", HEX64)
        path = safe_repo_file(root, str(raw_path))
        if sha256_bytes(path.read_bytes()) != digest:
            raise InstrumentValidationError(f"artifact SHA-256 mismatch: {raw_path}")
    expected_aggregate = require_full_hash(identity.get("digest"), "content identity digest", HEX64)
    if aggregate_digest(artifacts) != expected_aggregate:
        raise InstrumentValidationError("aggregate instrument content digest mismatch")
    return expected_aggregate


def validate_instrument(root: Path = ROOT, *, verify_git: bool = True) -> dict[str, object]:
    manifest_path = safe_repo_file(root, MANIFEST_RELATIVE.as_posix())
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise InstrumentValidationError("instrument manifest is not valid UTF-8 JSON") from error
    if not isinstance(manifest, dict):
        raise InstrumentValidationError("instrument manifest must be an object")
    if manifest.get("schema_version") != "architectural-investigation-instrument-manifest-v1":
        raise InstrumentValidationError("unsupported instrument manifest version")
    if manifest.get("object_type") != "ArchitecturalInvestigationInstrumentManifest":
        raise InstrumentValidationError("unexpected instrument manifest object type")
    if manifest.get("instrument_name") != "Architectural Investigation Instrument":
        raise InstrumentValidationError("unexpected instrument name")
    if manifest.get("instrument_version") != "1.0.0-candidate.1":
        raise InstrumentValidationError("unexpected instrument candidate version")
    if manifest.get("repository") != "joselunasrt8-creator/architecturalboundary-research":
        raise InstrumentValidationError("unexpected instrument repository")
    if manifest.get("package_path") != "instrument/architectural-investigation/v1":
        raise InstrumentValidationError("unexpected instrument package path")

    canonical_paths = manifest.get("proposed_canonical_paths")
    if not isinstance(canonical_paths, list) or set(canonical_paths) != EXPECTED_CANONICAL_PATHS:
        raise InstrumentValidationError("proposed canonical path set differs from Instrument v1 contract")

    identity = manifest.get("content_identity")
    if not isinstance(identity, dict):
        raise InstrumentValidationError("content_identity must be an object")
    if identity.get("algorithm") != "sha256-path-nul-digest-lf-v1":
        raise InstrumentValidationError("unsupported content identity algorithm")
    artifacts = identity.get("artifacts")
    if not isinstance(artifacts, list) or not all(isinstance(item, dict) for item in artifacts):
        raise InstrumentValidationError("content identity artifacts must be objects")
    if artifacts != sorted(artifacts, key=lambda item: item.get("path", "")):
        raise InstrumentValidationError("content identity artifacts must be in lexical path order")
    paths = [item.get("path") for item in artifacts]
    if set(paths) != EXPECTED_ARTIFACTS or len(paths) != len(EXPECTED_ARTIFACTS):
        raise InstrumentValidationError("content identity artifact set is incomplete or duplicated")
    for item in artifacts:
        raw_path = item.get("path")
        digest = require_full_hash(item.get("sha256"), f"sha256 for {raw_path}", HEX64)
        path = safe_repo_file(root, str(raw_path))
        if sha256_bytes(path.read_bytes()) != digest:
            raise InstrumentValidationError(f"artifact SHA-256 mismatch: {raw_path}")
    expected_aggregate = require_full_hash(identity.get("digest"), "content identity digest", HEX64)
    if aggregate_digest(artifacts) != expected_aggregate:
        raise InstrumentValidationError("aggregate instrument content digest mismatch")

    validate_readiness_coherence(manifest)

    gaps_text = safe_repo_file(
        root, "instrument/architectural-investigation/v1/unresolved-normative-gaps.md"
    ).read_text(encoding="utf-8")
    for gap in EXPECTED_GAPS:
        if gaps_text.count(f"## `{gap}`") != 1:
            raise InstrumentValidationError(f"gap register must define {gap} exactly once")

    blocked = manifest.get("preserved_blocked_execution")
    if not isinstance(blocked, dict):
        raise InstrumentValidationError("preserved blocked execution binding is missing")
    blocked_path = safe_repo_file(root, str(blocked.get("path")))
    blocked_digest = require_full_hash(blocked.get("sha256"), "blocked execution SHA-256", HEX64)
    if sha256_bytes(blocked_path.read_bytes()) != blocked_digest:
        raise InstrumentValidationError("blocked Issue #84 package digest mismatch")
    blocked_manifest = json.loads(blocked_path.read_text(encoding="utf-8"))
    if (
        blocked_manifest.get("object_id") != blocked.get("execution_id")
        or blocked_manifest.get("execution_validity") != "BLOCKED"
        or blocked_manifest.get("audit_outcome") != "NOT_REACHED"
        or blocked.get("superseded") is not False
    ):
        raise InstrumentValidationError("blocked Issue #84 execution was changed or superseded")

    freeze_path = safe_repo_file(root, FREEZE_RECORD_RELATIVE.as_posix())
    freeze_bytes = freeze_path.read_bytes()
    freeze_text = freeze_bytes.decode("utf-8")
    determination = str(manifest["readiness_determination"])
    expected_row = f"| Final determination | **{determination}** |"
    if freeze_text.count(expected_row) != 1:
        raise InstrumentValidationError("freeze record must contain exactly one final-determination row")
    manifest_digest = sha256_bytes(manifest_path.read_bytes())
    manifest_blob = git_blob_id(manifest_path.read_bytes())
    for value, label in [
        (expected_aggregate, "candidate content digest"),
        (manifest_digest, "manifest SHA-256"),
        (manifest_blob, "manifest Git blob"),
    ]:
        if value not in freeze_text:
            raise InstrumentValidationError(f"freeze record does not bind {label}")

    base_commit = require_full_hash(manifest.get("materialization_base_commit"), "materialization base commit", HEX40)
    previous = manifest.get("supersession")
    if not isinstance(previous, dict):
        raise InstrumentValidationError("supersession binding is missing")
    previous_path = str(previous.get("previous_readiness_record"))
    previous_blob = require_full_hash(
        previous.get("previous_readiness_record_git_blob"), "previous readiness blob", HEX40
    )
    safe_repo_file(root, previous_path)
    if not verify_git and manifest.get("readiness_determination") == "INSTRUMENT_V1_FROZEN_READY":
        raise InstrumentValidationError("ready instrument validation requires repository Git metadata")
    if verify_git:
        result = subprocess.run(
            ["git", "cat-file", "-e", f"{base_commit}^{{commit}}"], cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if result.returncode != 0:
            raise InstrumentValidationError("materialization base commit is unavailable")
        result = subprocess.run(
            ["git", "rev-parse", f"{base_commit}:{previous_path}"],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode != 0 or result.stdout.strip() != previous_blob:
            raise InstrumentValidationError("previous readiness record blob does not reproduce at base commit")

    compatibility = manifest.get("compatibility")
    if not isinstance(compatibility, dict) or compatibility.get("scientific_judgment_automation") != "PROHIBITED":
        raise InstrumentValidationError("scientific judgment automation must remain prohibited")
    return manifest


def validate_calibration_fixture(root: Path, manifest: dict[str, object]) -> None:
    fixture_path = safe_repo_file(
        root, "instrument/architectural-investigation/v1/candidate-2/calibration/fixture-v1.json"
    )
    try:
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise InstrumentValidationError("candidate.2 calibration fixture is not valid UTF-8 JSON") from error
    if not isinstance(fixture, dict):
        raise InstrumentValidationError("candidate.2 calibration fixture must be an object")
    if fixture.get("schema_version") != "architectural-investigation-calibration-fixture-v1":
        raise InstrumentValidationError("unsupported candidate.2 calibration fixture version")
    if fixture.get("object_type") != "ArchitecturalInvestigationCalibrationFixture":
        raise InstrumentValidationError("unexpected candidate.2 calibration fixture object type")
    if fixture.get("fixture_id") != "AII-V1-CAL-FIXTURE-001":
        raise InstrumentValidationError("unexpected candidate.2 calibration fixture identity")
    if fixture.get("instrument_version") != "1.0.0-candidate.2":
        raise InstrumentValidationError("calibration fixture instrument version mismatch")

    protocol = fixture.get("review_protocol")
    if not isinstance(protocol, dict):
        raise InstrumentValidationError("calibration review protocol is missing")
    if (
        protocol.get("minimum_qualified_independent_reviewers") != 2
        or protocol.get("blind_review_required") is not True
        or protocol.get("automatic_classification_prohibited") is not True
        or protocol.get("disagreement_disposition")
        != "PRESERVE_AND_ADJUDICATE_OR_REVISE_SPECIFICATION"
    ):
        raise InstrumentValidationError("calibration review protocol weakens required human review")

    cases = fixture.get("cases")
    expected_cases = {f"CAL-{number:03d}" for number in range(1, 9)}
    if not isinstance(cases, list) or not all(isinstance(case, dict) for case in cases):
        raise InstrumentValidationError("calibration cases must be objects")
    case_ids = [case.get("case_id") for case in cases]
    if set(case_ids) != expected_cases or len(case_ids) != len(expected_cases):
        raise InstrumentValidationError("calibration case inventory is incomplete or duplicated")

    evidence_ids: set[str] = set()
    for case in cases:
        case_id = str(case.get("case_id"))
        for field in ("question", "claim_type", "rationale"):
            if not isinstance(case.get(field), str) or not str(case[field]).strip():
                raise InstrumentValidationError(f"{case_id} is missing {field}")
        evidence_items = case.get("evidence_items")
        if not isinstance(evidence_items, list) or not evidence_items:
            raise InstrumentValidationError(f"{case_id} must contain evidence items")
        for item in evidence_items:
            if not isinstance(item, dict):
                raise InstrumentValidationError(f"{case_id} evidence items must be objects")
            evidence_id = item.get("evidence_id")
            if not isinstance(evidence_id, str) or evidence_id in evidence_ids:
                raise InstrumentValidationError("calibration evidence IDs must be nonempty and unique")
            evidence_ids.add(evidence_id)
            if item.get("evidence_class") not in EVIDENCE_CLASSES:
                raise InstrumentValidationError(f"{evidence_id} uses unknown evidence class")
            if item.get("source_authority") not in AUTHORITY_CLASSES:
                raise InstrumentValidationError(f"{evidence_id} uses unknown source authority")
            if item.get("revision_bound") is not True:
                raise InstrumentValidationError(f"{evidence_id} must remain revision-bound")
            if not isinstance(item.get("directness"), str) or not item["directness"]:
                raise InstrumentValidationError(f"{evidence_id} is missing directness")
            if not isinstance(item.get("execution_observed"), bool):
                raise InstrumentValidationError(f"{evidence_id} has invalid execution observation")

        expected = case.get("expected")
        if not isinstance(expected, dict):
            raise InstrumentValidationError(f"{case_id} is missing expected reviewer classification")
        if expected.get("claim_status") not in CLAIM_STATUSES:
            raise InstrumentValidationError(f"{case_id} uses unknown claim status")
        tracks = expected.get("applicable_tracks")
        if not isinstance(tracks, list) or not tracks or not set(tracks) <= MATURITY_TRACKS:
            raise InstrumentValidationError(f"{case_id} uses invalid maturity tracks")
        if len(tracks) != len(set(tracks)):
            raise InstrumentValidationError(f"{case_id} duplicates a maturity track")
        if expected.get("promotion_disposition") not in PROMOTION_DISPOSITIONS:
            raise InstrumentValidationError(f"{case_id} uses unknown promotion disposition")
        for field in ("highest_supported_states", "reachability_states", "prohibited_inferences"):
            value = expected.get(field)
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                raise InstrumentValidationError(f"{case_id} has invalid {field}")
        if not expected["prohibited_inferences"]:
            raise InstrumentValidationError(f"{case_id} must declare prohibited inferences")
        if expected.get("manual_judgment_required") is not True:
            raise InstrumentValidationError(f"{case_id} must preserve manual judgment")

    calibration = manifest.get("calibration")
    if not isinstance(calibration, dict):
        raise InstrumentValidationError("candidate.2 calibration manifest binding is missing")
    if (
        calibration.get("fixture_id") != fixture["fixture_id"]
        or set(calibration.get("case_ids", [])) != expected_cases
        or len(calibration.get("case_ids", [])) != len(expected_cases)
        or calibration.get("review_id") != "AII-V1-CAL-REVIEW-001"
        or calibration.get("review_independence") != "NOT_INDEPENDENT_OF_INSTRUMENT_AUTHORING"
        or calibration.get("result") != "INCOMPLETE_INDEPENDENT_REVIEW_REQUIRED"
    ):
        raise InstrumentValidationError("candidate.2 calibration manifest binding is incoherent")
    review_text = safe_repo_file(
        root, "instrument/architectural-investigation/v1/candidate-2/calibration/review-record.md"
    ).read_text(encoding="utf-8")
    for required in (
        "`AII-V1-CAL-REVIEW-001`",
        "`NOT_INDEPENDENT_OF_INSTRUMENT_AUTHORING`",
        "`INCOMPLETE_INDEPENDENT_REVIEW_REQUIRED`",
        "No second reviewer result exists",
    ):
        if required not in review_text:
            raise InstrumentValidationError(f"candidate.2 review record is missing: {required}")


def validate_candidate2_readiness_coherence(manifest: dict[str, object]) -> None:
    determination = manifest.get("readiness_determination")
    if determination not in {"IMPLEMENTATION_READY", "INSTRUMENT_SPECIFICATION_REVISION_REQUIRED"}:
        raise InstrumentValidationError("unknown candidate.2 readiness determination")
    resolved = manifest.get("resolved_gap_ids")
    unresolved = manifest.get("unresolved_gap_ids")
    if (
        not isinstance(resolved, list)
        or not isinstance(unresolved, list)
        or len(resolved) != len(set(resolved))
        or len(unresolved) != len(set(unresolved))
        or set(resolved) & set(unresolved)
        or set(resolved) | set(unresolved) != EXPECTED_GAPS
    ):
        raise InstrumentValidationError("candidate.2 gap partition is invalid or duplicated")
    if determination == "INSTRUMENT_SPECIFICATION_REVISION_REQUIRED":
        if set(resolved) != CANDIDATE2_RESOLVED_GAPS or set(unresolved) != CANDIDATE2_UNRESOLVED_GAPS:
            raise InstrumentValidationError("candidate.2 must preserve the evidence-bound gap partition")
        if manifest.get("containing_commit") is not None:
            raise InstrumentValidationError("unready candidate.2 cannot claim a containing commit")
        if (
            manifest.get("package_status") != "UNFROZEN_CANDIDATE"
            or manifest.get("canonical_path_status") != "PROPOSED_NOT_FROZEN"
        ):
            raise InstrumentValidationError("unready candidate.2 must remain an unfrozen candidate")
    else:
        if unresolved:
            raise InstrumentValidationError("implementation-ready candidate.2 cannot retain unresolved gaps")
        require_full_hash(manifest.get("containing_commit"), "containing_commit", HEX40)
        calibration = manifest.get("calibration")
        if not isinstance(calibration, dict) or calibration.get("result") == "INCOMPLETE_INDEPENDENT_REVIEW_REQUIRED":
            raise InstrumentValidationError("implementation-ready candidate.2 requires completed calibration")
    if manifest.get("audit_authorization") is not False:
        raise InstrumentValidationError("candidate.2 manifest must not grant audit authorization")


def validate_candidate2(root: Path = ROOT, *, verify_git: bool = True) -> dict[str, object]:
    manifest_path = safe_repo_file(root, CANDIDATE2_MANIFEST_RELATIVE.as_posix())
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise InstrumentValidationError("candidate.2 manifest is not valid UTF-8 JSON") from error
    if not isinstance(manifest, dict):
        raise InstrumentValidationError("candidate.2 manifest must be an object")
    expected_fields = {
        "schema_version": "architectural-investigation-instrument-manifest-v2",
        "object_type": "ArchitecturalInvestigationInstrumentManifest",
        "instrument_name": "Architectural Investigation Instrument",
        "instrument_version": "1.0.0-candidate.2",
        "repository": "joselunasrt8-creator/architecturalboundary-research",
        "package_path": "instrument/architectural-investigation/v1/candidate-2",
    }
    for field, expected in expected_fields.items():
        if manifest.get(field) != expected:
            raise InstrumentValidationError(f"unexpected candidate.2 {field}")
    canonical_paths = manifest.get("proposed_canonical_paths")
    if (
        not isinstance(canonical_paths, list)
        or set(canonical_paths) != CANDIDATE2_EXPECTED_CANONICAL_PATHS
        or len(canonical_paths) != len(CANDIDATE2_EXPECTED_CANONICAL_PATHS)
    ):
        raise InstrumentValidationError("candidate.2 proposed canonical path set differs from contract")
    for path in canonical_paths:
        safe_repo_file(root, path)

    content_digest = validate_content_identity(root, manifest, CANDIDATE2_EXPECTED_ARTIFACTS)
    validate_candidate2_readiness_coherence(manifest)
    validate_calibration_fixture(root, manifest)

    register_text = safe_repo_file(
        root, "instrument/architectural-investigation/v1/candidate-2/gap-resolution-register.md"
    ).read_text(encoding="utf-8")
    for gap in EXPECTED_GAPS:
        disposition = "RESOLVED" if gap in CANDIDATE2_RESOLVED_GAPS else "REMAINS"
        row_prefix = f"| `{gap}` | `{disposition}` |"
        if register_text.count(row_prefix) != 1:
            raise InstrumentValidationError(f"candidate.2 gap register must classify {gap} exactly once")

    dependencies = manifest.get("normative_dependencies")
    if not isinstance(dependencies, list) or not dependencies or not isinstance(dependencies[0], dict):
        raise InstrumentValidationError("candidate.2 normative dependency binding is missing")
    base = dependencies[0]
    base_path = safe_repo_file(root, str(base.get("path")))
    base_bytes = base_path.read_bytes()
    if (
        base.get("name") != "Architectural Investigation Instrument 1.0.0-candidate.1 manifest"
        or sha256_bytes(base_bytes) != base.get("sha256")
        or git_blob_id(base_bytes) != base.get("git_blob")
    ):
        raise InstrumentValidationError("candidate.1 manifest dependency does not reproduce")
    base_manifest = json.loads(base_bytes.decode("utf-8"))
    base_identity = base_manifest.get("content_identity")
    if not isinstance(base_identity, dict) or base_identity.get("digest") != base.get("content_digest"):
        raise InstrumentValidationError("candidate.1 content dependency does not reproduce")
    if base.get("containing_commit") is not None:
        raise InstrumentValidationError("candidate.2 cannot invent a containing commit for candidate.1")

    blocked = manifest.get("preserved_blocked_execution")
    if not isinstance(blocked, dict):
        raise InstrumentValidationError("candidate.2 blocked Issue #84 binding is missing")
    blocked_path = safe_repo_file(root, str(blocked.get("path")))
    if sha256_bytes(blocked_path.read_bytes()) != blocked.get("sha256"):
        raise InstrumentValidationError("candidate.2 blocked Issue #84 package digest mismatch")
    blocked_manifest = json.loads(blocked_path.read_text(encoding="utf-8"))
    if (
        blocked_manifest.get("object_id") != blocked.get("execution_id")
        or blocked_manifest.get("execution_validity") != "BLOCKED"
        or blocked_manifest.get("audit_outcome") != "NOT_REACHED"
        or blocked.get("superseded") is not False
    ):
        raise InstrumentValidationError("candidate.2 changes or supersedes blocked Issue #84 evidence")

    compatibility = manifest.get("compatibility")
    if not isinstance(compatibility, dict) or compatibility != {
        "issue_77_execution_record": "ISSUE_77_SEMANTICALLY_COMPATIBLE",
        "issue_78_calibration": "ISSUE_78_SEMANTICS_MATERIALIZED_CALIBRATION_INCOMPLETE",
        "structural_validation": "AVAILABLE_FOR_CANDIDATE_IDENTITY_ONLY",
        "scientific_judgment_automation": "PROHIBITED",
    }:
        raise InstrumentValidationError("candidate.2 compatibility boundary is incoherent")

    record_path = safe_repo_file(root, ISSUE107_RECORD_RELATIVE.as_posix())
    record_text = record_path.read_text(encoding="utf-8")
    determination = str(manifest["readiness_determination"])
    expected_row = f"| Final determination | **{determination}** |"
    if record_text.count(expected_row) != 1:
        raise InstrumentValidationError("Issue #107 record must contain exactly one final-determination row")
    manifest_digest = sha256_bytes(manifest_path.read_bytes())
    manifest_blob = git_blob_id(manifest_path.read_bytes())
    for value, label in (
        (content_digest, "candidate.2 content digest"),
        (manifest_digest, "candidate.2 manifest SHA-256"),
        (manifest_blob, "candidate.2 manifest Git blob"),
    ):
        if value not in record_text:
            raise InstrumentValidationError(f"Issue #107 record does not bind {label}")
    for statement in ("not legitimately bindable", "`BLOCKED` / `NOT_REACHED`"):
        if statement not in record_text:
            raise InstrumentValidationError(f"Issue #107 record is missing preserved boundary: {statement}")

    base_commit = require_full_hash(
        manifest.get("materialization_base_commit"), "candidate.2 materialization base commit", HEX40
    )
    if not verify_git and determination == "IMPLEMENTATION_READY":
        raise InstrumentValidationError("implementation-ready validation requires repository Git metadata")
    if verify_git:
        result = subprocess.run(
            ["git", "cat-file", "-e", f"{base_commit}^{{commit}}"],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode != 0:
            raise InstrumentValidationError("candidate.2 materialization base commit is unavailable")
        containing_commit = manifest.get("containing_commit")
        if containing_commit is not None:
            for path in [CANDIDATE2_MANIFEST_RELATIVE.as_posix(), *sorted(canonical_paths)]:
                result = subprocess.run(
                    ["git", "cat-file", "-e", f"{containing_commit}:{path}"],
                    cwd=root,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                if result.returncode != 0:
                    raise InstrumentValidationError(f"candidate.2 containing commit lacks {path}")
    return manifest


def validate_issue108_adjudication(
    root: Path = ROOT, *, verify_git: bool = True
) -> None:
    record_path = safe_repo_file(root, ISSUE108_RECORD_RELATIVE.as_posix())
    record_text = record_path.read_text(encoding="utf-8")
    manifest_path = safe_repo_file(root, CANDIDATE2_MANIFEST_RELATIVE.as_posix())
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes.decode("utf-8"))
    identity = manifest.get("content_identity")
    if not isinstance(identity, dict):
        raise InstrumentValidationError("candidate.2 content identity is missing")

    expected_bindings = {
        ISSUE108_CONTAINING_COMMIT: "candidate.2 containing commit",
        ISSUE108_CONTAINING_TREE: "candidate.2 containing tree",
        str(manifest.get("materialization_base_commit")): "candidate.2 materialization base",
        sha256_bytes(manifest_bytes): "candidate.2 manifest SHA-256",
        git_blob_id(manifest_bytes): "candidate.2 manifest Git blob",
        str(identity.get("digest")): "candidate.2 aggregate content digest",
        "`NOT_AVAILABLE`": "independent-review eligibility",
        "Qualified independent reviews\navailable: `0` of the required `2`.":
            "qualified reviewer count",
        "Inter-reviewer agreement and disagreement are therefore\n`NOT_MEASURABLE`":
            "unmeasurable reviewer comparison",
        "Adjudication is `NOT_REACHED`": "adjudication boundary",
        "`AII-V1-GAP-009` | `RESOLVED`": "containing-commit gap resolution",
        "`AII-V1-GAP-008` | `REMAINS`": "exemplar blocker",
        "`AII-V1-GAP-010` | `REMAINS`": "independent-review blocker",
        "`ISSUE_77_SEMANTICALLY_COMPATIBLE`": "Issue #77 compatibility",
        "`ISSUE_78_SEMANTICS_MATERIALIZED_CALIBRATION_INCOMPLETE`":
            "Issue #78 compatibility",
        "**not legitimately bindable**": "fresh Issue #84 boundary",
        "`BLOCKED` / `NOT_REACHED`": "preserved Issue #84 result",
    }
    for value, label in expected_bindings.items():
        if value not in record_text:
            raise InstrumentValidationError(f"Issue #108 record does not bind {label}")

    determination_row = (
        "| Final determination | **INSTRUMENT_SPECIFICATION_REVISION_REQUIRED** |"
    )
    if record_text.count(determination_row) != 1:
        raise InstrumentValidationError(
            "Issue #108 record must contain exactly one final-determination row"
        )
    if "No Instrument v1 freeze is produced or updated." not in record_text:
        raise InstrumentValidationError("Issue #108 record must preserve the no-freeze boundary")
    if "no Issue #108 second calibration classification was\nperformed" not in record_text:
        raise InstrumentValidationError(
            "Issue #108 record must not fabricate a second calibration review"
        )

    if not verify_git:
        return

    result = subprocess.run(
        ["git", "cat-file", "-e", f"{ISSUE108_CONTAINING_COMMIT}^{{commit}}"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise InstrumentValidationError("Issue #108 containing commit is unavailable")

    for revision, expected, label in (
        (f"{ISSUE108_CONTAINING_COMMIT}^{{tree}}", ISSUE108_CONTAINING_TREE, "tree"),
        (
            f"{ISSUE108_CONTAINING_COMMIT}^1",
            str(manifest.get("materialization_base_commit")),
            "materialization parent",
        ),
    ):
        result = subprocess.run(
            ["git", "rev-parse", revision],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode != 0 or result.stdout.strip() != expected:
            raise InstrumentValidationError(f"Issue #108 containing {label} does not reproduce")

    artifacts = identity.get("artifacts")
    if not isinstance(artifacts, list):
        raise InstrumentValidationError("candidate.2 artifact identity is missing")
    committed_paths = [
        {
            "path": CANDIDATE2_MANIFEST_RELATIVE.as_posix(),
            "sha256": sha256_bytes(manifest_bytes),
            "git_blob": git_blob_id(manifest_bytes),
        },
        *[
            {"path": item["path"], "sha256": item["sha256"]}
            for item in artifacts
            if isinstance(item, dict) and "path" in item and "sha256" in item
        ],
    ]
    if len(committed_paths) != len(CANDIDATE2_EXPECTED_ARTIFACTS) + 1:
        raise InstrumentValidationError("Issue #108 committed artifact inventory is incomplete")
    for item in committed_paths:
        path = str(item["path"])
        result = subprocess.run(
            ["git", "rev-parse", f"{ISSUE108_CONTAINING_COMMIT}:{path}"],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode != 0:
            raise InstrumentValidationError(f"Issue #108 containing commit lacks {path}")
        blob = result.stdout.strip()
        content = subprocess.run(
            ["git", "cat-file", "blob", blob],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if content.returncode != 0 or sha256_bytes(content.stdout) != item["sha256"]:
            raise InstrumentValidationError(f"Issue #108 committed digest mismatch: {path}")
        if item.get("git_blob") is not None and blob != item["git_blob"]:
            raise InstrumentValidationError(f"Issue #108 committed Git blob mismatch: {path}")


def main() -> None:
    git_check = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    verify_git = git_check.returncode == 0 and git_check.stdout.strip() == "true"
    try:
        manifest = validate_instrument(verify_git=verify_git)
        candidate2 = validate_candidate2(verify_git=verify_git)
        validate_issue108_adjudication(verify_git=verify_git)
    except (InstrumentValidationError, OSError, UnicodeDecodeError) as error:
        raise SystemExit(f"instrument v1 validation failed: {error}") from error
    print(
        "instrument v1 candidate identity valid: "
        f"{manifest['instrument_version']} / {manifest['readiness_determination']}"
    )
    print(
        "instrument v1 candidate identity valid: "
        f"{candidate2['instrument_version']} / {candidate2['readiness_determination']}"
    )
    print(
        "instrument v1 Issue #108 binding valid: "
        f"{ISSUE108_CONTAINING_COMMIT} / INSTRUMENT_SPECIFICATION_REVISION_REQUIRED"
    )
    if not verify_git:
        print("instrument Git-object validation unavailable: repository metadata absent")


if __name__ == "__main__":
    main()
