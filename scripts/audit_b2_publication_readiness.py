#!/usr/bin/env python3
"""B2 publication-readiness audit bound to a verified repository commit.

This script is intentionally conservative: it inspects repository objects and
reports readiness blockers, but it does not create evidence, alter scientific
content, or reinterpret conclusions.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
REPORT_DEFAULT = ROOT / "reports" / "b2-publication-readiness.md"

REQUIRED_PRECONDITIONS = [
    "papers/paper-b2/main.tex",
    "investigations/b2-governance-cohort/",
    "datasets/canonical/",
    "datasets/comparative/",
    "datasets/exports/",
    "scripts/validate.py",
    "scripts/check_registry.py",
    "scripts/build_dataset.py",
    "scripts/build_report.py",
]

COMMANDS_EXECUTED = [
    "python3 scripts/validate.py",
    "python3 scripts/check_registry.py",
    "python3 scripts/build_dataset.py",
    "python3 scripts/build_report.py",
    "git diff --check",
]

PLACEHOLDER_PATTERNS = re.compile(
    r"\b(TBD|TODO|placeholder|to be completed|intentionally empty|no scientific data synthesis|source records exist)\b",
    re.IGNORECASE,
)
LABEL_PATTERN = re.compile(r"\\label\{([^}]+)\}")


@dataclass
class ObjectCheck:
    name: str
    paths: list[str]
    path_exists: bool = False
    placeholder_exists: bool = False
    research_object_exists: bool = False
    populated: bool = False
    frozen: bool = False
    traceable: bool = False
    classification: str = "MISSING"
    findings: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def object_files(relative_paths: Iterable[str]) -> list[Path]:
    files: list[Path] = []
    for relative in relative_paths:
        path = ROOT / relative
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(
                sorted(
                    p for p in path.rglob("*")
                    if p.is_file() and ".git" not in p.parts and p.name != ".gitkeep"
                )
            )
    return files


def substantive_files(files: Iterable[Path]) -> list[Path]:
    substantive: list[Path] = []
    for path in files:
        text = read_text(path).strip()
        if not text:
            continue
        if path.name == "README.md" and PLACEHOLDER_PATTERNS.search(text):
            continue
        if len(text) > 120 and not PLACEHOLDER_PATTERNS.search(text):
            substantive.append(path)
    return substantive


def has_placeholder(files: Iterable[Path]) -> bool:
    return any(PLACEHOLDER_PATTERNS.search(read_text(path)) for path in files)


def has_freeze_marker(files: Iterable[Path]) -> bool:
    pattern = re.compile(r"\b(frozen|freeze|locked|registration freeze|prospectively preregistered)\b", re.IGNORECASE)
    return any(pattern.search(read_text(path)) for path in files)


def has_trace_marker(files: Iterable[Path]) -> bool:
    pattern = re.compile(r"\b(protocol|registry|source|commit|sha|trace|provenance|I[1-5]|BOR|SRF|ESM|DER|MSR)\b")
    return any(pattern.search(read_text(path)) for path in files)


def classify(check: ObjectCheck) -> None:
    if not check.path_exists:
        check.classification = "MISSING"
        check.blockers.append("required path does not exist")
    elif check.research_object_exists and check.populated and check.traceable and not check.placeholder_exists:
        check.classification = "COMPLETE"
    elif check.research_object_exists or check.populated or check.placeholder_exists or check.frozen or check.traceable:
        check.classification = "PARTIAL"
    else:
        check.classification = "MISSING"
        check.blockers.append("path exists but no auditable research object was found")

    if check.placeholder_exists:
        check.blockers.append("placeholder text remains")
    if check.path_exists and not check.populated:
        check.blockers.append("object is not populated")
    if check.path_exists and not check.traceable:
        check.blockers.append("object is not traceable to protocol, registry, source, or provenance markers")


def inspect_object(name: str, paths: list[str], *, requires_frozen: bool = False) -> ObjectCheck:
    check = ObjectCheck(name=name, paths=paths)
    check.path_exists = all((ROOT / path).exists() for path in paths)
    files = object_files(paths)
    substantive = substantive_files(files)
    check.placeholder_exists = has_placeholder(files)
    check.research_object_exists = bool(files)
    check.populated = bool(substantive)
    check.frozen = has_freeze_marker(files)
    check.traceable = has_trace_marker(files)
    if requires_frozen and not check.frozen:
        check.blockers.append("required freeze marker was not found")
    classify(check)
    if requires_frozen and check.classification == "COMPLETE" and not check.frozen:
        check.classification = "PARTIAL"
    check.findings.extend([
        f"files inspected: {len(files)}",
        f"substantive files: {len(substantive)}",
    ])
    return check


def verify_preconditions() -> list[str]:
    missing: list[str] = []
    for relative in REQUIRED_PRECONDITIONS:
        path = ROOT / relative.rstrip("/")
        if relative.endswith("/"):
            if not path.is_dir():
                missing.append(relative)
        elif not path.is_file():
            missing.append(relative)
    return missing


def duplicate_latex_labels() -> dict[str, list[str]]:
    seen: dict[str, list[str]] = {}
    for path in sorted((ROOT / "papers" / "paper-b2").glob("*.tex")):
        for label in LABEL_PATTERN.findall(read_text(path)):
            seen.setdefault(label, []).append(rel(path))
    return {label: paths for label, paths in seen.items() if len(paths) > 1}


def command_output(command: list[str]) -> tuple[int, str]:
    proc = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return proc.returncode, proc.stdout.strip()


def determine(checks: list[ObjectCheck], precondition_failures: list[str], duplicate_labels: dict[str, list[str]]) -> str:
    if precondition_failures:
        return "NULL_NOT_AUDITED"
    if duplicate_labels:
        return "BLOCKED"
    if all(check.classification == "COMPLETE" for check in checks):
        return "READY"
    return "BLOCKED"


def render_report(repository: str, commit: str, output: Path, workflow_run: str, timestamp: str, checks: list[ObjectCheck], precondition_failures: list[str], duplicate_labels: dict[str, list[str]], final: str) -> str:
    branch = os.environ.get("GITHUB_REF_NAME", "main")
    lines = [
        "# B2 Publication-Readiness Audit",
        "",
        "## Audited Object",
        f"- Repository: `{repository}`",
        f"- Branch: `{branch}`",
        f"- Exact audited commit: `{commit}`",
        f"- Exact workflow run: `{workflow_run}`",
        f"- Audit timestamp: `{timestamp}`",
        "",
        "## Commands Executed Before Audit",
    ]
    lines.extend(f"- `{command}`" for command in COMMANDS_EXECUTED)
    lines.extend(["", "## Artifact Matrix", "", "| Artifact | Classification | Path exists | Placeholder exists | Research object exists | Populated | Frozen | Traceable |", "| --- | --- | --- | --- | --- | --- | --- | --- |"])
    for check in checks:
        lines.append(
            f"| {check.name} | {check.classification} | {check.path_exists} | {check.placeholder_exists} | "
            f"{check.research_object_exists} | {check.populated} | {check.frozen} | {check.traceable} |"
        )
    lines.extend(["", "## Verification Findings"])
    if precondition_failures:
        lines.append("- Precondition failure: required canonical paths are missing.")
        lines.extend(f"  - `{path}`" for path in precondition_failures)
    else:
        lines.append("- Canonical path preconditions passed.")
    if duplicate_labels:
        lines.append("- Duplicate LaTeX labels detected:")
        for label, paths in duplicate_labels.items():
            lines.append(f"  - `{label}` in {', '.join(f'`{path}`' for path in paths)}")
    else:
        lines.append("- Duplicate LaTeX label check passed.")
    for check in checks:
        lines.append(f"- {check.name}: {', '.join(check.findings)}")
    lines.extend(["", "## Exact Blockers"])
    blockers = [f"{check.name}: {blocker}" for check in checks for blocker in check.blockers]
    if precondition_failures:
        blockers.extend(f"Missing precondition: {path}" for path in precondition_failures)
    if duplicate_labels:
        blockers.extend(f"Duplicate LaTeX label: {label}" for label in duplicate_labels)
    lines.extend(f"- {blocker}" for blocker in blockers) if blockers else lines.append("- None.")
    lines.extend(["", "## Ordered Closure Sequence"])
    if final == "NULL_NOT_AUDITED":
        lines.extend(["1. Restore all canonical precondition paths on `main`.", "2. Re-run this workflow from GitHub Actions against `main`."])
    elif final == "BLOCKED":
        lines.extend(["1. Close precondition and duplicate-label blockers.", "2. Replace placeholder-only objects with populated, traceable research objects.", "3. Ensure registration freeze evidence is explicit.", "4. Re-run validators and this audit workflow."])
    else:
        lines.append("1. Preserve the audited commit and publish the report artifact with release materials.")
    lines.extend(["", "## Final Determination", "", final, ""])
    return "\n".join(lines)


def build_checks() -> list[ObjectCheck]:
    return [
        inspect_object("I1-I5 registration", ["papers/paper-b2/b2_05_protocol_registration.tex", "investigations/b2-governance-cohort/preregistration.md"]),
        inspect_object("registration freeze", ["papers/paper-b2/b2_11a_registration_freeze.tex"], requires_frozen=True),
        inspect_object("BOR", ["investigations/b2-governance-cohort/bor", "papers/paper-b2/b2_07_baseline_observation_records.tex"]),
        inspect_object("SRF / ESM", ["investigations/b2-governance-cohort/srf", "papers/paper-b2/b2_08_execution_surface_matrix.tex"]),
        inspect_object("DER", ["investigations/b2-governance-cohort/der", "papers/paper-b2/b2_09_derived_object_registry.tex"]),
        inspect_object("MSR", ["investigations/b2-governance-cohort/msr", "papers/paper-b2/b2_10_measurement_registry.tex"]),
        inspect_object("Comparative Dataset", ["datasets/comparative", "papers/paper-b2/b2_11_comparative_dataset.tex"]),
        inspect_object("Analysis", ["investigations/b2-governance-cohort/analysis", "papers/paper-b2/b2_12_analysis.tex"]),
        inspect_object("Retained Classification", ["registry/retained_classifications.json", "papers/paper-b2/b2_14_retained_classification.tex"]),
        inspect_object("Threats to Validity", ["papers/paper-b2/b2_13_threats_to_validity.tex"]),
        inspect_object("manuscript", ["papers/paper-b2/main.tex"]),
        inspect_object("publication artifacts", ["datasets/canonical", "datasets/exports", "releases"]),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit B2 publication readiness for a verified commit.")
    parser.add_argument("--repository", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--output", default=str(REPORT_DEFAULT))
    args = parser.parse_args()

    output = Path(args.output)
    if not output.is_absolute():
        output = ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    workflow_run = os.environ.get("GITHUB_RUN_ID", "LOCAL_UNVERIFIED")
    precondition_failures = verify_preconditions()
    checks = [] if precondition_failures else build_checks()
    duplicates = {} if precondition_failures else duplicate_latex_labels()
    final = determine(checks, precondition_failures, duplicates)
    report = render_report(args.repository, args.commit, output, workflow_run, timestamp, checks, precondition_failures, duplicates, final)
    output.write_text(report, encoding="utf-8")
    print(f"B2 audit report written to {rel(output)}")
    print(f"final determination: {final}")
    return 1 if final == "NULL_NOT_AUDITED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
