from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def copy_repo(tmp_path: Path) -> Path:
    target = tmp_path / "repo"
    shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__", "reports"))
    return target


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def run_check(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python3", "scripts/check_registry.py"], cwd=repo, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def retained_path(repo: Path) -> Path:
    return repo / "investigations/b2-governance-cohort/results/b2-governance-cohort-i5.retained-classification.json"


def cohort_path(repo: Path) -> Path:
    return repo / "investigations/b2-governance-cohort/results/b2-governance-cohort-i5.cohort-conclusion.json"


def assert_fails(repo: Path, needle: str) -> None:
    result = run_check(repo)
    assert result.returncode != 0
    assert needle in result.stdout


def test_clean_canonical_repository_passes(tmp_path):
    repo = copy_repo(tmp_path)
    result = run_check(repo)
    assert result.returncode == 0
    assert "registry validation passed" in result.stdout


def test_missing_retained_classification_artifact_fails(tmp_path):
    repo = copy_repo(tmp_path)
    retained_path(repo).unlink()
    assert_fails(repo, "references missing path")


def test_wrong_retained_classification_id_fails(tmp_path):
    repo = copy_repo(tmp_path)
    data = load(retained_path(repo)); data["id"] = "wrong"
    write(retained_path(repo), data)
    assert_fails(repo, "broken retained-classification reference")


def test_wrong_retained_object_type_fails(tmp_path):
    repo = copy_repo(tmp_path)
    data = load(retained_path(repo)); data["object_type"] = "Wrong"
    write(retained_path(repo), data)
    assert_fails(repo, "object_type mismatch")


def test_wrong_retained_investigation_id_fails(tmp_path):
    repo = copy_repo(tmp_path)
    data = load(retained_path(repo)); data["investigation_id"] = "wrong"
    write(retained_path(repo), data)
    assert_fails(repo, "investigation_id mismatch")


def test_wrong_retained_protocol_version_fails(tmp_path):
    repo = copy_repo(tmp_path)
    data = load(retained_path(repo)); data["protocol_version"] = "protocol-v2"
    write(retained_path(repo), data)
    assert_fails(repo, "unexpected protocol_version")


def test_duplicate_retained_classification_ids_fail(tmp_path):
    repo = copy_repo(tmp_path)
    reg = load(repo / "registry/retained_classifications.json")
    reg["retained_classifications"].append(dict(reg["retained_classifications"][0]))
    write(repo / "registry/retained_classifications.json", reg)
    assert_fails(repo, "duplicate retained-classification IDs")


def test_missing_cohort_conclusion_artifact_fails(tmp_path):
    repo = copy_repo(tmp_path)
    cohort_path(repo).unlink()
    assert_fails(repo, "references missing path")


def test_wrong_cohort_conclusion_id_fails(tmp_path):
    repo = copy_repo(tmp_path)
    reg = load(repo / "registry/cohort_conclusions.json")
    reg["cohort_conclusions"][0]["cohort_conclusion_id"] = "expected-id"
    write(repo / "registry/cohort_conclusions.json", reg)
    assert_fails(repo, "cohort_conclusion_id does not match")


def test_broken_retained_classification_reference_fails(tmp_path):
    repo = copy_repo(tmp_path)
    data = load(cohort_path(repo)); data["source_retained_classification_ids"] = ["missing"]
    write(cohort_path(repo), data)
    assert_fails(repo, "broken retained-classification reference")


def test_cohort_size_mismatch_fails(tmp_path):
    repo = copy_repo(tmp_path)
    data = load(cohort_path(repo)); data["cohort_size"] = 8
    write(cohort_path(repo), data)
    assert_fails(repo, "cohort_size mismatch")


def test_incorrect_cohort_outcome_relative_to_i5_precedence_fails(tmp_path):
    repo = copy_repo(tmp_path)
    data = load(cohort_path(repo)); data["deterministic_conclusion"]["outcome"] = "supports"
    write(cohort_path(repo), data)
    assert_fails(repo, "incorrect cohort outcome")


def test_incorrect_basis_system_ids_fail(tmp_path):
    repo = copy_repo(tmp_path)
    data = load(cohort_path(repo)); data["deterministic_conclusion"]["basis_system_ids"] = ["aws-iam"]
    write(cohort_path(repo), data)
    assert_fails(repo, "incorrect basis_system_ids")


def test_orphaned_canonical_b2_result_artifacts_fail(tmp_path):
    repo = copy_repo(tmp_path)
    shutil.copy2(retained_path(repo), repo / "investigations/b2-governance-cohort/results/orphan.retained-classification.json")
    assert_fails(repo, "orphaned canonical B2 result artifact")
