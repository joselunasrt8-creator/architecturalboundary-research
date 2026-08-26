# Architectural Investigation Instrument v1 Candidate

## Identity and status

| Field | Value |
| --- | --- |
| Instrument name | Architectural Investigation Instrument |
| Candidate version | `1.0.0-candidate.1` |
| Repository | `joselunasrt8-creator/architecturalboundary-research` |
| Package path | `instrument/architectural-investigation/v1/` |
| Materialization base commit | `d10c0329f5fa871d131d4879ae6684865bf2f2fc` |
| Containing commit | `NOT_AVAILABLE_IN_UNCOMMITTED_WORKTREE` |
| Package status | `UNFROZEN_CANDIDATE` |
| Final determination | `INSTRUMENT_SPECIFICATION_REVISION_REQUIRED` |
| Audit authorization | `NOT_GRANTED` |

This package materializes the smallest reviewable repository-owned surface
derived from Issues #59, #77, and #78. It intentionally does not claim that
their closure supplied `IMPLEMENTATION_READY`. The unresolved calibration and
compatibility decisions are preserved in the
[normative gap register](unresolved-normative-gaps.md).

## Candidate canonical surfaces

These paths are proposed as the complete Instrument v1 normative surface once
the blocking gaps are resolved and a containing commit is recorded:

1. [Instrument specification](specification.md)
2. [Execution-record contract](execution-record-contract.md)
3. [Calibration contract](calibration-contract.md)
4. [Compatibility and supersession](compatibility-and-supersession.md)

The [normative gap register](unresolved-normative-gaps.md) is mandatory
readiness evidence but is not a substitute for resolved normative semantics.
The [instrument manifest](instrument-manifest.json) deterministically binds the
candidate bytes. The repository-owned
[freeze record](../../../docs/reference-execution/v1.0/architectural-investigation-instrument-v1-freeze-record.md)
owns the readiness determination.

## Binding rule

A future audit may bind Instrument v1 only when all of the following are true:

```text
manifest status = FROZEN
and containing commit is a full Git SHA
and every canonical path exists at that commit
and every recorded digest reproduces from that commit
and unresolved normative gaps are empty
and freeze determination = INSTRUMENT_V1_FROZEN_READY
and audit authorization is separately present
```

This candidate fails those predicates and therefore cannot govern an audit.

## Core invariants

```text
Issue Closed != Instrument Frozen
Specification != Executable Instrument Identity
Instrument Availability != Audit Authorization
Structural Validation != Scientific Judgment
Frozen Instrument != Mutable Execution
```
