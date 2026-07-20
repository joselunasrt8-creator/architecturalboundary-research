import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = (
    ROOT / "investigations/context-scaling-vs-explicit-abstraction/artifacts/canonical-source-packages-v1"
)
sys.path.insert(0, str(ARTIFACT_DIR))
MODULE_PATH = ARTIFACT_DIR / "canonical_source_constructor.py"
SPEC = importlib.util.spec_from_file_location("canonical_source_constructor", MODULE_PATH)
constructor = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = constructor
SPEC.loader.exec_module(constructor)

PROTOCOL_SHA256 = "e30ae79722eff29ab69acd814d317af4bbf7e54344545388808b1cbbacd643ad"
EXPECTED_ELIGIBLE = [
    "docs/higher_order_abstraction.md",
    "docs/minimal_promotion_package.md",
    "docs/publication.md",
    "docs/reference-execution/v1.0/freeze-readiness-record.md",
]


@pytest.fixture(scope="module")
def state():
    return constructor.enumerate_records()


@pytest.fixture(scope="module")
def rendered():
    return constructor.render_artifacts()


def test_frozen_option_b_protocol_is_byte_identical_to_merged_pr98():
    snapshot = constructor.GitSnapshot()
    frozen = snapshot.blob(constructor.PROTOCOL_FREEZE_COMMIT, constructor.PROTOCOL_REPOSITORY_PATH)
    current = constructor.PROTOCOL_PATH.read_bytes()
    assert current == frozen
    assert hashlib.sha256(current).hexdigest() == PROTOCOL_SHA256


def test_complete_pinned_tree_discovery_is_canonical_and_path_restricted(state):
    protocol = state["protocol"]
    snapshot = constructor.GitSnapshot()
    entries = snapshot.tree(
        protocol["repository"]["commit"], protocol["corpus_boundary"]["allowed_path_prefixes"]
    )
    discovered = constructor.selector.discover_candidate_paths((entry.path for entry in entries), protocol)
    ledger_paths = [item["path"] for item in state["ledger"]["candidates"]]
    assert len(discovered) == 81
    assert ledger_paths == discovered
    assert discovered == constructor.selector.discover_candidate_paths(reversed([entry.path for entry in entries]), protocol)
    assert all(constructor.selector.path_allowed(path, protocol) for path in discovered)
    assert not constructor.selector.path_allowed("docs/../README.md", protocol)
    assert not constructor.selector.path_allowed("investigations/context-scaling-vs-explicit-abstraction/README.md", protocol)
    assert not constructor.selector.path_allowed("investigations/other/artifacts/source.md", protocol)


def test_every_candidate_blob_and_verbatim_unit_is_bound_to_the_pinned_tree(state):
    snapshot = constructor.GitSnapshot()
    commit = state["protocol"]["repository"]["commit"]
    tree = {entry.path: entry for entry in snapshot.tree(commit, state["protocol"]["corpus_boundary"]["allowed_path_prefixes"])}
    for candidate in state["records"]:
        raw = snapshot.blob(commit, candidate["path"])
        assert constructor.git_blob_id(raw) == tree[candidate["path"]].object_id
        assert hashlib.sha256(raw).hexdigest() == candidate["blob_sha256"]
        assert candidate["content_utf8"].encode("utf-8") == raw
        for index, unit in enumerate(candidate["units"], start=1):
            assert unit["id"] == f"U{index:03d}"
            unit_bytes = raw[unit["start_byte"] : unit["end_byte"]]
            assert unit_bytes.decode("utf-8") == unit["content"]
            assert hashlib.sha256(unit_bytes).hexdigest() == unit["sha256"]


def test_prompt_and_tokenizer_accounting_are_loaded_from_the_frozen_revision(state, tmp_path, monkeypatch):
    poisoned = tmp_path / "prompt-bindings.json"
    poisoned.write_text('{"altered":true}\n')
    monkeypatch.setattr(constructor.selector, "PROMPT_BINDINGS_PATH", poisoned)
    _, _, bindings, binding_bytes, _ = constructor.frozen_inputs(constructor.GitSnapshot())
    assert bindings == state["bindings"]
    assert hashlib.sha256(binding_bytes).hexdigest() == state["bindings_sha256"]
    assert bindings["tokenizer"] == {
        "name": "o200k_base",
        "package": "tiktoken==0.9.0",
        "encoding": "UTF-8 without normalization",
    }
    eligible = next(record for record in state["records"] if record["path"] == EXPECTED_ELIGIBLE[0])
    assert eligible["token_accounting"]["condition_counts"] == constructor.selector.candidate_token_counts(
        eligible, bindings
    )


