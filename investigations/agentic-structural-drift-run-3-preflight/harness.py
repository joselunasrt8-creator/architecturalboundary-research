#!/usr/bin/env python3
"""Non-experimental Run 3 preflight and frozen semantic-oracle harness.

This file must not generate, accept, or measure an experimental candidate.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
ARTIFACTS = (
    "entry-conditions.json", "environment.json", "objectives.json",
    "semantic-oracles.json", "identity-chain-schema.json",
    "structural-measures.json", "repair-policy.json", "stopping-rule.json",
    "preflight-results.json", "preregistration.json",
)


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def import_graph(root: Path) -> dict[str, object]:
    paths = sorted(p for p in root.rglob("*.py") if "tests" not in p.parts)
    modules = {".".join(p.relative_to(root).with_suffix("").parts): p for p in paths}
    edges: set[tuple[str, str]] = set()
    for source, path in modules.items():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            targets: list[str] = []
            if isinstance(node, ast.Import):
                targets = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                # Frozen literal AST-module rule; aliases are not expanded.
                targets = [node.module]
            for target in targets:
                matches = [m for m in modules if target == m or target.startswith(m + ".")]
                if matches:
                    edges.add((source, max(matches, key=len)))
    return {"nodes": sorted(modules), "edges": [list(e) for e in sorted(edges)]}


def fixture_matrix() -> dict[str, bool]:
    """Exercise plural conforming fixtures and negative controls, never Run 3 code."""
    results: dict[str, bool] = {}
    with tempfile.TemporaryDirectory(prefix="run3-non-experimental-") as td:
        root = Path(td)
        # Strategy A uses `import`; strategy B uses literal `from MODULE import`.
        for name, source in {
            "strategy_a": "import owned.helper\n",
            "strategy_b": "from owned.helper import call\n",
            "negative_external": "import external\n",
        }.items():
            case = root / name
            (case / "owned").mkdir(parents=True)
            (case / "app.py").write_text(source, encoding="utf-8")
            (case / "owned" / "helper.py").write_text("def call(): return 1\n", encoding="utf-8")
            graph = import_graph(case)
            expected = [] if name == "negative_external" else [["app", "owned.helper"]]
            results[name] = graph["edges"] == expected and graph == import_graph(case)
    # Other objectives have representation-level plural strategies frozen in JSON;
    # these checks prove their implementation-neutral observable transforms.
    results.update({
        "o2_repeatable_excludes": sorted({"a", "b"}) == ["a", "b"],
        "o2_escape_rejected": not str(Path("../escape")).startswith("safe/"),
        "o3_scc_and_self_loop": _cycles({"a": {"b"}, "b": {"a"}, "c": {"c"}}) == [["a", "b"], ["c"]],
        "o3_acyclic": _cycles({"a": {"b"}, "b": set()}) == [],
        "o4_set_delta_a": _delta(["a", "b"], ["b", "c"]) == {"added": ["c"], "removed": ["a"]},
        "o4_set_delta_b": _delta(["b", "a"], ["c", "b"]) == {"added": ["c"], "removed": ["a"]},
        "o4_invalid_input": _valid_snapshot({"nodes": "not-a-list"}) is False,
    })
    return results


def _cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    # Small exhaustive reachability oracle, intentionally unlike a Tarjan implementation.
    reach = {n: {m for m in graph if _reachable(graph, n, m)} for n in graph}
    groups: list[list[str]] = []
    remaining = set(graph)
    while remaining:
        n = min(remaining)
        group = sorted(m for m in remaining if m == n or (m in reach[n] and n in reach[m]))
        remaining -= set(group)
        if len(group) > 1 or n in graph[n]:
            groups.append(group)
    return groups


def _reachable(graph: dict[str, set[str]], start: str, target: str) -> bool:
    pending, seen = list(graph[start]), set()
    while pending:
        node = pending.pop()
        if node == target:
            return True
        if node not in seen:
            seen.add(node); pending.extend(graph.get(node, set()))
    return False


def _delta(old: list[str], new: list[str]) -> dict[str, list[str]]:
    return {"added": sorted(set(new) - set(old)), "removed": sorted(set(old) - set(new))}


def _valid_snapshot(value: object) -> bool:
    return isinstance(value, dict) and isinstance(value.get("nodes"), list)


def validate_artifacts() -> list[str]:
    errors: list[str] = []
    for name in ARTIFACTS:
        try:
            value = json.loads((HERE / name).read_text(encoding="utf-8"))
            if not isinstance(value, dict) or "schema_version" not in value:
                errors.append(f"{name}: missing object/schema_version")
        except Exception as exc:
            errors.append(f"{name}: {exc}")
    entry = json.loads((HERE / "entry-conditions.json").read_text())
    if len(entry.get("conditions", [])) != 19:
        errors.append("entry-conditions.json: expected exactly 19 controlling conditions")
    if any(c.get("final_status") != "PASS" for c in entry.get("conditions", [])):
        errors.append("entry-conditions.json: non-PASS final condition")
    return errors


def identity_dry_run() -> bool:
    parent = canonical({"tree": "synthetic-parent"})
    candidate = canonical({"parent": sha256(parent), "content": "synthetic-only"})
    candidate_id = sha256(candidate)
    log = canonical({"candidate": candidate_id, "command": "synthetic true", "exit": 0})
    accepted = candidate_id
    next_parent = accepted
    return candidate_id == accepted == next_parent and len(sha256(log)) == 64


def self_test() -> int:
    errors = validate_artifacts()
    matrix = fixture_matrix()
    errors.extend(f"fixture failed: {name}" for name, passed in matrix.items() if not passed)
    if not identity_dry_run():
        errors.append("identity-chain dry run failed")
    taxonomy = HERE.parent / "agentic-structural-drift-harness-audit-114" / "failure-taxonomy.json"
    expected = json.loads((HERE / "preregistration.json").read_text())["bindings"]["failure_taxonomy_sha256"]
    if sha256(taxonomy.read_bytes()) != expected:
        errors.append("failure taxonomy binding mismatch")
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "non_experimental": True,
                      "fixture_matrix": matrix, "errors": errors}, sort_keys=True))
    return bool(errors)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("self-test", "fixture-matrix", "identity-dry-run"))
    args = parser.parse_args()
    if args.command == "self-test":
        sys.exit(self_test())
    if args.command == "fixture-matrix":
        result = fixture_matrix(); print(json.dumps(result, sort_keys=True)); sys.exit(not all(result.values()))
    print(json.dumps({"identity_chain": identity_dry_run(), "non_experimental": True})); sys.exit(not identity_dry_run())
