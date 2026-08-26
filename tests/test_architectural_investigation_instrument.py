"""Mechanical identity tests for the Instrument v1 candidate."""
from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

import pytest

from scripts.validate_architectural_investigation_instrument import (
    CANDIDATE2_MANIFEST_RELATIVE,
    FREEZE_RECORD_RELATIVE,
    ISSUE107_RECORD_RELATIVE,
    ISSUE108_RECORD_RELATIVE,
    MANIFEST_RELATIVE,
    InstrumentValidationError,
    aggregate_digest,
    validate_calibration_fixture,
    validate_candidate2,
    validate_candidate2_readiness_coherence,
    validate_instrument,
    validate_issue108_adjudication,
    validate_readiness_coherence,
)


ROOT = Path(__file__).resolve().parents[1]


def candidate() -> dict:
    return json.loads((ROOT / MANIFEST_RELATIVE).read_text(encoding="utf-8"))


def candidate2() -> dict:
    return json.loads((ROOT / CANDIDATE2_MANIFEST_RELATIVE).read_text(encoding="utf-8"))


def copy_validation_surface(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    package = root / MANIFEST_RELATIVE.parent
    package.parent.mkdir(parents=True)
    shutil.copytree(ROOT / MANIFEST_RELATIVE.parent, package)
    freeze = root / FREEZE_RECORD_RELATIVE
    freeze.parent.mkdir(parents=True)
    shutil.copy2(ROOT / FREEZE_RECORD_RELATIVE, freeze)
    issue107 = root / ISSUE107_RECORD_RELATIVE
    shutil.copy2(ROOT / ISSUE107_RECORD_RELATIVE, issue107)
    issue108 = root / ISSUE108_RECORD_RELATIVE
    shutil.copy2(ROOT / ISSUE108_RECORD_RELATIVE, issue108)
    previous = root / "docs/reference-execution/v1.0/freeze-readiness-record.md"
    shutil.copy2(ROOT / "docs/reference-execution/v1.0/freeze-readiness-record.md", previous)
    blocked = root / "investigations/structural-analysis-foundations-audit-1/execution-package-manifest.json"
    blocked.parent.mkdir(parents=True)
    shutil.copy2(
        ROOT / "investigations/structural-analysis-foundations-audit-1/execution-package-manifest.json",
        blocked,
    )
    return root


def test_canonical_candidate_identity_passes() -> None:
    manifest = validate_instrument(ROOT)
    assert manifest["readiness_determination"] == "INSTRUMENT_SPECIFICATION_REVISION_REQUIRED"
    assert manifest["containing_commit"] is None


def test_content_identity_is_deterministic() -> None:
    artifacts = candidate()["content_identity"]["artifacts"]
    assert aggregate_digest(artifacts) == aggregate_digest(copy.deepcopy(artifacts))
    assert aggregate_digest(artifacts) == candidate()["content_identity"]["digest"]


def test_changed_candidate_artifact_fails_closed(tmp_path: Path) -> None:
    root = copy_validation_surface(tmp_path)
    specification = root / "instrument/architectural-investigation/v1/specification.md"
    specification.write_text(specification.read_text(encoding="utf-8") + "changed\n", encoding="utf-8")
    with pytest.raises(InstrumentValidationError, match="artifact SHA-256 mismatch"):
        validate_instrument(root, verify_git=False)


def test_ready_state_cannot_retain_gaps() -> None:
    manifest = candidate()
    manifest["readiness_determination"] = "INSTRUMENT_V1_FROZEN_READY"
    manifest["containing_commit"] = "1" * 40
    manifest["package_status"] = "FROZEN"
    manifest["canonical_path_status"] = "FROZEN"
    with pytest.raises(InstrumentValidationError, match="ready instrument cannot retain unresolved gaps"):
        validate_readiness_coherence(manifest)


def test_ready_state_requires_full_containing_commit() -> None:
    manifest = candidate()
    manifest["readiness_determination"] = "INSTRUMENT_V1_FROZEN_READY"
    manifest["unresolved_gap_ids"] = []
    manifest["containing_commit"] = "main"
    with pytest.raises(InstrumentValidationError, match="containing_commit must be a lowercase full hash"):
        validate_readiness_coherence(manifest)


def test_unready_candidate_cannot_claim_containing_commit() -> None:
    manifest = candidate()
    manifest["containing_commit"] = "1" * 40
    with pytest.raises(InstrumentValidationError, match="must not claim a containing commit"):
        validate_readiness_coherence(manifest)


def test_blocked_issue_84_binding_is_enforced(tmp_path: Path) -> None:
    root = copy_validation_surface(tmp_path)
    blocked = root / "investigations/structural-analysis-foundations-audit-1/execution-package-manifest.json"
    data = json.loads(blocked.read_text(encoding="utf-8"))
    data["audit_outcome"] = "COMPLETE"
    blocked.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    with pytest.raises(InstrumentValidationError, match="blocked Issue #84 package digest mismatch"):
        validate_instrument(root, verify_git=False)


def test_validation_is_read_only() -> None:
    paths = [ROOT / MANIFEST_RELATIVE, ROOT / FREEZE_RECORD_RELATIVE]
    before = {path: path.read_bytes() for path in paths}
    validate_instrument(ROOT)
    after = {path: path.read_bytes() for path in paths}
    assert after == before


def test_canonical_candidate2_identity_passes() -> None:
    manifest = validate_candidate2(ROOT)
    assert manifest["readiness_determination"] == "INSTRUMENT_SPECIFICATION_REVISION_REQUIRED"
    assert manifest["unresolved_gap_ids"] == [
        "AII-V1-GAP-001",
        "AII-V1-GAP-008",
        "AII-V1-GAP-009",
        "AII-V1-GAP-010",
    ]


def test_candidate2_content_identity_is_deterministic() -> None:
    artifacts = candidate2()["content_identity"]["artifacts"]
    assert aggregate_digest(artifacts) == candidate2()["content_identity"]["digest"]


def test_changed_candidate2_fixture_fails_closed(tmp_path: Path) -> None:
    root = copy_validation_surface(tmp_path)
    fixture = root / "instrument/architectural-investigation/v1/candidate-2/calibration/fixture-v1.json"
    fixture.write_text(fixture.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(InstrumentValidationError, match="artifact SHA-256 mismatch"):
        validate_candidate2(root, verify_git=False)


def test_candidate2_fixture_requires_all_cases(tmp_path: Path) -> None:
    root = copy_validation_surface(tmp_path)
    fixture_path = root / "instrument/architectural-investigation/v1/candidate-2/calibration/fixture-v1.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    fixture["cases"].pop()
    fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
    with pytest.raises(InstrumentValidationError, match="case inventory"):
        validate_calibration_fixture(root, candidate2())


def test_candidate2_fixture_preserves_manual_judgment(tmp_path: Path) -> None:
    root = copy_validation_surface(tmp_path)
    fixture_path = root / "instrument/architectural-investigation/v1/candidate-2/calibration/fixture-v1.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    fixture["cases"][0]["expected"]["manual_judgment_required"] = False
    fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
    with pytest.raises(InstrumentValidationError, match="preserve manual judgment"):
        validate_calibration_fixture(root, candidate2())


def test_candidate2_cannot_claim_ready_with_remaining_gaps() -> None:
    manifest = candidate2()
    manifest["readiness_determination"] = "IMPLEMENTATION_READY"
    manifest["containing_commit"] = "1" * 40
    with pytest.raises(InstrumentValidationError, match="cannot retain unresolved gaps"):
        validate_candidate2_readiness_coherence(manifest)


def test_candidate2_ready_requires_completed_independent_calibration() -> None:
    manifest = candidate2()
    manifest["readiness_determination"] = "IMPLEMENTATION_READY"
    manifest["resolved_gap_ids"] = sorted(
        set(manifest["resolved_gap_ids"]) | set(manifest["unresolved_gap_ids"])
    )
    manifest["unresolved_gap_ids"] = []
    manifest["containing_commit"] = "1" * 40
    with pytest.raises(InstrumentValidationError, match="requires completed calibration"):
        validate_candidate2_readiness_coherence(manifest)


def test_candidate2_binds_preserved_candidate1(tmp_path: Path) -> None:
    root = copy_validation_surface(tmp_path)
    base_manifest = root / MANIFEST_RELATIVE
    data = json.loads(base_manifest.read_text(encoding="utf-8"))
    data["instrument_version"] = "1.0.0-candidate.changed"
    base_manifest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    with pytest.raises(InstrumentValidationError, match="candidate.1 manifest dependency"):
        validate_candidate2(root, verify_git=False)


def test_candidate2_validation_is_read_only() -> None:
    paths = [ROOT / CANDIDATE2_MANIFEST_RELATIVE, ROOT / ISSUE107_RECORD_RELATIVE]
    before = {path: path.read_bytes() for path in paths}
    validate_candidate2(ROOT)
    after = {path: path.read_bytes() for path in paths}
    assert after == before


def test_issue108_adjudication_identity_passes() -> None:
    validate_issue108_adjudication(ROOT)


def test_issue108_adjudication_cannot_fabricate_independence(tmp_path: Path) -> None:
    root = copy_validation_surface(tmp_path)
    record = root / ISSUE108_RECORD_RELATIVE
    text = record.read_text(encoding="utf-8")
    record.write_text(
        text.replace(
            "Qualified independent reviews\navailable: `0` of the required `2`.",
            "Qualified independent reviews\navailable: `2` of the required `2`.",
        ),
        encoding="utf-8",
    )
    with pytest.raises(InstrumentValidationError, match="qualified reviewer count"):
        validate_issue108_adjudication(root, verify_git=False)


def test_issue108_adjudication_is_read_only() -> None:
    paths = [ROOT / CANDIDATE2_MANIFEST_RELATIVE, ROOT / ISSUE108_RECORD_RELATIVE]
    before = {path: path.read_bytes() for path in paths}
    validate_issue108_adjudication(ROOT)
    after = {path: path.read_bytes() for path in paths}
    assert after == before
