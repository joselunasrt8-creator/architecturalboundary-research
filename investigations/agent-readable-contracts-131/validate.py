#!/usr/bin/env python3
"""Deterministically validate the Issue 131 prospective package, not its hypothesis."""
from __future__ import annotations
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
try:
    from jsonschema import Draft202012Validator
except ModuleNotFoundError:
    sys.path.insert(0, str(ROOT))
    from tools.jsonschema_fallback import Draft202012Validator


def load(name: str) -> dict:
    with (HERE / name).open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise SystemExit(f"{name} must contain an object")
    return value


def errors(schema: dict, value: dict) -> list[str]:
    return [error.message for error in Draft202012Validator(schema).iter_errors(value)]


def main() -> int:
    protocol = load("preregistration.json")
    readiness = load("readiness.json")
    contract_schema = load("candidate-contract.schema.json")
    evidence_schema = load("run-evidence.schema.json")
    expected = "EXPERIMENT_NOT_READY_FOR_EXECUTION"
    if protocol["determination"] != expected or readiness["determination"] != expected:
        raise SystemExit("bounded determinations disagree")
    entries = readiness["entries"]
    counts = {status: sum(x["status"] == status for x in entries) for status in ("PASS", "BLOCKED", "FAIL")}
    if counts != readiness["counts"]:
        raise SystemExit(f"readiness counts are stale: {counts}")
    if not any(x["mandatory"] and x["status"] != "PASS" for x in entries):
        raise SystemExit("NOT_READY requires a non-PASS mandatory entry")
    ids = [x["id"] for x in entries]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate readiness entry id")
    if len(protocol["cohort"]["tasks"]) < 2 or {x["class"] for x in protocol["cohort"]["tasks"]}.__len__() < 2:
        raise SystemExit("cohort needs two materially different task classes")
    if [x["id"] for x in protocol["conditions"]] != ["A", "B", "C"]:
        raise SystemExit("conditions A/B/C are not frozen in order")
    sample_contract = {
        "contract_id": "T1-contract", "representation_version": "issue-131-minimum-v1",
        "repository": {"identity": "architecturalboundary-research", "revision": protocol["cohort"]["revision"]},
        "purpose_scope": "T1 allowed surface only", "accepted_inputs": ["task prompt"],
        "valid_transformations": ["edit allowed paths"], "produced_outputs": ["patch", "validation logs"],
        "invariants_prohibitions": ["no authority grant"], "evidence_provenance": ["retain hashes"],
        "failure_semantics": {"null": "no unique valid transformation", "blocked": "required input unavailable"},
        "authority_boundary": "proposal and offline validation only", "handoff": "retain candidate without commit"
    }
    if errors(contract_schema, sample_contract):
        raise SystemExit(f"valid contract fixture rejected: {errors(contract_schema, sample_contract)}")
    invalid = json.loads(json.dumps(sample_contract)); invalid["repository"]["revision"] = "mutable-main"
    if not errors(contract_schema, invalid):
        raise SystemExit("contract schema accepted a mutable revision")
    evidence = {
        "run_id":"T1-A-1", "condition":"A", "task_id":"T1", "replicate":1,
        "repository_revision":protocol["cohort"]["revision"], "context_hashes":["0"*64],
        "prompt":"", "agent":{}, "environment":{}, "events":[], "output":None,
        "candidate_artifacts":[], "validation":[], "interventions":[], "resource_usage":{}, "disposition":"NULL"
    }
    if errors(evidence_schema, evidence):
        raise SystemExit(f"valid evidence fixture rejected: {errors(evidence_schema, evidence)}")
    invalid_evidence = dict(evidence); invalid_evidence["disposition"] = "SUCCESS"
    if not errors(evidence_schema, invalid_evidence):
        raise SystemExit("evidence schema accepted an unbounded disposition")
    print("Issue 131 prospective package: PASS (schema/consistency only; hypothesis not tested)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
