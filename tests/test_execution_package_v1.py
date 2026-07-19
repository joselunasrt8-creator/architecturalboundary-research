import importlib.util
import sys
from pathlib import Path

import pytest

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
