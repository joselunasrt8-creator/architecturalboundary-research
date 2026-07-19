import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "investigations/context-scaling-vs-explicit-abstraction/artifacts/canonical-source-packages-v1"
    / "source-selection-freeze.json"
)
EXECUTION_REGISTRY = (
    ROOT
    / "investigations/context-scaling-vs-explicit-abstraction/artifacts/execution-package-v1"
    / "source-package-registry.json"
)
PACKAGE_IDS = [f"SP{index:02d}" for index in range(1, 9)]


def load(path):
    return json.loads(path.read_bytes())


def test_source_selection_is_explicitly_blocked_before_package_construction():
    freeze = load(ARTIFACT)
    assert freeze["schema_version"] == "1"
    assert freeze["issue"] == 96
    assert freeze["authorization"] == "AUTHORIZED"
    assert freeze["selection_status"] == "BLOCKED"
    assert freeze["selected_rule"] is None
    assert freeze["construction_status"] == "NOT_STARTED"
    assert freeze["source_packages"] == {package_id: "NULL" for package_id in PACKAGE_IDS}


def test_option_a_contains_no_inferred_source_identity():
    option = load(ARTIFACT)["allowed_rules"]["A"]
    assert option["status"] == "UNSELECTED"
    assert option["required_document_count"] == 8
    assert option["documents"] == []
    assert set(option["required_fields_per_document"]) == {
        "canonical_order",
        "canonical_source_identifier",
        "title",
        "stable_locator",
        "version_or_commit",
        "retrieval_date",
        "document_sha256",
    }


def test_option_b_is_fail_closed_until_every_protocol_field_is_frozen():
    option = load(ARTIFACT)["allowed_rules"]["B"]
    assert option["status"] == "UNSELECTED"
    assert option["substitution_rule"] == "PROHIBITED"
    assert option["candidate_manifest"] == []
    assert option["inclusion_rules"] == []
    assert option["exclusion_rules"] == []
    assert option["minimum_document_requirements"] == []
    for field in (
        "corpus_boundary",
        "retrieval_date",
        "canonical_ordering",
        "duplicate_handling",
        "selection_rule",
        "stable_locator_rule",
        "version_binding_rule",
        "fewer_than_eight_rule",
    ):
        assert option[field] is None


def test_all_out_of_scope_actions_are_prohibited():
    prohibitions = load(ARTIFACT)["prohibitions"]
    assert set(prohibitions) == {
        "repository_inference",
        "convenience_substitution",
        "target_construction",
        "model_invocation",
        "abstraction_generation",
        "experiment_execution",
        "empirical_evidence_collection",
    }
    assert all(prohibitions.values())


def test_merged_execution_registry_remains_honestly_null():
    registry = load(EXECUTION_REGISTRY)
    assert [package["id"] for package in registry["packages"]] == PACKAGE_IDS
    assert all(package["status"] == "NULL" for package in registry["packages"])
    assert all(package["canonical_source_reference"] is None for package in registry["packages"])
    assert all(unit["content"] is None for package in registry["packages"] for unit in package["units"])
