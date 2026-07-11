import json
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ModuleNotFoundError:  # pragma: no cover - restricted local environments only
    from tools.jsonschema_fallback import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
REGISTRATION_PATH = ROOT / "investigations/b2-governance-cohort/preregistration/i1_i5_registration.json"
BOR_DIR = ROOT / "investigations/b2-governance-cohort/bor"
SCHEMA_PATH = ROOT / "schemas/bor.schema.json"

FORBIDDEN_OBJECT_TYPES = {
    "StructuredResearchFrame",
    "DerivedEvidenceRecord",
    "MeasurementSummaryRecord",
    "ComparativeDataset",
    "Analysis",
    "RetainedClassification",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_b2_bor_records_are_complete_baseline_observation_records():
    registration = load_json(REGISTRATION_PATH)
    cohort = registration["cohort_rule"]["frozen_cohort"]
    bor_paths = sorted(BOR_DIR.glob("*.bor.json"))
    assert len(bor_paths) == len(cohort)

    schema = load_json(SCHEMA_PATH)
    validator = Draft202012Validator(schema)
    seen_bor_ids = set()
    seen_members = set()

    for path in bor_paths:
        data = load_json(path)
        assert not list(validator.iter_errors(data)), path
        for field in [
            "id",
            "object_type",
            "schema_version",
            "protocol_version",
            "investigation_id",
            "cohort_member",
            "constraints",
            "retrieval",
            "admitted_evidence_rule",
            "evidence_sources",
            "observations",
        ]:
            assert field in data, f"{path} missing {field}"

        assert data["object_type"] == "BaselineObservationRecord"
        assert data["object_type"] not in FORBIDDEN_OBJECT_TYPES
        assert data["protocol_version"] == registration["protocol_version"] == "protocol-v1"
        assert data["investigation_id"] == registration["investigation_id"] == "b2-governance-cohort"
        assert data["id"] not in seen_bor_ids
        seen_bor_ids.add(data["id"])

        member = data["cohort_member"]["name"]
        assert member in cohort
        seen_members.add(member)
        expected_index = cohort.index(member)
        assert data["cohort_member"]["selection_basis"]["registration_object"] == str(REGISTRATION_PATH.relative_to(ROOT))
        assert data["cohort_member"]["selection_basis"]["registration_field"] == f"cohort_rule.frozen_cohort[{expected_index}]"

        constraints = data["constraints"]
        assert constraints["record_type"] == "baseline_observations_only"
        assert constraints["no_measurements_derived"] is True
        assert constraints["no_classification_assigned"] is True
        assert constraints["no_srf_der_msr_comparative_dataset_or_analysis_created"] is True
        assert constraints["candidate_invariant_wording_changed"] is False
        assert constraints["protocol_modified"] is False
        assert constraints["i1_i5_registration_modified"] is False

        evidence_ids = {source["source_id"] for source in data["evidence_sources"]}
        assert evidence_ids
        for source in data["evidence_sources"]:
            assert source["source_id"]
            assert source["source_type"] in registration["admitted_evidence_rule"]["admitted_evidence_types_ordered"]
            assert source["title"]
            assert source["publisher"]
            assert source["version_or_channel"]
            assert source["url"].startswith("https://")
            assert source["retrieved_at_utc"]

        observation_ids = set()
        assert data["observations"]
        for observation in data["observations"]:
            assert observation["observation_id"] not in observation_ids
            observation_ids.add(observation["observation_id"])
            assert observation["source_reference"] in evidence_ids
            assert observation["source_type"]
            assert observation["source_location"]
            assert observation["observation_text"]
            assert observation["rationale"]

    assert seen_members == set(cohort)
