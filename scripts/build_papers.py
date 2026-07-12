#!/usr/bin/env python3
"""Deterministically build all LaTeX papers under papers/."""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPERS_DIR = ROOT / "papers"
RELEASE_DIR = ROOT / "releases" / "papers"
BUILD_ROOT = ROOT / ".build" / "papers"
MAIN_TEX = "main.tex"
LATEX_WARNING_PATTERNS = {
    "undefined_citations": re.compile(r"LaTeX Warning: Citation `[^']+' on page .* undefined", re.MULTILINE),
    "undefined_references": re.compile(r"LaTeX Warning: Reference `[^']+' on page .* undefined", re.MULTILINE),
    "rerun_needed": re.compile(r"(Rerun to get cross-references right|There were undefined references|Label\(s\) may have changed)", re.MULTILINE),
    "duplicate_labels": re.compile(r"LaTeX Warning: Label `[^']+' multiply defined", re.MULTILINE),
}
BIBTEX_WARNING_PATTERNS = {
    "missing_references": re.compile(r"Warning--I didn't find a database entry for", re.MULTILINE),
    "undefined_citations": re.compile(r"I found no \\citation commands|I found no \\bibdata command", re.MULTILINE),
}


@dataclass(frozen=True)
class Paper:
    source_dir: Path

    @property
    def name(self) -> str:
        return self.source_dir.name

    @property
    def main_tex(self) -> Path:
        return self.source_dir / MAIN_TEX

    @property
    def relative_main(self) -> str:
        return str(self.main_tex.relative_to(ROOT))


@dataclass
class BuildResult:
    paper: Paper
    ok: bool
    pdf: Path | None = None
    warnings: dict[str, list[str]] = field(default_factory=dict)
    failure: str | None = None


def discover_papers() -> list[Paper]:
    """Discover buildable papers by sorted main.tex paths under papers/."""
    mains = sorted(path for path in PAPERS_DIR.rglob(MAIN_TEX) if path.is_file())
    return [Paper(path.parent) for path in mains]


def run_command(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def collect_pattern_warnings(text: str, patterns: dict[str, re.Pattern[str]]) -> dict[str, list[str]]:
    warnings: dict[str, list[str]] = {}
    for category, pattern in patterns.items():
        matches = sorted(set(match.group(0) for match in pattern.finditer(text)))
        if matches:
            warnings[category] = matches
    return warnings


def merge_warnings(left: dict[str, list[str]], right: dict[str, list[str]]) -> dict[str, list[str]]:
    merged = {key: list(value) for key, value in left.items()}
    for key, values in right.items():
        merged.setdefault(key, [])
        merged[key] = sorted(set([*merged[key], *values]))
    return merged


def bib_files_for(paper: Paper) -> list[Path]:
    return sorted(paper.source_dir.glob("*.bib"))


def build_paper(paper: Paper, *, keep_build: bool = False) -> BuildResult:
    output_dir = BUILD_ROOT / paper.name
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)

    warnings: dict[str, list[str]] = {}
    latex_cmd = [
        "pdflatex",
        "-halt-on-error",
        "-interaction=nonstopmode",
        f"-output-directory={output_dir}",
        paper.main_tex.name,
    ]

    first = run_command(latex_cmd, paper.source_dir)
    warnings = merge_warnings(warnings, collect_pattern_warnings(first.stdout, LATEX_WARNING_PATTERNS))
    if first.returncode != 0:
        return BuildResult(paper=paper, ok=False, warnings=warnings, failure=first.stdout)

    if bib_files_for(paper):
        bib = run_command(["bibtex", str(output_dir / "main")], paper.source_dir)
        warnings = merge_warnings(warnings, collect_pattern_warnings(bib.stdout, BIBTEX_WARNING_PATTERNS))
        if bib.returncode != 0:
            return BuildResult(paper=paper, ok=False, warnings=warnings, failure=bib.stdout)

    for _ in range(2):
        repeat = run_command(latex_cmd, paper.source_dir)
        warnings = merge_warnings(warnings, collect_pattern_warnings(repeat.stdout, LATEX_WARNING_PATTERNS))
        if repeat.returncode != 0:
            return BuildResult(paper=paper, ok=False, warnings=warnings, failure=repeat.stdout)

    pdf = output_dir / "main.pdf"
    if not pdf.exists():
        return BuildResult(paper=paper, ok=False, warnings=warnings, failure=f"expected PDF was not produced: {pdf}")

    release_pdf = RELEASE_DIR / f"{paper.name}.pdf"
    shutil.copy2(pdf, release_pdf)
    if not keep_build:
        shutil.rmtree(output_dir)
    return BuildResult(paper=paper, ok=True, pdf=release_pdf, warnings=warnings)


def print_result(result: BuildResult) -> None:
    status = "PASS" if result.ok else "FAIL"
    print(f"[{status}] {result.paper.name} ({result.paper.relative_main})")
    if result.pdf:
        print(f"  pdf: {result.pdf.relative_to(ROOT)}")
    if result.warnings:
        print("  warnings:")
        for category in sorted(result.warnings):
            print(f"    {category}: {len(result.warnings[category])}")
            for warning in result.warnings[category]:
                print(f"      - {warning}")
    if result.failure:
        print("  failure output:")
        print(result.failure.rstrip())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keep-build", action="store_true", help="retain intermediate LaTeX build files")
    args = parser.parse_args(argv)

    missing = [tool for tool in ("pdflatex", "bibtex") if shutil.which(tool) is None]
    if missing:
        print(f"missing required TeX tool(s): {', '.join(missing)}", file=sys.stderr)
        return 2

    papers = discover_papers()
    if not papers:
        print("no buildable papers discovered under papers/", file=sys.stderr)
        return 1

    results = [build_paper(paper, keep_build=args.keep_build) for paper in papers]
    for result in results:
        print_result(result)

    passed = sum(1 for result in results if result.ok)
    failed = len(results) - passed
    warning_count = sum(sum(len(items) for items in result.warnings.values()) for result in results)
    print(f"summary: {passed} passed, {failed} failed, {warning_count} warnings, {len(results)} discovered")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
