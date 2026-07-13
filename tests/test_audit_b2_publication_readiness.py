import importlib.util
import os
import shutil
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_b2_publication_readiness.py"

spec = importlib.util.spec_from_file_location("audit", SCRIPT)
audit = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = audit
spec.loader.exec_module(audit)


def copy_repo(tmp_path: Path) -> Path:
    target = tmp_path / "repo"
    ignore = shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__", "reports")
    shutil.copytree(ROOT, target, ignore=ignore)
    return target


def run_audit(repo: Path):
    env = os.environ.copy()
    env["GITHUB_RUN_ID"] = "12345"
    env["GITHUB_REF_NAME"] = "main"
    return subprocess.run(
        ["python3", "scripts/audit_b2_publication_readiness.py", "--repository", "owner/repo", "--commit", "abc123", "--output", "reports/b2-publication-readiness.md"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
    )


def report(repo: Path) -> str:
    return (repo / "reports" / "b2-publication-readiness.md").read_text(encoding="utf-8")


def test_verified_valid_repository_state_is_audited(tmp_path):
    repo = copy_repo(tmp_path)
    result = run_audit(repo)
    text = report(repo)
    assert result.returncode == 0
    assert "Exact audited commit: `abc123`" in text
    assert "Exact workflow run: `12345`" in text
    assert "NULL_NOT_AUDITED" not in text
    assert "| manuscript |" in text
    assert "| BOR | COMPLETE |" in text
    assert "| SRF | COMPLETE |" in text
    assert "| DER | COMPLETE |" in text
    assert "| Canonical MSR | COMPLETE |" in text
    assert "| Comparative Dataset | COMPLETE |" in text
    assert "| Analysis | COMPLETE |" in text
    assert "| Retained Classification | COMPLETE |" in text
    assert "| Cohort Conclusion | COMPLETE |" in text
    assert "missing id" not in text


def test_missing_canonical_path_returns_null_not_audited(tmp_path):
    repo = copy_repo(tmp_path)
    (repo / "papers" / "paper-b2" / "main.tex").unlink()
    result = run_audit(repo)
    text = report(repo)
    assert result.returncode == 1
    assert "NULL_NOT_AUDITED" in text
    assert "Missing precondition: papers/paper-b2/main.tex" in text


def test_missing_validator_returns_null_not_audited(tmp_path):
    repo = copy_repo(tmp_path)
    (repo / "scripts" / "validate.py").unlink()
    result = run_audit(repo)
    text = report(repo)
    assert result.returncode == 1
    assert "NULL_NOT_AUDITED" in text
    assert "Missing precondition: scripts/validate.py" in text


def test_stale_or_absent_evidence_objects_are_blocked(tmp_path):
    repo = copy_repo(tmp_path)
    shutil.rmtree(repo / "investigations" / "b2-governance-cohort" / "bor")
    (repo / "investigations" / "b2-governance-cohort" / "bor").mkdir()
    result = run_audit(repo)
    text = report(repo)
    assert result.returncode == 0
    assert "| BOR | MISSING |" in text
    assert "BOR: object is not populated" in text
    assert "BLOCKED" in text


def test_missing_srf_objects_are_blocked(tmp_path):
    repo = copy_repo(tmp_path)
    shutil.rmtree(repo / "investigations" / "b2-governance-cohort" / "srf")
    (repo / "investigations" / "b2-governance-cohort" / "srf").mkdir()
    result = run_audit(repo)
    text = report(repo)
    assert result.returncode == 0
    assert "| SRF | MISSING |" in text
    assert "SRF: object is not populated" in text
    assert "BLOCKED" in text


def test_missing_der_objects_are_blocked(tmp_path):
    repo = copy_repo(tmp_path)
    shutil.rmtree(repo / "investigations" / "b2-governance-cohort" / "der")
    (repo / "investigations" / "b2-governance-cohort" / "der").mkdir()
    result = run_audit(repo)
    text = report(repo)
    assert result.returncode == 0
    assert "| DER | MISSING |" in text
    assert "DER: object is not populated" in text
    assert "BLOCKED" in text


def test_broken_der_lineage_is_blocked(tmp_path):
    repo = copy_repo(tmp_path)
    target = repo / "investigations" / "b2-governance-cohort" / "der" / "openfga.der.json"
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace("srf-b2-openfga", "srf-b2-missing"), encoding="utf-8")
    result = run_audit(repo)
    text = report(repo)
    assert result.returncode == 0
    assert "| DER | PARTIAL |" in text
    assert "DER: broken SRF lineage" in text
    assert "BLOCKED" in text


def test_placeholder_only_object_is_partial_and_blocked(tmp_path):
    repo = copy_repo(tmp_path)
    target = repo / "investigations" / "b2-governance-cohort" / "analysis" / "b2-governance-cohort-i4.analysis.json"
    target.unlink()
    (repo / "investigations" / "b2-governance-cohort" / "analysis" / "README.md").write_text("# Analysis\n\nTODO placeholder.\n", encoding="utf-8")
    result = run_audit(repo)
    text = report(repo)
    assert result.returncode == 0
    assert "| Analysis | MISSING |" in text
    assert "Analysis: object is not populated" in text


def test_duplicate_latex_labels_block_readiness(tmp_path):
    repo = copy_repo(tmp_path)
    (repo / "papers" / "paper-b2" / "b2_01_abstract.tex").write_text("\\label{dup}\n", encoding="utf-8")
    (repo / "papers" / "paper-b2" / "b2_02_introduction.tex").write_text("\\label{dup}\n", encoding="utf-8")
    result = run_audit(repo)
    text = report(repo)
    assert result.returncode == 0
    assert "Duplicate LaTeX label: dup" in text
    assert "BLOCKED" in text


def test_null_not_audited_behavior_skips_scientific_determination(tmp_path):
    repo = copy_repo(tmp_path)
    shutil.rmtree(repo / "datasets" / "canonical")
    result = run_audit(repo)
    text = report(repo)
    assert result.returncode == 1
    assert "NULL_NOT_AUDITED" in text
    assert "## Artifact Matrix\n\n| Artifact |" in text
    assert "READY" not in text
