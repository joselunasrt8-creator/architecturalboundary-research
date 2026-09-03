import hashlib
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]


class CalibrationReadinessTest(unittest.TestCase):
    def test_historical_bindings_have_not_drifted(self):
        bindings = json.loads((ROOT / "artifact-bindings.json").read_text())
        for item in bindings["trees"]:
            actual = subprocess.check_output(
                ["git", "rev-parse", f'{item["merged_commit"]}:{item["path"]}'],
                cwd=REPO, text=True
            ).strip()
            self.assertEqual(actual, item["git_tree"])
        for item in bindings["interfaces"]:
            path = REPO / item["path"]
            blob = subprocess.check_output(
                ["git", "hash-object", str(path)], cwd=REPO, text=True
            ).strip()
            self.assertEqual(blob, item["git_blob"])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), item["sha256"])

    def test_fail_closed_decision_has_no_fabricated_bounds(self):
        record = json.loads((ROOT / "calibration-readiness.json").read_text())
        self.assertEqual(record["determination"], "FINAL_N_NOT_YET_FREEZABLE")
        self.assertEqual(record["experiment_readiness"], "BOTTLENECK_EXPERIMENT_NOT_READY")
        self.assertFalse(record["issue_110_outcomes_accessed"])
        self.assertIsNone(record["nuisance_result"]["bounds"])
        self.assertEqual(record["nuisance_result"]["eligible_source_records_found"], 0)
        self.assertTrue(all(
            row["status"] == "UNJUSTIFIED"
            for row in record["inferential_boundary"]["required_assumptions"]
        ))
        self.assertEqual(record["power_execution"]["status"], "NOT_RUN_GATE_FAILED")
        self.assertIsNone(record["power_execution"]["candidate_selected"])


if __name__ == "__main__":
    unittest.main()
