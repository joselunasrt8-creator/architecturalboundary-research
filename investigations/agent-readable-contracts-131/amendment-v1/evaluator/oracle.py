#!/usr/bin/env python3
"""Evaluator-owned Issue 131 oracle. Never include this path in agent context."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
from jsonschema import Draft202012Validator
BASE="009b87402504ffe305e436d771afe73de30f5169"
ALLOWED={"T1":{"schemas/investigation.schema.json","tests/test_issue131_t1.py"},"T2":{"scripts/validate.py","tests/test_issue131_t2.py"}}
def run(cmd,cwd): return subprocess.run(cmd,cwd=cwd,text=True,capture_output=True)
def changed(root):
 r=run(["git","diff","--name-only",BASE,"--"],root);
 if r.returncode: raise SystemExit(r.stderr)
 return set(r.stdout.splitlines())
def scope(task,root): return changed(root)<=ALLOWED[task]
def t1(root):
 schema=json.loads((root/"schemas/investigation.schema.json").read_text()); v=Draft202012Validator(schema)
 legacy={"id":"legacy","protocol_version":"1"}
 valid={"id":"new","protocol_version":"1","provenance_binding":{"revision":"0123456789abcdef0123456789abcdef01234567"}}
 malformed={"id":"bad","protocol_version":"1","provenance_binding":{"revision":"mutable-main"}}
 return not list(v.iter_errors(legacy)) and not list(v.iter_errors(valid)) and bool(list(v.iter_errors(malformed)))
def t2(root):
 current=run([sys.executable,"scripts/validate.py"],root)
 registry=root/"registry/investigations.json"; original=registry.read_bytes()
 try:
  data=json.loads(original); entries=data["investigations"]; data["investigations"]=[*entries,dict(entries[0])]
  registry.write_text(json.dumps(data,indent=2)+"\n"); duplicate=run([sys.executable,"scripts/validate.py"],root)
  data["investigations"][-1]["id"]="issue-131-oracle-distinct-id"; registry.write_text(json.dumps(data,indent=2)+"\n")
  distinct=run([sys.executable,"scripts/validate.py"],root)
 finally: registry.write_bytes(original)
 return current.returncode==0 and duplicate.returncode!=0 and "duplicate" in (duplicate.stdout+duplicate.stderr).lower() and distinct.returncode==0
def main():
 if len(sys.argv)!=3 or sys.argv[1] not in ALLOWED: raise SystemExit("usage: oracle.py T1|T2 CANDIDATE_ROOT")
 task=sys.argv[1]; root=Path(sys.argv[2]).resolve(); behavior=t1(root) if task=="T1" else t2(root)
 compatibility=run([sys.executable,"scripts/validate.py"],root).returncode==0
 passed=scope(task,root) and behavior and compatibility
 print(json.dumps({"task":task,"scope":scope(task,root),"behavior":behavior,"compatibility":compatibility,"disposition":"VALID" if passed else "INVALID"},sort_keys=True))
 return 0 if passed else 1
if __name__=="__main__": raise SystemExit(main())
