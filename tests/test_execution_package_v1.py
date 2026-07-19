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
