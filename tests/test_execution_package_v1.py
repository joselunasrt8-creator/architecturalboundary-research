import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "investigations/context-scaling-vs-explicit-abstraction/artifacts/execution-package-v1/execution_package.py"
SPEC = importlib.util.spec_from_file_location("execution_package_v1", MODULE_PATH)
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


def json_bytes(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2).encode() + b"\n"


def recalculate_source(package, bindings):
    for condition in module.CONDITIONS:
        package["token_accounting"]["condition_counts"][condition] = module.token_count(
            module._source_render(package, condition, bindings)
        )
    package["source_hashes"] = [unit["sha256"] for unit in package["units"]]
    package["package_hash"] = module.sha256({key: value for key, value in package.items() if key != "package_hash"})


def recalculate_target(target):
    target["target_record_hash"] = module.sha256({key: value for key, value in target.items() if key != "target_record_hash"})


def calculate_target_accounting(target, bindings, stage1):
    accounting = {}
    for condition in module.CONDITIONS:
        rendered = module._target_render(target, condition, bindings, stage1)
        accounting[condition] = {
            "retention_instruction_sha256": hashlib.sha256(bindings["retention_instructions"][condition].encode()).hexdigest(),
            "target_prompt_sha256": hashlib.sha256(target["target_prompt"].encode()).hexdigest(),
            "rendered_package_sha256": module.sha256(rendered.encode()),
            "token_count": module.token_count(rendered),
            "token_ceiling": module.TOKEN_CEILINGS[condition],
            "truncation": False,
            "compression": False,
            "substitution": False,
        }
    return accounting


def refresh_manifest(files, preregistration):
    manifest = {
        "schema_version": "1",
        "algorithm": "sha256",
        "files": [
            {"path": name, "sha256": module.sha256(files[name])}
            for name in sorted(module.PACKAGE_FILES)
        ],
        "external_files": [{"path": module.PREREGISTRATION_PATH, "sha256": module.sha256(preregistration)}],
    }
    files[module.MANIFEST_NAME] = json_bytes(manifest)


def install_anchor(files):
    parent = "1" * 40
    introduction = "2" * 40
    anchor = {
        "schema_version": "1",
        "algorithm": "sha256",
        "manifest_path": module.MANIFEST_NAME,
        "manifest_sha256": module.sha256(files[module.MANIFEST_NAME]),
        "manifest_commit": parent,
    }
    anchor_bytes = module.canonical_bytes(anchor) + b"\n"
    files[module.MANIFEST_ANCHOR_NAME] = anchor_bytes
    return {
        "introduction_commit": introduction,
        "parent_commit": parent,
        "frozen_anchor_bytes": anchor_bytes,
        "frozen_manifest_bytes": files[module.MANIFEST_NAME],
        "commit_is_ancestor": True,
    }


def freeze_fixture(fixture):
    refresh_manifest(fixture["files"], fixture["preregistration"])
    fixture["anchor_evidence"] = install_anchor(fixture["files"])


def replace_json(files, name, value, preregistration, *, refresh=True):
    files[name] = json_bytes(value)
    if refresh:
        refresh_manifest(files, preregistration)


