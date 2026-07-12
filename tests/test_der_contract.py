import importlib.util
import json
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from tools.jsonschema_fallback import Draft202012Validator as FallbackDraft202012Validator

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


def srf_path(name: str) -> str:
    return f"investigations/b2-governance-cohort/srf/{name}.srf.json"


def srf_record(name: str, surface_id: str, observation_ref: str) -> dict:
    return {
        "object_type": "ExecutionSurfaceRegistry",
        "schema_version": "canonical-srf-v1",
        "protocol_version": "protocol-v1",
        "investigation_id": "b2-governance-cohort",
        "id": f"srf-b2-{name}",
        "cohort_member": {"name": name},
        "bor_reference": {
            "bor_id": f"bor-b2-{name}",
            "path": f"investigations/b2-governance-cohort/bor/{name}.bor.json",
        },
        "constraints": {
            "record_type": "execution_surfaces_only",
            "bor_preserved": True,
            "no_derivation_performed": True,
            "no_measurements_derived": True,
            "no_classification_assigned": True,
            "no_cross_system_comparison": True,
            "candidate_invariant_wording_changed": False,
            "protocol_modified": False,
            "i1_i5_registration_modified": False,
        },
        "surfaces": {
            "execution_entry_points": [
                {
                    "id": surface_id,
                    "label": f"{name} entry",
                    "description": "Synthetic entry point for contract testing.",
                    "observation_refs": [observation_ref],
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
        "investigation_id": "b2-governance-cohort",
        "id": "der-b2-synthetic-boundary",
        "source_srf_ids": ["srf-b2-alpha"],
        "source_surface_ids": ["surface-alpha"],
        "source_observation_refs": ["obs-alpha"],
        "derivation_rule": {
            "derivation_source_reference": "protocol/protocol-v1/protocol.md#srf-to-der-contract",
            "description": "Derive only the bounded claim supported by the referenced SRF surface.",
        },
        "derived_claim": {
            "claim": "Synthetic derived claim for schema and lineage validation only.",
            "interpretation_boundary": "direct_derivation_only",
        },
        "provenance": {
            "created_from": [
                srf_path("alpha"),
                "protocol/protocol-v1/protocol.md",
            ],
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
    (tmp_path / "protocol/protocol-v1/protocol.md").write_text(
        "# Protocol\n\n## SRF to DER Contract\n", encoding="utf-8"
    )
    write_json(tmp_path / "schemas/der.schema.json", json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))
    write_json(tmp_path / "schemas/srf.schema.json", json.loads((ROOT / "schemas/srf.schema.json").read_text(encoding="utf-8")))
    write_json(tmp_path / srf_path("alpha"), srf_record("alpha", "surface-alpha", "obs-alpha"))
    write_json(tmp_path / srf_path("beta"), srf_record("beta", "surface-beta", "obs-beta"))
    (tmp_path / "investigations/b2-governance-cohort/der").mkdir(parents=True)
    monkeypatch.setattr(repository_validate, "ROOT", tmp_path)
    return tmp_path


def assert_der_contract_fails(repo: Path, data: dict, expected: str) -> None:
    write_json(repo / "investigations/b2-governance-cohort/der/synthetic.der.json", data)
    with pytest.raises(SystemExit, match=expected):
        repository_validate.validate_der_contract()


def test_valid_der_with_complete_srf_lineage_passes(synthetic_repo):
    write_json(
        synthetic_repo / "investigations/b2-governance-cohort/der/synthetic.der.json",
        der_record(),
    )
    repository_validate.validate_der_contract()


def test_valid_der_can_declare_multiple_srfs_and_reference_both(synthetic_repo):
    data = der_record(
        source_srf_ids=["srf-b2-alpha", "srf-b2-beta"],
        source_surface_ids=["surface-alpha", "surface-beta"],
        source_observation_refs=["obs-alpha", "obs-beta"],
    )
    data["provenance"]["created_from"] = [srf_path("alpha"), srf_path("beta"), "protocol/protocol-v1/protocol.md"]
    write_json(synthetic_repo / "investigations/b2-governance-cohort/der/synthetic.der.json", data)
    repository_validate.validate_der_contract()


def test_missing_der_id_is_invalid(synthetic_repo):
    assert_der_contract_fails(synthetic_repo, der_record(id=None), "schema validation failed")


def test_missing_investigation_id_is_invalid(synthetic_repo):
    assert_der_contract_fails(synthetic_repo, der_record(investigation_id=None), "schema validation failed")


def test_unknown_srf_id_is_invalid(synthetic_repo):
    data = der_record(source_srf_ids=["srf-b2-unknown"])
    data["provenance"]["created_from"] = ["protocol/protocol-v1/protocol.md"]
    assert_der_contract_fails(synthetic_repo, data, "references unknown SRF id")


def test_surface_from_undeclared_srf_is_invalid(synthetic_repo):
    assert_der_contract_fails(
        synthetic_repo,
        der_record(source_surface_ids=["surface-beta"]),
        "references undeclared SRF surface id",
    )


def test_observation_from_undeclared_srf_is_invalid(synthetic_repo):
    assert_der_contract_fails(
        synthetic_repo,
        der_record(source_observation_refs=["obs-beta"]),
        "references undeclared SRF observation ref",
    )


def test_unknown_surface_id_is_invalid(synthetic_repo):
    assert_der_contract_fails(
        synthetic_repo,
        der_record(source_surface_ids=["surface-unknown"]),
        "references undeclared SRF surface id",
    )


def test_unknown_observation_ref_is_invalid(synthetic_repo):
    assert_der_contract_fails(
        synthetic_repo,
        der_record(source_observation_refs=["obs-unknown"]),
        "references undeclared SRF observation ref",
    )


def test_source_srf_must_be_schema_valid_before_der_use(synthetic_repo):
    malformed = srf_record("alpha", "surface-alpha", "obs-alpha")
    malformed.pop("constraints")
    write_json(synthetic_repo / srf_path("alpha"), malformed)
    assert_der_contract_fails(synthetic_repo, der_record(), "schema validation failed")


def test_investigation_mismatch_between_der_and_srf_is_invalid(synthetic_repo):
    assert_der_contract_fails(
        synthetic_repo,
        der_record(investigation_id="other-investigation"),
        "investigation_id does not match directory",
    )


def test_duplicate_der_ids_are_invalid(synthetic_repo):
    write_json(synthetic_repo / "investigations/b2-governance-cohort/der/a.der.json", der_record())
    write_json(synthetic_repo / "investigations/b2-governance-cohort/der/b.der.json", der_record())
    with pytest.raises(SystemExit, match="duplicate DER id"):
        repository_validate.validate_der_contract()


def test_empty_or_structurally_meaningless_derivation_is_invalid(synthetic_repo):
    assert_der_contract_fails(
        synthetic_repo,
        der_record(source_surface_ids=[]),
        "schema validation failed",
    )


def test_absolute_derivation_source_is_invalid(synthetic_repo):
    data = der_record()
    data["derivation_rule"]["derivation_source_reference"] = "/etc/passwd"
    assert_der_contract_fails(synthetic_repo, data, "must be repository-relative")


def test_escaping_derivation_source_is_invalid(synthetic_repo):
    data = der_record()
    data["derivation_rule"]["derivation_source_reference"] = "../outside.md"
    assert_der_contract_fails(synthetic_repo, data, "escapes repository")


def test_missing_derivation_source_is_invalid(synthetic_repo):
    data = der_record()
    data["derivation_rule"]["derivation_source_reference"] = "protocol/protocol-v1/missing.md"
    assert_der_contract_fails(synthetic_repo, data, "does not exist")


def test_derivation_source_fragment_must_resolve_to_markdown_heading(synthetic_repo):
    data = der_record()
    data["derivation_rule"]["derivation_source_reference"] = "protocol/protocol-v1/protocol.md#missing-heading"
    assert_der_contract_fails(synthetic_repo, data, "fragment does not resolve")


def test_repository_contained_preregistration_derivation_source_is_valid(synthetic_repo):
    prereg = synthetic_repo / "investigations/b2-governance-cohort/preregistration/derivation.md"
    prereg.parent.mkdir(parents=True, exist_ok=True)
    prereg.write_text("# Registered Derivation\n", encoding="utf-8")
    data = der_record()
    data["derivation_rule"]["derivation_source_reference"] = (
        "investigations/b2-governance-cohort/preregistration/derivation.md#registered-derivation"
    )
    data["provenance"]["created_from"] = [srf_path("alpha"), "investigations/b2-governance-cohort/preregistration/derivation.md"]
    write_json(synthetic_repo / "investigations/b2-governance-cohort/der/synthetic.der.json", data)
    repository_validate.validate_der_contract()


def test_missing_provenance_path_is_invalid(synthetic_repo):
    data = der_record()
    data["provenance"]["created_from"] = [srf_path("alpha"), "missing/file.md"]
    assert_der_contract_fails(synthetic_repo, data, "DER provenance reference does not exist")


def test_outside_repository_provenance_path_is_invalid(synthetic_repo):
    data = der_record()
    data["provenance"]["created_from"] = [srf_path("alpha"), "/etc/passwd"]
    assert_der_contract_fails(synthetic_repo, data, "DER provenance reference must be repository-relative")


def test_existing_but_unrelated_provenance_object_is_invalid(synthetic_repo):
    unrelated = synthetic_repo / "protocol/protocol-v1/decision_rules.md"
    unrelated.write_text("# Decision Rules\n", encoding="utf-8")
    data = der_record()
    data["provenance"]["created_from"] = [srf_path("alpha"), "protocol/protocol-v1/protocol.md", "protocol/protocol-v1/decision_rules.md"]
    assert_der_contract_fails(synthetic_repo, data, "provenance contains unrelated")


def test_der_schema_rejects_uncontrolled_additional_properties():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    data = der_record(unregistered_field="not allowed")
    assert list(validator.iter_errors(data))


@pytest.mark.parametrize(
    "mutate",
    [
        lambda data: data.update({"object_type": "WrongObject"}),
        lambda data: data.update({"unexpected": "not allowed"}),
        lambda data: data.update({"id": "not a der id"}),
        lambda data: data.update({"source_srf_ids": []}),
        lambda data: data.update({"source_srf_ids": ["srf-b2-alpha", "srf-b2-alpha"]}),
        lambda data: data["derived_claim"].update({"interpretation_boundary": "invalid"}),
    ],
)
def test_fallback_validator_rejects_der_schema_keywords_consistently(mutate):
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    data = der_record()
    mutate(data)
    full_errors = list(Draft202012Validator(schema).iter_errors(data))
    fallback_errors = list(FallbackDraft202012Validator(schema).iter_errors(data))
    assert full_errors
    assert fallback_errors


def test_fallback_validator_accepts_valid_der_schema_shape():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    data = der_record()
    assert not list(Draft202012Validator(schema).iter_errors(data))
    assert not list(FallbackDraft202012Validator(schema).iter_errors(data))
