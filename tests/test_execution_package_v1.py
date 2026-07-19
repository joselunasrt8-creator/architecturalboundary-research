import importlib.util
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / 'investigations/context-scaling-vs-explicit-abstraction/artifacts/execution-package-v1/execution_package.py'
spec = importlib.util.spec_from_file_location('execution_package_v1', MODULE_PATH)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def fixture_record(key, scope):
    return {'id': 'T01', 'answer_key_sha256': module.sha256(key), 'scope_rubric_sha256': module.sha256(scope)}


def test_evaluator_derives_preregistered_booleans():
    key = {'required_literals': ['correct answer'], 'forbidden_literals': ['wrong answer']}
    scope = {'relation_literals': ['relation applies'], 'required_applicability_literals': ['within scope'], 'forbidden_applicability_literals': ['outside scope']}
    result = module.evaluate(b'Correct  ANSWER; relation applies within scope.', fixture_record(key, scope), key, scope)
    assert result['KEY_MATCH'] is True
    assert result['SCOPE_MATCH'] is True
    assert result['score'] is True
    assert set(result) == {'target_id', 'raw_output_sha256', 'answer_key_sha256', 'scope_rubric_sha256', 'KEY_MATCH', 'SCOPE_MATCH', 'score'}


def test_evaluator_rejects_duplicate_normalized_literals():
    key = {'required_literals': ['x', 'X'], 'forbidden_literals': []}
    scope = {'relation_literals': ['r'], 'required_applicability_literals': ['a'], 'forbidden_applicability_literals': []}
    with pytest.raises(ValueError, match='malformed literal registry'):
        module.evaluate(b'x r a', fixture_record(key, scope), key, scope)


def test_readiness_is_deterministic_null_without_fabricated_objects():
    first = module.readiness()
    assert first == module.readiness()
    assert first['outcome'] == 'NULL'
    assert 'SOURCE_CORPUS_NOT_FROZEN: no canonical source references and verbatim eligible units are present' in first['reasons']


def test_hashes_and_prompt_renders_are_reproducible():
    manifest = module.read_json('hash-manifest.json')
    assert all(item['sha256'] == __import__('hashlib').sha256((module.PACKAGE / item['path']).read_bytes()).hexdigest() for item in manifest['files'])
    bindings = module.read_json('prompt-bindings.json')
    assert bindings['hashes']['system_prompt'] == __import__('hashlib').sha256(bindings['system_prompt'].encode()).hexdigest()
    assert module.condition_permutation('SP01', 'structural_diagnosis') == module.condition_permutation('SP01', 'structural_diagnosis')


def null_record(reason):
    return {"status": "NULL", "reason": reason}


def test_audit_manifest_schema_requires_typed_complete_records():
    schema = module.read_json("audit-manifest-schema.json")
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    valid_pre_execution = {
        "run_identifiers": {"audit_id": "audit-null-readiness", "execution_state": "PRE_EXECUTION_NULL", "package_id": None, "target_id": None, "condition_id": None},
        **{field: null_record("frozen inputs are unavailable") for field in schema["required"] if field != "run_identifiers"},
    }
    assert not list(validator.iter_errors(valid_pre_execution))

    malformed = dict(valid_pre_execution)
    malformed["hashes"] = "not a typed null record"
    assert list(validator.iter_errors(malformed))

    execution = {
        "run_identifiers": {"audit_id": "audit-target-01", "execution_state": "EXECUTION_BOUND", "package_id": "SP01", "target_id": "T01", "condition_id": "C2", "invocation": "target"},
        "hashes": {name: "a" * 64 for name in ["package_sha256", "prompt_sha256", "request_sha256", "raw_response_sha256", "registry_sha256"]},
        "prompts": {name: "b" * 64 for name in ["system_prompt_sha256", "user_prompt_sha256", "rendered_prompt_sha256"]},
        "package_ids": ["SP01"],
        "target_ids": ["T01"],
        "tokenizer": {"name": "o200k_base", "package": "tiktoken==0.9.0", "encoding": "UTF-8 without normalization"},
        "model_binding": {"model": "gpt-4.1-2025-04-14", "endpoint": "https://api.openai.com/v1/responses", "decoding": {"temperature": 0, "top_p": 1, "max_output_tokens": 2048, "presence_penalty": 0, "frequency_penalty": 0, "seed": 20260719}, "request": {"endpoint": "https://api.openai.com/v1/responses", "request_sha256": "a" * 64, "started_at": "2026-07-19T00:00:00Z", "ended_at": "2026-07-19T00:00:01Z", "http_status": 200, "response_id": "resp_123"}},
        "condition_order": {"stage": "target", "position": 1, "condition_id": "C2"},
        "response_placeholders": {"raw_response_sha256": "c" * 64, "retained_output_sha256": "d" * 64, "byte_length": 1},
        "evaluator_placeholders": {"target_id": "T01", "raw_output_sha256": "c" * 64, "answer_key_sha256": "d" * 64, "scope_rubric_sha256": "e" * 64, "KEY_MATCH": True, "SCOPE_MATCH": True, "score": True},
        "environment_metadata": {"invocation_image_sha256": "f" * 64, "scoring_image_sha256": "a" * 64, "network": "controlled_api_only"},
        "credential_boundary": {"injected_for_invocation": True, "persisted": False, "request_count": 1},
        "operator_actions": [{"action": "frozen", "recorded_at": "2026-07-19T00:00:00Z"}],
    }
    assert not list(validator.iter_errors(execution))
    execution["hashes"]["request_sha256"] = None
    assert list(validator.iter_errors(execution))