@pytest.fixture(scope="module")
def valid_fixture():
    bindings = copy.deepcopy(module.EXPECTED_BINDINGS)
    bindings["scorer_image_sha256"] = "a" * 64
    packages = []
    for package_id in module.PACKAGE_IDS:
        units = []
        for unit_id in module.UNIT_IDS:
            content = f"Synthetic eligible content for {package_id} {unit_id}."
            units.append(
                {
                    "id": unit_id,
                    "status": "ELIGIBLE",
                    "content": content,
                    "sha256": hashlib.sha256(content.encode()).hexdigest(),
                    "source_reference": f"synthetic://{package_id}/{unit_id}",
                }
            )
        package = {
            "id": package_id,
            "status": "READY",
            "canonical_source_reference": f"synthetic-source-{package_id}",
            "immutable_locator": f"synthetic://source/{package_id}@v1",
            "document_order": "ascending synthetic document and block order",
            "unit_boundary_method": "synthetic paragraph boundary fixture",
            "unit_boundary_version": "1",
            "units": units,
            "source_hashes": [],
            "package_hash": "0" * 64,
            "duplicate_decisions": [],
            "exclusion_decisions": [],
            "duplicate_eligible_content_absent": True,
            "subsets": {"N=8": module.UNIT_IDS[:8], "M=16": module.UNIT_IDS},
            "token_accounting": {
                "tokenizer": "o200k_base",
                "package": "tiktoken==0.9.0",
                "condition_counts": {condition: 0 for condition in module.CONDITIONS},
                "condition_ceilings": module.TOKEN_CEILINGS,
                "truncation": False,
                "compression": False,
                "substitution": False,
            },
            "provenance": {"kind": "synthetic-test-fixture", "canonical": True},
        }
        recalculate_source(package, bindings)
        packages.append(package)
    sources = {
        "schema_version": "1",
        "package_version": module.PACKAGE_VERSION,
        "preregistration_path": module.PREREGISTRATION_PATH,
        "preregistration_commit": module.PREREGISTRATION_COMMIT,
        "preregistration_sha256": module.PREREGISTRATION_SHA256,
        "unitization": "Synthetic deterministic test unitization matching the registered ordering contract.",
        "packages": packages,
    }
    stage1 = {}
    for package_id in module.PACKAGE_IDS:
        stage1[package_id] = {}
        for condition in module.CONDITIONS:
            response = f"Synthetic retained source response for {package_id} {condition}."
            abstraction = (
                f"Synthetic retained abstraction for {package_id} {condition}." if condition in {"C2", "C4"} else None
            )
            retained = (
                [
                    {
                        "id": f"abstraction-{package_id}-{condition}",
                        "content": abstraction,
                        "sha256": hashlib.sha256(abstraction.encode()).hexdigest(),
                    }
                ]
                if abstraction is not None
                else []
            )
            stage1[package_id][condition] = {
                "raw_response_sha256": hashlib.sha256(
                    (response if abstraction is None else response + "\nABSTRACTION:\n" + abstraction).encode()
                ).hexdigest(),
                "source_response": response,
                "source_response_sha256": hashlib.sha256(response.encode()).hexdigest(),
                "abstraction_artifact": abstraction,
                "abstraction_artifact_sha256": hashlib.sha256(abstraction.encode()).hexdigest() if abstraction else None,
                "citation_identifiers": [f"{package_id}:U001", f"{package_id}:U002"],
                "retained_objects": retained,
                "stage1_output_hash": "0" * 64,
            }
            artifact = stage1[package_id][condition]
            artifact["stage1_output_hash"] = module.sha256(
                {key: value for key, value in artifact.items() if key != "stage1_output_hash"}
            )
    key_records = []
    rubric_records = []
    targets_list = []
    for index, (package_id, family) in enumerate(
        ((package, family) for package in module.PACKAGE_IDS for family in module.FAMILIES), start=1
    ):
        key = {"required_literals": [f"answer-{index:02d}"], "forbidden_literals": [f"incorrect-{index:02d}"]}
        rubric = {
            "relation_literals": [f"relation-{index:02d}"],
            "required_applicability_literals": [f"applicable-{index:02d}"],
            "forbidden_applicability_literals": [f"inapplicable-{index:02d}"],
        }
        key_records.append(key)
        rubric_records.append(rubric)
        target = {
            "id": f"T{index:02d}",
            "package_id": package_id,
            "family": family,
            "status": "ELIGIBLE",
            "target_prompt": f"Synthetic unseen target task {index:02d} for {family}.",
            "answer_key_sha256": module.sha256(key),
            "scope_rubric_sha256": module.sha256(rubric),
            "required_literals": key["required_literals"],
            "forbidden_literals": key["forbidden_literals"],
            "relation_literals": rubric["relation_literals"],
            "applicability_literals": rubric["required_applicability_literals"],
            "transfer_distance": {
                "domain": True,
                "surface_representation": True,
                "entities_vocabulary": True,
                "task_objective": False,
                "causal_structural_arrangement": False,
            },
            "overlap_checks": {
                "no_source_overlap": True,
                "no_answer_leakage": True,
                "no_rubric_leakage": True,
            },
            "eligibility_rationale": "Deterministic synthetic positive fixture.",
            "eligibility_determination": "ELIGIBLE",
            "target_record_hash": "0" * 64,
        }
        recalculate_target(target)
        targets_list.append(target)
    target_accounting = {
        target["id"]: calculate_target_accounting(target, bindings, stage1) for target in targets_list
    }
    targets = {
        "schema_version": "1",
        "package_version": module.PACKAGE_VERSION,
        "selection_rule": "Synthetic IDs sorted; first eligible target per family.",
        "expected_target_count": 24,
        "targets": targets_list,
        "stage1_outputs": stage1,
        "target_package_accounting": target_accounting,
        "status": "READY",
        "reason": "Complete deterministic synthetic fixture only.",
    }
    keys = {
        "schema_version": "1",
        "package_version": module.PACKAGE_VERSION,
        "status": "READY",
        "reason": "Complete deterministic synthetic fixture only.",
        "records": key_records,
    }
    rubrics = {
        "schema_version": "1",
        "package_version": module.PACKAGE_VERSION,
        "status": "READY",
        "reason": "Complete deterministic synthetic fixture only.",
        "records": rubric_records,
    }
    blocks = []
    for package_id in module.PACKAGE_IDS:
        for family in module.FAMILIES:
            _, digest, _, permutation = module.condition_permutation(package_id, family)
            blocks.append(
                {
                    "package_id": package_id,
                    "target_family": family,
                    "digest_sha256": digest,
                    "execution_conditions": permutation,
                }
            )
    order = {
        "schema_version": "1",
        "seed": module.SEED,
        "canonical_source_order": [
            {"package_id": package, "condition_id": condition}
            for package in module.PACKAGE_IDS
            for condition in module.CONDITIONS
        ],
        "canonical_target_order": module.canonical_analysis_order(targets),
        "target_condition_blocks": blocks,
        "verification_hash": module.sha256(blocks),
        "status": "READY",
    }
    files = {
        "README.md": b"Synthetic isolated execution-package fixture.\n",
        "source-package-registry.json": json_bytes(sources),
        "target-registry.json": json_bytes(targets),
        "prompt-bindings.json": json_bytes(bindings),
        "condition-order.json": json_bytes(order),
        "answer-key-registry.json": json_bytes(keys),
        "scope-rubric-registry.json": json_bytes(rubrics),
        "audit-manifest-schema.json": json_bytes(module.read_json("audit-manifest-schema.json")),
        "execution-readiness-report.md": b"Synthetic readiness fixture; no execution occurred.\n",
        "evaluator-specification.md": b"Synthetic fixture uses the frozen offline evaluator.\n",
        "execution_package.py": b"import hashlib\n# Offline synthetic validator fixture; no invocation code.\n",
    }
    preregistration = module.PREREGISTRATION.read_bytes()
    refresh_manifest(files, preregistration)
    anchor_evidence = install_anchor(files)
    return {"files": files, "preregistration": preregistration, "anchor_evidence": anchor_evidence}


