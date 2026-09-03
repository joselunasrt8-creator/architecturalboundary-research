import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]


class Issue127CalibrationTest(unittest.TestCase):
    def load(self, name):
        return json.loads((ROOT / name).read_text())

    def test_preregistration_precedes_evidence_commit_and_is_unchanged(self):
        freeze = "93e45f3"
        path = "investigations/bottleneck-migration-110-calibration-127/calibration-acquisition-protocol.json"
        frozen = subprocess.check_output(["git", "show", f"{freeze}:{path}"], cwd=REPO)
        self.assertEqual(frozen, (REPO / path).read_bytes())
        self.assertTrue(self.load("leakage-audit.json")["non_study_sources_only"])

    def test_historical_bindings_and_interfaces_have_not_drifted(self):
        bindings = self.load("artifact-bindings.json")
        for item in bindings["trees"]:
            actual = subprocess.check_output(
                ["git", "rev-parse", f'{item["merged_commit"]}:{item["path"]}'],
                cwd=REPO, text=True
            ).strip()
            self.assertEqual(item["git_tree"], actual)
        for item in bindings["interfaces"]:
            path = REPO / item["path"]
            blob = subprocess.check_output(["git", "hash-object", str(path)], cwd=REPO, text=True).strip()
            self.assertEqual(item["git_blob"], blob)
            self.assertEqual(item["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())

    def test_raw_evidence_hashes(self):
        registry = self.load("source-registry.json")
        for source in registry["sources"]:
            paths = source["preserved"] if isinstance(source["preserved"], list) else [source["preserved"]]
            hashes = source["sha256"] if isinstance(source["sha256"], list) else [source["sha256"]]
            for path, expected in zip(paths, hashes):
                self.assertEqual(expected, hashlib.sha256((ROOT / path).read_bytes()).hexdigest())

    def test_blocked_acquisitions_are_deterministic_utf8_json(self):
        raw = ROOT / "evidence" / "raw"
        self.assertFalse((raw / ".gitattributes").exists())
        self.assertEqual([], list(raw.glob("*.headers")))
        self.assertEqual([], list(raw.glob("*.status")))
        for path in sorted(raw.glob("*-acquisition.json")):
            payload = json.loads(path.read_bytes().decode("utf-8"))
            self.assertTrue(payload["requested_source"].startswith("https://"))
            self.assertEqual(56, payload["transport"]["exit_code"])
            self.assertEqual("000", payload["transport"]["effective_http_status"])
            self.assertEqual(403, payload["proxy_response"]["http_status"])
            self.assertEqual(142, payload["proxy_response"]["original_header_bytes"]["byte_length"])
            self.assertEqual(4, payload["proxy_response"]["original_status_capture_bytes"]["byte_length"])
            self.assertFalse(payload["source_content"]["acquired"])
            self.assertFalse(payload["source_content"]["usable"])
            self.assertEqual(0, payload["source_content"]["byte_length"])
            self.assertIsNone(payload["source_content"]["sha256"])

    def test_fail_closed_determination(self):
        nuisance = self.load("nuisance-bounds.json")
        self.assertEqual(8, len(nuisance["nuisance_quantities"]))
        self.assertTrue(all(row["bound"] is None for row in nuisance["nuisance_quantities"]))
        self.assertFalse(nuisance["synthetic_values_used"])
        decision = self.load("calibration-readiness.json")
        self.assertEqual("CALIBRATION_EVIDENCE_NOT_READY", decision["determination"])
        self.assertEqual("BOTTLENECK_EXPERIMENT_NOT_READY", decision["experiment_readiness"])
        self.assertFalse(decision["issue_110_outcomes_accessed"])
        self.assertFalse(decision["power_engine_run_for_final_n"])
        self.assertIsNone(decision["final_n"])
        self.assertEqual("NOT_JUSTIFIED", self.load("repository-independence-assessment.json")["assessment"])
        self.assertEqual("NOT_JUSTIFIED", self.load("joint-score-symmetry-assessment.json")["assessment"])
        self.assertEqual("ABSENT_BLOCKING", self.load("independent-adjudication.json")["status"])

    def test_descriptive_clopper_pearson_value_is_deterministic(self):
        expected_upper = 1 - (0.025 ** (1 / 2))
        interval = self.load("nuisance-bounds.json")["descriptive_nontransportable_calculations"][0]["interval"]
        self.assertAlmostEqual(expected_upper, interval[1], places=15)


if __name__ == "__main__":
    unittest.main()
