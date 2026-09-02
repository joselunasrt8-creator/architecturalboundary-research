import copy
import hashlib
import importlib.util
import json
import pathlib
import random
import sys
import unittest

ROOT = pathlib.Path(__file__).parent
sys.path.insert(0, str(ROOT))

def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT/filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

power = load("issue110_power", "power-engine.py")
analysis = load("issue110_analysis", "production_analysis.py")

def fixture(effect=True, manipulation=True, n=48, repositories=8):
    records = []
    for index in range(n):
        for condition in ("LOW", "HIGH"):
            high = condition == "HIGH"
            baseline_accepted = (index // repositories) % 2 == 0
            accepted = (high or baseline_accepted) if effect else baseline_accepted
            records.append({
                "pair_id": f"SYNTHETIC_{index}", "condition": condition,
                "repository_id": f"R{index%repositories}", "task_class": f"T{index%3}",
                "difficulty": index%2, "accepted": accepted,
                "active_minutes": (60 if high else 120) if effect else 100,
                "time_to_valid_minutes": (40 if high else 100) if effect else 80,
                "time_to_valid_event": index%5 != 0, "eligible": True,
                "binding_stages": ["S06"] if high else ["S05"],
                "manipulation": {"runnable_candidate_count": 2 if (not high or manipulation) else 1,
                    "time_to_first_runnable_minutes": 40 if high and manipulation else 100,
                    "ai_configuration_frozen": manipulation or not high,
                    "ai_use_stage_ids": ["S05"] if manipulation or not high else ["S04", "S05"]},
            })
    return records

class Issue110Amendment001Tests(unittest.TestCase):
    def test_deterministic_repository_hierarchical_bootstrap(self):
        first = analysis.analyze(fixture())
        second = analysis.analyze(copy.deepcopy(fixture()))
        self.assertEqual(first, second)
        self.assertEqual(first["resampling_unit"], "repository_then_paired_template_hierarchical_cluster")
        self.assertEqual(first["bootstrap_replicates"], 10_000)
        self.assertEqual(first["null_assignments_enumerated"], 256)
        self.assertTrue(first["primary_endpoint_evidentiary_conjunction"])

    def test_null_randomization_not_ordinary_bootstrap(self):
        result = analysis.analyze(fixture(effect=False))
        self.assertEqual(result["null_test"], "exact enumeration of all repository-cluster sign flips under the sharp null")
        self.assertTrue(all(pvalue >= .99 for pvalue in result["holm"]["adjusted_p"]))

    def test_tied_event_and_censor_are_grouped(self):
        rows = [
            {"time_to_valid_minutes": 2, "time_to_valid_event": True},
            {"time_to_valid_minutes": 2, "time_to_valid_event": False},
            {"time_to_valid_minutes": 4, "time_to_valid_event": True},
        ]
        self.assertAlmostEqual(analysis.rmst(rows, tau=4), 10/3)

    def test_holm(self):
        self.assertEqual(analysis.holm([.01, .04, .2])["adjusted_p"], [.03, .08, .2])

    def test_malformed_fails_closed(self):
        records = fixture()
        del records[0]["accepted"]
        with self.assertRaises(ValueError):
            analysis.analyze(records)

    def test_manipulation_failure_is_indeterminate(self):
        self.assertEqual(analysis.manipulation_check(fixture(manipulation=False))["failure_consequence"],
                         "BOTTLENECK_MIGRATION_INDETERMINATE")

    def test_binding_and_precedence(self):
        self.assertTrue(analysis.binding_migration(["S05"], ["S06"])["migration"])
        self.assertEqual(analysis.determination(blocked=True, manipulation=False, migration=True),
                         "EXPERIMENT_BLOCKED")
        self.assertEqual(analysis.determination(manipulation=False, migration=True),
                         "BOTTLENECK_MIGRATION_INDETERMINATE")

    def test_power_model_uses_reviewed_structures(self):
        configuration = power.run.__globals__["REGIMES"][0]
        self.assertIn("difficulty_effect", configuration)
        self.assertIn("repository_interaction_sd", configuration)
        self.assertAlmostEqual(power._weighted_rmst([(2, True, 1), (2, False, 1), (4, True, 1)], 4), 10/3)

    def test_smallest_grid_repository_count_can_attain_holm_threshold(self):
        core = analysis.exact_repository_signflip
        capability = power.finite_signflip_capability
        self.assertFalse(capability(4)["eligible"])
        self.assertFalse(capability(6)["eligible"])
        self.assertTrue(capability(8)["eligible"])
        extreme = core([(1.0, 1.0, -1.0)] * 8)
        self.assertEqual(extreme["assignments_enumerated"], 256)
        self.assertTrue(all(extreme["holm"]["reject"]))

    def test_committed_power_run(self):
        result = json.loads((ROOT/"power-results.json").read_text())
        self.assertEqual(result["replicates_per_design_regime"], 10_000)
        self.assertEqual(result["total_replicates_executed"], 120_000)
        self.assertTrue(all("repository_interaction_wald_power" in row for row in result["results"]))
        self.assertTrue(all("production_aligned_primary_power_95_wilson" in row for row in result["results"]))
        self.assertEqual(result["engine_sha256"], hashlib.sha256((ROOT/"power-engine.py").read_bytes()).hexdigest())
        self.assertEqual(result["inference_core_sha256"], hashlib.sha256((ROOT/"inference_core.py").read_bytes()).hexdigest())

if __name__ == "__main__":
    unittest.main()
