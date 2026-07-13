import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_publication_manifest.py"
spec = importlib.util.spec_from_file_location("publication_manifest_builder", SCRIPT)
publication_manifest_builder = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = publication_manifest_builder
spec.loader.exec_module(publication_manifest_builder)


def copy_repo(tmp_path: Path) -> Path:
    target = tmp_path / "repo"
    ignore = shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__", "reports", ".build")
    shutil.copytree(ROOT, target, ignore=ignore)
    return target


@pytest.fixture
def manifest_repo(tmp_path, monkeypatch):
    repo = copy_repo(tmp_path)
    monkeypatch.setattr(publication_manifest_builder, "ROOT", repo)
    monkeypatch.setattr(publication_manifest_builder, "OUTPUT_PATH", repo / "releases/publication-state-manifest.json")
    return repo


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_bytes() -> bytes:
    return publication_manifest_builder.stable_bytes(publication_manifest_builder.build_manifest())


def run_in_repo(repo: Path, command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=repo, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def test_publication_manifest_binds_research_state_and_is_fresh(manifest_repo):
    manifest = publication_manifest_builder.build_manifest()
    publication_manifest_builder.check_committed(manifest)
    state = manifest["publication_state"]
    sections = manifest["sections"]

    assert manifest["object_type"] == "PublicationStateManifest"
    assert state["dataset_path"] == "investigations/b2-governance-cohort/dataset/b2-governance-cohort-i4.dataset.json"
    assert state["research_object_manifest_hash"]
    assert state["dependency_contract_hash"]
    assert state["excluded_mutable_outputs"] == publication_manifest_builder.EXCLUDED_MUTABLE_OUTPUTS
    assert sections["comparative_dataset"][0]["sha256"]
    assert len(sections["bor_records"]) == 9
    assert len(sections["srf_records"]) == 9
    assert len(sections["der_records"]) == 9
    assert len(sections["msr_records"]) == 9


def test_two_consecutive_manifest_builds_are_byte_identical(manifest_repo):
    first = manifest_bytes()
    second = manifest_bytes()
    assert first == second


def test_manifest_check_is_side_effect_free(manifest_repo):
    manifest_path = manifest_repo / "releases/publication-state-manifest.json"
    dataset_path = manifest_repo / "investigations/b2-governance-cohort/dataset/b2-governance-cohort-i4.dataset.json"
    before = {path: file_digest(path) for path in [manifest_path, dataset_path]}

    publication_manifest_builder.check_committed(publication_manifest_builder.build_manifest())

    after = {path: file_digest(path) for path in [manifest_path, dataset_path]}
    assert after == before


def test_validation_before_manifest_check_keeps_expected_manifest_stable(manifest_repo):
    before = manifest_bytes()
    result = run_in_repo(manifest_repo, ["python3", "scripts/validate.py"])

    assert result.returncode == 0, result.stdout
    assert manifest_bytes() == before
    publication_manifest_builder.check_committed(publication_manifest_builder.build_manifest())


def test_manifest_excludes_itself(manifest_repo):
    manifest = publication_manifest_builder.build_manifest()
    manifest_path = "releases/publication-state-manifest.json"
    included_paths = [entry["path"] for entries in manifest["sections"].values() for entry in entries]

    assert manifest["manifest_path"] == manifest_path
    assert manifest_path not in included_paths


def test_mutable_publication_outputs_are_documented_and_excluded(manifest_repo):
    before = manifest_bytes()
    pdf = manifest_repo / "releases/papers/paper-b2.pdf"
    pdf.parent.mkdir(parents=True, exist_ok=True)
    pdf.write_bytes(b"mutable generated pdf bytes\n")

    after = manifest_bytes()
    manifest = publication_manifest_builder.build_manifest()

    assert after == before
    assert "publication_pdfs" not in manifest["sections"]
    assert manifest["publication_state"]["excluded_mutable_outputs"] == publication_manifest_builder.EXCLUDED_MUTABLE_OUTPUTS
    publication_manifest_builder.check_committed(manifest)


def test_publication_manifest_detects_committed_manifest_drift(manifest_repo):
    output = manifest_repo / "releases/publication-state-manifest.json"
    data = json.loads(output.read_text(encoding="utf-8"))
    data["publication_state"]["dependency_contract_hash"] = "0" * 64
    output.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="structure differs"):
        publication_manifest_builder.check_committed(publication_manifest_builder.build_manifest())


def test_publication_manifest_detects_research_object_drift(manifest_repo):
    dataset = manifest_repo / "investigations/b2-governance-cohort/dataset/b2-governance-cohort-i4.dataset.json"
    original = dataset.read_text(encoding="utf-8")
    dataset.write_text(original.replace('"cohort_size": 9', '"cohort_size": 8'), encoding="utf-8")

    with pytest.raises(SystemExit, match="structure differs"):
        publication_manifest_builder.check_committed(publication_manifest_builder.build_manifest())


def test_publication_manifest_requires_canonical_inputs(manifest_repo):
    (manifest_repo / "requirements.txt").unlink()

    with pytest.raises(SystemExit, match="missing manifest input: requirements.txt"):
        publication_manifest_builder.build_manifest()
