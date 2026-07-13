from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_cohort_conclusion.py"
spec = importlib.util.spec_from_file_location("b2_cohort_builder", SCRIPT)
builder = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = builder
spec.loader.exec_module(builder)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


@pytest.fixture()
def cohort_repo(tmp_path, monkeypatch):
    for relative in [
        "schemas/cohort_conclusion.schema.json",
        "schemas/retained_classification.schema.json",
        "investigations/b2-governance-cohort/preregistration/i1_i5_registration.json",
        "investigations/b2-governance-cohort/results/b2-governance-cohort-i5.retained-classification.json",
    ]:
        src = ROOT / relative
        dst = tmp_path / relative
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    monkeypatch.setattr(builder, "ROOT", tmp_path)
    monkeypatch.setattr(builder, "RETAINED_PATH", tmp_path / "investigations/b2-governance-cohort/results/b2-governance-cohort-i5.retained-classification.json")
    monkeypatch.setattr(builder, "OUTPUT_PATH", tmp_path / "investigations/b2-governance-cohort/results/b2-governance-cohort-i5.cohort-conclusion.json")
    monkeypatch.setattr(builder, "REGISTRATION_PATH", tmp_path / "investigations/b2-governance-cohort/preregistration/i1_i5_registration.json")
    monkeypatch.setattr(builder, "SCHEMA_PATH", tmp_path / "schemas/cohort_conclusion.schema.json")
    monkeypatch.setattr(builder, "RETAINED_SCHEMA_PATH", tmp_path / "schemas/retained_classification.schema.json")
    monkeypatch.setattr(builder, "verify_retained_fresh", lambda: None)
    return tmp_path


def retained(repo: Path) -> dict:
    return json.loads((repo / "investigations/b2-governance-cohort/results/b2-governance-cohort-i5.retained-classification.json").read_text())


def test_valid_canonical_generation(cohort_repo):
    data = builder.build_cohort_conclusion()
    builder.validate_schema(data, builder.SCHEMA_PATH, "cohort")
    assert data["object_type"] == "CanonicalCohortConclusion"
    assert data["cohort_size"] == 9
    assert data["deterministic_conclusion"]["outcome"] == "indeterminate"
    assert data["source_retained_classification_ids"] == ["retained-classification-b2-governance-cohort-i5"]


def test_stale_conclusion_detection(cohort_repo):
    data = builder.build_cohort_conclusion()
    data["deterministic_conclusion"]["outcome"] = "supports"
    write_json(builder.OUTPUT_PATH, data)
    with pytest.raises(SystemExit, match="structure differs"):
        builder.check_committed(builder.build_cohort_conclusion())


def test_missing_retained_classification_fails_closed(cohort_repo):
    builder.RETAINED_PATH.unlink()
    with pytest.raises(FileNotFoundError):
        builder.build_cohort_conclusion()


def test_duplicate_classifications_fail_closed(cohort_repo):
    data = retained(cohort_repo)
    data["per_system_classifications"][1]["system_id"] = data["per_system_classifications"][0]["system_id"]
    write_json(builder.RETAINED_PATH, data)
    with pytest.raises(SystemExit, match="duplicate"):
        builder.build_cohort_conclusion()


def test_protocol_mismatch_fails_closed(cohort_repo):
    data = retained(cohort_repo)
    data["protocol_version"] = "protocol-v2"
    write_json(builder.RETAINED_PATH, data)
    with pytest.raises(SystemExit, match="schema validation failed|identity mismatch"):
        builder.build_cohort_conclusion()


def test_lineage_mismatch_fails_closed(cohort_repo):
    data = retained(cohort_repo)
    data["cohort_classification"]["basis"] = ["aws-iam"]
    write_json(builder.RETAINED_PATH, data)
    with pytest.raises(SystemExit, match="cohort result differs"):
        builder.build_cohort_conclusion()


def test_byte_stability(cohort_repo):
    first = builder.stable_bytes(builder.build_cohort_conclusion())
    second = builder.stable_bytes(builder.build_cohort_conclusion())
    assert first == second


def test_freshness_mode_accepts_canonical_output(cohort_repo):
    data = builder.build_cohort_conclusion()
    write_json(builder.OUTPUT_PATH, data)
    builder.check_committed(builder.build_cohort_conclusion())


def test_forbidden_field_rejection(cohort_repo):
    data = builder.build_cohort_conclusion()
    data["measurements"] = []
    write_json(builder.OUTPUT_PATH, data)
    with pytest.raises(SystemExit, match="schema validation failed"):
        builder.check_committed(builder.build_cohort_conclusion())