def clone_fixture(valid_fixture):
    return copy.deepcopy(valid_fixture)


def readiness(fixture, **overrides):
    preregistration = overrides.pop("preregistration", fixture["preregistration"])
    pinned = overrides.pop("pinned", fixture["preregistration"])
    merged = overrides.pop("merged", True)
    anchor_evidence = overrides.pop("anchor_evidence", fixture["anchor_evidence"])
    assert not overrides
    return module.readiness_from_bytes(
        fixture["files"], preregistration, pinned, commit_is_merged=merged, anchor_evidence=anchor_evidence
    )


def test_complete_synthetic_fixture_is_deterministically_ready(valid_fixture):
    first = readiness(valid_fixture)
    second = readiness(valid_fixture)
    assert first == second
    assert first["outcome"] == "READY"
    assert first["source_stage"] == "READY"
    assert first["target_stage"] == "READY"
    assert all(first["checks"].values())


def test_source_stage_ready_does_not_require_future_stage1_outputs(valid_fixture):
    fixture = clone_fixture(valid_fixture)
    targets = json.loads(fixture["files"]["target-registry.json"])
    targets["stage1_outputs"] = None
    targets["target_package_accounting"] = None
    fixture["files"]["target-registry.json"] = json_bytes(targets)
    freeze_fixture(fixture)
    result = readiness(fixture)
    assert result["outcome"] == "NULL"
    assert result["source_stage"] == "READY"
    assert result["target_stage"] == "NULL"
    assert result["checks"]["SOURCE_STAGE_READY"] is True
    assert result["checks"]["STAGE1_OUTPUTS_VALID"] is False


def test_ci_pins_python_supported_by_preregistered_tokenizer():
    workflow = (ROOT / ".github/workflows/validate.yml").read_text()
    requirements = (ROOT / "requirements.txt").read_text().splitlines()
    assert 'python-version: "3.13"' in workflow
    assert 'python-version: "3.x"' not in workflow
    assert "tiktoken==0.9.0" in requirements
    assert module.EXPECTED_BINDINGS["tokenizer"]["package"] == "tiktoken==0.9.0"


def test_committed_package_remains_deterministically_null():
    first = module.readiness()
    second = module.readiness()
    assert first == second
    assert first["outcome"] == "NULL"
    assert first["source_stage"] == "NULL"
    assert first["target_stage"] == "NULL"
    assert first["checks"]["SOURCE_INPUT_BUDGET_VALID"] is False


def test_duplicate_package_id_returns_null(valid_fixture):
    fixture = clone_fixture(valid_fixture)
    sources = json.loads(fixture["files"]["source-package-registry.json"])
    sources["packages"][1]["id"] = "SP01"
    replace_json(fixture["files"], "source-package-registry.json", sources, fixture["preregistration"])
    assert readiness(fixture)["outcome"] == "NULL"


def test_missing_sp08_returns_null(valid_fixture):
    fixture = clone_fixture(valid_fixture)
    sources = json.loads(fixture["files"]["source-package-registry.json"])
    sources["packages"].pop()
    replace_json(fixture["files"], "source-package-registry.json", sources, fixture["preregistration"])
    assert readiness(fixture)["outcome"] == "NULL"


def test_duplicate_source_units_return_null(valid_fixture):
    fixture = clone_fixture(valid_fixture)
    sources = json.loads(fixture["files"]["source-package-registry.json"])
    sources["packages"][0]["units"][1] = copy.deepcopy(sources["packages"][0]["units"][0])
    replace_json(fixture["files"], "source-package-registry.json", sources, fixture["preregistration"])
    assert readiness(fixture)["outcome"] == "NULL"


