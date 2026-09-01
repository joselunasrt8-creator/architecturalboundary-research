#!/usr/bin/env python3
"""Frozen, candidate-independent static structural measurement for Run 3.

The measured tree is data.  This program never imports or executes code from it.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path, PurePosixPath


def module_name(relative: Path) -> str:
    parts = list(relative.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def excluded(relative: Path, exclusions: tuple[PurePosixPath, ...]) -> bool:
    posix = PurePosixPath(relative.as_posix())
    return any(posix == item or item in posix.parents for item in exclusions)


def cycles(nodes: set[str], edges: set[tuple[str, str]]) -> list[list[str]]:
    graph = {node: [] for node in nodes}
    for source, target in edges:
        if source in graph and target in graph:
            graph[source].append(target)
    for targets in graph.values():
        targets.sort()
    index = 0
    stack: list[str] = []
    indices: dict[str, int] = {}
    low: dict[str, int] = {}
    active: set[str] = set()
    result: list[list[str]] = []

    def visit(node: str) -> None:
        nonlocal index
        indices[node] = low[node] = index
        index += 1
        stack.append(node)
        active.add(node)
        for target in graph[node]:
            if target not in indices:
                visit(target)
                low[node] = min(low[node], low[target])
            elif target in active:
                low[node] = min(low[node], indices[target])
        if low[node] == indices[node]:
            component: list[str] = []
            while True:
                member = stack.pop()
                active.remove(member)
                component.append(member)
                if member == node:
                    break
            component.sort()
            if len(component) > 1 or (component[0], component[0]) in edges:
                result.append(component)

    for node in sorted(nodes):
        if node not in indices:
            visit(node)
    return sorted(result)


def measure(root: Path, exclusions: tuple[PurePosixPath, ...]) -> dict[str, object]:
    root = root.resolve(strict=True)
    files = sorted(
        path for path in root.rglob("*.py")
        if path.is_file() and not excluded(path.relative_to(root), exclusions)
    )
    module_files = [(module_name(path.relative_to(root)), path) for path in files]
    modules = {name for name, _ in module_files if name}
    edges: set[tuple[str, str]] = set()
    unmeasurable: list[dict[str, object]] = []
    for source, path in module_files:
        if not source:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.as_posix())
        except (OSError, UnicodeError, SyntaxError) as error:
            unmeasurable.append({"module": source, "reason": type(error).__name__})
            continue
        for node in ast.walk(tree):
            targets: list[str] = []
            if isinstance(node, ast.Import):
                targets = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                # Literal AST semantics: names imported from the module are not appended.
                targets = [node.module]
            for target in targets:
                if target in modules:
                    edges.add((source, target))
    production_edges = {(a, b) for a, b in edges if not (a == "tests" or a.startswith("tests."))}
    violations = {
        "prohibited_direction": sorted([a, b] for a, b in production_edges if a.startswith("tools.") and b.startswith("scripts.")),
        "production_imports_tests": sorted([a, b] for a, b in production_edges if b == "tests" or b.startswith("tests.")),
        "investigation_boundary": sorted(
            [a, b] for a, b in production_edges
            if ((a.startswith(("scripts.", "tools.")) and b.startswith("investigations."))
                or (a.startswith("investigations.") and b.startswith("scripts.")))
        ),
    }
    return {
        "schema_version": "1.0",
        "nodes": sorted(modules),
        "edges": sorted([a, b] for a, b in edges),
        "cycles": cycles(modules, edges),
        "violations": violations,
        "unmeasurable": sorted(unmeasurable, key=lambda item: (str(item["module"]), str(item["reason"]))),
    }


def delta(before: dict[str, object], after: dict[str, object]) -> dict[str, object]:
    def pairs(value: object) -> set[tuple[str, str]]:
        if not isinstance(value, list) or any(not isinstance(x, list) or len(x) != 2 or not all(isinstance(y, str) for y in x) for x in value):
            raise ValueError("edges must be a list of two-string lists")
        return {(x[0], x[1]) for x in value}
    def names(value: object) -> set[str]:
        if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
            raise ValueError("nodes must be a list of strings")
        return set(value)
    old_nodes, new_nodes = names(before.get("nodes")), names(after.get("nodes"))
    old_edges, new_edges = pairs(before.get("edges")), pairs(after.get("edges"))
    return {
        "added_nodes": sorted(new_nodes - old_nodes), "removed_nodes": sorted(old_nodes - new_nodes),
        "added_edges": sorted([a, b] for a, b in new_edges - old_edges),
        "removed_edges": sorted([a, b] for a, b in old_edges - new_edges),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument("--compare", type=Path)
    args = parser.parse_args()
    exclusions: list[PurePosixPath] = []
    for raw in args.exclude:
        item = PurePosixPath(raw)
        if item.is_absolute() or ".." in item.parts:
            parser.error("exclusions must be repository-relative and cannot escape root")
        exclusions.append(item)
    try:
        result = measure(args.root, tuple(sorted(set(exclusions), key=str)))
        if args.compare:
            before = json.loads(args.compare.read_text(encoding="utf-8"))
            if not isinstance(before, dict):
                raise ValueError("comparison snapshot must be an object")
            result["comparison"] = delta(before, result)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
