import importlib.util
import json
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate.py"
SCHEMA_PATH = ROOT / "schemas" / "der.schema.json"

spec = importlib.util.spec_from_file_location("repository_validate", SCRIPT)
repository_validate = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = repository_validate
spec.loader.exec_module(repository_validate)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def srf_record() -> dict:
    return {
        "object_type": "ExecutionSurfaceRegistry",
        "schema_version": "canonical-srf-v1",
        "protocol_version": "protocol-v1",
        "investigation_id": "synthetic-investigation",
        "id": "srf-synthetic-system",
        "surfaces": {
            "execution_entry_points": [
                {
                    "id": "surface-entry",
                    "label": "Entry",
                    "description": "Synthetic entry point for contract testing.",
                    "observation_refs": ["obs-entry"],
                }
            ],
            "authorization_surfaces": [],
            "validation_surfaces": [],
            "policy_evaluation_surfaces": [],
            "protected_resources": [],
            "execution_boundaries": [],
            "observable_execution_flow": [],
        },
    }


def der_record(**overrides) -> dict:
    data = {
        "object_type": "DerivedEvidenceRecord",
        "schema_version": "canonical-der-v1",
        "protocol_version": "protocol-v1",
        "investigation_id": "synthetic-investigation",
        "id": "der-synthetic-boundary",
        "source_srf_ids": ["srf-synthetic-system"],
        "source_surface_ids": ["surface-entry"],
        "source_observation_refs": ["obs-entry"],
        "derivation_rule": {
            "registered_derivation_reference": "protocol/protocol-v1/protocol.md#srf-to-der-contract",
            "description": "Derive only the bounded claim supported by the referenced SRF surface.",
        },
        "derived_claim": {
            "claim": "Synthetic derived claim for schema and lineage validation only.",
            "interpretation_boundary": "direct_derivation_only",
        },
        "provenance": {
            "created_from": ["investigations/synthetic-investigation/srf/synthetic.srf.json"],
            "notes": "Synthetic fixture; not a canonical research result.",
        },
    }
    for key, value in overrides.items():
        if value is None:
            data.pop(key, None)
        else:
            data[key] = value
    return data


@pytest.fixture
def synthetic_repo(tmp_path, monkeypatch):
    (tmp_path / "protocol/protocol-v1").mkdir(parents=True)
    (tmp_path / "protocol/protocol-v1/protocol.md").write_text("# Protocol\n", encoding="utf-8")
    write_json(tmp_path / "schemas/der.schema.json", json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))
    write_json(tmp_path / "investigations/synthetic-investigation/srf/synthetic.srf.json", srf_record())
    (tmp_path / "investigations/synthetic-investigation/der").mkdir(parents=True)
    monkeypatch.setattr(repository_validate, "ROOT", tmp_path)
    return tmp_path


def assert_der_contract_fails(repo: Path, data: dict, expected: str) -> None:
    write_json(repo / "investigations/synthetic-investigation/der/synthetic.der.json", data)
    with pytest.raises(SystemExit, match=expected):
        repository_validate.validate_der_contract()


def test_valid_der_with_complete_srf_lineage_passes(synthetic_repo):
    write_json(
        synthetic_repo / "investigations/synthetic-investigation/der/synthetic.der.json",
        der_record(),
    )
    repository_validate.validate_der_contract()


def test_missing_der_id_is_invalid(synthetic_repo):
    assert_der_contract_fails(synthetic_repo, der_record(id=None), "DER schema validation failed")


def test_missing_investigation_id_is_invalid(synthetic_repo):
    assert_der_contract_fails(synthetic_repo, der_record(investigation_id=None), "DER schema validation failed")


def test_unknown_srf_id_is_invalid(synthetic_repo):
    assert_der_contract_fails(
        synthetic_repo,
        der_record(source_srf_ids=["srf-unknown"]),
        "references unknown SRF id",
    )


def test_unknown_surface_id_is_invalid(synthetic_repo):
    assert_der_contract_fails(
        synthetic_repo,
        der_record(source_surface_ids=["surface-unknown"]),
        "references unknown SRF surface id",
    )


def test_unknown_observation_ref_is_invalid(synthetic_repo):
    assert_der_contract_fails(
        synthetic_repo,
        der_record(source_observation_refs=["obs-unknown"]),
        "references unknown SRF observation ref",
    )


def test_investigation_mismatch_between_der_and_srf_is_invalid(synthetic_repo):
    assert_der_contract_fails(
        synthetic_repo,
        der_record(investigation_id="other-investigation"),
        "investigation_id does not match directory",
    )


def test_duplicate_der_ids_are_invalid(synthetic_repo):
    write_json(synthetic_repo / "investigations/synthetic-investigation/der/a.der.json", der_record())
    write_json(synthetic_repo / "investigations/synthetic-investigation/der/b.der.json", der_record())
    with pytest.raises(SystemExit, match="duplicate DER id"):
        repository_validate.validate_der_contract()


def test_empty_or_structurally_meaningless_derivation_is_invalid(synthetic_repo):
    assert_der_contract_fails(
        synthetic_repo,
        der_record(source_surface_ids=[]),
        "DER schema validation failed",
    )


def test_unregistered_derivation_rule_is_invalid(synthetic_repo):
    data = der_record()
    data["derivation_rule"]["registered_derivation_reference"] = "protocol/protocol-v1/missing.md"
    assert_der_contract_fails(synthetic_repo, data, "references unregistered derivation rule")


def test_der_schema_rejects_uncontrolled_additional_properties():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    data = der_record(unregistered_field="not allowed")
    assert list(validator.iter_errors(data))
