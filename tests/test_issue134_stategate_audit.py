import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "investigations/stategate-internal-consumer-134/evidence.json"


def test_blocked_audit_preserves_bounded_claims():
    evidence = json.loads(AUDIT.read_text(encoding="utf-8"))

    assert evidence["classification"] == "SAME_OWNER_INTERNAL_CONSUMER_EVIDENCE"
    assert evidence["terminal_determination"] == "BLOCKED_BY_REPOSITORY_PERMISSIONS"
    assert evidence["stategate"]["integration_added"] is False
    assert evidence["stategate"]["canonical_proof_artifact"] == "NOT_PRODUCED"
    assert evidence["natural_workflow_observations"] == []
    assert evidence["controlled_semantics"]["counted_as_workflow_value"] is False
    assert evidence["routing"]["posted"] is False


def test_inspected_git_object_is_available():
    evidence = json.loads(AUDIT.read_text(encoding="utf-8"))
    git_dir = ROOT / ".git"

    assert git_dir.is_dir()
    commit = evidence["inspected_state"]["commit"]
    expected_tree = evidence["inspected_state"]["tree"]
    actual_tree = subprocess.run(
        ["git", "show", "-s", "--format=%T", commit],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    assert actual_tree == expected_tree
