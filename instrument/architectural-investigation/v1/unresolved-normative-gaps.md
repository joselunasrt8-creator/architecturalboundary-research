# Instrument v1 Unresolved Normative Gap Register

Every entry is blocking for `INSTRUMENT_V1_FROZEN_READY`. The register preserves
the gaps already identified by repository evidence and does not resolve them by
author inference.

## `AII-V1-GAP-001` — No `IMPLEMENTATION_READY` determination

Issue #59's last recorded review and priority states are
`SPECIFICATION_REVISION_REQUIRED`. Closing the issue supplied no later
evidence-bound `IMPLEMENTATION_READY` determination.

## `AII-V1-GAP-002` — Evidence-class definitions incomplete

Issue #78 enumerates evidence classes but does not define for every class what
it can and cannot support, direct/inferential status, revision-binding rule,
execution implication, and conflict handling.

## `AII-V1-GAP-003` — Source-authority contract incomplete

Issue #78 describes a twelve-level vocabulary but enumerates eleven values and
does not provide complete per-value capability or precedence rules.

## `AII-V1-GAP-004` — Maturity predicates incomplete

The maturity tracks and state names exist, but evidence predicates for every
state and the claim-type-to-track decision table do not.

## `AII-V1-GAP-005` — Conflict resolution undefined

The five conflict categories are named, but deterministic precedence and human
review boundaries are not defined. Missing and contradictory evidence lack a
complete state-by-state effect.

## `AII-V1-GAP-006` — Legitimacy dimensions lack a crosswalk

The ContinuityOS additions are not integrated with the general tracks,
evidence classes, source-authority classes, or coverage measures:

- legitimacy maturity: `NORMATIVE_INVARIANT`,
  `RUNTIME_LOCAL_ENFORCEMENT`, `REPOSITORY_WIDE_ENFORCEMENT`,
  `INFRASTRUCTURE_ENFORCEMENT`, `EXTERNALLY_VERIFIED_ENFORCEMENT`,
  `NON_BYPASS_CLOSURE`;
- canonical-source conflict: `SINGLE_CANONICAL_SOURCE`,
  `MULTIPLE_COMPATIBLE_PROJECTIONS`, `SPLIT_OPERATIVE_AUTHORITY`,
  `DECLARED_CANONICAL_BUT_NOT_CONSUMED`, `CANONICAL_SOURCE_UNRESOLVED`;
- containment reachability: `FAILURE_RESPONSE_DECLARED`,
  `INTERCEPTION_POINT_IDENTIFIED`, `ENFORCEMENT_IMPLEMENTED`,
  `ENFORCEMENT_SELECTED`, `FAILURE_OBSERVED`, `RESULT_PRESERVED`,
  `EXTERNAL_BYPASS_EXCLUDED`; and
- sovereignty coverage: `REPOSITORY_CONTROLLED`, `EXTERNALLY_CONFIGURED`,
  `EXTERNALLY_ATTESTED`, `EXTERNALLY_VERIFIED`, `BREAK_GLASS_ONLY`,
  `UNRESOLVED`.

## `AII-V1-GAP-007` — Reproducibility test absent

No version-controlled classification fixture with predefined correct
classifications and dispositions exists for independent-auditor comparison.

## `AII-V1-GAP-008` — Calibration exemplars not reconciled

The required mappings to Structural Analysis Foundations, SYNAPSE, MindShift,
and the ContinuityOS revision are not preserved as a reviewed calibration set.
The blocked #84 package cannot substitute for such a set.

## `AII-V1-GAP-009` — No immutable containing commit

The candidate files exist only in the Issue #106 worktree. No accepted Git
commit contains the package, so the minimum exact repository-commit identity
required by Issue #106 cannot yet be recorded.

## `AII-V1-GAP-010` — Independent completion review absent

The completion tests in #59 and #78 require reproducible independent review.
No preserved independent result establishes consistent application of the
controlled semantics.

## Consequence

```text
Unresolved calibration semantics
or absent IMPLEMENTATION_READY
or absent containing commit
=> INSTRUMENT_SPECIFICATION_REVISION_REQUIRED
=> no executable Instrument v1 identity
=> fresh Issue #84 rerun not legitimately bindable
```
