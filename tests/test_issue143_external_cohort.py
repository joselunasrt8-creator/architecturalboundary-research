import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "investigations/external-generalization-143"


def load(relative):
    return json.loads((BASE / relative).read_text(encoding="utf-8"))


def test_issue143_validator_passes():
    subprocess.run(
        [sys.executable, str(BASE / "validate.py")], cwd=ROOT, check=True,
        text=True, capture_output=True,
    )


def test_hosted_lineage_defect_is_preserved_as_invalidity():
    result = load("result.json")
    assert result["preregistration"]["hosted_commit_verified"] is False
    assert result["preregistration"]["hosted_separation_verified"] is False
    assert result["cohort_determination"] == "COHORT_INVALID"
    assert "prospective" in result["decision_rule_applied"].lower()


def test_recorded_targets_remain_bound_without_ephemeral_local_paths():
    prereg = load("preregistration.json")
    result = load("result.json")
    frozen = {item["id"]: item["commit"] for item in prereg["cohort_selection"]["targets"]}
    observed = {item["target_id"]: item["terminal"] for item in result["target_results"]}
    assert set(observed) == set(frozen)
    assert all(len(commit) == 40 for commit in frozen.values())
    assert set(observed.values()) == {"BLOCKED_BY_AUTHORITATIVE_BINDING"}
    assert all(
        item["evidence_status"] == "RETAINED_AUDIT_RECORD_NOT_VALID_COHORT_EVIDENCE"
        for item in result["target_results"]
    )