def test_duplicate_source_content_across_packages_returns_null(valid_fixture):
    fixture = clone_fixture(valid_fixture)
    sources = json.loads(fixture["files"]["source-package-registry.json"])
    first = sources["packages"][0]["units"][0]
    duplicate = sources["packages"][1]["units"][0]
    duplicate["content"] = first["content"].upper()
    duplicate["sha256"] = hashlib.sha256(duplicate["content"].encode()).hexdigest()
    recalculate_source(sources["packages"][1], json.loads(fixture["files"]["prompt-bindings.json"]))
    replace_json(fixture["files"], "source-package-registry.json", sources, fixture["preregistration"])
    result = readiness(fixture)
    assert result["checks"]["EIGHT_SOURCE_PACKAGES"] is False
    assert result["outcome"] == "NULL"


def test_malformed_source_hash_returns_null(valid_fixture):
    fixture = clone_fixture(valid_fixture)
    sources = json.loads(fixture["files"]["source-package-registry.json"])
    sources["packages"][0]["units"][0]["sha256"] = "not-a-hash"
    replace_json(fixture["files"], "source-package-registry.json", sources, fixture["preregistration"])
    assert readiness(fixture)["outcome"] == "NULL"


def test_actual_token_overflow_returns_null_without_hard_coding(valid_fixture):
    fixture = clone_fixture(valid_fixture)
    bindings = json.loads(fixture["files"]["prompt-bindings.json"])
    sources = json.loads(fixture["files"]["source-package-registry.json"])
    package = sources["packages"][0]
    package["units"][0]["content"] = "overflow " * 5000
    package["units"][0]["sha256"] = hashlib.sha256(package["units"][0]["content"].encode()).hexdigest()
    recalculate_source(package, bindings)
    replace_json(fixture["files"], "source-package-registry.json", sources, fixture["preregistration"])
    result = readiness(fixture)
    assert result["outcome"] == "NULL"
    assert result["checks"]["EIGHT_SOURCE_PACKAGES"] is True
    assert result["checks"]["SOURCE_INPUT_BUDGET_VALID"] is False


def test_duplicate_target_id_returns_null(valid_fixture):
    fixture = clone_fixture(valid_fixture)
    targets = json.loads(fixture["files"]["target-registry.json"])
    targets["targets"][1]["id"] = "T01"
    replace_json(fixture["files"], "target-registry.json", targets, fixture["preregistration"])
    assert readiness(fixture)["outcome"] == "NULL"


def test_missing_target_family_returns_null(valid_fixture):
    fixture = clone_fixture(valid_fixture)
    targets = json.loads(fixture["files"]["target-registry.json"])
    targets["targets"][2]["family"] = "structural_diagnosis"
    replace_json(fixture["files"], "target-registry.json", targets, fixture["preregistration"])
    assert readiness(fixture)["outcome"] == "NULL"


def test_malformed_answer_key_hash_returns_null(valid_fixture):
    fixture = clone_fixture(valid_fixture)
    targets = json.loads(fixture["files"]["target-registry.json"])
    targets["targets"][0]["answer_key_sha256"] = []
    replace_json(fixture["files"], "target-registry.json", targets, fixture["preregistration"])
    assert readiness(fixture)["outcome"] == "NULL"


def test_malformed_scope_rubric_returns_null(valid_fixture):
    fixture = clone_fixture(valid_fixture)
    rubrics = json.loads(fixture["files"]["scope-rubric-registry.json"])
    rubrics["records"][0]["relation_literals"] = []
    replace_json(fixture["files"], "scope-rubric-registry.json", rubrics, fixture["preregistration"])
    assert readiness(fixture)["outcome"] == "NULL"


@pytest.mark.parametrize(
    ("key", "rubric"),
    [
        (
            {"required_literals": ["Alpha"], "forbidden_literals": ["  alpha "]},
            {
                "relation_literals": ["relation"],
                "required_applicability_literals": ["applicable"],
                "forbidden_applicability_literals": [],
            },
        ),
        (
            {"required_literals": ["answer"], "forbidden_literals": []},
            {
                "relation_literals": ["relation"],
                "required_applicability_literals": ["ＡＰＰ"],
                "forbidden_applicability_literals": ["app"],
            },
        ),
        (
            {"required_literals": ["answer"], "forbidden_literals": []},
            {
                "relation_literals": ["blocked"],
                "required_applicability_literals": ["applicable"],
                "forbidden_applicability_literals": ["BLOCKED"],
            },
        ),
        (
            {"required_literals": ["forbidden scope"], "forbidden_literals": []},
            {
                "relation_literals": ["relation"],
                "required_applicability_literals": ["applicable"],
                "forbidden_applicability_literals": ["forbidden\t scope"],
            },
        ),
    ],
)
def test_normalized_literal_conflicts_fail_before_evaluation(key, rubric):
    target = {"id": "T01", "answer_key_sha256": module.sha256(key), "scope_rubric_sha256": module.sha256(rubric)}
    with pytest.raises(ValueError):
        module.evaluate(b"answer relation applicable", target, key, rubric)


