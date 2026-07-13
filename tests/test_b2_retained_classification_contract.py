import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_retained_classification.py"
spec = importlib.util.spec_from_file_location("b2_retained_builder", SCRIPT)
builder = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = builder
spec.loader.exec_module(builder)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def configure(monkeypatch, repo: Path):
    monkeypatch.setattr(builder, "ROOT", repo)
    monkeypatch.setattr(builder, "ANALYSIS_PATH", repo / "investigations/b2-governance-cohort/analysis/b2-governance-cohort-i4.analysis.json")
    monkeypatch.setattr(builder, "DATASET_PATH", repo / "investigations/b2-governance-cohort/dataset/b2-governance-cohort-i4.dataset.json")
    monkeypatch.setattr(builder, "REGISTRATION_PATH", repo / "investigations/b2-governance-cohort/preregistration/i1_i5_registration.json")
    monkeypatch.setattr(builder, "OUTPUT_PATH", repo / "investigations/b2-governance-cohort/results/b2-governance-cohort-i5.retained-classification.json")
    monkeypatch.setattr(builder, "SCHEMA_PATH", repo / "schemas/retained_classification.schema.json")
    monkeypatch.setattr(builder, "ANALYSIS_SCHEMA_PATH", repo / "schemas/analysis.schema.json")


@pytest.fixture
def rc_repo(tmp_path, monkeypatch):
    for relative in [
        "schemas/analysis.schema.json",
        "schemas/retained_classification.schema.json",
        "investigations/b2-governance-cohort/analysis/b2-governance-cohort-i4.analysis.json",
        "investigations/b2-governance-cohort/dataset/b2-governance-cohort-i4.dataset.json",
        "investigations/b2-governance-cohort/preregistration/i1_i5_registration.json",
    ]:
        dest = tmp_path / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, dest)
    for stage in ["der", "srf", "bor", "msr"]:
        shutil.copytree(ROOT / "investigations/b2-governance-cohort" / stage, tmp_path / "investigations/b2-governance-cohort" / stage)
    configure(monkeypatch, tmp_path)
    monkeypatch.setattr(builder, "verify_analysis_fresh", lambda: None)
    return tmp_path


def committed(repo: Path) -> dict:
    data = builder.build_retained_classification()
    write_json(repo / "investigations/b2-governance-cohort/results/b2-governance-cohort-i5.retained-classification.json", data)
    builder.check_committed(data)
    return data


def test_positive_frozen_i5_deterministic_lineage_missingness_and_schema(rc_repo):
    data = committed(rc_repo)
    assert data["decision_rule_ref"].endswith("#/deterministic_decision_rule/I5")
    assert data["lineage"]["analysis_path"] == "investigations/b2-governance-cohort/analysis/b2-governance-cohort-i4.analysis.json"
    assert len(data["lineage"]["msr_paths"]) == 9
    assert len(data["lineage"]["der_paths"]) == 9
    assert len(data["lineage"]["srf_paths"]) == 9
    assert len(data["lineage"]["bor_paths"]) == 9
    outcomes = {row["system_id"]: row for row in data["per_system_classifications"]}
    assert outcomes["aws-iam"]["classification"] == "supports"
    assert outcomes["envoy-ext-authz"]["classification"] == "indeterminate"
    assert outcomes["envoy-ext-authz"]["missing_measurements"] == ["m_R", "m_RL"]
    assert data["cohort_classification"]["outcome"] == "indeterminate"
    assert builder.stable_bytes(data) == builder.stable_bytes(builder.build_retained_classification())


def test_committed_artifact_matches_fresh_rebuild(rc_repo):
    data = committed(rc_repo)
    builder.check_committed(builder.build_retained_classification())
    assert (rc_repo / "investigations/b2-governance-cohort/results/b2-governance-cohort-i5.retained-classification.json").read_bytes() == builder.stable_bytes(data)


