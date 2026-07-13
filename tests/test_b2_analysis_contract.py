import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_analysis.py"
spec = importlib.util.spec_from_file_location("b2_analysis_builder", SCRIPT)
b2_analysis_builder = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = b2_analysis_builder
spec.loader.exec_module(b2_analysis_builder)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def configure_builder(monkeypatch, repo: Path) -> Path:
    output = repo / "investigations/b2-governance-cohort/analysis/b2-governance-cohort-i4.analysis.json"
    monkeypatch.setattr(b2_analysis_builder, "ROOT", repo)
    monkeypatch.setattr(b2_analysis_builder, "DATASET_PATH", repo / "investigations/b2-governance-cohort/dataset/b2-governance-cohort-i4.dataset.json")
    monkeypatch.setattr(b2_analysis_builder, "OUTPUT_PATH", output)
    monkeypatch.setattr(b2_analysis_builder, "SCHEMA_PATH", repo / "schemas/analysis.schema.json")
    monkeypatch.setattr(b2_analysis_builder, "DATASET_SCHEMA_PATH", repo / "schemas/dataset.schema.json")
    return output


@pytest.fixture
def analysis_repo(tmp_path, monkeypatch):
    for relative in ["schemas/analysis.schema.json", "schemas/dataset.schema.json"]:
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, destination)
    destination = tmp_path / "investigations/b2-governance-cohort/dataset/b2-governance-cohort-i4.dataset.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / destination.relative_to(tmp_path), destination)
    configure_builder(monkeypatch, tmp_path)
    return tmp_path


def committed_analysis(repo: Path) -> dict:
    output = repo / "investigations/b2-governance-cohort/analysis/b2-governance-cohort-i4.analysis.json"
    data = b2_analysis_builder.build_analysis()
    write_json(output, data)
    b2_analysis_builder.check_committed(data)
    return data


def test_canonical_analysis_positive_projection_is_fresh(analysis_repo):
    data = committed_analysis(analysis_repo)
    assert data["provenance"]["created_from"] == ["investigations/b2-governance-cohort/dataset/b2-governance-cohort-i4.dataset.json"]
    assert data["measurement_distributions"]["m_R"] == {"observed_1": 8, "observed_0": 0, "missing": 1}
    assert data["measurement_distributions"]["m_E"] == {"observed_1": 7, "observed_0": 0, "missing": 2}
    assert data["deferred_outputs"] == ["retained_classification", "cohort_conclusion"]


@pytest.mark.parametrize(
    ("mutate", "expected"),
    [
        (lambda d: d["measurement_distributions"]["m_R"].__setitem__("missing", 0), "structure differs"),
        (lambda d: d["system_measurement_matrix"].reverse(), "structure differs"),
        (lambda d: d.__setitem__("retained_classifications", []), "schema validation failed"),
        (lambda d: d.__setitem__("cohort_conclusion", "indeterminate"), "schema validation failed"),
    ],
)
def test_committed_analysis_drift_and_forbidden_outputs_fail_closed(analysis_repo, mutate, expected):
    data = committed_analysis(analysis_repo)
    mutate(data)
    output = analysis_repo / "investigations/b2-governance-cohort/analysis/b2-governance-cohort-i4.analysis.json"
    write_json(output, data)
    with pytest.raises(SystemExit, match=expected):
        b2_analysis_builder.check_committed(b2_analysis_builder.build_analysis())


def test_analysis_rejects_dataset_with_non_comparative_fields(analysis_repo):
    dataset_path = analysis_repo / "investigations/b2-governance-cohort/dataset/b2-governance-cohort-i4.dataset.json"
    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    dataset["rows"][0]["classification"] = "supports"
    write_json(dataset_path, dataset)
    with pytest.raises(SystemExit, match="schema validation failed"):
        b2_analysis_builder.build_analysis()


def test_byte_instability_fails_closed(analysis_repo):
    data = committed_analysis(analysis_repo)
    output = analysis_repo / "investigations/b2-governance-cohort/analysis/b2-governance-cohort-i4.analysis.json"
    output.write_text(json.dumps(data, sort_keys=True) + "\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="bytes differ"):
        b2_analysis_builder.check_committed(b2_analysis_builder.build_analysis())
