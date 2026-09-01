#!/usr/bin/env python3
"""Deterministic prospective clustered Monte Carlo power engine for Amendment 001."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEED = 11020260901
REPLICATES = 10_000
DESIGNS = ((64, 4), (128, 4), (288, 6), (512, 8))  # pairs, repositories
REGIMES = (
    {"name": "favorable", "baseline": .40, "yield_effect": .20, "pair_correlation": .60, "repository_sd": .05, "task_sd": .10, "timing_cv": .35, "attrition": .05, "censoring": .05, "environment_failure": .02},
    {"name": "moderate", "baseline": .40, "yield_effect": .15, "pair_correlation": .35, "repository_sd": .10, "task_sd": .20, "timing_cv": .55, "attrition": .10, "censoring": .15, "environment_failure": .05},
    {"name": "conservative", "baseline": .40, "yield_effect": .10, "pair_correlation": .10, "repository_sd": .15, "task_sd": .30, "timing_cv": .80, "attrition": .25, "censoring": .25, "environment_failure": .10},
)

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()

def clamp(x):
    return max(.01, min(.99, x))

def simulate_cell(pairs, repositories, regime, rng, replicates):
    successes = interaction_hits = retained_sum = 0
    tasks = 4
    for _ in range(replicates):
        repo_shift = [rng.gauss(0, regime["repository_sd"]) for _ in range(repositories)]
        task_shift = [rng.gauss(0, regime["task_sd"]) for _ in range(tasks)]
        retention=(1-regime["attrition"])*(1-regime["environment_failure"])
        n=max(0,round(rng.gauss(pairs*retention,math.sqrt(pairs*retention*(1-retention)))))
        retained_sum += n
        if n < max(12, repositories*2):
            continue
        # Gaussian aggregate draws are a prospective Monte Carlo model, not empirical estimates.
        heterogeneity=math.sqrt(sum(x*x for x in repo_shift)/repositories+sum(x*x for x in task_shift)/tasks)
        pair_var=2*regime["baseline"]*(1-regime["baseline"])*(1-regime["pair_correlation"])
        se=math.sqrt(pair_var/n + heterogeneity*heterogeneity/max(repositories*tasks,1))
        mean=rng.gauss(regime["yield_effect"],se)
        yield_hit=mean-1.644854*se >= .10
        timing_se=240*regime["timing_cv"]/math.sqrt(n)
        time_gain=rng.gauss(72*(1-regime["censoring"]),timing_se)
        throughput_hit=mean >= .10 and rng.gauss(.20,.08+regime["timing_cv"]/math.sqrt(n)) >= .15
        time_hit=time_gain-1.644854*timing_se >= 36
        migration_hit=rng.gauss(.35,.15/math.sqrt(n)+heterogeneity/4) >= .20
        if yield_hit and throughput_hit and time_hit and migration_hit: successes += 1
        repo_effects=[rng.gauss(regime["yield_effect"]+x,se*math.sqrt(repositories)) for x in repo_shift]
        if max(repo_effects)-min(repo_effects) >= .10: interaction_hits += 1
    return {"primary_conjunctive_power": round(successes/replicates, 6), "repository_interaction_detection_rate": round(interaction_hits/replicates, 6), "mean_retained_pairs": round(retained_sum/replicates, 3)}

def run(replicates=REPLICATES, seed=SEED):
    if replicates < 10_000: raise ValueError("production run requires at least 10,000 replicates per design/regime")
    config={"seed":seed,"replicates_per_design_regime":replicates,"designs":[{"pairs":p,"executions":2*p,"repositories":r,"task_classes":4,"difficulty_bands":2} for p,r in DESIGNS],"regimes":REGIMES,
            "model_features":["paired LOW/HIGH","repository clusters","task class","difficulty","within-pair correlation","repository and task variation","attrition","right censoring","acceptance yield","throughput","time to valid","conjunctive migration"]}
    rng=random.Random(seed); rows=[]
    for pairs,repos in DESIGNS:
        for regime in REGIMES:
            rows.append({"pairs":pairs,"executions":pairs*2,"repositories":repos,"regime":regime["name"],"replicates_executed":replicates,**simulate_cell(pairs,repos,regime,rng,replicates)})
    engine_sha=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(); config_sha=hashlib.sha256(canonical(config)).hexdigest()
    return {"schema_version":"1.0","artifact_role":"PROSPECTIVE_ASSUMPTION_SENSITIVITY_NOT_EMPIRICAL_DATA","seed":seed,"replicates_per_design_regime":replicates,"total_replicates_executed":replicates*len(rows),"engine_sha256":engine_sha,"configuration_sha256":config_sha,"configuration":config,"results":rows,"final_n":"FINAL_N_NOT_YET_FREEZABLE","reason":"Regime nuisance values are synthetic assumptions; no permissible outcome-blind calibration bounds have been frozen."}

def main():
    p=argparse.ArgumentParser(); p.add_argument("--output",default=str(ROOT/"power-results.json")); p.add_argument("--replicates",type=int,default=REPLICATES); a=p.parse_args()
    Path(a.output).write_text(json.dumps(run(a.replicates),indent=2,sort_keys=True)+"\n")
if __name__ == "__main__": main()
