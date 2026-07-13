#!/usr/bin/env python3
"""Build/check the canonical B2 cohort-conclusion artifact from retained classifications and frozen I5."""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
INVESTIGATION_ID="b2-governance-cohort"; PROTOCOL_VERSION="protocol-v1"; COHORT_SIZE=9
RETAINED_PATH=ROOT/"investigations/b2-governance-cohort/results/b2-governance-cohort-i5.retained-classification.json"
OUTPUT_PATH=ROOT/"investigations/b2-governance-cohort/results/b2-governance-cohort-i5.cohort-conclusion.json"
REGISTRATION_PATH=ROOT/"investigations/b2-governance-cohort/preregistration/i1_i5_registration.json"
SCHEMA_PATH=ROOT/"schemas/cohort_conclusion.schema.json"
RETAINED_SCHEMA_PATH=ROOT/"schemas/retained_classification.schema.json"
try:
    from jsonschema import Draft202012Validator
except ModuleNotFoundError:
    sys.path.insert(0, str(ROOT)); from tools.jsonschema_fallback import Draft202012Validator

def rel(p: Path)->str: return str(p.relative_to(ROOT))
def load_json(path: Path)->dict:
    with path.open(encoding="utf-8") as h: data=json.load(h)
    if not isinstance(data,dict): raise SystemExit(f"JSON object required: {rel(path)}")
    return data
def validate_schema(data:dict,path:Path,label:str)->None:
    schema=load_json(path); errors=sorted(Draft202012Validator(schema).iter_errors(data),key=lambda e:list(e.path))
    if errors: raise SystemExit(f"{label} schema validation failed: {'; '.join(e.message for e in errors)}")
def stable_bytes(data:dict)->bytes: return (json.dumps(data,indent=2,sort_keys=False)+"\n").encode()