def test_altered_preregistration_returns_null(valid_fixture):
    fixture = clone_fixture(valid_fixture)
    altered = fixture["preregistration"] + b"\naltered\n"
    refresh_manifest(fixture["files"], altered)
    result = readiness(fixture, preregistration=altered, pinned=fixture["preregistration"])
    assert result["outcome"] == "NULL"
    assert result["checks"]["PREREGISTRATION_MATCH"] is False


def test_incorrect_preregistration_commit_returns_null(valid_fixture):
    fixture = clone_fixture(valid_fixture)
    sources = json.loads(fixture["files"]["source-package-registry.json"])
    sources["preregistration_commit"] = "0" * 40
    replace_json(fixture["files"], "source-package-registry.json", sources, fixture["preregistration"])
    assert readiness(fixture)["checks"]["PREREGISTRATION_MATCH"] is False


def test_altered_prompts_return_null_even_with_reproduced_manifest(valid_fixture):
    fixture = clone_fixture(valid_fixture)
    bindings = json.loads(fixture["files"]["prompt-bindings.json"])
    bindings["system_prompt"] += " altered"
    bindings["hashes"]["system_prompt"] = hashlib.sha256(bindings["system_prompt"].encode()).hexdigest()
    replace_json(fixture["files"], "prompt-bindings.json", bindings, fixture["preregistration"])
    result = readiness(fixture)
    assert result["outcome"] == "NULL"
    assert result["checks"]["PROMPTS_MATCH"] is False


def test_incorrect_condition_order_returns_null(valid_fixture):
    fixture = clone_fixture(valid_fixture)
    order = json.loads(fixture["files"]["condition-order.json"])
    order["target_condition_blocks"][0]["execution_conditions"] = ["C1", "C2", "C3", "C4"]
    order["verification_hash"] = module.sha256(order["target_condition_blocks"])
    replace_json(fixture["files"], "condition-order.json", order, fixture["preregistration"])
    assert readiness(fixture)["checks"]["CONDITION_ORDER_VALID"] is False


def test_incomplete_manifest_returns_null(valid_fixture):
    fixture = clone_fixture(valid_fixture)
    manifest = json.loads(fixture["files"]["hash-manifest.json"])
    manifest["files"] = [item for item in manifest["files"] if item["path"] != "prompt-bindings.json"]
    fixture["files"]["hash-manifest.json"] = json_bytes(manifest)
    result = readiness(fixture)
    assert result["outcome"] == "NULL"
    assert result["checks"]["HASHES_COMPLETE"] is False


def test_target_render_counts_target_task_and_retained_objects(valid_fixture):
    targets = json.loads(valid_fixture["files"]["target-registry.json"])
    bindings = json.loads(valid_fixture["files"]["prompt-bindings.json"])
    target = targets["targets"][0]
    rendered = module._target_render(target, "C2", bindings, targets["stage1_outputs"])
    assert target["target_prompt"] in rendered
    assert targets["stage1_outputs"]["SP01"]["C2"]["source_response"] in rendered
    assert targets["stage1_outputs"]["SP01"]["C2"]["abstraction_artifact"] in rendered
    assert "SP01:U001" in rendered


def test_target_stage_rejects_missing_c2_abstraction_and_accounting(valid_fixture):
    fixture = clone_fixture(valid_fixture)
    targets = json.loads(fixture["files"]["target-registry.json"])
    targets["stage1_outputs"]["SP01"]["C2"]["abstraction_artifact"] = None
    fixture["files"]["target-registry.json"] = json_bytes(targets)
    freeze_fixture(fixture)
    result = readiness(fixture)
    assert result["source_stage"] == "READY"
    assert result["target_stage"] == "NULL"
    assert result["checks"]["STAGE1_OUTPUTS_VALID"] is False


