#!/usr/bin/env python3
"""Deterministically validate registry contracts and registered paths."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry"
REQUIRED = {
    "architectural_boundaries.json": "architectural_boundaries",
    "investigations.json": "investigations",
    "terminology.json": "terminology",
    "classifications.json": "classifications",
    "protocol_versions.json": "protocol_versions",
    "retained_classifications.json": "retained_classifications",
    "candidate_invariants.json": "candidate_invariants",
}


def load_json(path: Path) -> object:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def require_path(relative: str, source: str) -> None:
    if not (ROOT / relative).exists():
        raise SystemExit(f"{source} references missing path: {relative}")


def main() -> None:
    loaded: dict[str, object] = {}
    for filename, key in REQUIRED.items():
        path = REGISTRY / filename
        if not path.exists():
            raise SystemExit(f"missing registry contract: registry/{filename}")
        data = load_json(path)
        if not isinstance(data, dict) or key not in data:
            raise SystemExit(f"registry/{filename} missing top-level key: {key}")
        loaded[filename] = data

    investigations = loaded["investigations.json"]["investigations"]  # type: ignore[index]
    if not isinstance(investigations, list):
        raise SystemExit("registry/investigations.json investigations must be a list")
    for item in investigations:
        if not isinstance(item, dict):
            raise SystemExit("investigation registry entries must be objects")
        require_path(str(item.get("path", "")), "registry/investigations.json")

    versions = loaded["protocol_versions.json"]["protocol_versions"]  # type: ignore[index]
    if not isinstance(versions, list):
        raise SystemExit("registry/protocol_versions.json protocol_versions must be a list")
    for item in versions:
        if not isinstance(item, dict):
            raise SystemExit("protocol registry entries must be objects")
        require_path(str(item.get("path", "")), "registry/protocol_versions.json")

    terminology = loaded["terminology.json"]
    if isinstance(terminology, dict) and terminology.get("authority"):
        require_path(str(terminology["authority"]), "registry/terminology.json")

    print("registry validation passed")


if __name__ == "__main__":
    main()