def test_frozen_selection_fails_closed_with_only_four_eligible_documents(state):
    eligible = [item["path"] for item in state["ledger"]["candidates"] if item["status"] == "ELIGIBLE"]
    assert eligible == EXPECTED_ELIGIBLE
    assert state["selection"]["selection_result"] == "NULL"
    assert state["selection"]["selected_paths"] == []
    assert state["selection"]["assignments"] == {package_id: None for package_id in constructor.PACKAGE_IDS}
    rejected = [item for item in state["ledger"]["candidates"] if item["status"] == "INELIGIBLE"]
    assert len(rejected) == 77
    assert all(item["reasons"] for item in rejected)


def test_duplicate_prevention_and_first_occurrence_rule_are_deterministic(state):
    eligible = [record for record in state["records"] if record["path"] in EXPECTED_ELIGIBLE]
    normalized_hashes = {
        hashlib.sha256(constructor.selector.normalized_document(record["content_utf8"]).encode()).hexdigest()
        for record in eligible
    }
    assert len(normalized_hashes) == len(eligible)
    for index, first in enumerate(eligible):
        for second in eligible[index + 1 :]:
            assert not constructor.selector.substantial_overlap(first["content_utf8"], second["content_utf8"], state["protocol"])


def test_changed_pinned_blob_fails_closed():
    class TamperedSnapshot(constructor.GitSnapshot):
        def blob(self, commit, path):
            value = super().blob(commit, path)
            if commit == "ba18a99ab6276948aebf74f4240e5de75a30d62d" and path == EXPECTED_ELIGIBLE[0]:
                return value + b"tampered"
            return value

    with pytest.raises(ValueError, match="pinned blob object mismatch"):
        constructor.enumerate_records(TamperedSnapshot())


def test_null_selection_writes_no_packages_and_does_not_modify_execution_registry(rendered):
    assert not any(path.name in {f"SP{index:02d}.json" for index in range(1, 9)} for path in rendered)
    assert constructor.EXECUTION_REGISTRY_PATH not in rendered
    frozen_registry = constructor.GitSnapshot().blob(
        "ba18a99ab6276948aebf74f4240e5de75a30d62d",
        "investigations/context-scaling-vs-explicit-abstraction/artifacts/execution-package-v1/source-package-registry.json",
    )
    assert constructor.EXECUTION_REGISTRY_PATH.read_bytes() == frozen_registry
    selection = json.loads(rendered[constructor.SELECTION_PATH])
    assert selection["selection_result"] == "NULL"
    assert selection["construction_status"] == "NOT_STARTED"
    assert selection["eligible_paths"] == EXPECTED_ELIGIBLE


def test_committed_artifacts_are_complete_hashed_and_byte_reproducible(rendered):
    committed = constructor.committed_artifacts()
    assert committed == rendered
    assert constructor.validate_artifacts(committed)
    assert constructor.render_artifacts() == rendered


def test_changed_or_incomplete_artifacts_fail_closed(rendered):
    changed = dict(rendered)
    changed[constructor.LEDGER_PATH] += b"\n"
    assert not constructor.validate_artifacts(changed)

    incomplete = dict(rendered)
    del incomplete[constructor.SELECTION_PATH]
    assert not constructor.validate_artifacts(incomplete)

    changed_manifest = dict(rendered)
    manifest = json.loads(changed_manifest[constructor.MANIFEST_PATH])
    manifest["governed_files"].pop(str(constructor.SELECTION_PATH.relative_to(ROOT)))
    changed_manifest[constructor.MANIFEST_PATH] = constructor.pretty_bytes(manifest)
    assert not constructor.validate_artifacts(changed_manifest)