def source_audit_record(valid_fixture, condition="C1"):
    sources = json.loads(valid_fixture["files"]["source-package-registry.json"])
    targets = json.loads(valid_fixture["files"]["target-registry.json"])
    bindings = json.loads(valid_fixture["files"]["prompt-bindings.json"])
    package = sources["packages"][0]
    units = package["units"][: 8 if condition in {"C1", "C2"} else 16]
    zero = "0" * 64
    artifact = targets["stage1_outputs"]["SP01"][condition]
    raw_text = artifact["source_response"]
    if condition in {"C2", "C4"}:
        raw_text += "\nABSTRACTION:\n" + artifact["abstraction_artifact"]
    raw = raw_text.encode()
    request = module.canonical_source_request(package, condition, bindings)
    request_hash = module.sha256(request)
    return {
        "run_identifiers": {
            "audit_id": f"source-SP01-{condition}",
            "execution_state": "SOURCE_EXECUTION_BOUND",
            "package_id": "SP01",
            "target_id": None,
            "target_family": None,
            "condition_id": condition,
            "invocation": "source",
        },
        "hashes": {
            "package_sha256": package["package_hash"],
            "request_sha256": request_hash,
            "raw_response_sha256": module.sha256(raw),
        },
        "token_accounting": {
            "supplied_source_unit_ids": [unit["id"] for unit in units],
            "supplied_source_unit_hashes": [unit["sha256"] for unit in units],
            "retained_object_inventory": ["source_response"],
            "abstraction_slot_inventory": ["abstraction_artifact"] if condition in {"C2", "C4"} else [],
            "rendered_input_sha256": module.sha256(module._source_render(package, condition, bindings).encode()),
            "tokenizer": "tiktoken==0.9.0/o200k_base",
            "token_count": package["token_accounting"]["condition_counts"][condition],
            "token_ceiling": module.TOKEN_CEILINGS[condition],
            "budget_result": True,
            "model_output_tokens": 10,
            "source_prompt_sha256": module.EXPECTED_BINDINGS["hashes"]["source_prompt_template"],
            "target_prompt_sha256": zero,
            "package_record_sha256": package["package_hash"],
            "target_record_sha256": zero,
        },
        "model_binding": {
            "request": request,
            "request_sha256": request_hash,
            "started_at": "2026-07-19T12:00:00Z",
            "ended_at": "2026-07-19T12:00:01Z",
        },
        "response": {
            "raw_response_sha256": module.sha256(raw),
            "retained_raw_response_utf8": raw_text,
            "immutable_artifact_reference": None,
            "parsed_final_response": artifact["source_response"],
            "parsed_final_response_sha256": artifact["source_response_sha256"],
            "abstraction_artifact": artifact["abstraction_artifact"],
            "abstraction_artifact_sha256": artifact["abstraction_artifact_sha256"],
            "stage1_output_hash": artifact["stage1_output_hash"],
        },
        "evaluator": None,
        "condition_order": {"position": module.CONDITIONS.index(condition) + 1, "condition_id": condition},
        "credential_boundary": {"request_count": 1, "retry": False},
        "operator_actions": [
            {"action": "request", "recorded_at": "2026-07-19T12:00:00Z"},
            {"action": "response_retained", "recorded_at": "2026-07-19T12:00:01Z"},
            {"action": "offline_evaluation", "recorded_at": "2026-07-19T12:00:02Z"},
        ],
        "scorer_image_sha256": bindings["scorer_image_sha256"],
    }


def test_source_audit_schema_requires_no_target_material(valid_fixture):
    schema = module.read_json("audit-manifest-schema.json")
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    record = source_audit_record(valid_fixture)
    assert not list(validator.iter_errors(record))
    record["run_identifiers"]["package_id"] = 1
    assert list(validator.iter_errors(record))


def test_source_audit_semantics_bind_inventory_order_budget_and_timestamps(valid_fixture):
    sources = json.loads(valid_fixture["files"]["source-package-registry.json"])
    targets = json.loads(valid_fixture["files"]["target-registry.json"])
    bindings = json.loads(valid_fixture["files"]["prompt-bindings.json"])
    order = json.loads(valid_fixture["files"]["condition-order.json"])
    record = source_audit_record(valid_fixture, "C3")
    kwargs = {"sources": sources, "targets": targets, "bindings": bindings}
    assert module.semantic_audit_valid(record, order, **kwargs)
    missing = copy.deepcopy(record)
    missing["token_accounting"]["supplied_source_unit_ids"].pop()
    missing["token_accounting"]["supplied_source_unit_hashes"].pop()
    assert not module.semantic_audit_valid(missing, order, **kwargs)
    over = copy.deepcopy(record)
    over["token_accounting"]["token_count"] = 8193
    assert not module.semantic_audit_valid(over, order, **kwargs)
    misplaced = copy.deepcopy(record)
    misplaced["condition_order"]["position"] = 1
    assert not module.semantic_audit_valid(misplaced, order, **kwargs)
    bad_time = copy.deepcopy(record)
    bad_time["model_binding"]["ended_at"] = "2026-07-19T11:59:59Z"
    assert not module.semantic_audit_valid(bad_time, order, **kwargs)


