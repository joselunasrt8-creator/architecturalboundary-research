#!/usr/bin/env python3
"""Generate fixed-seed synthetic rehearsals and prospective design calculations."""
import json, math
from pathlib import Path
from analysis import analyze

ROOT=Path(__file__).parent
LABEL="SYNTHETIC_REHEARSAL_ONLY"
SCENARIOS=[
 ("strong_replicated_migration","BOTTLENECK_MIGRATION_SUPPORTED",{}),
 ("implementation_remains_dominant","BOTTLENECK_MIGRATION_NOT_SUPPORTED",{"remain":1}),
 ("proportional_acceleration","BOTTLENECK_MIGRATION_NOT_SUPPORTED",{"remain":1,"proportional":1}),
 ("precise_null_effect","BOTTLENECK_MIGRATION_NOT_SUPPORTED",{"remain":1,"null":1}),
 ("opposite_effect","BOTTLENECK_MIGRATION_NOT_SUPPORTED",{"remain":1,"opposite":1}),
 ("repository_specific_migration","BOTTLENECK_MIGRATION_DOMAIN_DEPENDENT",{"domain":"repository"}),
 ("task_class_specific_migration","BOTTLENECK_MIGRATION_DOMAIN_DEPENDENT",{"domain":"task_class"}),
 ("failed_high_manipulation","BOTTLENECK_MIGRATION_INDETERMINATE",{"manipulation":0}),
 ("harness_artifact","EXPERIMENT_BLOCKED",{"harness":0}),
 ("environment_artifact","EXPERIMENT_BLOCKED",{"environment":1}),
 ("insufficient_sample_information","BOTTLENECK_MIGRATION_INDETERMINATE",{"power":0}),
 ("stopping_censoring","BOTTLENECK_MIGRATION_INDETERMINATE",{"censor":1,"power":0}),
 ("heterogeneous_not_global","BOTTLENECK_MIGRATION_DOMAIN_DEPENDENT",{"domain":"opposite_intervals"})]

def evidence(stage,bound):
 return {"stage_id":stage,"entered_at":"SYNTHETIC_T00","exited_at":"SYNTHETIC_T01","active_minutes":10,"wait_minutes":0,"outcome":"PASS","binding_evidence":[{"type":"throughput","candidate_clause_met":bound,"binding_clause_met":bound,"effect":.2 if bound else 0,"ci_low":.05 if bound else -.05,"ci_high":.3 if bound else .05}]}
def dataset(name,opt):
 records=[]; n=32
 for i in range(n):
  repo=f"SYNTHETIC_REPO_{i%4}"; cls=f"SYNTHETIC_CLASS_{(i//4)%4}"
  migrate=not opt.get("remain")
  if opt.get("domain")=="repository": migrate=i%4<1
  if opt.get("domain")=="task_class": migrate=(i//4)%4<1
  if opt.get("domain")=="opposite_intervals": migrate=(i%4+(i//4)%4)%2==0
  for condition in ("LOW","HIGH"):
   accepted=(condition=="HIGH" and migrate and not opt.get("null") and not opt.get("opposite")) or (condition=="LOW" and opt.get("opposite"))
   impl=condition=="LOW" or opt.get("remain",False); replacement=condition=="HIGH" and migrate
   bad=i<8
   r={"record_id":f"SYNTHETIC::{name}::{i}::{condition}","pair_id":f"SYNTHETIC_PAIR_{i}","repository_id":repo,"task_template_id":f"SYNTHETIC_TASK_{i}","task_class":cls,"difficulty_band":"SYNTHETIC_MODERATE","condition":condition,"operator_blinded_id":"SYNTHETIC_OPERATOR","randomized_order":1 if condition=="LOW" else 2,"environment_id":"SYNTHETIC_ENV","ai_configuration_id":None if condition=="LOW" else "SYNTHETIC_AI","candidate_ids":[f"SYNTHETIC_CANDIDATE_{i}"],"stage_observations":[evidence("S05",impl),evidence("S06",replacement)],"active_minutes":80 if condition=="LOW" else 40,"wait_minutes":0,"attempts":1,"candidate_count":1 if condition=="LOW" else 2,"first_failure_stage":None if accepted else "S05","terminal_cause":"ACCEPTED" if accepted else "CAP","rework_events":[],"accepted_all_gates":bool(accepted),"environment_events":["SYNTHETIC_OUTAGE"] if opt.get("environment") and bad else [],"instrumentation_events":[],"harness_valid":not("harness" in opt and bad),"oracle_valid":True,"stopping_reason":"WALL_CAP" if opt.get("censor") else ("ACCEPTED" if accepted else "IMPLEMENTATION_CAP"),"adjudication":{"status":"SYNTHETIC_FINAL"},"manipulation":{"runnable_candidates":2 if opt.get("manipulation",1) else 1,"configuration_frozen":True},"classifiable":not(opt.get("censor") and bad)}
   records.append(r)
 return {"schema_version":"1.0","dataset_kind":LABEL,"synthetic_warning":"FICTIONAL NUMERIC DATA; NOT AN EMPIRICAL OBSERVATION","planned_pairs":n,"adequately_powered":bool(opt.get("power",1)),"administrative_stop":None,"interaction_signal":opt.get("domain","none"),"records":records}
def main():
 fixtures=[]; results=[]
 for name,expected,opt in SCENARIOS:
  d=dataset(name,opt); got=analyze(d); fixtures.append({"scenario":name,"expected":expected,"dataset":d}); results.append({"scenario":name,"expected":expected,"observed":got["final_determination"],"pass":got["final_determination"]==expected,"analysis":got})
 (ROOT/"synthetic-scenarios.json").write_text(json.dumps({"schema_version":"1.0","dataset_kind":LABEL,"warning":"ALL DATASETS ARE FICTIONAL; NO EMPIRICAL EXECUTION OCCURRED","scenarios":fixtures},indent=2,sort_keys=True)+"\n")
 (ROOT/"analysis-rehearsal-results.json").write_text(json.dumps({"schema_version":"1.0","synthetic_only":True,"all_pass":all(x["pass"] for x in results),"results":results},indent=2,sort_keys=True)+"\n")
if __name__=="__main__": main()
