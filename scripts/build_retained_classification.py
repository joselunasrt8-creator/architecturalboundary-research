#!/usr/bin/env python3
"""Build/check the canonical B2 retained-classification artifact from Analysis and frozen I5."""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
INVESTIGATION_ID="b2-governance-cohort"; PROTOCOL_VERSION="protocol-v1"
MEASUREMENTS=("m_R","m_L","m_E","m_RL","m_LE")
ANALYSIS_PATH=ROOT/"investigations/b2-governance-cohort/analysis/b2-governance-cohort-i4.analysis.json"
DATASET_PATH=ROOT/"investigations/b2-governance-cohort/dataset/b2-governance-cohort-i4.dataset.json"
REGISTRATION_PATH=ROOT/"investigations/b2-governance-cohort/preregistration/i1_i5_registration.json"
OUTPUT_PATH=ROOT/"investigations/b2-governance-cohort/results/b2-governance-cohort-i5.retained-classification.json"
SCHEMA_PATH=ROOT/"schemas/retained_classification.schema.json"
ANALYSIS_SCHEMA_PATH=ROOT/"schemas/analysis.schema.json"
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

def verify_analysis_fresh()->None:
    subprocess.run([sys.executable, str(ROOT/"scripts/build_analysis.py"), "--check"], cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def load_i5()->dict:
    reg=load_json(REGISTRATION_PATH); rule=reg.get("deterministic_decision_rule")
    expected={"id":"I5","per_system_classification":[{"outcome":"indeterminate","condition":"any of m_R, m_L, m_E, m_RL, or m_LE is missing"},{"outcome":"supports","condition":"m_R=m_L=m_E=m_RL=m_LE=1"},{"outcome":"violates","condition":"otherwise; at least one required component is present and equals 0"}],"cohort_outcome":[{"outcome":"indeterminate","condition":"there exists a system with per-system classification indeterminate"},{"outcome":"violates","condition":"there exists a system with per-system classification violates"},{"outcome":"supports","condition":"all systems have per-system classification supports"}],"precedence":["indeterminate","violates","supports"],"deterministic":True}
    if rule != expected: raise SystemExit("frozen B2 I5 registration differs from expected preregistered rule")
    return rule

def der_records()->dict[str,tuple[dict,Path]]:
    out={}
    for path in sorted((ROOT/"investigations/b2-governance-cohort/der").glob("*.der.json")):
        data=load_json(path); out[data["id"]]=(data,path)
    return out
def srf_records()->dict[str,tuple[dict,Path]]:
    out={}
    for path in sorted((ROOT/"investigations/b2-governance-cohort/srf").glob("*.srf.json")):
        data=load_json(path); out[data["id"]]=(data,path)
    return out

def classify(measurements:dict)->tuple[str,list[str]]:
    vals=[measurements.get(m) for m in MEASUREMENTS]
    if any(v is None for v in vals): return "indeterminate", [m for m in MEASUREMENTS if measurements.get(m) is None]
    if all(v == 1 for v in vals): return "supports", []
    if any(v == 0 for v in vals): return "violates", []
    raise SystemExit("invalid measurement vector for I5 classification")

def build_retained_classification()->dict:
    verify_analysis_fresh(); rule=load_i5(); analysis=load_json(ANALYSIS_PATH); validate_schema(analysis, ANALYSIS_SCHEMA_PATH, rel(ANALYSIS_PATH))
    rows=analysis.get("system_measurement_matrix")
    if not isinstance(rows,list) or len(rows)!=9: raise SystemExit("analysis must contain exactly 9 system rows")
    system_ids=[r.get("system_id") for r in rows if isinstance(r,dict)]
    if len(system_ids)!=len(rows) or len(set(system_ids))!=len(rows): raise SystemExit("analysis contains missing or duplicate system ids")
    if system_ids != sorted(system_ids): raise SystemExit("analysis system rows are not canonical system_id ascending")
    ders=der_records(); srfs=srf_records(); per=[]; all_msr=[]; all_der=[]; all_srf=[]; all_bor=[]
    for row in rows:
        if not isinstance(row,dict): raise SystemExit("analysis row must be object")
        measurements=row.get("measurements")
        if not isinstance(measurements,dict) or set(measurements)!=set(MEASUREMENTS): raise SystemExit("analysis row has incomplete measurement inputs")
        if any(measurements[m] not in (0,1,None) for m in MEASUREMENTS): raise SystemExit("analysis row has malformed measurement input")
        outcome, missing=classify(measurements); lineage=row.get("lineage")
        if not isinstance(lineage,dict): raise SystemExit("analysis row lineage malformed")
        msr_path=lineage.get("msr_path"); source_der_ids=lineage.get("source_der_ids")
        if not isinstance(msr_path,str) or not isinstance(source_der_ids,list) or not source_der_ids: raise SystemExit("analysis row lineage incomplete")
        der_paths=[]; srf_paths=[]; bor_paths=[]
        for der_id in source_der_ids:
            if der_id not in ders: raise SystemExit(f"analysis references unknown DER id: {der_id}")
            der, der_path=ders[der_id]; der_paths.append(rel(der_path))
            for srf_id in der.get("source_srf_ids",[]):
                if srf_id not in srfs: raise SystemExit(f"DER references unknown SRF id: {srf_id}")
                srf,srf_path=srfs[srf_id]; srf_paths.append(rel(srf_path))
                bor_ref=srf.get("bor_reference",{})
                if not isinstance(bor_ref,dict) or not isinstance(bor_ref.get("path"),str): raise SystemExit("SRF BOR provenance malformed")
                bor_paths.append(bor_ref["path"])
        item={"system_id":row["system_id"],"msr_id":row["msr_id"],"measurements":{m:measurements[m] for m in MEASUREMENTS},"classification":outcome,"missing_measurements":missing,"lineage":{"analysis_ref":rel(ANALYSIS_PATH)+f"#/system_measurement_matrix/{row['system_id']}","dataset_ref":analysis["input_dataset_ref"],"msr_path":msr_path,"source_der_ids":source_der_ids,"der_paths":sorted(set(der_paths)),"srf_paths":sorted(set(srf_paths)),"bor_paths":sorted(set(bor_paths)),"decision_rule_ref":rel(REGISTRATION_PATH)+"#/deterministic_decision_rule/I5"}}
        per.append(item); all_msr.append(msr_path); all_der+=der_paths; all_srf+=srf_paths; all_bor+=bor_paths
    outcomes=[i["classification"] for i in per]
    if "indeterminate" in outcomes: cohort="indeterminate"; basis=[i["system_id"] for i in per if i["classification"]=="indeterminate"]
    elif "violates" in outcomes: cohort="violates"; basis=[i["system_id"] for i in per if i["classification"]=="violates"]
    else: cohort="supports"; basis=[i["system_id"] for i in per]
    return {"object_type":"CanonicalRetainedClassification","schema_version":"canonical-retained-classification-v1","protocol_version":PROTOCOL_VERSION,"investigation_id":INVESTIGATION_ID,"id":"retained-classification-b2-governance-cohort-i5","classification_stage":"B2 Retained Classification","input_analysis_ref":rel(ANALYSIS_PATH),"input_dataset_ref":analysis["input_dataset_ref"],"decision_rule_ref":rel(REGISTRATION_PATH)+"#/deterministic_decision_rule/I5","cohort_size":analysis["cohort_size"],"row_ordering":analysis["row_ordering"],"measurement_fields":list(MEASUREMENTS),"per_system_classifications":per,"cohort_classification":{"outcome":cohort,"precedence":rule["precedence"],"basis":basis},"lineage":{"analysis_path":rel(ANALYSIS_PATH),"dataset_path":analysis["input_dataset_ref"],"registration_path":rel(REGISTRATION_PATH),"msr_paths":sorted(set(all_msr)),"der_paths":sorted(set(all_der)),"srf_paths":sorted(set(all_srf)),"bor_paths":sorted(set(all_bor))},"provenance":{"method":"CanonicalAnalysis -> frozen I5 deterministic retained classification","created_from":[rel(ANALYSIS_PATH),analysis["input_dataset_ref"],rel(REGISTRATION_PATH)]},"generation":{"builder":"scripts/build_retained_classification.py","mode":"deterministic-rebuild","repository_root":"."}}

def check_committed(expected:dict)->None:
    if not OUTPUT_PATH.exists(): raise SystemExit(f"missing canonical retained classification: {rel(OUTPUT_PATH)}")
    b=OUTPUT_PATH.read_bytes(); committed=json.loads(b)
    if not isinstance(committed,dict): raise SystemExit("committed retained classification must be a JSON object")
    validate_schema(committed, SCHEMA_PATH, rel(OUTPUT_PATH))
    if any(k in committed for k in ("cohort_conclusion","conclusion")): raise SystemExit("retained classification must not issue cohort conclusion fields")
    if committed != expected: raise SystemExit("committed retained classification structure differs from deterministic I5 rebuild")
    if b != stable_bytes(expected): raise SystemExit("committed retained classification bytes differ from deterministic rebuild")

def main()->None:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--check",action="store_true"); args=p.parse_args()
    data=build_retained_classification(); validate_schema(data, SCHEMA_PATH, "deterministic B2 retained classification")
    if args.check: check_committed(data); print(f"canonical retained classification fresh: {rel(OUTPUT_PATH)}"); return
    OUTPUT_PATH.parent.mkdir(parents=True,exist_ok=True); OUTPUT_PATH.write_bytes(stable_bytes(data)); print(f"wrote {rel(OUTPUT_PATH)}")
if __name__=="__main__": main()
