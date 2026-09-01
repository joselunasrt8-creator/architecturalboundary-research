# Run 3 corrective preflight amendment

This is a prospective correction to the merged PR #117 preflight. It preserves
that package byte-for-byte as historical v1 evidence but supersedes its effect
on execution readiness. For this review, v1 is
`PRELIMINARY_READY_PENDING_POST_MERGE_REVIEW_CORRECTIONS`.

The lineage is Issue #114 → PR #117 preflight v1 → post-merge methodological
review → this corrective amendment → final readiness determination.

## Corrections

The first reported gap is confirmed. V1's structural command runs the accepted
tree's `scripts/structural_snapshot.py`, although that file is candidate
modifiable. `independent_structural_measure.py` instead lives outside the O1–O4
scope, never imports or executes measured-tree code, and applies exactly one
content-bound implementation to T0 and every later accepted tree. Candidate
code is input, never the instrument. Its five observables and limitations are
frozen in `structural-measures.json`; structural results remain withheld,
independent non-gates.

The second gap is also confirmed. The replacement future-candidate `oracle.py`
adds direct black-box assertions for literal `ImportFrom` semantics (the target
of `from owned import helper` is `owned`), two exclusions in one invocation, a
self-loop, and both added and removed edges. `oracle-coverage.json` maps every
frozen O1–O4 requirement to an executable assertion. Assertions depend only on
objective semantics, explicit CLI contracts, or deterministic representation,
not implementation shape.

## T0 and experimental boundary

The independent instrument measured the historical T0 commit
`f8e5a2c88f2ae7154052ffd90e225b1c2f3ab166` and tree
`18cd9de245d2a0cdb73218ba500cc368485c71ac` externally. The canonical baseline
contains 35 nodes, 10 edges, no cycles, no unmeasurable files, and no enumerated
violations. This is administrative preregistered evidence, not T1 or an
experimental transition.

No Run 3 candidate was generated, candidate acceptance was not invoked, T1 was
not accepted, and no experimental structural outcome was produced.

## Freeze and readiness

`amendment.json` binds the v1 tree, historical evidence trees, inherited policy
files, corrected artifacts, T0 identity/output, and the artifact-set identity.
An execution session must verify every identity before generating O1; a mismatch
requires a new prospective preflight and means `RUN_3_NOT_READY`.

The complete Issue #114 boundary was recomputed after both corrections. The
result is 19 PASS, 0 FAIL, 0 BLOCKED. Therefore the corrective determination is:

**RUN_3_READY**

This determination does not execute or itself authorize hidden execution of
Run 3; execution remains a distinct future action.
