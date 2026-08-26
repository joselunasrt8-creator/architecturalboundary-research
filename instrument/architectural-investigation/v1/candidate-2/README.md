# Architectural Investigation Instrument 1.0.0-candidate.2

## Status

| Field | Value |
| --- | --- |
| Instrument | Architectural Investigation Instrument |
| Version | `1.0.0-candidate.2` |
| Repository | `joselunasrt8-creator/architecturalboundary-research` |
| Package path | `instrument/architectural-investigation/v1/candidate-2/` |
| Materialization base | `1.0.0-candidate.1` content digest `9888d755916ffae082e54161f5b716ec5b26ca8b5d43b5b9848cbca07bc09b00` |
| Containing commit | `NOT_AVAILABLE_IN_UNCOMMITTED_WORKTREE` |
| Package state | `UNFROZEN_CANDIDATE` |
| Readiness determination | `INSTRUMENT_SPECIFICATION_REVISION_REQUIRED` |
| Audit authorization | `NOT_GRANTED` |

Candidate.2 preserves candidate.1 and resolves its general evidence, authority,
maturity, conflict, precedence, supersession, legitimacy, and fixture-definition
gaps. It does not rewrite the #106 record or blocked #84 execution.

## Candidate.2 normative overlay

Candidate.2 consumes the candidate.1
[specification](../specification.md) and
[execution-record contract](../execution-record-contract.md), then replaces the
unresolved candidate.1 calibration meanings with:

- [Evidence and authority semantics](evidence-and-authority.md)
- [Maturity and transition predicates](maturity-and-transitions.md)
- [Conflict, precedence, and supersession rules](conflict-precedence-and-supersession.md)
- [Legitimacy crosswalk](legitimacy-crosswalk.md)
- [Readiness and immutable-binding rules](readiness-and-binding.md)
- [#77/#78 compatibility assessment](compatibility.md)

Calibration evidence is preserved under [calibration/](calibration/README.md).
The [gap-resolution register](gap-resolution-register.md) maps every candidate.1
gap to resolved or remaining evidence.

The [candidate.2 manifest](instrument-manifest.json) is the deterministic package
identity. It is not a frozen Instrument v1 identity.

## Binding rule

Candidate.2 cannot govern an audit. A later freeze requires all remaining gaps
to be resolved, two qualified independent calibration reviews or a preserved
adjudication, and a full containing commit from which every artifact and digest
reproduces. Instrument freeze still does not grant audit authorization.
