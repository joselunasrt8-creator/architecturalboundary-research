#!/usr/bin/env python3
"""Validate the research-first repository topology deterministically."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_TOP_LEVEL = [
    "analysis", "ci", "datasets", "docs", "evidence", "figures", "investigations",
    "papers", "protocol", "registry", "releases", "schemas", "scripts", "validation",
]
REQUIRED_PATHS = [
    "README.md", "ROADMAP.md", "LICENSE", "CONTRIBUTING.md", "CITATION.cff", "REPRODUCIBILITY.md", "MOVES.md",
    "ci/README.md", "ci/validate.yml",
    "docs/README.md", "docs/methodology.md", "docs/research_pipeline.md", "docs/glossary.md", "docs/figures/.gitkeep",
    "protocol/README.md", "protocol/changelog.md", "protocol/protocol-v1/README.md", "protocol/protocol-v1/protocol.md",
    "protocol/protocol-v1/terminology.md", "protocol/protocol-v1/decision_rules.md",
    "protocol/protocol-v1/schemas/README.md", "protocol/protocol-v1/templates/README.md",
    "papers/paper-0-protocol/README.md", "papers/paper-b1/README.md", "papers/paper-b2/main.tex",
    "datasets/README.md", "datasets/canonical/README.md", "datasets/comparative/README.md", "datasets/exports/README.md",
    "scripts/build_dataset.py", "scripts/build_report.py", "scripts/check_registry.py",
]
INVESTIGATIONS = ["investigations/template", "investigations/b1-three-system-pilot", "investigations/b2-governance-cohort"]
INVESTIGATION_ITEMS = [
    "README.md", "preregistration.md", "literature/README.md", "bor/README.md", "srf/README.md",
    "der/README.md", "msr/README.md", "dataset/README.md", "analysis/README.md", "results/README.md",
    "figures/README.md", "artifacts/README.md",
]
SCHEMAS = [
    "schemas/bor.schema.json", "schemas/srf.schema.json", "schemas/der.schema.json",
    "schemas/msr.schema.json", "schemas/dataset.schema.json", "schemas/investigation.schema.json",
]
REGISTRIES = [
    "registry/architectural_boundaries.json", "registry/investigations.json", "registry/terminology.json",
    "registry/classifications.json", "registry/protocol_versions.json", "registry/retained_classifications.json",
    "registry/candidate_invariants.json",
]
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
TEX_INPUT = re.compile(r"\\(?:input|include|bibliography)\{([^}]+)\}")


def require_path(relative: str) -> None:
    if not (ROOT / relative).exists():
        raise SystemExit(f"missing required path: {relative}")


def require_json(relative: str) -> object:
    require_path(relative)
    with (ROOT / relative).open(encoding="utf-8") as handle:
        data = json.load(handle)
    if relative.endswith(".schema.json") and "$schema" not in data:
        raise SystemExit(f"schema missing $schema key: {relative}")
    return data


def validate_yaml_syntax() -> None:
    yaml_files = [*ROOT.rglob("*.yml"), *ROOT.rglob("*.yaml"), *ROOT.rglob("*.cff")]
    try:
        import yaml  # type: ignore
    except Exception:
        # Deterministic fallback: reject tabs and obviously empty structural files.
        for path in yaml_files:
            text = path.read_text(encoding="utf-8")
            if "\t" in text:
                raise SystemExit(f"YAML-like file contains tab indentation: {path.relative_to(ROOT)}")
        return
    for path in yaml_files:
        with path.open(encoding="utf-8") as handle:
            yaml.safe_load(handle)


def validate_markdown_links() -> None:
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK.finditer(text):
            target = match.group(1).split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            if not (path.parent / target).resolve().exists():
                raise SystemExit(f"broken Markdown link in {path.relative_to(ROOT)}: {match.group(1)}")


def validate_latex_inputs() -> None:
    for path in ROOT.rglob("*.tex"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for raw in TEX_INPUT.findall(text):
            candidates = [path.parent / raw]
            if not Path(raw).suffix:
                candidates.extend([path.parent / f"{raw}.tex", path.parent / f"{raw}.bib"])
            if not any(candidate.exists() for candidate in candidates):
                raise SystemExit(f"broken LaTeX reference in {path.relative_to(ROOT)}: {raw}")


def validate_registered_paths() -> None:
    for relative in ["registry/investigations.json", "registry/protocol_versions.json"]:
        data = require_json(relative)
        key = "investigations" if "investigations" in data else "protocol_versions"
        for item in data[key]:
            registered = item.get("path")
            if not registered or not (ROOT / registered).exists():
                raise SystemExit(f"{relative} references missing path: {registered}")


def validate_move_ledger() -> None:
    require_path("MOVES.md")
    text = (ROOT / "MOVES.md").read_text(encoding="utf-8")
    required_destinations = ["papers/paper-b2/main.tex", "papers/paper-b2/references.bib"]
    for destination in required_destinations:
        if destination not in text:
            raise SystemExit(f"MOVES.md missing destination: {destination}")


def main() -> None:
    for relative in REQUIRED_TOP_LEVEL:
        if not (ROOT / relative).is_dir():
            raise SystemExit(f"missing required top-level directory: {relative}")
    for relative in REQUIRED_PATHS:
        require_path(relative)
    for base in INVESTIGATIONS:
        for item in INVESTIGATION_ITEMS:
            require_path(f"{base}/{item}")
    for relative in [*SCHEMAS, *REGISTRIES]:
        require_json(relative)
    validate_yaml_syntax()
    validate_registered_paths()
    validate_markdown_links()
    validate_latex_inputs()
    validate_move_ledger()
    subprocess.run(["python3", "scripts/check_registry.py"], cwd=ROOT, check=True)
    print("repository topology validation passed")


if __name__ == "__main__":
    main()
