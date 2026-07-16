"""Targeted proof for deterministic Minimal Promotion Package validation."""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from scripts.validate_minimal_promotion_packages import (
    OUTCOME_PURPOSES,
    PackageValidationError,
    canonical_package_digest,
    discover_packages,
    validate_package,
)

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_PATH = ROOT / "investigations/b2-governance-cohort/promotion-packages/b2-governance-cohort-indeterminate-evidence-review-v1.0.json"
INVALID_DIR = ROOT / "tests/fixtures/minimal_promotion_package_invalid"


def canonical_package() -> dict:
    return json.loads(PACKAGE_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def local_git_copy(tmp_path: Path) -> Path:
    clone = tmp_path / "repo"
    subprocess.run(["git", "clone", "--quiet", "--no-hardlinks", str(ROOT), str(clone)], check=True)
    return clone


def refresh_digest(package: dict) -> None:
    package["package_content_digest"]["digest"] = canonical_package_digest(package)


def pointer_parent(document: dict, pointer: str) -> tuple[object, str]:
    parts = [part.replace("~1", "/").replace("~0", "~") for part in pointer.lstrip("/").split("/")]
    parent: object = document
    for part in parts[:-1]:
        parent = parent[int(part)] if isinstance(parent, list) else parent[part]
    return parent, parts[-1]


def remove_artifact_class(value: object, artifact_class: str) -> object:
    if isinstance(value, list):
        return [remove_artifact_class(item, artifact_class) for item in value if not (isinstance(item, dict) and item.get("artifact_class") == artifact_class)]
    if isinstance(value, dict):
        return {key: remove_artifact_class(item, artifact_class) for key, item in value.items()}
    return value


def apply_fixture(package: dict, fixture: dict) -> dict:
    result = copy.deepcopy(package)
    operation = fixture["operation"]
    if operation == "remove_artifact_class":
        result = remove_artifact_class(result, fixture["value"])
    else:
        changes = fixture.get("values", {fixture.get("path"): fixture.get("value")})
        for pointer, value in changes.items():
            parent, key = pointer_parent(result, pointer)
            if operation == "delete":
                if isinstance(parent, list):
                    del parent[int(key)]
                else:
                    del parent[key]
            else:
                if isinstance(parent, list):
                    parent[int(key)] = value
                else:
                    parent[key] = value
    if "package_content_digest" in result:
        refresh_digest(result)
    return result


def test_canonical_b2_package_passes() -> None:
    validate_package(canonical_package())


@pytest.mark.parametrize("fixture_path", sorted(INVALID_DIR.glob("*.json")), ids=lambda path: path.stem)
def test_required_invalid_examples_fail(fixture_path: Path) -> None:
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    with pytest.raises(PackageValidationError):
        validate_package(apply_fixture(canonical_package(), fixture))


def test_unsupported_schema_version_fails() -> None:
    package = canonical_package()
    package["schema_version"] = "minimal-promotion-package-schema-v2"
    refresh_digest(package)
    with pytest.raises(PackageValidationError):
        validate_package(package)


def test_invalid_package_identity_fails() -> None:
    package = canonical_package()
    package["package_id"] = "Invalid_ID"
    refresh_digest(package)
    with pytest.raises(PackageValidationError):
        validate_package(package)


@pytest.mark.parametrize("field", ["source_commit_sha", "producer_commit"])
def test_invalid_package_source_commits_fail(field: str) -> None:
    package = canonical_package()
    package[field] = "main"
    refresh_digest(package)
    with pytest.raises(PackageValidationError):
        validate_package(package)


@pytest.mark.parametrize(
    ("outcome", "purpose", "valid"),
    [(outcome, purpose, purpose in allowed) for outcome, allowed in OUTCOME_PURPOSES.items() for purpose in sorted({item for values in OUTCOME_PURPOSES.values() for item in values})],
)
def test_complete_documented_outcome_purpose_matrix(outcome: str, purpose: str, valid: bool) -> None:
    package = canonical_package()
    package["cohort_outcome"] = outcome
    package["package_purpose"] = purpose
    refresh_digest(package)
    if valid:
        validate_package(package)
    else:
        with pytest.raises(PackageValidationError):
            validate_package(package)


@pytest.mark.parametrize("path", ["/etc/passwd", "../protocol.md", "protocol/../README.md", "workspace/protocol.md"])
def test_invalid_repository_paths_fail(path: str) -> None:
    package = canonical_package()
    package["source_artifact_refs_and_hashes"][0]["repository_relative_path"] = path
    refresh_digest(package)
    with pytest.raises(PackageValidationError):
        validate_package(package)


def test_package_digest_mismatch_fails() -> None:
    package = canonical_package()
    package["candidate_claim"] += " changed"
    with pytest.raises(PackageValidationError, match="package SHA-256 mismatch"):
        validate_package(package)


def test_validation_is_deterministic_across_repeated_runs() -> None:
    package = canonical_package()
    before = copy.deepcopy(package)
    for _ in range(5):
        validate_package(package)
    assert package == before
    assert len({canonical_package_digest(package) for _ in range(5)}) == 1


def test_historical_blob_validates_when_checkout_file_differs(local_git_copy: Path) -> None:
    protocol = local_git_copy / "protocol/protocol-v1/protocol.md"
    protocol.write_bytes(b"different uncommitted working-tree bytes\n")

    validate_package(canonical_package(), root=local_git_copy)


def test_checkout_match_cannot_rescue_recorded_commit_mismatch(local_git_copy: Path) -> None:
    package = canonical_package()
    current_bytes = b"digest matches only the mutable checkout\n"
    (local_git_copy / "protocol/protocol-v1/protocol.md").write_bytes(current_bytes)
    package["source_artifact_refs_and_hashes"][0]["digest"]["digest"] = hashlib.sha256(current_bytes).hexdigest()
    refresh_digest(package)

    with pytest.raises(PackageValidationError, match="mismatch at recorded commit"):
        validate_package(package, root=local_git_copy)


def test_unknown_artifact_commit_fails(local_git_copy: Path) -> None:
    package = canonical_package()
    package["source_artifact_refs_and_hashes"][0]["source_commit"] = "0" * 40
    refresh_digest(package)

    with pytest.raises(PackageValidationError, match="commit object does not exist"):
        validate_package(package, root=local_git_copy)


def test_missing_artifact_path_at_valid_commit_fails(local_git_copy: Path) -> None:
    package = canonical_package()
    package["source_artifact_refs_and_hashes"][0]["repository_relative_path"] = "protocol/missing.md"
    refresh_digest(package)

    with pytest.raises(PackageValidationError, match="path does not exist at recorded commit"):
        validate_package(package, root=local_git_copy)


def test_non_file_at_valid_commit_fails(local_git_copy: Path) -> None:
    package = canonical_package()
    package["source_artifact_refs_and_hashes"][0]["repository_relative_path"] = "protocol"
    refresh_digest(package)

    with pytest.raises(PackageValidationError, match="path is not a file at recorded commit"):
        validate_package(package, root=local_git_copy)


def test_package_commit_fields_must_be_consistent(local_git_copy: Path) -> None:
    package = canonical_package()
    package["producer_commit"] = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=local_git_copy, check=True, stdout=subprocess.PIPE, text=True
    ).stdout.strip()
    refresh_digest(package)

    with pytest.raises(PackageValidationError, match="must equal"):
        validate_package(package, root=local_git_copy)


