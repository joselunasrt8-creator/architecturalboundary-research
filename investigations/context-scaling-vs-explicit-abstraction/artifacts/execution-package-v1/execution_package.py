#!/usr/bin/env python3
"""Offline validators for the frozen Context/Abstraction execution package.

This module deliberately has no invocation code.  It fails closed: malformed or
incomplete registries produce deterministic NULL readiness rather than authority.
"""
from __future__ import annotations
import hashlib, json, re, subprocess, unicodedata
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
from typing import Any

PACKAGE=Path(__file__).resolve().parent; ROOT=PACKAGE.parents[3]
PREREGISTRATION=ROOT/'investigations/context-scaling-vs-explicit-abstraction/preregistration.md'
PACKAGE_IDS=[f'SP{i:02d}' for i in range(1,9)]; UNIT_IDS=[f'U{i:03d}' for i in range(1,17)]
FAMILIES=['structural_diagnosis','constraint_aware_recommendation','causal_explanation']; CONDITIONS=['C1','C2','C3','C4']; SEED=20260719
SHA256=re.compile(r'^[0-9a-f]{64}$')
PACKAGE_FILES={'README.md','source-package-registry.json','target-registry.json','prompt-bindings.json','condition-order.json','answer-key-registry.json','scope-rubric-registry.json','audit-manifest-schema.json','execution-readiness-report.md','evaluator-specification.md','execution_package.py'}
EXPECTED_PROMPT_HASHES={'system_prompt':'5bf8463177eb1599b50cbea5d8f6d80fdd467618de0e805a106b9d424e18b3f2','source_prompt_template':'df6412072f515e2b0e47249cd14b5da8413e0e219100d27f98c72e8275fc1c5e','target_prompt_template':'45f393b381a3555c52c87ddca5dffdd8290ad68803964f7ebd1559e94939ac13','retention_instructions':{'C1':'4bed96dea30ead94e0c041d18e213b28eb4083a3ddb42147991868758005225e','C2':'906cda79904e79f40ddacad75fc888246c754059b03b883b4f2c451071e54bc4','C3':'4bed96dea30ead94e0c041d18e213b28eb4083a3ddb42147991868758005225e','C4':'906cda79904e79f40ddacad75fc888246c754059b03b883b4f2c451071e54bc4'}}
def canonical_bytes(x:Any)->bytes:return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def sha256(x:Any)->str:return hashlib.sha256(x if isinstance(x,bytes) else canonical_bytes(x)).hexdigest()
def normalized(x:str)->str:return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',x).casefold()).strip()
def read_json(name:str)->Any:
 with (PACKAGE/name).open(encoding='utf8') as f:return json.load(f)
def valid_hash(x:Any)->bool:return isinstance(x,str) and bool(SHA256.fullmatch(x))
def closed(x:Any, fields:set[str])->bool:return isinstance(x,dict) and set(x)==fields

def _literals(x:Any, fields:set[str], nonempty:set[str])->None:
 if not closed(x,fields):raise ValueError('malformed literal registry')
 all_values=[]
 for name in fields:
  values=x[name]
  if not isinstance(values,list) or (name in nonempty and not values) or not all(isinstance(v,str) and normalized(v) for v in values):raise ValueError('malformed literal registry')
  all_values += [normalized(v) for v in values]
 if len(all_values)!=len(set(all_values)) or {'key_match','scope_match'}&set(all_values):raise ValueError('malformed literal registry')

def evaluate(raw_output:bytes,target_record:dict[str,Any],answer_key:dict[str,Any],scope_rubric:dict[str,Any])->dict[str,Any]:
 if not closed(target_record,{'id','answer_key_sha256','scope_rubric_sha256'}) or not isinstance(target_record['id'],str) or not valid_hash(target_record['answer_key_sha256']) or not valid_hash(target_record['scope_rubric_sha256']):raise ValueError('malformed target record')
 try: text=raw_output.decode('utf8','strict')
 except (AttributeError,UnicodeDecodeError) as e:raise ValueError('undecodable output') from e
 if not text:raise ValueError('empty raw output')
 _literals(answer_key,{'required_literals','forbidden_literals'},{'required_literals'}); _literals(scope_rubric,{'relation_literals','required_applicability_literals','forbidden_applicability_literals'},{'relation_literals','required_applicability_literals'})
 if sha256(answer_key)!=target_record['answer_key_sha256'] or sha256(scope_rubric)!=target_record['scope_rubric_sha256']:raise ValueError('hash mismatch')
 out=normalized(text); key=all(normalized(x) in out for x in answer_key['required_literals']) and not any(normalized(x) in out for x in answer_key['forbidden_literals']); scope=all(normalized(x) in out for x in scope_rubric['relation_literals']+scope_rubric['required_applicability_literals']) and not any(normalized(x) in out for x in scope_rubric['forbidden_applicability_literals'])
 return {'target_id':target_record['id'],'raw_output_sha256':sha256(raw_output),'answer_key_sha256':sha256(answer_key),'scope_rubric_sha256':sha256(scope_rubric),'KEY_MATCH':key,'SCOPE_MATCH':scope,'score':key and scope}

