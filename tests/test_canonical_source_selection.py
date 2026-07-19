import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = (
    ROOT / "investigations/context-scaling-vs-explicit-abstraction/artifacts/canonical-source-packages-v1"
)
MODULE_PATH = ARTIFACT_DIR / "canonical_source_selector.py"
SPEC = importlib.util.spec_from_file_location("canonical_source_selector", MODULE_PATH)
selector = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = selector
SPEC.loader.exec_module(selector)

PROTOCOL = selector.load_protocol()
BINDINGS = selector.load_bindings()
COUNTER = lambda text: len(text.split())


def make_candidate(path, seed):
    unit_contents = []
    for index in range(1, 17):
        unit_contents.append(
            " ".join(
                [
                    seed,
                    f"unit{index:02d}",
                    "human",
                    "authored",
                    "substantive",
                    "source",
                    "document",
                    "explains",
                    "structural",
                    "constraints",
                    "causal",
                    "relations",
                    "applicability",
                    "limitations",
                    "evidence",
                    "provenance",
                    "mechanism",
                    "boundary",
                    "system",
                    "analysis",
                    "method",
                    "example",
                    "reasoning",
                    "conclusion",
                ]
            )
        )
    content = "\n\n".join(unit_contents)
    raw = content.encode()
    units = []
    cursor = 0
    for index, unit_content in enumerate(unit_contents, start=1):
        unit_bytes = unit_content.encode()
        start = raw.index(unit_bytes, cursor)
        end = start + len(unit_bytes)
        units.append(
            {
                "id": f"U{index:03d}",
                "start_byte": start,
                "end_byte": end,
                "content": unit_content,
                "sha256": hashlib.sha256(unit_bytes).hexdigest(),
            }
        )
        cursor = end
    candidate = {
        "path": path,
        "commit": PROTOCOL["repository"]["commit"],
        "stable_locator": PROTOCOL["eligibility"]["stable_binding"]["stable_locator_template"].format(
            commit=PROTOCOL["repository"]["commit"], path=path
        ),
        "content_utf8": content,
        "blob_sha256": hashlib.sha256(raw).hexdigest(),
        "document_role": "SUBSTANTIVE_SOURCE",
        "provenance": {
            "authorship_classification": "HUMAN_AUTHORED",
            "authorship_evidence": [f"synthetic provenance evidence for {path}"],
            "generated": False,
            "provenance_clear": True,
            "derived_from": [],
        },
        "units": units,
        "token_accounting": {
            "tokenizer_name": "o200k_base",
            "tokenizer_package": "tiktoken==0.9.0",
            "condition_counts": {},
            "truncation": False,
            "compression": False,
            "substitution": False,
        },
        "leakage": {
            "contains_target_tasks": False,
            "contains_answer_keys": False,
            "contains_scope_rubrics": False,
            "contains_prior_experiment_outputs": False,
            "contains_experiment_specific_instructions": False,
            "selected_after_target_performance": False,
        },
    }
    candidate["token_accounting"]["condition_counts"] = selector.candidate_token_counts(
        candidate, BINDINGS, COUNTER
    )
    return candidate


def candidates(count, prefix="docs/source"):
    return [make_candidate(f"{prefix}-{index:02d}.md", f"seed{index:02d}") for index in range(1, count + 1)]


def test_option_b_protocol_is_frozen_without_executing_selection_or_construction():
    assert selector.validate_protocol(PROTOCOL)
    assert PROTOCOL["repository"] == {
        "name_with_owner": "joselunasrt8-creator/architecturalboundary-research",
        "remote": "https://github.com/joselunasrt8-creator/architecturalboundary-research.git",
        "ref_type": "commit",
        "commit": "ba18a99ab6276948aebf74f4240e5de75a30d62d",
        "retrieval_date": "2026-07-19",
    }
    assert PROTOCOL["selected_rule"] == "B"
    assert PROTOCOL["selection_execution"]["status"] == "NOT_EXECUTED"
    assert PROTOCOL["selection_execution"]["result"] == "NULL"
    assert PROTOCOL["selection_execution"]["candidate_manifest"] == []
    assert PROTOCOL["construction_status"] == "NOT_STARTED"
    assert all(value == "NULL" for value in PROTOCOL["source_packages"].values())