def test_source_audit_binds_raw_parse_abstraction_and_stage1_record(valid_fixture):
    sources = json.loads(valid_fixture["files"]["source-package-registry.json"])
    targets = json.loads(valid_fixture["files"]["target-registry.json"])
    bindings = json.loads(valid_fixture["files"]["prompt-bindings.json"])
    order = json.loads(valid_fixture["files"]["condition-order.json"])
    record = source_audit_record(valid_fixture, "C2")
    kwargs = {"sources": sources, "targets": targets, "bindings": bindings}
    assert module.semantic_audit_valid(record, order, **kwargs)

    parsed = copy.deepcopy(record)
    parsed["response"]["parsed_final_response"] += " fabricated"
    parsed["response"]["parsed_final_response_sha256"] = hashlib.sha256(
        parsed["response"]["parsed_final_response"].encode()
    ).hexdigest()
    assert not module.semantic_audit_valid(parsed, order, **kwargs)

    abstraction = copy.deepcopy(record)
    abstraction["response"]["abstraction_artifact"] += " fabricated"
    abstraction["response"]["abstraction_artifact_sha256"] = hashlib.sha256(
        abstraction["response"]["abstraction_artifact"].encode()
    ).hexdigest()
    assert not module.semantic_audit_valid(abstraction, order, **kwargs)

    altered_targets = copy.deepcopy(targets)
    altered_targets["stage1_outputs"]["SP01"]["C2"]["source_response"] += " substituted"
    assert not module.semantic_audit_valid(
        record,
        order,
        sources=sources,
        targets=altered_targets,
        bindings=bindings,
    )

    fabricated_hash = copy.deepcopy(record)
    fabricated_hash["response"]["raw_response_sha256"] = "f" * 64
    fabricated_hash["hashes"]["raw_response_sha256"] = "f" * 64
    assert not module.semantic_audit_valid(fabricated_hash, order, **kwargs)


def test_source_audit_accepts_verified_immutable_response_reference(valid_fixture):
    sources = json.loads(valid_fixture["files"]["source-package-registry.json"])
    targets = json.loads(valid_fixture["files"]["target-registry.json"])
    bindings = json.loads(valid_fixture["files"]["prompt-bindings.json"])
    order = json.loads(valid_fixture["files"]["condition-order.json"])
    record = source_audit_record(valid_fixture, "C4")
    raw = record["response"]["retained_raw_response_utf8"].encode()
    record["response"]["retained_raw_response_utf8"] = None
    record["response"]["immutable_artifact_reference"] = {
        "path": "retained/source-SP01-C4.raw.txt",
        "sha256": module.sha256(raw),
    }
    assert module.semantic_audit_valid(
        record,
        order,
        sources=sources,
        targets=targets,
        bindings=bindings,
        raw_output=raw,
    )
    assert not module.semantic_audit_valid(
        record,
        order,
        sources=sources,
        targets=targets,
        bindings=bindings,
        raw_output=raw + b" altered",
    )


def test_source_audit_rejects_noncanonical_request_and_scorer_digest(valid_fixture):
    sources = json.loads(valid_fixture["files"]["source-package-registry.json"])
    targets = json.loads(valid_fixture["files"]["target-registry.json"])
    bindings = json.loads(valid_fixture["files"]["prompt-bindings.json"])
    order = json.loads(valid_fixture["files"]["condition-order.json"])
    record = source_audit_record(valid_fixture)
    kwargs = {"sources": sources, "targets": targets, "bindings": bindings}

    altered_request = copy.deepcopy(record)
    altered_request["model_binding"]["request"]["rendered_user_prompt"] += " altered"
    new_hash = module.sha256(altered_request["model_binding"]["request"])
    altered_request["model_binding"]["request_sha256"] = new_hash
    altered_request["hashes"]["request_sha256"] = new_hash
    assert not module.semantic_audit_valid(altered_request, order, **kwargs)

    scorer = copy.deepcopy(record)
    scorer["scorer_image_sha256"] = "b" * 64
    assert not module.semantic_audit_valid(scorer, order, **kwargs)