def condition_permutation(p:str,f:str)->tuple[str,list[str]]:
 d=hashlib.sha256(f'context-transfer-condition-order-v1|{SEED}|{p}|{f}'.encode()).hexdigest(); n=int(d[:16],16); a=CONDITIONS.copy()
 for i in range(3,0,-1):j=(n//(4**(3-i)))%(i+1);a[i],a[j]=a[j],a[i]
 return d,a

def _bindings_valid(b:Any)->bool:
 try:
  req={'schema_version','system_prompt','source_prompt_template','target_prompt_template','retention_instructions','hashes','model','tokenizer','decoding','timeout_seconds','token_ceilings'}
  if not closed(b,req) or b['schema_version']!='1' or b['model']!='gpt-4.1-2025-04-14' or b['timeout_seconds']!=120 or b['tokenizer']!={'name':'o200k_base','package':'tiktoken==0.9.0','encoding':'UTF-8 without normalization'} or b['token_ceilings']!={'C1':4096,'C2':4096,'C3':8192,'C4':8192} or b['decoding']!={'temperature':0,'top_p':1,'max_output_tokens':2048,'presence_penalty':0,'frequency_penalty':0,'seed':SEED,'omitted_optional_parameters':True}:return False
  if not isinstance(b['retention_instructions'],dict) or set(b['retention_instructions'])!=set(CONDITIONS) or not all(isinstance(b['retention_instructions'][c],str) for c in CONDITIONS) or b['hashes']!=EXPECTED_PROMPT_HASHES:return False
  return all(isinstance(b[x],str) and hashlib.sha256(b[x].encode()).hexdigest()==b['hashes'][x] for x in ('system_prompt','source_prompt_template','target_prompt_template')) and all(hashlib.sha256(b['retention_instructions'][c].encode()).hexdigest()==b['hashes']['retention_instructions'][c] for c in CONDITIONS)
 except (KeyError,TypeError):return False

def _source_render(p:dict[str,Any],c:str,b:dict[str,Any])->str:
 units=p['units'][:8 if c in {'C1','C2'} else 16]; text='\n'.join(f"{u['id']}: {u['content']}" for u in units); return b['system_prompt']+'\n\n'+b['source_prompt_template'].format(package_id=p['id'],condition_id=c,source_units=text,retention_instruction=b['retention_instructions'][c])
def _target_render(t:dict[str,Any],c:str,b:dict[str,Any],stage1:dict[str,Any])->str:
 artifact=stage1[t['package_id']][c]; retained=artifact['source_response'] + ('\n'+artifact['abstraction_artifact'] if c in {'C2','C4'} else '')
 return b['system_prompt']+'\n\n'+b['target_prompt_template'].format(target_id=t['id'],condition_id=c,retained_package=retained)+'\n\n'+t['target_prompt']
def token_count(text:str)->int:
 import tiktoken
 if metadata.version('tiktoken')!='0.9.0':raise RuntimeError('tokenizer version mismatch')
 return len(tiktoken.get_encoding('o200k_base').encode(text))

def valid_sources(s:Any)->bool:
 try:
  if not closed(s,{'schema_version','package_version','preregistration_commit','preregistration_sha256','unitization','packages'}) or not isinstance(s['packages'],list) or [p.get('id') if isinstance(p,dict) else None for p in s['packages']]!=PACKAGE_IDS:return False
  pfields={'id','status','canonical_source_reference','immutable_locator','document_order','unit_boundary_method','unit_boundary_version','units','source_hashes','package_hash','duplicate_decisions','exclusion_decisions','duplicate_eligible_content_absent','subsets','token_accounting','provenance'}
  ufields={'id','status','content','sha256','source_reference'}
  for p in s['packages']:
   if not closed(p,pfields) or p['status']!='READY' or not all(isinstance(p[k],str) and p[k] for k in ('canonical_source_reference','immutable_locator','document_order','unit_boundary_method','unit_boundary_version')) or not valid_hash(p['package_hash']) or p['duplicate_eligible_content_absent'] is not True or not isinstance(p['duplicate_decisions'],list) or not isinstance(p['exclusion_decisions'],list):return False
   us=p['units']
   if not isinstance(us,list) or [u.get('id') if isinstance(u,dict) else None for u in us]!=UNIT_IDS:return False
   if any(not closed(u,ufields) or u['status']!='ELIGIBLE' or not isinstance(u['content'],str) or not u['content'] or not isinstance(u['source_reference'],str) or not u['source_reference'] or not valid_hash(u['sha256']) or hashlib.sha256(u['content'].encode()).hexdigest()!=u['sha256'] for u in us):return False
   if len({u['content'] for u in us})!=16 or len({u['sha256'] for u in us})!=16 or len({u['source_reference'] for u in us})!=16:return False
   if p['source_hashes']!=[u['sha256'] for u in us] or sha256({'id':p['id'],'immutable_locator':p['immutable_locator'],'units':us})!=p['package_hash']:return False
   if not closed(p['subsets'],{'N=8','M=16'}) or p['subsets']!={'N=8':UNIT_IDS[:8],'M=16':UNIT_IDS}:return False
   ta=p['token_accounting'];
   if not closed(ta,{'tokenizer','package','N=8','M=16','C1_C2_budget','C3_C4_budget'}) or ta['tokenizer']!='o200k_base' or ta['package']!='tiktoken==0.9.0' or not all(isinstance(ta[x],int) and ta[x]>=0 for x in ('N=8','M=16','C1_C2_budget','C3_C4_budget')) or ta['C1_C2_budget']>4096 or ta['C3_C4_budget']>8192:return False
  return True
 except (KeyError,TypeError):return False

def valid_targets(t:Any,keys:Any,rubrics:Any)->bool:
 try:
  if not closed(t,{'schema_version','package_version','selection_rule','expected_target_count','targets','status','reason'}) or t['expected_target_count']!=24 or t['status']!='READY' or not isinstance(t['targets'],list) or len(t['targets'])!=24 or not closed(keys,{'records'}) or not closed(rubrics,{'records'}) or not isinstance(keys['records'],list) or not isinstance(rubrics['records'],list):return False
  kh={sha256(x):x for x in keys['records'] if isinstance(x,dict)}; rh={sha256(x):x for x in rubrics['records'] if isinstance(x,dict)}
  if len(kh)!=len(keys['records']) or len(rh)!=len(rubrics['records']):return False
  fields={'id','package_id','family','status','target_prompt','answer_key_sha256','scope_rubric_sha256','required_literals','forbidden_literals','relation_literals','applicability_literals','transfer_distance','overlap_checks','eligibility_rationale','eligibility_determination','target_record_hash','retained_package_accounting'}; seen=set(); ids=set()
  for r in t['targets']:
   if not closed(r,fields) or not isinstance(r['id'],str) or not re.fullmatch(r'T\d{2}',r['id']) or r['id'] in ids or r['package_id'] not in PACKAGE_IDS or r['family'] not in FAMILIES or r['status']!='ELIGIBLE' or not isinstance(r['target_prompt'],str) or not r['target_prompt'] or not valid_hash(r['answer_key_sha256']) or not valid_hash(r['scope_rubric_sha256']) or not isinstance(r['eligibility_rationale'],str) or not r['eligibility_rationale'] or r['eligibility_determination']!='ELIGIBLE' or not isinstance(r['overlap_checks'],dict) or not all(isinstance(v,bool) for v in r['overlap_checks'].values()) or not all(r['overlap_checks'].values()):return False
   ids.add(r['id']); pair=(r['package_id'],r['family'])
   if pair in seen: return False
   seen.add(pair); d=r['transfer_distance']
   if not closed(d,{'domain','surface_representation','entities_vocabulary','task_objective','causal_structural_arrangement'}) or not all(isinstance(v,bool) for v in d.values()) or sum(d.values())<3:return False
   if r['answer_key_sha256'] not in kh or r['scope_rubric_sha256'] not in rh:return False
   _literals(kh[r['answer_key_sha256']],{'required_literals','forbidden_literals'},{'required_literals'});_literals(rh[r['scope_rubric_sha256']],{'relation_literals','required_applicability_literals','forbidden_applicability_literals'},{'relation_literals','required_applicability_literals'})
   if r['required_literals']!=kh[r['answer_key_sha256']]['required_literals'] or r['forbidden_literals']!=kh[r['answer_key_sha256']]['forbidden_literals'] or r['relation_literals']!=rh[r['scope_rubric_sha256']]['relation_literals'] or r['applicability_literals']!=rh[r['scope_rubric_sha256']]['required_applicability_literals']:return False
   if not closed(r['retained_package_accounting'],set(CONDITIONS)) or not all(isinstance(v,dict) and closed(v,{'retained_instructions_sha256','target_prompt_sha256'}) and valid_hash(v['retained_instructions_sha256']) and valid_hash(v['target_prompt_sha256']) for v in r['retained_package_accounting'].values()):return False
   data={k:v for k,v in r.items() if k!='target_record_hash'}
   if not valid_hash(r['target_record_hash']) or sha256(data)!=r['target_record_hash']:return False
  return seen=={(p,f) for p in PACKAGE_IDS for f in FAMILIES} and len(kh)==len(keys['records']) and len(rh)==len(rubrics['records'])
 except (KeyError,TypeError,ValueError):return False

def valid_token_budgets(s:Any,t:Any,b:Any,stage1:Any)->tuple[bool,bool]:
 if not (_bindings_valid(b) and valid_sources(s)) :return False,False
 try:
  source=all(token_count(_source_render(p,c,b))<=b['token_ceilings'][c] for p in s['packages'] for c in CONDITIONS)
  if not isinstance(stage1,dict) or not valid_targets(t,{'records':[]},{'records':[]}): return source,False # targets must be validated by readiness with registries
  return source,False
 except (ImportError,RuntimeError,ValueError,TypeError,KeyError,metadata.PackageNotFoundError):return False,False

def target_budget_preflight(s:Any,t:Any,keys:Any,rubrics:Any,b:Any,stage1:Any)->bool:
 if not valid_targets(t,keys,rubrics) or not isinstance(stage1,dict):return False
 try:
  if set(stage1)!=set(PACKAGE_IDS):return False
  for p in PACKAGE_IDS:
   if not isinstance(stage1[p],dict) or set(stage1[p])!=set(CONDITIONS):return False
   for c,a in stage1[p].items():
    if not closed(a,{'source_response','abstraction_artifact','source_response_sha256','abstraction_artifact_sha256'}) or not isinstance(a['source_response'],str) or not a['source_response'] or (c in {'C2','C4'} and (not isinstance(a['abstraction_artifact'],str) or not a['abstraction_artifact'])) or (c in {'C1','C3'} and a['abstraction_artifact'] is not None) or hashlib.sha256(a['source_response'].encode()).hexdigest()!=a['source_response_sha256'] or (a['abstraction_artifact'] is not None and hashlib.sha256(a['abstraction_artifact'].encode()).hexdigest()!=a['abstraction_artifact_sha256']):return False
  return all(token_count(_target_render(r,c,b,stage1))<=b['token_ceilings'][c] for r in t['targets'] for c in CONDITIONS)
 except (KeyError,TypeError,ValueError,RuntimeError,ImportError,metadata.PackageNotFoundError):return False

def preregistration_matches(s:Any,m:Any)->bool:
 try:
  h=s['preregistration_sha256']; commit=s['preregistration_commit']; ext=m['external_files']; pinned=subprocess.check_output(['git','show',f'{commit}:investigations/context-scaling-vs-explicit-abstraction/preregistration.md'],cwd=ROOT)
  return valid_hash(h) and hashlib.sha256(PREREGISTRATION.read_bytes()).hexdigest()==h==hashlib.sha256(pinned).hexdigest() and ext==[{'path':'investigations/context-scaling-vs-explicit-abstraction/preregistration.md','sha256':h}]
 except (KeyError,TypeError,OSError,subprocess.CalledProcessError):return False

def valid_condition_order(o:Any)->bool:
 try:
  if not isinstance(o,dict) or o.get('seed')!=SEED or o.get('canonical_target_order')!='NULL: targets are not frozen' or not valid_hash(o.get('verification_hash')):return False
  source=[{'package_id':p,'condition_id':c} for p in PACKAGE_IDS for c in CONDITIONS]
  if o.get('canonical_source_order')!=source:return False
  blocks=o['target_condition_blocks']; exp=[(p,f) for p in PACKAGE_IDS for f in FAMILIES]
  if not isinstance(blocks,list) or [(x.get('package_id'),x.get('target_family')) if isinstance(x,dict) else None for x in blocks]!=exp:return False
  return all(x.get('digest_sha256')==condition_permutation(x['package_id'],x['target_family'])[0] and x.get('execution_conditions')==condition_permutation(x['package_id'],x['target_family'])[1] for x in blocks)
 except (KeyError,TypeError):return False
def _parse_time(x:Any)->datetime|None:
 try:return datetime.fromisoformat(x.replace('Z','+00:00')) if isinstance(x,str) else None
 except ValueError:return None

def semantic_audit_valid(record:Any, order:Any, targets:Any=None)->bool:
 """Cross-field lineage, permutation, chronology and one-request validation."""
 try:
  state=record['run_identifiers']['execution_state']
  if state=='PRE_EXECUTION_NULL': return all(isinstance(v,dict) and v.get('status')=='NULL' for k,v in record.items() if k!='run_identifiers')
  run=record['run_identifiers']; binding=record['model_binding']; req=binding['request']; hashes=record['hashes']; response=record['response']; actions=record['operator_actions']
  start,end=_parse_time(binding['started_at']),_parse_time(binding['ended_at'])
  if not start or not end or end<start or (end-start).total_seconds()>120 or hashes['request_sha256']!=req['request_sha256'] or hashes['raw_response_sha256']!=response['raw_response_sha256'] or record['credential_boundary']['request_count']!=1:return False
  times=[_parse_time(a['recorded_at']) for a in actions]; names=[a['action'] for a in actions]
  if not all(times) or times!=sorted(times) or names.count('request')!=1 or not {'request','response_retained','offline_evaluation'} <= set(names) or not(names.index('request')<names.index('response_retained')<names.index('offline_evaluation')):return False
  if state=='SOURCE_EXECUTION_BOUND':
   source=[x for x in order['canonical_source_order'] if x['package_id']==run['package_id']]; position=record['condition_order']['position']
   if not isinstance(position,int) or isinstance(position,bool) or not 1<=position<=len(source):return False
   return run['invocation']=='source' and run['target_id'] is None and run['target_family'] is None and record['evaluator'] is None and record['token_accounting']['target_record_sha256']=='0'*64 and source[position-1]=={'package_id':run['package_id'],'condition_id':run['condition_id']} and record['condition_order']['condition_id']==run['condition_id']
  if state!='TARGET_EXECUTION_BOUND' or run['invocation']!='target' or not isinstance(run['target_id'],str):return False
  ev=record['evaluator']
  if run['target_id']!=ev['target_id'] or response['raw_response_sha256']!=ev['raw_output_sha256'] or ev['score'] != (ev['KEY_MATCH'] and ev['SCOPE_MATCH']):return False
  blocks=order['target_condition_blocks']; block=next((x for x in blocks if x['package_id']==run['package_id'] and x['target_family']==run['target_family']),None)
  if not block or block['execution_conditions'][record['condition_order']['position']-1]!=run['condition_id'] or record['condition_order']['condition_id']!=run['condition_id']:return False
  if targets is not None:
   target=next((x for x in targets.get('targets',[]) if isinstance(x,dict) and x.get('id')==run['target_id']),None)
   if not target or target['package_id']!=run['package_id'] or target['family']!=run['target_family'] or target['answer_key_sha256']!=ev['answer_key_sha256'] or target['scope_rubric_sha256']!=ev['scope_rubric_sha256']:return False
  return True
 except (KeyError,TypeError,IndexError):return False

def valid_audit_schema(schema:Any)->bool:
 try:
  from jsonschema import Draft202012Validator,FormatChecker
  Draft202012Validator.check_schema(schema); Draft202012Validator(schema,format_checker=FormatChecker())
  return schema.get('additionalProperties') is False and set(schema.get('$defs',{})) >= {'pre_execution','source_execution','target_execution','sha256'}
 except Exception:return False

def evaluator_valid()->bool:
 """Evaluator is immutable and its deterministic regression fixtures agree."""
 try:
  manifest=read_json('hash-manifest.json'); path=next(x for x in manifest['files'] if x['path']=='execution_package.py')
  key={'required_literals':['yes'],'forbidden_literals':['no']}; rubric={'relation_literals':['rel'],'required_applicability_literals':['app'],'forbidden_applicability_literals':[]}; r={'id':'T01','answer_key_sha256':sha256(key),'scope_rubric_sha256':sha256(rubric)}
  return path['sha256']==hashlib.sha256((PACKAGE/'execution_package.py').read_bytes()).hexdigest() and evaluate(b'yes rel app',r,key,rubric)['score'] and not evaluate(b'no rel app',r,key,rubric)['score']
 except (KeyError,ValueError,TypeError):return False

def no_execution_occurred()->bool:
 patterns=('response','request','empirical','result','audit')
 allowed={'audit-manifest-schema.json'}
 files=[p.name.lower() for p in PACKAGE.iterdir() if p.is_file() and p.name not in allowed]
 return not any(any(token in name for token in patterns) for name in files) and read_json('target-registry.json').get('status')=='NULL'

def invocation_boundary_valid(bindings:Any)->bool:
 # Controls are frozen specifications only; absent executable enforcement is not authority.
 return False

def hashes_complete(manifest:Any)->bool:
 try:
  files=manifest['files']; paths=[x['path'] for x in files]
  return isinstance(files,list) and set(paths)==PACKAGE_FILES and len(paths)==len(set(paths)) and all(isinstance(x,dict) and set(x)=={'path','sha256'} and x['path'] in PACKAGE_FILES and valid_hash(x['sha256']) and hashlib.sha256((PACKAGE/x['path']).read_bytes()).hexdigest()==x['sha256'] for x in files)
 except (KeyError,TypeError,OSError):return False

def readiness()->dict[str,Any]:
 try:
  s,t,m,b,k,r,a,o=(read_json(x) for x in ('source-package-registry.json','target-registry.json','hash-manifest.json','prompt-bindings.json','answer-key-registry.json','scope-rubric-registry.json','audit-manifest-schema.json','condition-order.json'))
  stage1=t.get('stage1_outputs') if isinstance(t,dict) else None
  source_budget=False
  if _bindings_valid(b) and valid_sources(s):
   try: source_budget=all(token_count(_source_render(p,c,b))<=b['token_ceilings'][c] for p in s['packages'] for c in CONDITIONS)
   except (ImportError,RuntimeError,ValueError,TypeError,KeyError,metadata.PackageNotFoundError):source_budget=False
  checks={'PREREGISTRATION_MATCH':preregistration_matches(s,m),'EIGHT_SOURCE_PACKAGES':valid_sources(s),'TWENTY_FOUR_TARGETS':valid_targets(t,k,r),'SOURCE_BUDGET_VALID':source_budget,'TARGET_BUDGET_PREFLIGHT_VALID':target_budget_preflight(s,t,k,r,b,stage1),'PROMPTS_MATCH':_bindings_valid(b),'HASHES_COMPLETE':hashes_complete(m),'CONDITION_ORDER_VALID':valid_condition_order(o),'EVALUATOR_VALID':evaluator_valid(),'AUDIT_MANIFEST_COMPLETE':valid_audit_schema(a),'NO_EXECUTION_OCCURRED':no_execution_occurred(),'INVOCATION_BOUNDARY_VALID':invocation_boundary_valid(b)}
 except (OSError,json.JSONDecodeError,TypeError,KeyError):checks={x:False for x in ('PREREGISTRATION_MATCH','EIGHT_SOURCE_PACKAGES','TWENTY_FOUR_TARGETS','SOURCE_BUDGET_VALID','TARGET_BUDGET_PREFLIGHT_VALID','PROMPTS_MATCH','HASHES_COMPLETE','CONDITION_ORDER_VALID','EVALUATOR_VALID','AUDIT_MANIFEST_COMPLETE','NO_EXECUTION_OCCURRED','INVOCATION_BOUNDARY_VALID')}
 reasons=[f'READINESS_{name}_FAILED' for name,ok in checks.items() if not ok]
 return {'outcome':'READY' if all(checks.values()) else 'NULL','checks':checks,'reasons':reasons}
def main()->None:print(json.dumps(readiness(),sort_keys=True,separators=(',',':')))
if __name__=='__main__':main()
