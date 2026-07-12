import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate.py"
spec = importlib.util.spec_from_file_location("repository_validate_msr", SCRIPT)
repository_validate = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = repository_validate
spec.loader.exec_module(repository_validate)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bor(name: str, obs: str) -> dict:
    return {"object_type":"BaselineObservationRecord","schema_version":"canonical-bor-v1","protocol_version":"protocol-v1","investigation_id":"b2-governance-cohort","id":f"bor-b2-{name}","cohort_member":{"name":name},"observations":[{"observation_id":obs,"summary":"Synthetic observation for MSR tests.","evidence":{"source_type":"Official product documentation (vendor/project docs) and reference architecture descriptions","title":"Synthetic source","url":"https://example.invalid/synthetic","retrieved":"2026-01-01"}}]}


def srf(name: str, surface: str, obs: str) -> dict:
    return {"object_type":"ExecutionSurfaceRegistry","schema_version":"canonical-srf-v1","protocol_version":"protocol-v1","investigation_id":"b2-governance-cohort","id":f"srf-b2-{name}","cohort_member":{"name":name},"bor_reference":{"bor_id":f"bor-b2-{name}","path":f"investigations/b2-governance-cohort/bor/{name}.bor.json"},"constraints":{"record_type":"execution_surfaces_only","bor_preserved":True,"no_derivation_performed":True,"no_measurements_derived":True,"no_classification_assigned":True,"no_cross_system_comparison":True,"candidate_invariant_wording_changed":False,"protocol_modified":False,"i1_i5_registration_modified":False},"surfaces":{"execution_entry_points":[{"id":surface,"label":"surface","description":"Synthetic surface.","observation_refs":[obs]}],"authorization_surfaces":[],"validation_surfaces":[],"policy_evaluation_surfaces":[],"protected_resources":[],"execution_boundaries":[],"observable_execution_flow":[]}}


def der(name: str, did: str, surface: str, obs: str) -> dict:
    return {"object_type":"DerivedEvidenceRecord","schema_version":"canonical-der-v1","protocol_version":"protocol-v1","investigation_id":"b2-governance-cohort","id":did,"source_srf_ids":[f"srf-b2-{name}"],"source_surface_ids":[surface],"source_observation_refs":[obs],"derivation_rule":{"derivation_source_reference":"protocol/protocol-v1/protocol.md#srf-to-der-contract","description":"Derive only bounded synthetic claim."},"derived_claim":{"claim":"Synthetic DER claim for MSR tests.","interpretation_boundary":"direct_derivation_only"},"provenance":{"created_from":[f"investigations/b2-governance-cohort/srf/{name}.srf.json","protocol/protocol-v1/protocol.md"],"notes":"Synthetic fixture."}}


def msr(name: str, did: str, obs: str) -> dict:
    comps = ["m_R", "m_L", "m_E", "m_RL", "m_LE"]
    return {"object_type":"MeasurementStudyRecord","schema_version":"canonical-msr-v1","protocol_version":"protocol-v1","investigation_id":"b2-governance-cohort","system_id":name,"id":f"msr-b2-{name}","source_der_ids":[did],"measurement_registry_ref":{"registration_id":"b2-i1-i5-registration","measurement_vector_id":"I4","path":"investigations/b2-governance-cohort/preregistration/i1_i5_registration.json"},"measurements":[{"measurement_id":c,"rule_id":f"I4.{c}","operationalization_ref":"investigations/b2-governance-cohort/preregistration/i1_i5_registration.json#/measurement_vector/components","value_type":"boolean_or_missing","allowed_domain":[0,1,None],"value":1,"status":"observed","source_der_ids":[did],"evidence_trace_refs":[obs]} for c in comps],"status":"reference_execution","provenance":{"created_from":[f"investigations/b2-governance-cohort/der/{name}.der.json","investigations/b2-governance-cohort/preregistration/i1_i5_registration.json"],"method":"DER -> registered I4 measurement rule -> MSR","notes":"Synthetic fixture."}}