def target_audit_record(valid_fixture):
    sources = json.loads(valid_fixture["files"]["source-package-registry.json"])
    targets = json.loads(valid_fixture["files"]["target-registry.json"])
    bindings = json.loads(valid_fixture["files"]["prompt-bindings.json"])
    keys = json.loads(valid_fixture["files"]["answer-key-registry.json"])
    rubrics = json.loads(valid_fixture["files"]["scope-rubric-registry.json"])
    target = targets["targets"][0]
    raw = b"answer-01 relation-01 applicable-01"
    evaluator = module.evaluate(
        raw,
        {"id": target["id"], "answer_key_sha256": target["answer_key_sha256"], "scope_rubric_sha256": target["scope_rubric_sha256"]},
        keys["records"][0],
        rubrics["records"][0],
    )
    zero = "0" * 64
    _, _, _, permutation = module.condition_permutation("SP01", "structural_diagnosis")
    condition = permutation[0]
    package = sources["packages"][0]
    rendered = module._target_render(target, condition, bindings, targets["stage1_outputs"])
    request = module.canonical_target_request(target, condition, bindings, targets["stage1_outputs"])
    request_hash = module.sha256(request)
    accounting = targets["target_package_accounting"][target["id"]][condition]
    return raw, {
        "run_identifiers": {
            "audit_id": f"target-T01-{condition}",
            "execution_state": "TARGET_EXECUTION_BOUND",
            "package_id": "SP01",
            "target_id": "T01",
            "target_family": "structural_diagnosis",
            "condition_id": condition,
            "invocation": "target",
        },
        "hashes": {
            "package_sha256": package["package_hash"],
            "request_sha256": request_hash,
            "raw_response_sha256": module.sha256(raw),
        },
        "token_accounting": {
            "supplied_source_unit_ids": [],
            "supplied_source_unit_hashes": [],
            "retained_object_inventory": ["source_response"],
            "abstraction_slot_inventory": [],
            "rendered_input_sha256": module.sha256(rendered.encode()),
            "tokenizer": "tiktoken==0.9.0/o200k_base",
            "token_count": accounting["token_count"],
            "token_ceiling": module.TOKEN_CEILINGS[condition],
            "budget_result": True,
            "model_output_tokens": 10,
            "source_prompt_sha256": module.EXPECTED_BINDINGS["hashes"]["source_prompt_template"],
            "target_prompt_sha256": module.EXPECTED_BINDINGS["hashes"]["target_prompt_template"],
            "package_record_sha256": package["package_hash"],
            "target_record_sha256": target["target_record_hash"],
        },
        "model_binding": {
            "request": request,
            "request_sha256": request_hash,
            "started_at": "2026-07-19T12:00:00Z",
            "ended_at": "2026-07-19T12:00:01Z",
        },
        "response": {
            "raw_response_sha256": module.sha256(raw),
            "retained_raw_response_utf8": raw.decode(),
            "immutable_artifact_reference": None,
            "parsed_final_response": raw.decode(),
            "parsed_final_response_sha256": module.sha256(raw),
            "abstraction_artifact": None,
            "abstraction_artifact_sha256": None,
            "stage1_output_hash": None,
        },
        "evaluator": evaluator,
        "condition_order": {"position": 1, "condition_id": condition},
        "credential_boundary": {"request_count": 1, "retry": False},
        "operator_actions": [
            {"action": "request", "recorded_at": "2026-07-19T12:00:00Z"},
            {"action": "response_retained", "recorded_at": "2026-07-19T12:00:01Z"},
            {"action": "offline_evaluation", "recorded_at": "2026-07-19T12:00:02Z"},
        ],
        "scorer_image_sha256": bindings["scorer_image_sha256"],
    }


def test_target_audit_recomputes_evaluator_and_binds_permutation(valid_fixture):
    raw, record = target_audit_record(valid_fixture)
    order = json.loads(valid_fixture["files"]["condition-order.json"])
    targets = json.loads(valid_fixture["files"]["target-registry.json"])
    sources = json.loads(valid_fixture["files"]["source-package-registry.json"])
    keys = json.loads(valid_fixture["files"]["answer-key-registry.json"])
    rubrics = json.loads(valid_fixture["files"]["scope-rubric-registry.json"])
    bindings = json.loads(valid_fixture["files"]["prompt-bindings.json"])
    kwargs = {
        "sources": sources,
        "targets": targets,
        "keys": keys,
        "rubrics": rubrics,
        "raw_output": raw,
        "bindings": bindings,
    }
    assert module.semantic_audit_valid(record, order, **kwargs)
    fabricated = copy.deepcopy(record)
    fabricated["evaluator"]["KEY_MATCH"] = False
    fabricated["evaluator"]["score"] = False
    assert not module.semantic_audit_valid(fabricated, order, **kwargs)
    wrong_position = copy.deepcopy(record)
    wrong_position["condition_order"]["position"] = 2
    assert not module.semantic_audit_valid(wrong_position, order, **kwargs)
    wrong_hash = copy.deepcopy(record)
    wrong_hash["hashes"]["raw_response_sha256"] = "0" * 64
    assert not module.semantic_audit_valid(wrong_hash, order, **kwargs)


def test_audit_schema_enforces_score_conjunction_and_strict_objects(valid_fixture):
    schema = module.read_json("audit-manifest-schema.json")
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    _, record = target_audit_record(valid_fixture)
    assert not list(validator.iter_errors(record))
    record["evaluator"]["score"] = False
    assert list(validator.iter_errors(record))
    record = source_audit_record(valid_fixture)
    record["token_accounting"]["unexpected"] = True
    assert list(validator.iter_errors(record))


def test_manifest_exact_coverage_and_hash_reproduction(valid_fixture):
    manifest = json.loads(valid_fixture["files"]["hash-manifest.json"])
    assert module.hashes_complete(
        manifest,
        valid_fixture["files"],
        valid_fixture["preregistration"],
        valid_fixture["anchor_evidence"],
    )
    assert {item["path"] for item in manifest["files"]} == module.PACKAGE_FILES


def test_regenerated_manifest_cannot_bypass_frozen_anchor(valid_fixture):
    fixture = clone_fixture(valid_fixture)
    bindings = json.loads(fixture["files"]["prompt-bindings.json"])
    bindings["system_prompt"] += " post-freeze alteration"
    fixture["files"]["prompt-bindings.json"] = json_bytes(bindings)
    refresh_manifest(fixture["files"], fixture["preregistration"])
    result = readiness(fixture)
    assert result["checks"]["HASHES_COMPLETE"] is False
    assert result["source_stage"] == "NULL"