def mutate_analysis(repo: Path, mutator):
    path = repo / "investigations/b2-governance-cohort/analysis/b2-governance-cohort-i4.analysis.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    mutator(data)
    write_json(path, data)


@pytest.mark.parametrize(
    ("mutator", "expected"),
    [
        (lambda d: d["system_measurement_matrix"].pop(), "schema validation failed"),
        (lambda d: d["system_measurement_matrix"][1].__setitem__("system_id", "aws-iam"), "duplicate"),
        (lambda d: d["system_measurement_matrix"][0]["measurements"].pop("m_R"), "schema validation failed"),
        (lambda d: d["system_measurement_matrix"][0]["lineage"].pop("msr_path"), "lineage incomplete"),
        (lambda d: d["system_measurement_matrix"][0]["lineage"].__setitem__("source_der_ids", ["missing-der"]), "unknown DER"),
        (lambda d: d["system_measurement_matrix"][0]["measurements"].__setitem__("m_R", 2), "schema validation failed"),
        (lambda d: d["system_measurement_matrix"][0].__setitem__("classification", "supports"), "schema validation failed"),
        (lambda d: d.__setitem__("cohort_conclusion", "anything"), "schema validation failed"),
    ],
)
def test_negative_analysis_input_failures(rc_repo, mutator, expected):
    mutate_analysis(rc_repo, mutator)
    with pytest.raises(SystemExit, match=expected):
        builder.build_retained_classification()



def test_stale_analysis_rejected_before_classification(rc_repo, monkeypatch):
    def stale():
        raise SystemExit("committed analysis structure differs from deterministic dataset analysis")
    monkeypatch.setattr(builder, "verify_analysis_fresh", stale)
    with pytest.raises(SystemExit, match="committed analysis structure differs"):
        builder.build_retained_classification()

def test_modified_i5_registration_fails_closed(rc_repo):
    path = rc_repo / "investigations/b2-governance-cohort/preregistration/i1_i5_registration.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["deterministic_decision_rule"]["precedence"] = ["violates", "indeterminate", "supports"]
    write_json(path, data)
    with pytest.raises(SystemExit, match="I5 registration differs"):
        builder.build_retained_classification()


@pytest.mark.parametrize(
    ("mutator", "expected"),
    [
        (lambda d: d["per_system_classifications"][0].__setitem__("classification", "unknown"), "schema validation failed"),
        (lambda d: d["per_system_classifications"][0].__setitem__("manual_classification", "supports"), "schema validation failed"),
        (lambda d: d["per_system_classifications"][0]["lineage"].pop("bor_paths"), "schema validation failed"),
        (lambda d: d["per_system_classifications"][0]["lineage"].__setitem__("host_path", "/tmp/x"), "schema validation failed"),
        (lambda d: d["per_system_classifications"][2].__setitem__("missing_measurements", []), "structure differs"),
        (lambda d: d["per_system_classifications"][0].__setitem__("confidence", "high"), "schema validation failed"),
        (lambda d: d.__setitem__("cohort_conclusion", "indeterminate"), "schema validation failed"),
        (lambda d: d["generation"].__setitem__("created_at", "2026-07-13T00:00:00Z"), "schema validation failed"),
        (lambda d: d["cohort_classification"].__setitem__("outcome", "supports"), "structure differs"),
    ],
)
def test_negative_committed_artifact_failures(rc_repo, mutator, expected):
    data = committed(rc_repo)
    mutator(data)
    write_json(rc_repo / "investigations/b2-governance-cohort/results/b2-governance-cohort-i5.retained-classification.json", data)
    with pytest.raises(SystemExit, match=expected):
        builder.check_committed(builder.build_retained_classification())


def test_byte_instability_fails_closed(rc_repo):
    data = committed(rc_repo)
    out = rc_repo / "investigations/b2-governance-cohort/results/b2-governance-cohort-i5.retained-classification.json"
    out.write_text(json.dumps(data, sort_keys=True) + "\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="bytes differ"):
        builder.check_committed(builder.build_retained_classification())
