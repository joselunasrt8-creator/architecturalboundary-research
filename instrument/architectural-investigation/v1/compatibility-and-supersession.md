# Instrument v1 Compatibility and Supersession

## Issue #77 execution-record compatibility

| #77 contract surface | Candidate path and section | State |
| --- | --- | --- |
| Canonical execution package | `execution-record-contract.md` — Required package | Materialized |
| Execution identity | `execution-record-contract.md` — Execution identity | Materialized |
| Scope and coverage | `execution-record-contract.md` — Scope and coverage declaration | Materialized; controlled measures unresolved in #78 |
| Inspection log | `execution-record-contract.md` — Inspection log | Materialized |
| Claim ledger | `execution-record-contract.md` — Claim-level evidence ledger | Materialized; controlled semantics unresolved in #78 |
| Boundary decomposition | `execution-record-contract.md` — Boundary-decomposed finding | Materialized |
| Four outputs | `execution-record-contract.md` — Four output surfaces | Materialized |
| Negative evidence | `execution-record-contract.md` — Negative, missing, and contradictory evidence | Materialized |
| Stopping determination | `specification.md` and `execution-record-contract.md` | Materialized |
| Static disclosure | `execution-record-contract.md` — Static-audit disclosure | Materialized |

The candidate removes #77's competing eight-dimension maturity definition and
delegates controlled maturity, evidence, authority, coverage, and promotion
semantics exclusively to the #78-derived calibration surface. This implements
the documented #77/#78 ownership boundary without claiming the #78 gaps are
resolved.

## Issue #78 compatibility

The candidate preserves every vocabulary, reachability ladder, coverage
measure, promotion predicate, independence invariant, and ContinuityOS-derived
dimension explicitly recorded by Issue #78 and the #59 calibration comments.
It marks the missing definitions and crosswalk as blocking rather than choosing
them. Compatibility is therefore `STRUCTURALLY_MAPPED_SEMANTICALLY_UNRESOLVED`.

## Upstream immutable coordination dependencies

The previous readiness record binds these external Continufy-owned references:

| Dependency | Commit | Git blob | Role |
| --- | --- | --- | --- |
| Research & Development Instrument `1.0.0` | `398098c231530379769c2c0660f1f3217d5e7b62` | `27a9d9ab4904182b31d63a8f7c43f6a8b8927d9a` | Common stage and preservation contract; not local instrument authority |
| Coordination contract | `398098c231530379769c2c0660f1f3217d5e7b62` | `327c304e222bfab75d0aa9bbf3a19bcea85f217b` | Keeps execution and determinations repository-local |
| Downstream execution-plan template | `398098c231530379769c2c0660f1f3217d5e7b62` | `45dcf7f58e89713eae9c3a118e3add4d4fd36a73` | Record-shape guidance; not substitute semantics |

These dependencies remain external and do not cure the local calibration gaps.

## Version semantics

- `1.0.0-candidate.1` identifies this first repository-owned materialization.
- Candidate identifiers are never executable audit identities.
- A change to unresolved controlled semantics requires a new candidate identity.
- `1.0.0` may be assigned only after all gaps are resolved, the package is
  independently reviewed, a containing commit and reproducible digests are
  recorded, and the readiness determination is `INSTRUMENT_V1_FROZEN_READY`.
- After freeze, semantic changes require a new version; observations from an
  execution cannot amend the version governing that execution.

## Supersession lineage

- The July record `ABR-RE-V1-FREEZE-2026-07-19` remains immutable evidence that
  its assessed revision was `BLOCKED`.
- The Issue #106 freeze record supersedes that record only for the current
  instrument-materialization assessment. It does not rewrite the earlier fact.
- The blocked Issue #84 package `AII-SAF-20260825-001` remains `BLOCKED` /
  `NOT_REACHED` and is not migrated, upgraded, or made successful.
- This candidate supersedes no frozen instrument because no prior local frozen
  instrument exists.
- A later ready instrument must name this candidate and freeze record in its
  `supersedes` lineage and must use a fresh Issue #84 execution ID.

## Authorization boundary

Availability of a future frozen package proves only that an instrument can be
bound. Audit authorization, target binding, operator authority, and permitted
mutation remain separate execution inputs.
