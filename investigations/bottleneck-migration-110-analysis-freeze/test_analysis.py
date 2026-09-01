import copy, json, unittest
from pathlib import Path
from analysis import analyze, validate
from simulate import SCENARIOS, dataset

class FreezeTests(unittest.TestCase):
 def test_scenarios(self):
  for name,expected,opt in SCENARIOS: self.assertEqual(analyze(dataset(name,opt))["final_determination"],expected,name)
 def test_incomplete_fails_closed(self):
  d=dataset("invalid",{}); del d["records"][0]["harness_valid"]
  with self.assertRaises(ValueError): validate(d)
 def test_unpaired_fails_closed(self):
  d=dataset("invalid",{}); d["records"].pop()
  with self.assertRaises(ValueError): validate(d)
 def test_deterministic(self):
  d=dataset("stable",{}); self.assertEqual(analyze(d),analyze(copy.deepcopy(d)))
 def test_committed_rehearsal(self):
  out=json.loads((Path(__file__).parent/"analysis-rehearsal-results.json").read_text()); self.assertTrue(out["all_pass"]); self.assertEqual(len(out["results"]),13)
 def test_power_ranges_are_not_claimed_as_simulation_output(self):
  root=Path(__file__).parent
  self.assertFalse((root/"power-simulation.json").exists())
  model=json.loads((root/"power-model-specification.json").read_text())
  self.assertEqual(model["execution_status"],"NOT_IMPLEMENTED_NOT_RUN")
  self.assertEqual(model["future_monte_carlo_requirement"]["output"],"NOT_CREATED")
  sizes=json.loads((root/"sample-size-analysis.json").read_text())
  self.assertTrue(all(x["range_status"]=="PLANNING_APPROXIMATION_NOT_MONTE_CARLO_OUTPUT" for x in sizes["candidate_designs"]))
if __name__=="__main__": unittest.main()
