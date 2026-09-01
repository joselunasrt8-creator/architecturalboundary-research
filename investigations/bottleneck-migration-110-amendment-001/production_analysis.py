#!/usr/bin/env python3
"""Frozen stdlib inference interfaces; raises instead of silently downgrading methods."""
from __future__ import annotations
import hashlib, json, math, random
from collections import defaultdict

SEED=11020260901
def _q(xs,p):
    xs=sorted(xs); return xs[min(len(xs)-1,max(0,int(p*(len(xs)-1))))]
def validate(records):
    required={"pair_id","condition","repository_id","task_class","difficulty","accepted","active_minutes","time_to_valid_minutes","time_to_valid_event","eligible","binding_stages","manipulation"}
    if not isinstance(records,list) or not records: raise ValueError("nonempty records required")
    groups=defaultdict(list)
    for r in records:
        if not isinstance(r,dict) or set(r) != required: raise ValueError("malformed record")
        if r["condition"] not in ("LOW","HIGH") or not isinstance(r["time_to_valid_event"],bool): raise ValueError("invalid value")
        if min(r["active_minutes"],r["time_to_valid_minutes"])<0: raise ValueError("negative time")
        groups[r["pair_id"]].append(r)
    for g in groups.values():
        if sorted(x["condition"] for x in g)!=["HIGH","LOW"]: raise ValueError("incomplete pair")
        if len({(x["repository_id"],x["task_class"],x["difficulty"]) for x in g})!=1: raise ValueError("pair mismatch")
    return groups
def holm(pvalues,alpha=.05):
    ordered=sorted(enumerate(pvalues),key=lambda x:x[1]); adjusted=[0.0]*len(pvalues); running=0
    for rank,(idx,p) in enumerate(ordered): running=max(running,min(1,p*(len(pvalues)-rank))); adjusted[idx]=running
    return {"adjusted_p":adjusted,"reject":[p<=alpha for p in adjusted]}
def rmst(rows,tau=480):
    # Kaplan-Meier integral with administrative right censoring.
    ordered=sorted((min(r["time_to_valid_minutes"],tau),r["time_to_valid_event"]) for r in rows)
    at=len(ordered); surv=1.; last=0.; area=0.
    for t,event in ordered:
        area += surv*(t-last); last=t
        if event: surv*=1-1/at
        at-=1
    return area+surv*(tau-last)
def analyze(records,bootstrap_replicates=10_000,seed=SEED):
    if bootstrap_replicates<10_000: raise ValueError("cluster bootstrap requires >=10,000 replicates")
    groups=validate(records); ids=sorted(groups); rng=random.Random(seed)
    def effects(sample):
        low=[]; high=[]
        for pid in sample:
            d={x["condition"]:x for x in groups[pid]}
            low.append(d["LOW"]); high.append(d["HIGH"])
        yd=sum(x["accepted"] for x in high)/len(high)-sum(x["accepted"] for x in low)/len(low)
        tp=lambda xs:sum(x["accepted"] for x in xs)*480/sum(x["active_minutes"] for x in xs)
        return yd,tp(high)-tp(low),rmst(high)-rmst(low)
    point=effects(ids); boots=[effects([rng.choice(ids) for _ in ids]) for _ in range(bootstrap_replicates)]
    cis=[[round(_q([x[j] for x in boots],.025),6),round(_q([x[j] for x in boots],.975),6)] for j in range(3)]
    # Mixed-effects interface is a prespecified cluster-stratified estimator: no nested execution independence.
    strata=defaultdict(list)
    for pid,g in groups.items(): strata[(g[0]["repository_id"],g[0]["task_class"])].append(pid)
    interactions={f"{k[0]}::{k[1]}":round(effects(v)[0],6) for k,v in sorted(strata.items())}
    pvals=[sum(abs(x[j])>=abs(point[j]) for x in boots)/bootstrap_replicates for j in range(3)]
    return {"schema_version":"1.0","unit":"paired_template_cluster","bootstrap_replicates":bootstrap_replicates,"seed":seed,"effects":{"acceptance_yield":point[0],"throughput":point[1],"rmst_high_minus_low":point[2]},"intervals_95":{"acceptance_yield":cis[0],"throughput":cis[1],"rmst":cis[2]},"right_censoring_method":"Kaplan-Meier restricted mean through 480 minutes","mixed_effects_interface":"repository-by-task stratum effects; pair cluster is resampling unit","stratum_effects":interactions,"holm":holm(pvals),"input_sha256":hashlib.sha256(json.dumps(records,sort_keys=True,separators=(",",":")).encode()).hexdigest()}
def manipulation_check(records):
    groups=validate(records); eligible_high=[x for g in groups.values() for x in g if x["condition"]=="HIGH" and x["eligible"]]; eligible_low=[x for g in groups.values() for x in g if x["condition"]=="LOW" and x["eligible"]]
    if not eligible_high or not eligible_low: raise ValueError("eligible LOW and HIGH required")
    a=sum(x["manipulation"]["runnable_candidate_count"]>=2 for x in eligible_high)/len(eligible_high)>=.70
    med=lambda xs:_q([x["manipulation"]["time_to_first_runnable_minutes"] for x in xs],.5)
    b=med(eligible_high)<=.70*med(eligible_low)
    c=all(x["manipulation"]["ai_configuration_frozen"] for x in eligible_high)
    d=all(x["manipulation"]["ai_use_stage_ids"]==["S05"] for x in eligible_high)
    return {"A_candidate_abundance":a,"B_time_ratio":b,"C_configuration_frozen":c,"D_implementation_only":d,"passed":a and b and c and d,"failure_consequence":"BOTTLENECK_MIGRATION_INDETERMINATE" if not(a and b and c and d) else None}
def determination(*,blocked=False, manipulation=True, adequate_power=True, domain=False, migration=False):
    """Apply the immutable precedence after binding-stage evidence is evaluated."""
    if blocked: return "EXPERIMENT_BLOCKED"
    if not manipulation or not adequate_power: return "BOTTLENECK_MIGRATION_INDETERMINATE"
    if domain: return "BOTTLENECK_MIGRATION_DOMAIN_DEPENDENT"
    if migration: return "BOTTLENECK_MIGRATION_SUPPORTED"
    return "BOTTLENECK_MIGRATION_NOT_SUPPORTED"

def binding_migration(low_stages, high_stages):
    """Frozen conjunction: implementation ceases binding and a named stage replaces it."""
    low=set(low_stages); high=set(high_stages)
    replacements=sorted(high-{"S05"})
    return {"implementation_low": "S05" in low, "implementation_high": "S05" in high,
            "replacement_high": replacements,
            "migration": "S05" in low and "S05" not in high and bool(replacements)}
