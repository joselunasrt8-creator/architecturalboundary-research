#!/usr/bin/env python3
"""Prospectively frozen black-box acceptance oracle for future Run 3 candidates."""
from __future__ import annotations
import argparse, json, subprocess, sys, tempfile
from pathlib import Path

def write(root: Path, name: str, value: str) -> None:
    path = root / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(value, encoding="utf-8")

def invoke(candidate: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(candidate / "scripts/structural_snapshot.py"), *args], cwd=candidate,
                          text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=False)

def load(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    assert result.returncode == 0, result.stderr
    value = json.loads(result.stdout)
    assert result.stdout == json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
    assert isinstance(value.get("nodes"), list) and isinstance(value.get("edges"), list)
    return value

def edges(value: dict[str, object]) -> set[tuple[str, str]]:
    return {(x["from"], x["to"]) if isinstance(x, dict) else (x[0], x[1]) for x in value["edges"]}  # type: ignore[index]

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--objective", required=True, choices=("O1","O2","O3","O4")); parser.add_argument("--candidate-tree", required=True, type=Path)
    args = parser.parse_args(); candidate = args.candidate_tree.resolve()
    with tempfile.TemporaryDirectory(prefix="run3-candidate-oracle-") as td:
        root = Path(td)
        write(root, "app/main.py", "from owned import helper\nimport owned.direct\nimport external\n")
        write(root, "owned/__init__.py", ""); write(root, "owned/helper.py", ""); write(root, "owned/direct.py", "")
        first = load(invoke(candidate, str(root))); second = load(invoke(candidate, str(root)))
        assert first == second
        assert first["nodes"] == sorted(first["nodes"]) and first["nodes"] == ["app.main", "owned", "owned.direct", "owned.helper"]
        assert edges(first) == {("app.main", "owned"), ("app.main", "owned.direct")}
        if args.objective in {"O2","O3","O4"}:
            write(root, "skip_one/a.py", "import owned\n"); write(root, "skip_two/b.py", "import owned\n")
            excluded = load(invoke(candidate, "--root", str(root), "--exclude", "skip_two", "--exclude", "skip_one"))
            assert excluded.get("exclusions") == ["skip_one", "skip_two"]
            assert not ({"skip_one.a", "skip_two.b"} & set(excluded["nodes"]))
            assert invoke(candidate, "--root", str(root), "--exclude", "../escape").returncode != 0
        if args.objective in {"O3","O4"}:
            write(root, "cycle/a.py", "import cycle.b\n"); write(root, "cycle/b.py", "import cycle.a\n"); write(root, "selfish.py", "import selfish\n")
            cyclic = load(invoke(candidate, "--root", str(root), "--exclude", "skip_one", "--exclude", "skip_two"))
            assert cyclic.get("cycles") == [["cycle.a", "cycle.b"], ["selfish"]]
            write(root, "cycle/b.py", ""); write(root, "selfish.py", "")
            acyclic = load(invoke(candidate, "--root", str(root), "--exclude", "skip_one", "--exclude", "skip_two")); assert acyclic.get("cycles") == []
        if args.objective == "O4":
            before = root / "before.json"; before.write_text(json.dumps(acyclic), encoding="utf-8")
            (root / "owned/direct.py").unlink(); write(root, "app/main.py", "from owned import helper\nimport new\n"); write(root, "new.py", "")
            compared = load(invoke(candidate, "--root", str(root), "--exclude", "skip_one", "--exclude", "skip_two", "--compare", str(before)))
            change = compared.get("comparison"); assert isinstance(change, dict)
            assert change.get("added_nodes") == ["new"] and change.get("removed_nodes") == ["owned.direct"]
            assert change.get("added_edges") == [["app.main", "new"]] and change.get("removed_edges") == [["app.main", "owned"], ["app.main", "owned.direct"]]
            ordinary = load(invoke(candidate, "--root", str(root), "--exclude", "skip_one", "--exclude", "skip_two")); assert "comparison" not in ordinary
            bad = root / "bad.json"; bad.write_text('{"nodes":"bad","edges":[]}', encoding="utf-8"); assert invoke(candidate, "--root", str(root), "--compare", str(bad)).returncode != 0
    print(json.dumps({"objective": args.objective, "status": "PASS"}, sort_keys=True)); return 0

if __name__ == "__main__": raise SystemExit(main())
