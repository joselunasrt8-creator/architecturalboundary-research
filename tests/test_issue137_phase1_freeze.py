import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_issue137_phase1_freeze_vocabulary_and_guards():
    result = subprocess.run(
        [sys.executable, "investigations/ecosystem-inspection-137/validate.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "shape/vocabulary only; no outcomes tested" in result.stdout
