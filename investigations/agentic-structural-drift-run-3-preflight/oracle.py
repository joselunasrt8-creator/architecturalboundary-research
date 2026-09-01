#!/usr/bin/env python3
"""Frozen black-box semantic oracle for a future immutable Run 3 candidate."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def write(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def invoke(candidate: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(candidate / "scripts/structural_snapshot.py"), *args],
        cwd=candidate, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        timeout=30, check=False,
    )


def load_ok(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    assert result.returncode == 0, result.stderr
    value = json.loads(result.stdout)
    assert result.stdout == json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
    assert isinstance(value.get("nodes"), list) and isinstance(value.get("edges"), list)
    return value


def edge_set(value: dict[str, object]) -> set[tuple[str, str]]:
    edges = value["edges"]
    assert isinstance(edges, list)
    return {(edge["from"], edge["to"]) for edge in edges}  # type: ignore[index]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--objective", required=True, choices=("O1", "O2", "O3", "O4"))
    parser.add_argument("--candidate-tree", required=True, type=Path)
    args = parser.parse_args()
    candidate = args.candidate_tree.resolve()
    with tempfile.TemporaryDirectory(prefix="run3-oracle-") as td:
        fixture = Path(td)
        write(fixture, "app/main.py", "import owned.helper\nimport external\n")
        write(fixture, "owned/helper.py", "")
        first = load_ok(invoke(candidate, str(fixture)))
        second = load_ok(invoke(candidate, str(fixture)))
        assert first == second
        assert first["nodes"] == ["app.main", "owned.helper"]
        assert edge_set(first) == {("app.main", "owned.helper")}

        if args.objective in {"O2", "O3", "O4"}:
            write(fixture, "excluded/hidden.py", "import owned.helper\n")
            excluded = load_ok(invoke(candidate, "--root", str(fixture), "--exclude", "excluded"))
            assert "excluded.hidden" not in excluded["nodes"]
            assert excluded.get("exclusions") == ["excluded"]
            escape = invoke(candidate, "--root", str(fixture), "--exclude", "../escape")
            assert escape.returncode != 0

        if args.objective in {"O3", "O4"}:
            write(fixture, "app/main.py", "import owned.helper\n")
            write(fixture, "owned/helper.py", "import app.main\n")
            cyclic = load_ok(invoke(candidate, str(fixture)))
            assert cyclic.get("cycles") == [["app.main", "owned.helper"]]
            write(fixture, "owned/helper.py", "")
            acyclic = load_ok(invoke(candidate, str(fixture)))
            assert acyclic.get("cycles") == []

        if args.objective == "O4":
            before = fixture / "before.json"
            before.write_text(json.dumps(acyclic), encoding="utf-8")
            write(fixture, "new.py", "")
            compared = load_ok(invoke(candidate, str(fixture), "--compare", str(before)))
            comparison = compared.get("comparison")
            assert isinstance(comparison, dict)
            assert comparison.get("added_nodes") == ["new"]
            assert comparison.get("removed_nodes") == []
            bad = fixture / "bad.json"; bad.write_text('{"nodes":"bad"}', encoding="utf-8")
            assert invoke(candidate, str(fixture), "--compare", str(bad)).returncode != 0
    print(json.dumps({"objective": args.objective, "status": "PASS"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
