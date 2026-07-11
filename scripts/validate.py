#!/usr/bin/env python3
"""Validate the research-first repository topology."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PATHS = [
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "CITATION.cff",
    "REPRODUCIBILITY.md",
    "protocol/protocol-v1/protocol.md",
    "protocol/changelog.md",
    "papers/b2/main.tex",
    "investigations/templates/README.md",
    "registry/investigations.json",
    "registry/protocol_versions.json",
]
TOP_LEVEL_READMES = [
    "protocol/README.md",
    "papers/README.md",
    "investigations/README.md",
    "datasets/README.md",
    "evidence/README.md",
    "analysis/README.md",
    "schemas/README.md",
    "registry/README.md",
    "figures/README.md",
    "scripts/README.md",
    "validation/README.md",
    "releases/README.md",
]
SCHEMAS = [
    "schemas/bor.schema.json",
    "schemas/srf.schema.json",
    "schemas/der.schema.json",
    "schemas/msr.schema.json",
    "schemas/dataset.schema.json",
    "schemas/investigation.schema.json",
]


def require_path(relative: str) -> None:
    path = ROOT / relative
    if not path.exists():
        raise SystemExit(f"missing required path: {relative}")


def require_json(relative: str) -> None:
    path = ROOT / relative
    require_path(relative)
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if relative.endswith(".schema.json") and "$schema" not in data:
        raise SystemExit(f"schema missing $schema key: {relative}")


def main() -> None:
    for relative in REQUIRED_PATHS + TOP_LEVEL_READMES + SCHEMAS:
        require_path(relative)
    for relative in [
        "registry/investigations.json",
        "registry/protocol_versions.json",
        "registry/retained_classifications.json",
        "registry/candidate_invariants.json",
        *SCHEMAS,
    ]:
        require_json(relative)
    print("repository topology validation passed")


if __name__ == "__main__":
    main()
