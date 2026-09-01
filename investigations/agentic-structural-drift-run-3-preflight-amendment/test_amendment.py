#!/usr/bin/env python3
"""Non-experimental fixture preflight for the independent instrument."""
from __future__ import annotations
import importlib.util, tempfile
from pathlib import Path

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("independent_measure", HERE / "independent_structural_measure.py")
assert spec and spec.loader
measure_module = importlib.util.module_from_spec(spec); spec.loader.exec_module(measure_module)

def put(root: Path, name: str, text: str) -> None:
    path = root / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text, encoding="utf-8")

def test_controls() -> None:
    with tempfile.TemporaryDirectory(prefix="non-experimental-structural-controls-") as td:
        root = Path(td)
        put(root,"tools/a.py","import scripts.b\nimport tests.t\nimport investigations.i\n")
        put(root,"scripts/b.py","import investigations.i\n"); put(root,"tests/t.py",""); put(root,"investigations/i.py","import scripts.b\n")
        put(root,"pair/a.py","import pair.b\n"); put(root,"pair/b.py","import pair.a\n"); put(root,"self.py","import self\n"); put(root,"clean.py","import external\n")
        first = measure_module.measure(root, ()); second = measure_module.measure(root, ())
        assert first == second
        assert ["tools.a","scripts.b"] in first["violations"]["prohibited_direction"]
        assert ["tools.a","tests.t"] in first["violations"]["production_imports_tests"]
        assert len(first["violations"]["investigation_boundary"]) == 3
        assert first["cycles"] == [["investigations.i","scripts.b"],["pair.a","pair.b"],["self"]]
        put(root,"new.py","import clean\n"); after = measure_module.measure(root, ())
        change = measure_module.delta(first, after)
        assert change["added_nodes"] == ["new"] and change["added_edges"] == [["new","clean"]]
        (root / "new.py").unlink(); assert measure_module.delta(after, measure_module.measure(root, ())) == {"added_nodes":[],"removed_nodes":["new"],"added_edges":[],"removed_edges":[["new","clean"]]}
        put(root,"broken.py","def nope(:\n"); assert {x["reason"] for x in measure_module.measure(root, ())["unmeasurable"]} == {"SyntaxError"}

def test_malformed_delta() -> None:
    try: measure_module.delta({"nodes":"bad","edges":[]},{"nodes":[],"edges":[]})
    except ValueError: return
    raise AssertionError("malformed delta was accepted")