def test_artifact_digest_mismatch_is_checked_at_recorded_commit(local_git_copy: Path) -> None:
    package = canonical_package()
    package["source_artifact_refs_and_hashes"][0]["digest"]["digest"] = "0" * 64
    refresh_digest(package)

    with pytest.raises(PackageValidationError, match="mismatch at recorded commit"):
        validate_package(package, root=local_git_copy)


def test_validation_does_not_modify_working_tree(local_git_copy: Path) -> None:
    protocol = local_git_copy / "protocol/protocol-v1/protocol.md"
    protocol.write_bytes(b"pre-existing working-tree change\n")
    before = subprocess.run(
        ["git", "status", "--short", "--untracked-files=all"], cwd=local_git_copy, check=True, stdout=subprocess.PIPE
    ).stdout

    validate_package(canonical_package(), root=local_git_copy)

    after = subprocess.run(
        ["git", "status", "--short", "--untracked-files=all"], cwd=local_git_copy, check=True, stdout=subprocess.PIPE
    ).stdout
    assert after == before


def test_discovers_packages_across_investigations_in_stable_order(tmp_path: Path) -> None:
    expected = [
        tmp_path / "investigations/a-study/promotion-packages/a.json",
        tmp_path / "investigations/z-study/promotion-packages/z.json",
    ]
    for path in reversed(expected):
        path.parent.mkdir(parents=True)
        path.write_text("{}\n", encoding="utf-8")

    assert discover_packages(tmp_path) == expected
    assert discover_packages(tmp_path) == expected


def test_discovery_ignores_json_outside_canonical_directories(tmp_path: Path) -> None:
    unrelated = tmp_path / "other/package.json"
    unrelated.parent.mkdir()
    unrelated.write_text("{}\n", encoding="utf-8")

    assert discover_packages(tmp_path) == []


def test_discovery_ignores_symlinked_packages(tmp_path: Path) -> None:
    outside = tmp_path / "outside.json"
    outside.write_text("{}\n", encoding="utf-8")
    package_dir = tmp_path / "investigations/study/promotion-packages"
    package_dir.mkdir(parents=True)
    (package_dir / "linked.json").symlink_to(outside)

    assert discover_packages(tmp_path) == []


def test_canonical_b2_package_is_discovered_and_valid() -> None:
    discovered = discover_packages(ROOT)
    assert PACKAGE_PATH in discovered
    validate_package(canonical_package(), root=ROOT)