def test_candidate_discovery_is_restricted_and_canonically_ordered():
    paths = [
        "papers/zeta.tex",
        "docs/beta.md",
        "docs/alpha.md",
        "investigations/other-study/protocol.md",
        "investigations/other-study/artifacts/generated.md",
        "investigations/other-study/dataset/records.md",
        "investigations/context-scaling-vs-explicit-abstraction/preregistration.md",
        "docs/generated.fixture.md",
        "README.md",
        "docs/code.py",
    ]
    assert selector.discover_candidate_paths(paths, PROTOCOL) == [
        "docs/alpha.md",
        "docs/beta.md",
        "investigations/other-study/protocol.md",
        "papers/zeta.tex",
    ]
    assert selector.discover_candidate_paths(reversed(paths), PROTOCOL) == selector.discover_candidate_paths(
        paths, PROTOCOL
    )


def test_duplicate_documents_are_rejected_and_cannot_displace_canonical_first_occurrence():
    records = candidates(8)
    duplicate = copy.deepcopy(records[0])
    duplicate["path"] = "docs/source-01z-copy.md"
    duplicate["stable_locator"] = PROTOCOL["eligibility"]["stable_binding"]["stable_locator_template"].format(
        commit=PROTOCOL["repository"]["commit"], path=duplicate["path"]
    )
    records.insert(1, duplicate)
    result = selector.select_candidates(records, PROTOCOL, BINDINGS, COUNTER)
    review = {item["path"]: item for item in result["reviewed_candidates"]}
    assert review["docs/source-01z-copy.md"] == {
        "path": "docs/source-01z-copy.md",
        "status": "INELIGIBLE",
        "reasons": ["EXACT_DUPLICATE"],
    }
    assert result["selection_result"] == "READY"
    assert result["assignments"]["SP01"] == "docs/source-01.md"
    assert "docs/source-01z-copy.md" not in result["selected_paths"]


def test_ineligible_document_cannot_be_replaced_from_outside_frozen_corpus():
    records = candidates(7)
    ineligible = make_candidate("docs/source-08.md", "seed08")
    ineligible["provenance"]["generated"] = True
    outside = make_candidate("releases/convenient-source.md", "outside")
    result = selector.select_candidates(records + [ineligible, outside], PROTOCOL, BINDINGS, COUNTER)
    assert result["selection_result"] == "NULL"
    assert result["selected_paths"] == []
    assert all(value is None for value in result["assignments"].values())
    review = {item["path"]: item for item in result["reviewed_candidates"]}
    assert "INELIGIBLE_PROVENANCE" in review["docs/source-08.md"]["reasons"]
    assert "OUTSIDE_FROZEN_CORPUS" in review["releases/convenient-source.md"]["reasons"]


def test_fewer_than_eight_eligible_documents_returns_null():
    result = selector.select_candidates(candidates(7), PROTOCOL, BINDINGS, COUNTER)
    assert result["selection_result"] == "NULL"
    assert result["selected_paths"] == []
    assert all(value is None for value in result["assignments"].values())
    assert result["construction_status"] == "NOT_STARTED"


def test_exactly_first_eight_eligible_candidates_are_selected_and_assigned_in_order():
    records = list(reversed(candidates(10)))
    result = selector.select_candidates(records, PROTOCOL, BINDINGS, COUNTER)
    expected = [f"docs/source-{index:02d}.md" for index in range(1, 9)]
    assert result["selection_result"] == "READY"
    assert result["selected_paths"] == expected
    assert result["assignments"] == {
        f"SP{index:02d}": path for index, path in enumerate(expected, start=1)
    }
    assert result["construction_status"] == "NOT_STARTED"


def test_same_commit_and_candidate_records_produce_byte_identical_results():
    records = candidates(9)
    first = selector.selection_bytes(selector.select_candidates(records, PROTOCOL, BINDINGS, COUNTER))
    second = selector.selection_bytes(selector.select_candidates(copy.deepcopy(records), PROTOCOL, BINDINGS, COUNTER))
    assert first == second
    assert first.endswith(b"\n")
    assert json.loads(first)["corpus_commit"] == PROTOCOL["repository"]["commit"]
