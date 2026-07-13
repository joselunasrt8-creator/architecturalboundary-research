import importlib.util
import json
import shutil
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


def test_publication_manifest_binds_research_state_and_is_fresh(manifest_repo):
    manifest = publication_manifest_builder.build_manifest()
    publication_manifest_builder.check_committed(manifest)
    state = manifest["publication_state"]
    sections = manifest["sections"]

    assert manifest["object_type"] == "PublicationStateManifest"
    assert state["dataset_path"] == "investigations/b2-governance-cohort/dataset/b2-governance-cohort-i4.dataset.json"
    assert state["research_object_manifest_hash"]
    assert state["dependency_contract_hash"]
    assert sections["comparative_dataset"][0]["sha256"]
    assert len(sections["bor_records"]) == 9
    assert len(sections["srf_records"]) == 9
    assert len(sections["der_records"]) == 9
    assert len(sections["msr_records"]) == 9


def test_publication_manifest_detects_committed_manifest_drift(manifest_repo):
    output = manifest_repo / "releases/publication-state-manifest.json"
    data = json.loads(output.read_text(encoding="utf-8"))
    data["publication_state"]["publication_artifact_count"] = 999
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
