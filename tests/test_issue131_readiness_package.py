import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "investigations/agent-readable-contracts-131/validate.py"


def test_issue131_prospective_package_contract():
    result = subprocess.run([sys.executable, str(VALIDATOR)], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert "hypothesis not tested" in result.stdout
