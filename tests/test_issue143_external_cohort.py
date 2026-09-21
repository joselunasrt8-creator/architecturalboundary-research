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


def test_preregistration_precedes_and_excludes_outcomes():
    result = load("result.json")
    commit = result["preregistration"]["commit"]
    paths = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", commit], cwd=ROOT, check=True,
        text=True, capture_output=True,
    ).stdout.splitlines()
    prefix = "investigations/external-generalization-143/"
    assert prefix + "preregistration.json" in paths
    assert prefix + "result.json" not in paths
    assert not any(path.startswith(prefix + "targets/") for path in paths)


def test_frozen_target_objects_reproduce_locally():
    prereg = load("preregistration.json")
    for target in prereg["cohort_selection"]["targets"]:
        root = Path(target["local_source_root_at_freeze"])
        observed = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, check=True,
            text=True, capture_output=True,
        ).stdout.strip()
        assert observed == target["commit"]
        kind = subprocess.run(
            ["git", "cat-file", "-t", target["commit"]], cwd=root, check=True,
            text=True, capture_output=True,
        ).stdout.strip()
        assert kind == "commit"
