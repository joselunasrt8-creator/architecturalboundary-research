import copy, importlib.util, json, pathlib, unittest
ROOT=pathlib.Path(__file__).parent
def load(name,file):
 s=importlib.util.spec_from_file_location(name,ROOT/file); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
power=load("power","power-engine.py"); analysis=load("analysis","production_analysis.py")
def fixture(effect=True,manip=True,n=24):
 out=[]
 for i in range(n):
  for c in ("LOW","HIGH"):
   high=c=="HIGH"; accepted=high if effect else i%2==0
   out.append({"pair_id":f"SYNTHETIC_{i}","condition":c,"repository_id":f"R{i%4}","task_class":f"T{i%3}","difficulty":i%2,"accepted":accepted,"active_minutes":60 if high else 120,"time_to_valid_minutes":40 if high else 100,"time_to_valid_event":i%5!=0,"eligible":True,"binding_stages":["S06"] if high else ["S05"],"manipulation":{"runnable_candidate_count":2 if (not high or manip) else 1,"time_to_first_runnable_minutes":40 if high and manip else 100,"ai_configuration_frozen":manip or not high,"ai_use_stage_ids":["S05"] if manip or not high else ["S04","S05"]}})
 return out
class Tests(unittest.TestCase):
 def test_replay_and_cluster_bootstrap(self):
  a=analysis.analyze(fixture()); b=analysis.analyze(copy.deepcopy(fixture())); self.assertEqual(a,b); self.assertEqual(a["bootstrap_replicates"],10000); self.assertEqual(a["unit"],"paired_template_cluster")
 def test_censoring_and_holm(self): self.assertIn("Kaplan-Meier",analysis.analyze(fixture())["right_censoring_method"]); self.assertEqual(len(analysis.holm([.01,.04,.2])["adjusted_p"]),3)
 def test_malformed_fails_closed(self):
  x=fixture(); del x[0]["accepted"]
  with self.assertRaises(ValueError): analysis.analyze(x)
 def test_manipulation_failure_indeterminate(self): self.assertEqual(analysis.manipulation_check(fixture(manip=False))["failure_consequence"],"BOTTLENECK_MIGRATION_INDETERMINATE")
 def test_binding_and_precedence(self):
  self.assertTrue(analysis.binding_migration(["S05"],["S06"])["migration"])
  self.assertEqual(analysis.determination(blocked=True,manipulation=False,migration=True),"EXPERIMENT_BLOCKED")
  self.assertEqual(analysis.determination(manipulation=False,migration=True),"BOTTLENECK_MIGRATION_INDETERMINATE")
 def test_committed_power_run(self):
  x=json.loads((ROOT/"power-results.json").read_text()); self.assertEqual(x["replicates_per_design_regime"],10000); self.assertEqual(x["total_replicates_executed"],120000); self.assertEqual(x["engine_sha256"],__import__("hashlib").sha256((ROOT/"power-engine.py").read_bytes()).hexdigest())
if __name__=="__main__": unittest.main()
