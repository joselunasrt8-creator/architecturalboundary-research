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


def test_active_manuscript_stale_state_language_blocks_readiness(tmp_path):
    repo = copy_repo(tmp_path)
    target = repo / "papers" / "paper-b2" / "b2_16_conclusion.tex"
    target.write_text(target.read_text(encoding="utf-8") + "\nTODO active stale lifecycle marker.\n", encoding="utf-8")
    result = run_audit(repo)
    text = report(repo)
    assert result.returncode == 0
    assert "Active stale publication-state language" in text
    assert "BLOCKED" in text


def test_archived_stale_language_does_not_block_readiness(tmp_path):
    repo = copy_repo(tmp_path)
    write_expected_pdfs(repo)
    archived = repo / "investigations" / "b2-governance-cohort" / "artifacts" / "archived-note.md"
    archived.parent.mkdir(parents=True, exist_ok=True)
    archived.write_text("TODO archived historical note only.\n", encoding="utf-8")
    result = run_audit(repo)
    text = report(repo)
    assert result.returncode == 0
    assert "final determination: READY" in result.stdout
    assert "Archived-only stale-language findings ignored" in text
    assert "Active stale publication-state language:" not in text


def write_expected_pdfs(repo: Path, *, empty: str | None = None, extra: bool = False, missing: str | None = None):
    release = repo / "releases" / "papers"
    release.mkdir(parents=True, exist_ok=True)
    for pdf in release.glob("*.pdf"):
        pdf.unlink()
    for name in ["paper-0-protocol.pdf", "paper-b2.pdf"]:
        if name == missing:
            continue
        (release / name).write_bytes(b"" if name == empty else b"%PDF-1.4\nnon-empty\n")
    if extra:
        (release / "unexpected.pdf").write_bytes(b"%PDF-1.4\nextra\n")


