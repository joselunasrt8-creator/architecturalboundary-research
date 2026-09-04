import subprocess
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "investigations/agent-readable-contracts-131/validate.py"


def test_issue131_prospective_package_contract():
    result = subprocess.run([sys.executable, str(VALIDATOR)], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert "hypothesis not tested" in result.stdout


def test_issue131_context_equivalence_and_oracle_integrity():
    result = subprocess.run([sys.executable, str(VALIDATOR)], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr

    package = ROOT / "investigations/agent-readable-contracts-131/amendment-v1"
    sources = [
        item["source"]
        for path in (package / "contexts/manifests").glob("*.json")
        for item in json.loads(path.read_text(encoding="utf-8"))["presentation_order"]
    ]
    assert not any(source.startswith("evaluator/") or "/evaluator/" in source for source in sources)
