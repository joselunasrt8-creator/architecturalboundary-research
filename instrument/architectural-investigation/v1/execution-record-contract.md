# Architectural Investigation Instrument v1 — Candidate Execution-Record Contract

## Status and ownership

This document materializes the execution-record container owned by Issue #77.
It consumes the controlled semantics owned by
[calibration-contract.md](calibration-contract.md) and does not define a
competing maturity ladder, evidence taxonomy, authority ranking, coverage
measure, or promotion rule.

## Required package

Every audit execution preserves:

1. Audit Request;
2. Scope and Coverage Declaration;
3. Inspection Log;
4. Claim-Level Evidence Ledger;
5. Boundary-Decomposed Findings;
6. Repository Findings;
7. Research Methodology Candidates;
8. Structology Candidates;
9. Instrument-Improvement Observations;
10. Negative and Missing Evidence;
11. Manual-Judgment Register;
12. Stopping Determination;
13. Execution-Validity Record;
14. concise execution summary; and
15. validation record and artifact manifest.

An output surface must exist even when its bounded value is empty,
`NOT_REACHED`, or unsupported.

## Execution identity

Record the execution ID; instrument name, version, containing commit, canonical
paths, and manifest digest; procedure version; repository owner/name and exact
revision; branch or release context; analyst identity or role; custodian;
execution start and completion timestamps; audit mode; environment and access
limitations; authorization; external-evidence mode; and rerun or supersession
lineage.

## Scope and coverage declaration

Record the governing question; included and excluded surfaces; artifact classes
present, inspected, sampled, uninspected, and inaccessible; binary and generated
artifact handling; current-revision, historical, remote-governance, external,
and claim-surface coverage; commands authorized, executed, prohibited, or
omitted; sampling rule; intended completeness claim; access blocks; and stopping
rule.

Coverage classifications and measures must use the calibration contract. Counts
and percentages never imply semantic completeness.

## Inspection log

Each material activity records an activity ID, timestamp, artifact or surface,
stable path/identity and locator, inspection mode, command where applicable,
observed result, limitation, linked claim IDs, mutation status, and whether the
result is static evidence, direct execution observation, or preserved result.

## Claim-level evidence ledger

Every material claim records:

- claim ID and exact bounded claim text;
- output surface and claim type;
- inspected source path, stable locator, and repository revision;
- evidence class and independent source-authority class from the calibration
  contract;
- direct observation versus inference;
- supporting and contrary evidence;
- missing evidence and uninspected dependencies;
- evidence-reachability state and missing transitions where applicable;
- applicable maturity track and highest directly supported state;
- inference steps and manual-judgment reference;
- limitation and uncertainty;
- confidence; reviewer notes; and
- exactly one claim status:

```text
SUPPORTED
SUPPORTED_WITH_LIMITATIONS
CONTESTED
INSUFFICIENT_EVIDENCE
INFERENCE_ONLY
WITHDRAWN
INVALID
```

## Boundary-decomposed finding

Each mixed finding separates repository, Research Methodology, Structology, and
instrument components. Each component records its abstraction, evidence basis,
layer rationale, excluded implementation details, proposed owner, applicable
maturity track/state, and a promotion disposition from the calibration
contract. No component inherits evidence or maturity silently from another.

## Four output surfaces

- **Repository Findings:** bounded defect, ambiguity, negative result, or
  supported property; affected authority or behavior; bounded follow-up; and
  static versus executable confirmation status.
- **Research Methodology Candidates:** general methodological abstraction,
  generalization rationale, repository-specific exclusions, owner, calibrated
  maturity, and non-authoritative disposition.
- **Structology Candidates:** domain-neutral structural abstraction, transfer
  argument, boundary below methodology, excluded implementation bundle,
  calibrated maturity, and non-authoritative disposition.
- **Instrument-Improvement Observations:** observed limitation, execution
  evidence, affected surface, expected improvement, recurrence, compatibility
  and scientific risk, and deferred disposition.

## Negative, missing, and contradictory evidence

Explicitly record unsupported and rejected candidates, contradictions, claimed
capabilities not executed, missing schemas/fixtures/tests/decisions/provenance,
inaccessible artifacts, uninspected areas, unresolved references and authority
conflicts, exclusions, and places where no change is justified. An empty section
requires an explicit evidence-bound rationale.

## Manual judgments

For every manual judgment record the question, available evidence, decision,
rationale, uncertainty, whether another reviewer could reasonably disagree, and
effect on final findings. Deterministic validation may require these fields but
cannot decide their contents.

## Stopping and final determinations

Record exactly one stopping state, exactly one execution-validity determination,
and exactly one audit outcome from
[specification.md](specification.md). Explain whether additional inspection
could materially change any output and why stopping is permitted.

## Static-audit disclosure

A static audit must state that static inspection is not runtime verification and
must list code/tests/validators/workflows not executed, commands actually
performed, repository status observed, mutation status, and claims remaining
unverified without execution.

## Validation record

Record every structural validator and test command, exact outcome, unavailable
tooling, identity/digest/reference checks, and `git diff --check`. Passing
validation means only that the package satisfies mechanically checkable
structure.
