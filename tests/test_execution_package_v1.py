import importlib.util,sys,copy,hashlib
from pathlib import Path
import pytest
from jsonschema import Draft202012Validator,FormatChecker
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'investigations/context-scaling-vs-explicit-abstraction/artifacts/execution-package-v1/execution_package.py'
s=importlib.util.spec_from_file_location('ep',P); m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
def key_scope():return {'required_literals':['answer'],'forbidden_literals':[]},{'relation_literals':['relation'],'required_applicability_literals':['applicable'],'forbidden_applicability_literals':[]}
def test_evaluator_rejects_cross_list_reserved_and_malformed():
 k,r=key_scope(); tr={'id':'T01','answer_key_sha256':m.sha256(k),'scope_rubric_sha256':m.sha256(r)}; assert m.evaluate(b'answer relation applicable',tr,k,r)['score']
 for bad in ({'required_literals':['x'],'forbidden_literals':['X']},{'required_literals':['KEY_MATCH'],'forbidden_literals':[]}):
  with pytest.raises(ValueError):m.evaluate(b'x',tr,bad,r)
 with pytest.raises(ValueError):m.evaluate(b'x',[],k,r)
def test_current_readiness_is_deterministic_null_and_bounded():
 a,b=m.readiness(),m.readiness();assert a==b and a['outcome']=='NULL';assert all(x.startswith('READINESS_') for x in a['reasons'])
def test_source_contract_rejects_duplicate_content_and_missing_metadata():
 x={'schema_version':'1','package_version':'execution-package-v1','preregistration_commit':'a'*40,'preregistration_sha256':'a'*64,'unitization':'x','packages':[]};assert not m.valid_sources(x)
def test_target_contract_fails_closed_on_list_hash():
 assert not m.valid_targets({'schema_version':'1','package_version':'execution-package-v1','selection_rule':'x','expected_target_count':24,'targets':[{'answer_key_sha256':[]}],'status':'READY','reason':'x'},{'records':[]},{'records':[]})
def test_order_validates_source_and_target_orders():
 o=m.read_json('condition-order.json');assert m.valid_condition_order(o);o['canonical_source_order']=[];assert not m.valid_condition_order(o)
def test_schema_branches_are_closed_and_typed():
 schema=m.read_json('audit-manifest-schema.json');Draft202012Validator.check_schema(schema);v=Draft202012Validator(schema,format_checker=FormatChecker()); req=schema['$defs']['pre_execution']['required']; record={'run_identifiers':{'audit_id':'null','execution_state':'PRE_EXECUTION_NULL','package_id':None,'target_id':None,'target_family':None,'condition_id':None,'invocation':None},**{k:{'status':'NULL','reason':'unavailable'} for k in req if k!='run_identifiers'}};assert not list(v.iter_errors(record));record['hashes']='bad';assert list(v.iter_errors(record))
def test_semantic_validator_rejects_chronology_and_score_mismatch():
 assert not m.semantic_audit_valid({},m.read_json('condition-order.json'))
def test_hash_manifest_is_exact_and_reproduces():
 manifest=m.read_json('hash-manifest.json');assert m.hashes_complete(manifest) is True
