#!/usr/bin/env python3
"""Execute the frozen Option B selector and construct SP01--SP08.

All corpus and prompt bytes are read from the commit frozen by
``source-selection-freeze.json``.  The working tree is only an output surface;
it is never a source-selection input.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import canonical_source_selector as selector


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PROTOCOL_PATH = HERE / "source-selection-freeze.json"
LEDGER_PATH = HERE / "candidate-review-ledger.json"
SELECTION_PATH = HERE / "selection-result.json"
MANIFEST_PATH = HERE / "hash-manifest.json"
EXECUTION_DIR = HERE.parent / "execution-package-v1"
EXECUTION_REGISTRY_PATH = EXECUTION_DIR / "source-package-registry.json"
PROMPT_BINDINGS_REPOSITORY_PATH = (
    "investigations/context-scaling-vs-explicit-abstraction/artifacts/"
    "execution-package-v1/prompt-bindings.json"
)
PROTOCOL_REPOSITORY_PATH = (
    "investigations/context-scaling-vs-explicit-abstraction/artifacts/"
    "canonical-source-packages-v1/source-selection-freeze.json"
)
PROTOCOL_FREEZE_COMMIT = "f2590be67c5763b7ef31827f473813007e695ff3"
UNITIZATION_VERSION = "canonical-verbatim-blocks-v1"
PACKAGE_IDS = selector.PACKAGE_IDS
CONDITIONS = selector.CONDITIONS
UNIT_IDS = selector.UNIT_IDS
HEX64 = re.compile(r"[0-9a-f]{64}")
LEAKAGE_MARKERS = {
    "contains_answer_keys": ("answer-key-registry", "answer key for target"),
    "contains_scope_rubrics": ("scope-rubric-registry", "scope rubric for target"),
    "contains_prior_experiment_outputs": ("stage1_outputs", "source_execution_bound"),
    "contains_experiment_specific_instructions": (
        "context-scaling-vs-explicit-abstraction",
        "source_stage_ready",
        "target_stage_ready",
    ),
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def pretty_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git_blob_id(value: bytes) -> str:
    return hashlib.sha1(f"blob {len(value)}\0".encode("ascii") + value).hexdigest()


def object_hash(value: Mapping[str, Any]) -> str:
    return sha256_bytes(canonical_bytes(value))


@dataclass(frozen=True)
class TreeEntry:
    mode: str
    object_type: str
    object_id: str
    path: str


class GitSnapshot:
    """Read-only access to exact Git objects."""

    def __init__(self, root: Path = ROOT) -> None:
        self.root = root

    def _run(self, *args: str) -> bytes:
        return subprocess.check_output(["git", *args], cwd=self.root)

    def require_commit(self, commit: str) -> None:
        resolved = self._run("rev-parse", "--verify", f"{commit}^{{commit}}").decode().strip()
        if resolved != commit:
            raise ValueError(f"commit binding did not resolve exactly: {commit}")

    def tree(self, commit: str, roots: list[str]) -> list[TreeEntry]:
        raw = self._run("ls-tree", "-rz", "--full-tree", commit, "--", *roots)
        entries: list[TreeEntry] = []
        for record in raw.split(b"\0"):
            if not record:
                continue
            metadata, path_bytes = record.split(b"\t", 1)
            mode, object_type, object_id = metadata.decode("ascii").split(" ")
            entries.append(TreeEntry(mode, object_type, object_id, path_bytes.decode("utf-8", "strict")))
        return entries

    def blob(self, commit: str, path: str) -> bytes:
        return self._run("show", f"{commit}:{path}")

    def last_author(self, commit: str, path: str) -> dict[str, str]:
        raw = self._run(
            "log",
            "-1",
            "--format=%H%x00%an%x00%ae%x00%aI",
            commit,
            "--",
            path,
        ).rstrip(b"\n")
        parts = raw.decode("utf-8", "strict").split("\0")
        if len(parts) != 4 or not all(parts):
            raise ValueError(f"missing frozen authorship evidence for {path}")
        return dict(zip(("commit", "author_name", "author_email", "authored_at"), parts, strict=True))


def _line_offsets(raw: bytes) -> list[tuple[int, int, str]]:
    lines: list[tuple[int, int, str]] = []
    cursor = 0
    for line in raw.splitlines(keepends=True):
        end = cursor + len(line)
        lines.append((cursor, end, line.decode("utf-8", "strict")))
        cursor = end
    if cursor < len(raw):
        lines.append((cursor, len(raw), raw[cursor:].decode("utf-8", "strict")))
    return lines


def _is_heading(text: str, suffix: str) -> bool:
    stripped = text.strip()
    if suffix == ".md":
        return re.match(r"^#{1,6}\s+\S", stripped) is not None
    return re.match(r"^\\(?:part|chapter|section|subsection|subsubsection)\*?\{", stripped) is not None


def atomic_blocks(raw: bytes, suffix: str) -> list[tuple[int, int]]:
    """Return deterministic verbatim blocks with headings attached forward."""
    raw.decode("utf-8", "strict")
    lines = _line_offsets(raw)
    primitive: list[tuple[int, int]] = []
    index = 0
    while index < len(lines):
        start, end, text = lines[index]
        if not text.strip():
            index += 1
            continue
        stripped = text.lstrip()
        fence = re.match(r"(`{3,}|~{3,})", stripped)
        if fence:
            marker = fence.group(1)[0]
            count = len(fence.group(1))
            index += 1
            while index < len(lines):
                end = lines[index][1]
                if re.match(rf"^\s*{re.escape(marker)}{{{count},}}\s*$", lines[index][2]):
                    index += 1
                    break
                index += 1
            primitive.append((start, end))
            continue
        environment = re.match(r"\s*\\begin\{([^}]+)\}", text)
        if environment:
            close = f"\\end{{{environment.group(1)}}}"
            index += 1
            while index < len(lines):
                end = lines[index][1]
                index += 1
                if close in lines[index - 1][2]:
                    break
            primitive.append((start, end))
            continue
        index += 1
        while index < len(lines) and lines[index][2].strip():
            end = lines[index][1]
            index += 1
        primitive.append((start, end))

    attached: list[tuple[int, int]] = []
    pending_start: int | None = None
    for start, end in primitive:
        content = raw[start:end].decode("utf-8", "strict")
        if _is_heading(content, suffix):
            if pending_start is None:
                pending_start = start
            continue
        if pending_start is not None:
            start = pending_start
            pending_start = None
        attached.append((start, end))
    if pending_start is not None:
        attached.append((pending_start, primitive[-1][1]))
    return attached


def meaningful_units(raw: bytes, suffix: str, minimum_words: int) -> list[dict[str, Any]]:
    units: list[dict[str, Any]] = []
    for start, end in atomic_blocks(raw, suffix):
        content_bytes = raw[start:end]
        content = content_bytes.decode("utf-8", "strict")
        if len(selector.word_tokens(content)) < minimum_words:
            continue
        units.append(
            {
                "id": f"U{len(units) + 1:03d}",
                "start_byte": start,
                "end_byte": end,
                "content": content,
                "sha256": sha256_bytes(content_bytes),
            }
        )
    return units


def _provenance(snapshot: GitSnapshot, commit: str, path: str) -> dict[str, Any]:
    author = snapshot.last_author(commit, path)
    bot = re.search(r"(?:\[bot\]|bot@|noreply@github\.com$)", author["author_email"], re.I) is not None
    evidence = (
        f"git commit {author['commit']} records author {author['author_name']} "
        f"<{author['author_email']}> at {author['authored_at']} for {path}"
    )
    return {
        "authorship_classification": "UNCLEAR" if bot else "HUMAN_AUTHORED",
        "authorship_evidence": [evidence],
        "generated": bot,
        "provenance_clear": not bot,
        "derived_from": [],
    }


def _leakage(content: str) -> dict[str, bool]:
    normalized = selector.normalized_document(content)
    values = {
        field: any(marker in normalized for marker in markers)
        for field, markers in LEAKAGE_MARKERS.items()
    }
    values["contains_target_tasks"] = "target task for condition" in normalized
    values["selected_after_target_performance"] = False
    return values


def candidate_record(
    snapshot: GitSnapshot,
    entry: TreeEntry,
    protocol: dict[str, Any],
    bindings: dict[str, Any],
) -> dict[str, Any]:
    commit = protocol["repository"]["commit"]
    raw = snapshot.blob(commit, entry.path)
    if git_blob_id(raw) != entry.object_id:
        raise ValueError(f"pinned blob object mismatch: {entry.path}")
    content = raw.decode("utf-8", "strict")
    word_count = len(selector.word_tokens(content))
    minimum_words = protocol["eligibility"]["substantive_content"]["meaningful_unit_minimum_word_tokens"]
    units = meaningful_units(raw, Path(entry.path).suffix, minimum_words)
    candidate = {
        "path": entry.path,
        "commit": commit,
        "stable_locator": protocol["eligibility"]["stable_binding"]["stable_locator_template"].format(
            commit=commit, path=entry.path
        ),
        "content_utf8": content,
        "blob_sha256": sha256_bytes(raw),
        "document_role": "SUBSTANTIVE_SOURCE" if word_count >= 320 else "INSUFFICIENT_SUBSTANTIVE_CONTENT",
        "provenance": _provenance(snapshot, commit, entry.path),
        "units": units,
        "token_accounting": {
            "tokenizer_name": "o200k_base",
            "tokenizer_package": "tiktoken==0.9.0",
            "condition_counts": {},
            "truncation": False,
            "compression": False,
            "substitution": False,
        },
        "leakage": _leakage(content),
    }
    candidate["token_accounting"]["condition_counts"] = selector.candidate_token_counts(candidate, bindings)
    return candidate


def frozen_inputs(snapshot: GitSnapshot) -> tuple[dict[str, Any], bytes, dict[str, Any], bytes, list[TreeEntry]]:
    protocol_bytes = PROTOCOL_PATH.read_bytes()
    protocol = json.loads(protocol_bytes)
    frozen_protocol = snapshot.blob(PROTOCOL_FREEZE_COMMIT, PROTOCOL_REPOSITORY_PATH)
    if protocol_bytes != frozen_protocol:
        raise ValueError("frozen Option B protocol bytes changed")
    if not selector.validate_protocol(protocol):
        raise ValueError("frozen Option B protocol is invalid")
    commit = protocol["repository"]["commit"]
    snapshot.require_commit(commit)
    bindings_bytes = snapshot.blob(commit, PROMPT_BINDINGS_REPOSITORY_PATH)
    bindings = json.loads(bindings_bytes)
    entries = snapshot.tree(commit, protocol["corpus_boundary"]["allowed_path_prefixes"])
    return protocol, protocol_bytes, bindings, bindings_bytes, entries


def enumerate_records(snapshot: GitSnapshot = GitSnapshot()) -> dict[str, Any]:
    protocol, protocol_bytes, bindings, bindings_bytes, entries = frozen_inputs(snapshot)
    path_entries = {entry.path: entry for entry in entries}
    discovered = selector.discover_candidate_paths(path_entries, protocol)
    records: list[dict[str, Any]] = []
    for path in discovered:
        entry = path_entries[path]
        if entry.mode == "120000" or entry.object_type != "blob":
            raise ValueError(f"non-blob candidate prohibited: {path}")
        records.append(candidate_record(snapshot, entry, protocol, bindings))
    selection = selector.select_candidates(records, protocol, bindings)
    review = {item["path"]: item for item in selection["reviewed_candidates"]}
    ledger_records = []
    for record in records:
        item = review[record["path"]]
        ledger_records.append(
            {
                "path": record["path"],
                "tree_object_id": path_entries[record["path"]].object_id,
                "document_sha256": record["blob_sha256"],
                "byte_length": len(record["content_utf8"].encode("utf-8")),
                "unicode_word_tokens": len(selector.word_tokens(record["content_utf8"])),
                "meaningful_unit_count": len(record["units"]),
                "provenance": record["provenance"],
                "leakage": record["leakage"],
                "token_accounting": record["token_accounting"],
                "status": item["status"],
                "reasons": item["reasons"],
            }
        )
    ledger = {
        "schema_version": "1",
        "protocol_sha256": sha256_bytes(protocol_bytes),
        "corpus_repository": protocol["repository"]["name_with_owner"],
        "corpus_commit": protocol["repository"]["commit"],
        "prompt_bindings": {
            "path": PROMPT_BINDINGS_REPOSITORY_PATH,
            "commit": protocol["repository"]["commit"],
            "sha256": sha256_bytes(bindings_bytes),
        },
        "ordering_rule": protocol["candidate_ordering"]["rule"],
        "candidate_count": len(ledger_records),
        "candidates": ledger_records,
    }
    return {
        "protocol": protocol,
        "bindings": bindings,
        "records": records,
        "selection": selection,
        "ledger": ledger,
        "protocol_sha256": sha256_bytes(protocol_bytes),
        "bindings_sha256": sha256_bytes(bindings_bytes),
    }


def _package_artifact(
    package_id: str,
    candidate: dict[str, Any],
    protocol: dict[str, Any],
) -> dict[str, Any]:
    units = candidate["units"][:16]
    document_identifier = f"DOC-{candidate['blob_sha256']}"
    body: dict[str, Any] = {
        "schema_version": "1",
        "package_id": package_id,
        "status": "READY",
        "document_identifier": document_identifier,
        "source_document": {
            "repository": protocol["repository"]["name_with_owner"],
            "repository_relative_path": candidate["path"],
            "repository_commit": candidate["commit"],
            "stable_locator": candidate["stable_locator"],
            "encoding": "strict UTF-8",
            "normalization": "none; original UTF-8 bytes retained verbatim",
            "byte_length": len(candidate["content_utf8"].encode("utf-8")),
            "sha256": candidate["blob_sha256"],
            "content": candidate["content_utf8"],
        },
        "unitization": {
            "method": protocol["eligibility"]["unitization"]["boundary_rule"],
            "version": UNITIZATION_VERSION,
            "selection": "first sixteen meaningful units in deterministic document order",
            "available_meaningful_units": len(candidate["units"]),
            "units": units,
        },
        "subsets": {"N=8": UNIT_IDS[:8], "M=16": UNIT_IDS},
        "token_accounting": candidate["token_accounting"],
        "provenance": candidate["provenance"],
        "eligibility": {
            "status": "ELIGIBLE",
            "duplicate_handling": "first canonical occurrence retained",
            "truncation": False,
            "compression": False,
            "substitution": False,
            "experiment_leakage": False,
        },
    }
    return {**body, "package_sha256": object_hash(body)}


def _registry(packages: list[dict[str, Any]]) -> dict[str, Any]:
    records = []
    for index, package in enumerate(packages, start=1):
        document = package["source_document"]
        units = package["unitization"]["units"]
        body = {
            "id": package["package_id"],
            "status": "READY",
            "canonical_source_reference": package["document_identifier"],
            "immutable_locator": document["stable_locator"],
            "document_order": f"{index:02d}:{document['repository_relative_path']}",
            "unit_boundary_method": package["unitization"]["method"],
            "unit_boundary_version": package["unitization"]["version"],
            "units": [
                {
                    "id": unit["id"],
                    "status": "ELIGIBLE",
                    "content": unit["content"],
                    "sha256": unit["sha256"],
                    "source_reference": (
                        f"{document['stable_locator']}#bytes={unit['start_byte']}-{unit['end_byte']}"
                    ),
                }
                for unit in units
            ],
            "source_hashes": [unit["sha256"] for unit in units],
            "duplicate_decisions": [],
            "exclusion_decisions": [],
            "duplicate_eligible_content_absent": True,
            "subsets": package["subsets"],
            "token_accounting": {
                "tokenizer": package["token_accounting"]["tokenizer_name"],
                "package": package["token_accounting"]["tokenizer_package"],
                "condition_counts": package["token_accounting"]["condition_counts"],
                "condition_ceilings": {"C1": 4096, "C2": 4096, "C3": 8192, "C4": 8192},
                "truncation": False,
                "compression": False,
                "substitution": False,
            },
            "provenance": {
                "document_sha256": document["sha256"],
                "repository_commit": document["repository_commit"],
                "repository_relative_path": document["repository_relative_path"],
                "authorship": package["provenance"],
                "package_artifact_sha256": package["package_sha256"],
            },
        }
        records.append({**body, "package_hash": object_hash(body)})
    return {
        "schema_version": "1",
        "package_version": "execution-package-v1",
        "preregistration_path": "investigations/context-scaling-vs-explicit-abstraction/preregistration.md",
        "preregistration_commit": "aed5ff895d3afb0a03b819bc5112327b479b8905",
        "preregistration_sha256": "79c9f23be0b5f0742ea220d88b22663f4ae6dc1350353f5becbc38296029c3b6",
        "unitization": "Frozen Option B canonical-verbatim-blocks-v1; first sixteen meaningful units",
        "packages": records,
    }


def render_artifacts(snapshot: GitSnapshot = GitSnapshot()) -> dict[Path, bytes]:
    state = enumerate_records(snapshot)
    selection = state["selection"]
    ledger_bytes = pretty_bytes(state["ledger"])
    ready = selection["selection_result"] == "READY"
    packages: list[dict[str, Any]] = []
    if ready:
        by_path = {record["path"]: record for record in state["records"]}
        packages = [
            _package_artifact(package_id, by_path[selection["assignments"][package_id]], state["protocol"])
            for package_id in PACKAGE_IDS
        ]
    eligible_paths = [
        item["path"] for item in state["ledger"]["candidates"] if item["status"] == "ELIGIBLE"
    ]
    selection_body = {
        "schema_version": "1",
        "protocol_sha256": state["protocol_sha256"],
        "corpus_commit": state["protocol"]["repository"]["commit"],
        "prompt_bindings_sha256": state["bindings_sha256"],
        "ordering_rule": state["protocol"]["candidate_ordering"]["rule"],
        "selection_rule": state["protocol"]["selection"]["rule"],
        "selection_result": "READY" if ready else "NULL",
        "construction_status": "READY" if ready else "NOT_STARTED",
        "reason": (
            "The first eight eligible candidates were assigned deterministically."
            if ready
            else f"Only {len(eligible_paths)} of eight required eligible documents exist in the frozen corpus."
        ),
        "candidate_review_ledger_sha256": sha256_bytes(ledger_bytes),
        "eligible_paths": eligible_paths,
        "selected_paths": selection["selected_paths"] if ready else [],
        "assignments": selection["assignments"],
        "package_sha256": {package["package_id"]: package["package_sha256"] for package in packages},
        "prohibitions_respected": {
            "manual_ordering": True,
            "subjective_relevance_ranking": True,
            "substitution": True,
            "model_invocation": True,
            "abstraction_generation": True,
            "target_construction": True,
            "experiment_execution": True,
            "empirical_evidence_collection": True,
        },
    }
    artifacts: dict[Path, bytes] = {
        LEDGER_PATH: ledger_bytes,
        SELECTION_PATH: pretty_bytes(selection_body),
    }
    if ready:
        artifacts[EXECUTION_REGISTRY_PATH] = pretty_bytes(_registry(packages))
        for package in packages:
            artifacts[HERE / f"{package['package_id']}.json"] = pretty_bytes(package)
    governed = {
        str(path.relative_to(ROOT)): sha256_bytes(data)
        for path, data in sorted(artifacts.items(), key=lambda item: str(item[0]))
    }
    governed[str(PROTOCOL_PATH.relative_to(ROOT))] = state["protocol_sha256"]
    manifest = {
        "schema_version": "1",
        "corpus_commit": state["protocol"]["repository"]["commit"],
        "protocol_freeze_commit": PROTOCOL_FREEZE_COMMIT,
        "prompt_bindings": {
            "path": PROMPT_BINDINGS_REPOSITORY_PATH,
            "commit": state["protocol"]["repository"]["commit"],
            "sha256": state["bindings_sha256"],
        },
        "governed_files": dict(sorted(governed.items())),
    }
    artifacts[MANIFEST_PATH] = pretty_bytes(manifest)
    return artifacts


def validate_artifacts(files: Mapping[Path, bytes], snapshot: GitSnapshot = GitSnapshot()) -> bool:
    try:
        manifest = json.loads(files[MANIFEST_PATH])
        governed = manifest["governed_files"]
        if set(governed) != {str(path.relative_to(ROOT)) for path in files if path != MANIFEST_PATH} | {
            str(PROTOCOL_PATH.relative_to(ROOT))
        }:
            return False
        for repository_path, digest in governed.items():
            if HEX64.fullmatch(digest) is None:
                return False
            path = ROOT / repository_path
            data = PROTOCOL_PATH.read_bytes() if path == PROTOCOL_PATH else files[path]
            if sha256_bytes(data) != digest:
                return False
        expected = render_artifacts(snapshot)
        return set(files) == set(expected) and all(files[path] == data for path, data in expected.items())
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError):
        return False


def committed_artifacts() -> dict[Path, bytes]:
    manifest = json.loads(MANIFEST_PATH.read_bytes())
    paths = [ROOT / repository_path for repository_path in manifest["governed_files"]]
    paths = [path for path in paths if path != PROTOCOL_PATH]
    paths.append(MANIFEST_PATH)
    return {path: path.read_bytes() for path in paths}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify committed artifacts without writing")
    args = parser.parse_args()
    if args.check:
        committed = committed_artifacts()
        valid = validate_artifacts(committed)
        selection_result = json.loads(committed[SELECTION_PATH])["selection_result"] if valid else "NULL"
        print(json.dumps({"artifacts": "VALID" if valid else "INVALID", "selection_result": selection_result}))
        return 0 if valid else 1
    rendered = render_artifacts()
    result = json.loads(rendered[SELECTION_PATH])["selection_result"]
    for path, data in rendered.items():
        path.write_bytes(data)
    print(f"SP01-SP08 {result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