def verify_retained_fresh()->None:
    subprocess.run([sys.executable, str(ROOT/"scripts/build_retained_classification.py"), "--check"], cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def load_i5()->dict:
    reg=load_json(REGISTRATION_PATH); rule=reg.get("deterministic_decision_rule")
    expected={"id":"I5","per_system_classification":[{"outcome":"indeterminate","condition":"any of m_R, m_L, m_E, m_RL, or m_LE is missing"},{"outcome":"supports","condition":"m_R=m_L=m_E=m_RL=m_LE=1"},{"outcome":"violates","condition":"otherwise; at least one required component is present and equals 0"}],"cohort_outcome":[{"outcome":"indeterminate","condition":"there exists a system with per-system classification indeterminate"},{"outcome":"violates","condition":"there exists a system with per-system classification violates"},{"outcome":"supports","condition":"all systems have per-system classification supports"}],"precedence":["indeterminate","violates","supports"],"deterministic":True}
    if rule != expected: raise SystemExit("frozen B2 I5 registration differs from expected preregistered rule")
    return rule

def build_cohort_conclusion()->dict:
    verify_retained_fresh(); rule=load_i5(); retained=load_json(RETAINED_PATH); validate_schema(retained, RETAINED_SCHEMA_PATH, rel(RETAINED_PATH))
    if retained.get("object_type")!="CanonicalRetainedClassification": raise SystemExit("source retained classification has unexpected object_type")
    if retained.get("protocol_version")!=PROTOCOL_VERSION or retained.get("investigation_id")!=INVESTIGATION_ID: raise SystemExit("source retained classification identity mismatch")
    if retained.get("cohort_size")!=COHORT_SIZE: raise SystemExit("source retained classification cohort size mismatch")
    per=retained.get("per_system_classifications")
    if not isinstance(per,list) or len(per)!=COHORT_SIZE: raise SystemExit("source retained classification must contain exactly 9 system classifications")
    system_ids=[item.get("system_id") for item in per if isinstance(item,dict)]
    if len(system_ids)!=COHORT_SIZE or len(set(system_ids))!=COHORT_SIZE: raise SystemExit("source retained classification contains missing or duplicate system ids")
    if system_ids != sorted(system_ids): raise SystemExit("source retained classification system ids are not canonical ascending")
    outcomes=[item.get("classification") for item in per if isinstance(item,dict)]
    if any(outcome not in ("supports","violates","indeterminate") for outcome in outcomes): raise SystemExit("source retained classification contains unsupported classification")
    rc_cohort=retained.get("cohort_classification")
    if not isinstance(rc_cohort,dict): raise SystemExit("source retained classification missing cohort classification")
    if "indeterminate" in outcomes: outcome="indeterminate"; basis=[item["system_id"] for item in per if item["classification"]=="indeterminate"]
    elif "violates" in outcomes: outcome="violates"; basis=[item["system_id"] for item in per if item["classification"]=="violates"]
    else: outcome="supports"; basis=system_ids
    if rc_cohort.get("outcome")!=outcome or rc_cohort.get("basis")!=basis or rc_cohort.get("precedence")!=rule["precedence"]: raise SystemExit("source retained classification cohort result differs from frozen I5 rebuild")
    lineage=retained.get("lineage")
    if not isinstance(lineage,dict): raise SystemExit("source retained classification lineage malformed")
    return {"object_type":"CanonicalCohortConclusion","schema_version":"canonical-cohort-conclusion-v1","protocol_version":PROTOCOL_VERSION,"investigation_id":INVESTIGATION_ID,"cohort_conclusion_id":"cohort-conclusion-b2-governance-cohort-i5","source_retained_classification_ids":[retained["id"]],"source_retained_classification_refs":[rel(RETAINED_PATH)],"cohort_size":COHORT_SIZE,"protocol_decision_rule_ref":rel(REGISTRATION_PATH)+"#/deterministic_decision_rule/I5/cohort_outcome","deterministic_conclusion":{"outcome":outcome,"precedence":rule["precedence"],"basis_retained_classification_ids":[retained["id"]],"basis_system_ids":basis},"lineage":{"retained_classification_path":rel(RETAINED_PATH),"analysis_path":lineage["analysis_path"],"dataset_path":lineage["dataset_path"],"registration_path":lineage["registration_path"],"msr_paths":lineage["msr_paths"],"der_paths":lineage["der_paths"],"srf_paths":lineage["srf_paths"],"bor_paths":lineage["bor_paths"]},"provenance":{"method":"CanonicalRetainedClassification -> frozen I5 deterministic cohort conclusion","created_from":[rel(RETAINED_PATH),rel(REGISTRATION_PATH)]},"generation":{"builder":"scripts/build_cohort_conclusion.py","mode":"deterministic-rebuild","repository_root":"."}}

def check_committed(expected:dict)->None:
    if not OUTPUT_PATH.exists(): raise SystemExit(f"missing canonical cohort conclusion: {rel(OUTPUT_PATH)}")
    b=OUTPUT_PATH.read_bytes(); committed=json.loads(b)
    if not isinstance(committed,dict): raise SystemExit("committed cohort conclusion must be a JSON object")
    validate_schema(committed, SCHEMA_PATH, rel(OUTPUT_PATH))
    forbidden=("analysis","measurements","dataset_rows","per_system_classifications","explanation","discussion","interpretation","future_work")
    if any(k in committed for k in forbidden): raise SystemExit("cohort conclusion contains fields outside protocol-authorized output")
    if committed != expected: raise SystemExit("committed cohort conclusion structure differs from deterministic I5 rebuild")
    if b != stable_bytes(expected): raise SystemExit("committed cohort conclusion bytes differ from deterministic rebuild")

def main()->None:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--check",action="store_true"); args=p.parse_args()
    data=build_cohort_conclusion(); validate_schema(data, SCHEMA_PATH, "deterministic B2 cohort conclusion")
    if args.check: check_committed(data); print(f"canonical cohort conclusion fresh: {rel(OUTPUT_PATH)}"); return
    OUTPUT_PATH.parent.mkdir(parents=True,exist_ok=True); OUTPUT_PATH.write_bytes(stable_bytes(data)); print(f"wrote {rel(OUTPUT_PATH)}")
if __name__=="__main__": main()
