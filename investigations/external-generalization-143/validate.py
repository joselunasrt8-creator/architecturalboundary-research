#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "investigations/external-generalization-143"
TARGET_TERMINALS = {
    "VALID_DETERMINATE_RESULT", "VALID_INDETERMINATE_RESULT", "PREEXECUTION_STOP",
    "BLOCKED_BY_AUTHORITATIVE_BINDING", "BLOCKED_BY_REQUIRED_MEASUREMENTS",
    "METHODOLOGY_FAILURE", "EXECUTION_INVALID",
}
COHORT_TERMINALS = {
    "EXTERNAL_GENERALIZATION_SUPPORTED_WITHIN_COHORT",
    "EXTERNAL_GENERALIZATION_PARTIALLY_SUPPORTED", "GENERALIZATION_NOT_DEMONSTRATED",
    "METHODOLOGY_DOES_NOT_TRANSFER", "COHORT_INDETERMINATE", "COHORT_INVALID",
}

def load(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)

def main():
    prereg = load(BASE / "preregistration.json")
    result = load(BASE / "result.json")
    assert prereg["object_type"] == "ProspectiveExternalCohortPreregistration"
    assert result["object_type"] == "ExternalGeneralizationCohortResult"
    assert len(result["preregistration"]["commit"]) == 40
    assert result["preregistration"]["hosted_commit_verified"] is False
    assert result["preregistration"]["hosted_separation_verified"] is False
    assert result["cohort_determination"] == "COHORT_INVALID"

    frozen = {target["id"]: target for target in prereg["cohort_selection"]["targets"]}
    assert 3 <= len(frozen) <= 5
    assert all(len(target["commit"]) == 40 for target in frozen.values())

    records = {path.stem: load(path) for path in sorted((BASE / "targets").glob("*.json"))}
    assert set(records) == set(frozen)
    for target_id, record in records.items():
        assert record["target_id"] == target_id
        assert record["repository_identity"]["commit"] == frozen[target_id]["commit"]
        assert record["terminal_determination"] in TARGET_TERMINALS
        assert len(record["source_manifest"]) == len(prereg["required_source_classes"])
        assert record["prospective_binding"]["preregistration_commit"] == result["preregistration"]["commit"]
        assert (ROOT / record["authoritative_binding"]["blocking_record"]).is_file()

    outcomes = {item["target_id"]: item["terminal"] for item in result["target_results"]}
    assert outcomes == {key: records[key]["terminal_determination"] for key in sorted(records)}
    assert result["cohort_determination"] in COHORT_TERMINALS
    assert all(item["evidence_status"] == "RETAINED_AUDIT_RECORD_NOT_VALID_COHORT_EVIDENCE"
               for item in result["target_results"])

    rerun = load(BASE / "reproducibility/nvm-sh-nvm-rerun.json")
    assert rerun["comparison"]["terminal_reproduced"] is True
    assert rerun["pinned_inputs"]["commit"] == frozen[rerun["target_id"]]["commit"]
    print("Issue #143 external cohort artifacts: valid invalidity record")

if __name__ == "__main__":
    main()
