import importlib.util,sys,copy,hashlib
from pathlib import Path
import pytest
from jsonschema import Draft202012Validator,FormatChecker
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'investigations/context-scaling-vs-explicit-abstraction/artifacts/execution-package-v1/execution_package.py'
s=importlib.util.spec_from_file_location('ep',P); m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
def key_scope():return {'required_literals':['answer'],'forbidden_literals':[]},{'relation_literals':['relation'],'required_applicability_literals':['applicable'],'forbidden_applicability_literals':[]}
def source_audit_record():
 z='0'*64
 return {'run_identifiers':{'audit_id':'source-SP01-C1','execution_state':'SOURCE_EXECUTION_BOUND','package_id':'SP01','target_id':None,'target_family':None,'condition_id':'C1','invocation':'source'},'hashes':{'package_sha256':z,'request_sha256':z,'raw_response_sha256':z},'token_accounting':{'supplied_source_unit_ids':['U001'],'supplied_source_unit_hashes':[z],'retained_object_inventory':[],'abstraction_slot_inventory':[],'rendered_input_sha256':z,'tokenizer':'tiktoken==0.9.0/o200k_base','token_count':1,'token_ceiling':4096,'budget_result':True,'model_output_tokens':1,'source_prompt_sha256':z,'target_prompt_sha256':z,'package_record_sha256':z,'target_record_sha256':z},'model_binding':{'request':{'endpoint':'https://api.openai.com/v1/responses','request_sha256':z},'started_at':'2026-07-19T12:00:00Z','ended_at':'2026-07-19T12:00:01Z'},'response':{'raw_response_sha256':z},'evaluator':None,'condition_order':{'position':1,'condition_id':'C1'},'credential_boundary':{'request_count':1,'retry':False},'operator_actions':[{'action':'request','recorded_at':'2026-07-19T12:00:00Z'},{'action':'response_retained','recorded_at':'2026-07-19T12:00:01Z'},{'action':'offline_evaluation','recorded_at':'2026-07-19T12:00:02Z'}]}
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
 source=source_audit_record();assert not list(v.iter_errors(source));source['run_identifiers']['package_id']=1;assert list(v.iter_errors(source));source=source_audit_record();source['token_accounting']['supplied_source_unit_ids']=[1];assert list(v.iter_errors(source))
 stack=[schema]
 while stack:
  item=stack.pop()
  if isinstance(item,dict):
   if 'pattern' in item:assert item.get('type')=='string'
   stack.extend(item.values())
  elif isinstance(item,list):stack.extend(item)
def test_semantic_validator_rejects_chronology_and_score_mismatch():
 order=m.read_json('condition-order.json');record=source_audit_record();assert m.semantic_audit_valid(record,order);record['condition_order']['position']=4;assert not m.semantic_audit_valid(record,order);assert not m.semantic_audit_valid({},order)
def test_target_render_includes_frozen_target_prompt():
 b=m.read_json('prompt-bindings.json');stage1={'SP01':{'C1':{'source_response':'retained source','abstraction_artifact':None}}};rendered=m._target_render({'id':'T01','package_id':'SP01','target_prompt':'FROZEN UNSEEN TASK'},'C1',b,stage1);assert rendered.endswith('FROZEN UNSEEN TASK')
def test_hash_manifest_is_exact_and_reproduces():
 manifest=m.read_json('hash-manifest.json');assert m.hashes_complete(manifest) is True
