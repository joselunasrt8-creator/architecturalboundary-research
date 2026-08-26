# Candidate.2 Compatibility Assessment

## Issue #77

Candidate.1's execution-record container remains the controlling record shape.
Every controlled field now resolves to candidate.2 semantics:

| #77 field family | Candidate.2 owner | Compatibility |
| --- | --- | --- |
| Evidence class and source authority | `evidence-and-authority.md` | Semantically defined |
| Claim type and maturity | `maturity-and-transitions.md` | Track mapping and predicates defined |
| Coverage and negative evidence | Candidate.1 record contract plus candidate.2 evidence/maturity rules | Defined without semantic-completeness inference |
| Boundary decomposition and promotion | Candidate.1 specification/record contract plus evidence predicates | Human judgment retained |
| Stopping, validity, outcome | Candidate.1 specification | Compatible |
| Identity, rerun, supersession | Candidate.2 conflict and readiness contracts | Compatible |

Assessment: `ISSUE_77_SEMANTICALLY_COMPATIBLE`.

## Issue #78

Candidate.2 supplies the per-class capabilities/incapabilities, authority
contract, claim-track mapping, state predicates, conflict rules, negative and
contradictory effects, promotion boundary, legitimacy crosswalk, and calibration
fixture required by #78.

The controlled semantic mapping is complete, but the required independent
calibration review and immutable exemplar evidence are not. Assessment:
`ISSUE_78_SEMANTICS_MATERIALIZED_CALIBRATION_INCOMPLETE`.

## Candidate.1 supersession

Candidate.2 does not edit candidate.1. On a future valid freeze, candidate.2's
evidence/authority, maturity, conflict, legitimacy, readiness, and compatibility
surfaces would supersede candidate.1's unresolved calibration and compatibility
surfaces. Candidate.1's specification and execution-record container remain
normative dependencies unless a later consolidated version replaces them.

Candidate.1's manifest, content digest, #106 determination, and gap register
remain historical evidence.
