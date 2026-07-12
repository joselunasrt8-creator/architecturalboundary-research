import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_dataset.py"
spec = importlib.util.spec_from_file_location("b2_dataset_builder", SCRIPT)
b2_dataset_builder = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = b2_dataset_builder
spec.loader.exec_module(b2_dataset_builder)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def configure_builder(monkeypatch, repo: Path) -> Path:
    output = repo / "investigations/b2-governance-cohort/dataset/b2-governance-cohort-i4.dataset.json"
    monkeypatch.setattr(b2_dataset_builder, "ROOT", repo)
    monkeypatch.setattr(b2_dataset_builder, "MSR_DIR", repo / "investigations/b2-governance-cohort/msr")
    monkeypatch.setattr(b2_dataset_builder, "OUTPUT_PATH", output)
    monkeypatch.setattr(b2_dataset_builder, "SCHEMA_PATH", repo / "schemas/dataset.schema.json")
    return output


@pytest.fixture
def dataset_repo(tmp_path, monkeypatch):
    for relative in ["schemas/dataset.schema.json", "schemas/msr.schema.json"]:
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, destination)
    shutil.copytree(
        ROOT / "investigations/b2-governance-cohort/msr",
        tmp_path / "investigations/b2-governance-cohort/msr",
    )
    configure_builder(monkeypatch, tmp_path)
    monkeypatch.setattr(b2_dataset_builder, "validate_full_msr_contract", lambda: None)
    return tmp_path


@pytest.fixture
def full_contract_repo(tmp_path, monkeypatch):
    for relative in [
        "protocol/protocol-v1/protocol.md",
        "schemas/bor.schema.json",
        "schemas/srf.schema.json",
        "schemas/der.schema.json",
        "schemas/msr.schema.json",
        "schemas/dataset.schema.json",
        "investigations/b2-governance-cohort/preregistration/i1_i5_registration.json",
    ]:
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, destination)
    for stage in ["bor", "srf", "der", "msr"]:
        shutil.copytree(
            ROOT / "investigations/b2-governance-cohort" / stage,
            tmp_path / "investigations/b2-governance-cohort" / stage,
        )
    configure_builder(monkeypatch, tmp_path)
    return tmp_path


def committed_dataset(repo: Path) -> dict:
    output = repo / "investigations/b2-governance-cohort/dataset/b2-governance-cohort-i4.dataset.json"
    data = b2_dataset_builder.build_dataset()
    write_json(output, data)
    b2_dataset_builder.check_committed(data)
    return data


def expect_stale(repo: Path, data: dict, expected: str = "differs") -> None:
    output = repo / "investigations/b2-governance-cohort/dataset/b2-governance-cohort-i4.dataset.json"
    write_json(output, data)
    expected_dataset = b2_dataset_builder.build_dataset()
    with pytest.raises(SystemExit, match=expected):
        b2_dataset_builder.check_committed(expected_dataset)


def test_canonical_dataset_positive_projection_is_fresh(dataset_repo):
    data = committed_dataset(dataset_repo)
    assert [row["system_id"] for row in data["rows"]] == sorted(row["system_id"] for row in data["rows"])
    assert len(data["rows"]) == 9


def test_standalone_builder_runs_full_msr_contract_before_projection(full_contract_repo):
    msr_path = full_contract_repo / "investigations/b2-governance-cohort/msr/aws-iam.msr.json"
    msr = json.loads(msr_path.read_text(encoding="utf-8"))
    msr["measurements"][0]["value"] = 0
    write_json(msr_path, msr)

    with pytest.raises(SystemExit, match="measurement result conflicts with basis determination"):
        b2_dataset_builder.build_dataset()


def test_missing_msr_fails_closed(dataset_repo):
    (dataset_repo / "investigations/b2-governance-cohort/msr/aws-iam.msr.json").unlink()
    with pytest.raises(SystemExit, match="expected exactly 9 B2 MSRs"):
        b2_dataset_builder.build_dataset()


def test_duplicate_system_fails_closed(dataset_repo):
    msr_dir = dataset_repo / "investigations/b2-governance-cohort/msr"
    (msr_dir / "openfga.msr.json").unlink()
    duplicate = json.loads((msr_dir / "aws-iam.msr.json").read_text(encoding="utf-8"))
    duplicate["id"] = "msr-b2-aws-iam-duplicate-reference-execution"
    write_json(msr_dir / "aws-iam-duplicate.msr.json", duplicate)

    with pytest.raises(SystemExit, match="more than one canonical MSR exists for system aws-iam"):
        b2_dataset_builder.build_dataset()


@pytest.mark.parametrize(
    ("mutate", "expected"),
    [
        (lambda d: d["rows"][0].__setitem__("m_R", 0), "structure differs"),
        (lambda d: d["rows"][0].__setitem__("msr_id", "msr-b2-openfga-reference-execution"), "structure differs"),
        (lambda d: d["rows"][2].__setitem__("m_R", 0), "structure differs"),
        (lambda d: d["source_msr_ids"].__setitem__(0, "msr-b2-openfga-reference-execution"), "schema validation failed"),
        (lambda d: d["rows"].reverse(), "structure differs"),
        (lambda d: d["rows"][0]["lineage"].pop("source_der_ids"), "schema validation failed"),
        (lambda d: d["rows"][0].__setitem__("analysis", {"classification": "supports"}), "schema validation failed"),
    ],
)
def test_committed_dataset_drift_paths_fail_closed(dataset_repo, mutate, expected):
    data = committed_dataset(dataset_repo)
    mutate(data)
    expect_stale(dataset_repo, data, expected)


def test_byte_instability_fails_closed(dataset_repo):
    data = committed_dataset(dataset_repo)
    output = dataset_repo / "investigations/b2-governance-cohort/dataset/b2-governance-cohort-i4.dataset.json"
    output.write_text(json.dumps(data, sort_keys=True) + "\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="bytes differ"):
        b2_dataset_builder.check_committed(b2_dataset_builder.build_dataset())