@pytest.fixture
def repo(tmp_path, monkeypatch):
    (tmp_path / "protocol/protocol-v1").mkdir(parents=True)
    (tmp_path / "protocol/protocol-v1/protocol.md").write_text("# Protocol\n\n## SRF to DER Contract\n", encoding="utf-8")
    for schema in ["bor", "srf", "der", "msr"]:
        write_json(tmp_path / f"schemas/{schema}.schema.json", json.loads((ROOT / f"schemas/{schema}.schema.json").read_text()))
    reg = json.loads((ROOT / "investigations/b2-governance-cohort/preregistration/i1_i5_registration.json").read_text())
    write_json(tmp_path / "investigations/b2-governance-cohort/preregistration/i1_i5_registration.json", reg)
    for name, did, surface, obs in [("alpha", "der-b2-alpha-boundary", "surface-alpha", "obs-alpha"), ("beta", "der-b2-beta-boundary", "surface-beta", "obs-beta")]:
        write_json(tmp_path / f"investigations/b2-governance-cohort/bor/{name}.bor.json", bor(name, obs))
        write_json(tmp_path / f"investigations/b2-governance-cohort/srf/{name}.srf.json", srf(name, surface, obs))
        write_json(tmp_path / f"investigations/b2-governance-cohort/der/{name}.der.json", der(name, did, surface, obs))
    monkeypatch.setattr(repository_validate, "ROOT", tmp_path)
    return tmp_path


def fails(repo: Path, data: dict, expected: str):
    write_json(repo / "investigations/b2-governance-cohort/msr/alpha.msr.json", data)
    with pytest.raises(SystemExit, match=expected):
        repository_validate.validate_msr_contract()


def test_valid_msr_passes_and_resolves_lineage(repo):
    write_json(repo / "investigations/b2-governance-cohort/msr/alpha.msr.json", msr("alpha", "der-b2-alpha-boundary", "obs-alpha"))
    repository_validate.validate_msr_contract()


def test_valid_reference_msrs_pass_in_repository():
    repository_validate.validate_msr_contract()


def test_negative_msr_contract_paths(repo):
    base = msr("alpha", "der-b2-alpha-boundary", "obs-alpha")
    cases = []
    d=json.loads(json.dumps(base)); d["source_der_ids"]=["missing"]; cases.append((d,"references missing DER id"))
    d=json.loads(json.dumps(base)); d["measurements"][0]["source_der_ids"]=["der-b2-beta-boundary"]; cases.append((d,"measurement uses undeclared DER"))
    d=json.loads(json.dumps(base)); d["system_id"]="beta"; cases.append((d,"references DER from another system"))
    d=json.loads(json.dumps(base)); d["measurements"][0]["rule_id"]="I4.unknown"; cases.append((d,"schema validation failed"))
    d=json.loads(json.dumps(base)); d["measurements"][0]["value"]=2; cases.append((d,"schema validation failed"))
    d=json.loads(json.dumps(base)); d["measurements"][1]["measurement_id"]="m_R"; d["measurements"][1]["rule_id"]="I4.m_R"; cases.append((d,"contains duplicate measurement"))
    d=json.loads(json.dumps(base)); d["measurements"]=d["measurements"][:-1]; cases.append((d,"schema validation failed"))
    d=json.loads(json.dumps(base)); d["provenance"]["created_from"]=["investigations/b2-governance-cohort/preregistration/i1_i5_registration.json"]; cases.append((d,"schema validation failed"))
    d=json.loads(json.dumps(base)); d["measurements"][0]["evidence_trace_refs"]=["obs-beta"]; cases.append((d,"evidence trace is outside declared DER lineage"))
    d=json.loads(json.dumps(base)); d["analysis"]={"classification":"supports"}; cases.append((d,"schema validation failed"))
    for data, expected in cases:
        (repo / "investigations/b2-governance-cohort/msr/alpha.msr.json").unlink(missing_ok=True)
        fails(repo, data, expected)