def test_evaluator_rejects_cross_list_and_reserved_literal_conflicts():
    scope = {'relation_literals': ['r'], 'required_applicability_literals': ['a'], 'forbidden_applicability_literals': []}
    key = {'required_literals': ['correct'], 'forbidden_literals': ['CORRECT']}
    with pytest.raises(ValueError, match='malformed literal registry'):
        module.evaluate(b'correct r a', fixture_record(key, scope), key, scope)
    key = {'required_literals': ['KEY_MATCH'], 'forbidden_literals': []}
    with pytest.raises(ValueError, match='malformed literal registry'):
        module.evaluate(b'key_match r a', fixture_record(key, scope), key, scope)


def complete_readiness_fixture():
    key = {'required_literals': ['answer'], 'forbidden_literals': []}
    rubric = {'relation_literals': ['relation'], 'required_applicability_literals': ['applicable'], 'forbidden_applicability_literals': []}
    packages = []
    for package_id in module.PACKAGE_IDS:
        units = []
        for number in range(1, 17):
            content = f'{package_id} unit {number}'
            units.append({'id': f'U{number:03d}', 'status': 'ELIGIBLE', 'content': content, 'sha256': __import__('hashlib').sha256(content.encode()).hexdigest()})
        packages.append({'id': package_id, 'status': 'READY', 'units': units, 'rendered_source_inputs': {condition: f'{package_id} source {condition}' for condition in module.CONDITIONS}})
    targets = []
    for package_id in module.PACKAGE_IDS:
        for family in module.FAMILIES:
            targets.append({'id': f'T-{package_id}-{family}', 'package_id': package_id, 'family': family, 'status': 'ELIGIBLE', 'answer_key_sha256': module.sha256(key), 'scope_rubric_sha256': module.sha256(rubric), 'transfer_distance': {'domain': True, 'surface_representation': True, 'entities_vocabulary': True, 'task_objective': False, 'causal_structural_arrangement': False}, 'rendered_target_inputs': {condition: f'{package_id} {family} {condition}' for condition in module.CONDITIONS}})
    manifest_files = [{'path': path, 'sha256': __import__('hashlib').sha256((module.PACKAGE / path).read_bytes()).hexdigest()} for path in module.PACKAGE_FILES]
    return {
        'source-package-registry.json': {'preregistration_commit': 'aed5ff895d3afb0a03b819bc5112327b479b8905', 'preregistration_sha256': __import__('hashlib').sha256(module.PREREGISTRATION.read_bytes()).hexdigest(), 'packages': packages},
        'target-registry.json': {'targets': targets},
        'answer-key-registry.json': {'records': [key]}, 'scope-rubric-registry.json': {'records': [rubric]},
        'hash-manifest.json': {'files': manifest_files, 'external_files': [{'path': 'investigations/context-scaling-vs-explicit-abstraction/preregistration.md', 'sha256': __import__('hashlib').sha256(module.PREREGISTRATION.read_bytes()).hexdigest()}]},
        'prompt-bindings.json': {'model': 'gpt-4.1-2025-04-14'},
        'audit-manifest-schema.json': module.read_json('audit-manifest-schema.json'),
    }


def test_readiness_returns_ready_for_complete_valid_fixture(monkeypatch):
    fixture = complete_readiness_fixture()
    monkeypatch.setattr(module, 'read_json', lambda name: fixture[name])
    monkeypatch.setattr(module, 'token_count', lambda rendered: len(rendered.split()))
    assert module.readiness()['outcome'] == 'READY'


def test_readiness_returns_null_for_adversarial_malformed_records(monkeypatch):
    fixture = complete_readiness_fixture()
    fixture['target-registry.json']['targets'][0]['transfer_distance']['domain'] = False
    fixture['target-registry.json']['targets'][0]['transfer_distance']['surface_representation'] = False
    monkeypatch.setattr(module, 'read_json', lambda name: fixture[name])
    monkeypatch.setattr(module, 'token_count', lambda rendered: 1)
    result = module.readiness()
    assert result['outcome'] == 'NULL'
    assert result['checks']['TWENTY_FOUR_TARGETS'] is False
