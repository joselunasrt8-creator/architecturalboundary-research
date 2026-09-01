#!/usr/bin/env python3
"""Deterministic prospective analyzer for Issue #110 (synthetic or future data)."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

DETERMINATIONS = ["EXPERIMENT_BLOCKED", "BOTTLENECK_MIGRATION_INDETERMINATE",
                  "BOTTLENECK_MIGRATION_DOMAIN_DEPENDENT", "BOTTLENECK_MIGRATION_SUPPORTED",
                  "BOTTLENECK_MIGRATION_NOT_SUPPORTED"]
STAGES = {f"S{i:02d}" for i in range(1, 13)}

def fail(message):
    raise ValueError(message)

def validate(data):
    required = {"schema_version", "dataset_kind", "planned_pairs", "adequately_powered",
                "administrative_stop", "records"}
    if not isinstance(data, dict) or required - data.keys(): fail("missing study fields")
    if data["dataset_kind"] not in ("SYNTHETIC_REHEARSAL_ONLY", "FUTURE_EMPIRICAL_RESULTS"):
        fail("invalid dataset_kind")
    if not isinstance(data["planned_pairs"], int) or data["planned_pairs"] < 1: fail("invalid planned_pairs")
    if not isinstance(data["records"], list): fail("records must be an array")
    ids = set()
    needed = {"record_id", "pair_id", "repository_id", "task_template_id", "task_class",
              "difficulty_band", "condition", "operator_blinded_id", "randomized_order",
              "environment_id", "ai_configuration_id", "candidate_ids", "stage_observations",
              "active_minutes", "wait_minutes", "attempts", "candidate_count", "first_failure_stage",
              "terminal_cause", "rework_events", "accepted_all_gates", "environment_events",
              "instrumentation_events", "harness_valid", "oracle_valid", "stopping_reason",
              "adjudication", "manipulation", "classifiable"}
    for r in data["records"]:
        if not isinstance(r, dict) or needed-r.keys(): fail("incomplete record")
        if r["record_id"] in ids: fail("duplicate record_id")
        ids.add(r["record_id"])
        if r["condition"] not in ("LOW", "HIGH") or r["randomized_order"] not in (1,2): fail("bad assignment")
        if r["first_failure_stage"] is not None and r["first_failure_stage"] not in STAGES: fail("bad stage")
        if not isinstance(r["accepted_all_gates"], bool) or not isinstance(r["classifiable"], bool): fail("bad boolean")
        if min(r["active_minutes"], r["wait_minutes"], r["attempts"], r["candidate_count"]) < 0: fail("negative measure")
        for s in r["stage_observations"]:
            if set(s) != {"stage_id","entered_at","exited_at","active_minutes","wait_minutes","outcome","binding_evidence"}: fail("bad stage observation")
            if s["stage_id"] not in STAGES or s["outcome"] not in ("PASS","FAIL","NOT_REACHED","NOT_APPLICABLE"): fail("bad stage observation value")
            for b in s["binding_evidence"]:
                if set(b) != {"type","candidate_clause_met","binding_clause_met","effect","ci_low","ci_high"}: fail("bad binding evidence")
                if b["type"] not in ("failure","throughput","time","rework","coordination"): fail("bad binding type")
    grouped=defaultdict(list)
    for r in data["records"]: grouped[r["pair_id"]].append(r)
    for rows in grouped.values():
        if sorted(x["condition"] for x in rows) != ["HIGH","LOW"]: fail("each pair requires exactly LOW and HIGH")
        keys=("repository_id","task_template_id","task_class","difficulty_band","environment_id")
        if any(rows[0][k] != rows[1][k] for k in keys): fail("pair identity/control mismatch")
    return grouped

def wilson(successes, n):
    if not n: return [None,None]
    z=1.95996398454; p=successes/n; d=1+z*z/n
    c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [round(c-h,6),round(c+h,6)]

def analyze(data):
    pairs=validate(data); records=data["records"]
    valid_pairs=[v for v in pairs.values() if all(x["classifiable"] for x in v)]
    defect=sum(any((not x["harness_valid"] or not x["oracle_valid"] or x["environment_events"]) for x in p) for p in pairs.values())
    blocked=bool(data["administrative_stop"]) or defect/data["planned_pairs"]>.20 or len(valid_pairs)/data["planned_pairs"]<.75
    bycond={c:[r for r in records if r["condition"]==c and r["classifiable"]] for c in ("LOW","HIGH")}
    est={}
    for c,rs in bycond.items():
        accepted=sum(r["accepted_all_gates"] for r in rs); active=sum(r["active_minutes"] for r in rs)
        est[c]={"eligible":len(rs),"accepted":accepted,"acceptance_yield":round(accepted/len(rs),6) if rs else None,
                "yield_95_wilson":wilson(accepted,len(rs)),"throughput_per_8_active_hours":round(accepted*480/active,6) if active else None}
    if all(est[c]["acceptance_yield"] is not None for c in est):
        est["effects"]={"acceptance_yield_high_minus_low":round(est["HIGH"]["acceptance_yield"]-est["LOW"]["acceptance_yield"],6),
          "throughput_high_minus_low":round(est["HIGH"]["throughput_per_8_active_hours"]-est["LOW"]["throughput_per_8_active_hours"],6)}
    else: est["effects"]={}
    times=[]
    failures={c:Counter() for c in ("LOW","HIGH")}
    for p in valid_pairs:
        d={r["condition"]:r for r in p}; times.append(d["HIGH"]["active_minutes"]+d["HIGH"]["wait_minutes"]-d["LOW"]["active_minutes"]-d["LOW"]["wait_minutes"])
    for c,rs in bycond.items(): failures[c].update(r["first_failure_stage"] or "NONE" for r in rs)
    est["paired_time_to_valid_high_minus_low"]={"n":len(times),"mean_minutes":round(sum(times)/len(times),6) if times else None,"censoring":"stopping-cap records retained as right-censored; no imputation"}
    est["first_failure_stage"]={c:dict(sorted(v.items())) for c,v in failures.items()}
    def binds(r,stage="S05"):
        return any(s["stage_id"]==stage and any(b["type"] in ("failure","throughput") and b["candidate_clause_met"] and b["binding_clause_met"] and b["ci_low"]>0 for b in s["binding_evidence"]) for s in r["stage_observations"])
    migrations=[]
    for p in valid_pairs:
        d={r["condition"]:r for r in p}; replacement=[]
        for sid in sorted(STAGES-{"S05"}):
            if binds(d["HIGH"],sid) and not binds(d["LOW"],sid): replacement.append(sid)
        migrations.append({"pair_id":d["LOW"]["pair_id"],"repository":d["LOW"]["repository_id"],"task_class":d["LOW"]["task_class"],
          "implementation_low":binds(d["LOW"]),"implementation_high":binds(d["HIGH"]),"replacement_high":replacement,
          "migration":binds(d["LOW"]) and not binds(d["HIGH"]) and bool(replacement)})
    strata=defaultdict(list)
    for m in migrations: strata[(m["repository"],m["task_class"])].append(m["migration"])
    strata_out=[{"repository":k[0],"task_class":k[1],"n":len(v),"migration_rate":round(sum(v)/len(v),6),"passes":all(v)} for k,v in sorted(strata.items())]
    high=bycond["HIGH"]
    manipulation=bool(high) and sum(r["manipulation"]["runnable_candidates"]>=2 for r in high)/len(high)>=.70 and all(r["manipulation"]["configuration_frozen"] for r in high)
    valid_controls=all(r["harness_valid"] and r["oracle_valid"] and not r["environment_events"] and not r["instrumentation_events"] for r in records)
    passing=[x for x in strata_out if x["passes"]]; failing=[x for x in strata_out if not x["passes"]]
    repos={x["repository"] for x in passing}; classes={x["task_class"] for x in passing}
    support_base=len(repos)>=2 and len(classes)>=2 and est.get("effects",{}).get("acceptance_yield_high_minus_low",-1)>=.10
    domain=bool(passing and failing) and (data.get("interaction_signal") in ("repository","task_class","opposite_intervals"))
    support=support_base and not domain
    indeterminate=(not blocked) and (not manipulation or not valid_controls or not data["adequately_powered"] or not valid_pairs)
    determination=("EXPERIMENT_BLOCKED" if blocked else "BOTTLENECK_MIGRATION_INDETERMINATE" if indeterminate else
      "BOTTLENECK_MIGRATION_DOMAIN_DEPENDENT" if domain else "BOTTLENECK_MIGRATION_SUPPORTED" if support else "BOTTLENECK_MIGRATION_NOT_SUPPORTED")
    return {"schema_version":"1.0","input_sha256":hashlib.sha256(json.dumps(data,sort_keys=True,separators=(",",":")).encode()).hexdigest(),
      "estimands":est,"binding_stage_determinations":migrations,"stratum_results":strata_out,
      "interaction_results":{"signal":data.get("interaction_signal","none"),"domain_pattern":domain},
      "manipulation_valid":manipulation,"artifact_environment_harness_valid":valid_controls,
      "adequately_powered":data["adequately_powered"],"final_determination":determination}

def main():
    p=argparse.ArgumentParser(); p.add_argument("input"); p.add_argument("--output"); a=p.parse_args()
    out=analyze(json.loads(Path(a.input).read_text())); rendered=json.dumps(out,indent=2,sort_keys=True)+"\n"
    if a.output: Path(a.output).write_text(rendered)
    else: print(rendered,end="")
if __name__=="__main__": main()