def test_ci_generated_audit_records_github_identity(tmp_path):
    repo = copy_repo(tmp_path)
    write_expected_pdfs(repo)
    env = os.environ.copy()
    env.update({
        "GITHUB_REPOSITORY": "owner/repo",
        "GITHUB_SHA": "deadbeef",
        "GITHUB_RUN_ID": "98765",
        "GITHUB_REF_NAME": "feature/pr-34",
        "GITHUB_SERVER_URL": "https://github.example.test",
    })
    result = subprocess.run(
        ["python3", "scripts/audit_b2_publication_readiness.py", "--output", "reports/b2-publication-readiness.md", "--verify-pdfs"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
    )
    text = report(repo)
    assert result.returncode == 0
    assert "Repository: `owner/repo`" in text
    assert "Branch: `feature/pr-34`" in text
    assert "Exact audited commit: `deadbeef`" in text
    assert "Exact workflow run: `98765`" in text
    assert "Exact workflow run URL: `https://github.example.test/owner/repo/actions/runs/98765`" in text
    assert "LOCAL_UNVERIFIED" not in text
    assert "READY" in text


def test_missing_expected_pdf_fails_final_ready(tmp_path):
    repo = copy_repo(tmp_path)
    write_expected_pdfs(repo, missing="paper-b2.pdf")
    result = subprocess.run(
        ["python3", "scripts/audit_b2_publication_readiness.py", "--repository", "owner/repo", "--commit", "abc", "--output", "reports/b2-publication-readiness.md", "--verify-pdfs"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "GITHUB_RUN_ID": "12345", "GITHUB_REF_NAME": "main"},
    )
    text = report(repo)
    assert result.returncode == 1
    assert "missing expected publication PDF: releases/papers/paper-b2.pdf" in text
    assert "SOURCE_READY" in text
    assert "\nREADY\n" not in text


def test_empty_expected_pdf_fails_final_ready(tmp_path):
    repo = copy_repo(tmp_path)
    write_expected_pdfs(repo, empty="paper-b2.pdf")
    result = subprocess.run(
        ["python3", "scripts/audit_b2_publication_readiness.py", "--repository", "owner/repo", "--commit", "abc", "--output", "reports/b2-publication-readiness.md", "--verify-pdfs"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "GITHUB_RUN_ID": "12345", "GITHUB_REF_NAME": "main"},
    )
    text = report(repo)
    assert result.returncode == 1
    assert "empty publication PDF: releases/papers/paper-b2.pdf" in text
    assert "SOURCE_READY" in text


def test_unexpected_pdf_fails_final_ready(tmp_path):
    repo = copy_repo(tmp_path)
    write_expected_pdfs(repo, extra=True)
    result = subprocess.run(
        ["python3", "scripts/audit_b2_publication_readiness.py", "--repository", "owner/repo", "--commit", "abc", "--output", "reports/b2-publication-readiness.md", "--verify-pdfs"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "GITHUB_RUN_ID": "12345", "GITHUB_REF_NAME": "main"},
    )
    text = report(repo)
    assert result.returncode == 1
    assert "unexpected publication PDF: releases/papers/unexpected.pdf" in text
    assert "SOURCE_READY" in text


def test_local_missing_pdfs_do_not_produce_false_ready(tmp_path):
    repo = copy_repo(tmp_path)
    result = run_audit(repo)
    text = report(repo)
    assert result.returncode == 0
    assert "SOURCE_READY" in text
    assert "missing expected publication PDF" in text
    assert "final determination: SOURCE_READY" in result.stdout


def test_successful_ci_rendering_permits_ready(tmp_path):
    repo = copy_repo(tmp_path)
    write_expected_pdfs(repo)
    result = subprocess.run(
        ["python3", "scripts/audit_b2_publication_readiness.py", "--repository", "owner/repo", "--commit", "abc", "--output", "reports/b2-publication-readiness.md", "--verify-pdfs"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "GITHUB_RUN_ID": "12345", "GITHUB_REF_NAME": "main"},
    )
    text = report(repo)
    assert result.returncode == 0
    assert "verified non-empty publication PDF: `releases/papers/paper-0-protocol.pdf`" in text
    assert "verified non-empty publication PDF: `releases/papers/paper-b2.pdf`" in text
    assert "final determination: READY" in result.stdout


def test_committed_documentation_has_no_stale_local_identity():
    text = (ROOT / "docs" / "publication_readiness_audit.md").read_text(encoding="utf-8")
    assert "Branch: `work`" not in text
    assert "27d6e82" not in text
    assert "Audit timestamp:" not in text
    assert "Exact workflow run: `LOCAL_UNVERIFIED`" not in text
    assert "b2-publication-readiness-audit" in text
    assert "reports/b2-publication-readiness.md" in text


def test_validate_workflow_runs_audit_after_pdf_build_and_verification():
    text = (ROOT / ".github" / "workflows" / "validate.yml").read_text(encoding="utf-8")
    build = text.index("name: Build publication PDFs")
    verify = text.index("name: Verify publication PDF artifacts")
    audit_step = text.index("name: Run CI-bound B2 publication-readiness audit")
    upload_pdf = text.index("name: Upload publication PDFs")
    assert build < verify < audit_step < upload_pdf
    pre_audit = text[:audit_step]
    assert "python3 scripts/build_papers.py" in pre_audit
    assert "find releases/papers" in pre_audit


def test_audit_command_list_contains_only_pre_audit_commands():
    assert "python3 scripts/build_papers.py" in audit.COMMANDS_EXECUTED_BEFORE_AUDIT
    assert "git diff --check" not in audit.COMMANDS_EXECUTED_BEFORE_AUDIT
    assert "python3 scripts/audit_b2_publication_readiness.py --verify-pdfs" not in audit.COMMANDS_EXECUTED_BEFORE_AUDIT
    assert audit.COMMANDS_EXECUTED_BEFORE_AUDIT.index("python3 scripts/build_papers.py") < audit.COMMANDS_EXECUTED_BEFORE_AUDIT.index("Verify publication PDF artifacts (exact expected set and non-empty files)")
