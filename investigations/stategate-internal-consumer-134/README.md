# Issue 134 — StateGate internal-consumer audit

## Bounded result

**BLOCKED_BY_REPOSITORY_PERMISSIONS**

This is a same-owner internal-consumer audit, not independent adoption,
external validation, market validation, commercial validation, or evidence of
universal Continufy value. No StateGate integration was added and no existing
control was weakened. The machine-readable audit record is
[`evidence.json`](evidence.json).

## Inspected state and stale assumptions

The available checkout was inspected on 2026-09-08 at commit
`838163e917d72397e996e179f1cb0484572814c4` (tree
`995f814959cb39fc293d22323e1a5a751390af37`) on the local branch `work`. The
checkout has no configured Git remote and no local or remote-tracking `main`
ref. The validation workflows name `main` as their push and pull-request target,
but the current GitHub default branch could not be verified.

Requests for architecturalboundary-research Issue 134, StateGate Issue 66, and
repository metadata were denied (web access returned HTTP 401; direct GitHub
API access returned a proxy HTTP 403). The GitHub CLI had no authenticated host.
Consequently, assumptions that the issue text, its dependencies, StateGate's
measurement rubric and proof contract, the default branch, rulesets, required
checks, open pull requests, and StateGate's immutable revision were available
were stale for this execution environment. Repository history was available
through 2026-09-03, but repository-host state was not.

The blocker is load-bearing. Without the StateGate source/proof contract and a
verified full commit SHA, an integration could not satisfy the immutable-pin,
exact-state, canonical-proof, or fail-closed requirements. Without repository
host access, it also could not be installed as a required check, exercised on a
real pull request, or evaluated against branch protection. Inventing those
semantics locally would have broadened StateGate and would not test the stated
comparison.

## Baseline frozen before mutation

The repository baseline is the exact commit and tree above. Its executable
GitHub Actions controls are:

* `.github/workflows/validate.yml`, triggered for pushes and pull requests
  targeting `main`, with full-history checkout, Python 3.13, pinned Python
  dependencies, the pytest suite, repository validation, registry and derived
  artifact freshness checks, report and paper builds, publication-manifest
  verification, CI-bound B2 audit generation and artifact uploads, and
  whitespace checking;
* `.github/workflows/b2-publication-readiness.yml`, manually dispatched against
  `main`, which records repository/branch/commit/run identity, checks canonical
  paths, runs repository validators and the B2 audit, and uploads its reports;
* `ci/validate.yml`, which is explicitly a non-executable pointer rather than a
  duplicate workflow; and
* repository requirements pinning `jsonschema==4.25.1`, `pytest==8.4.2`, and
  `tiktoken==0.9.0`.

Native GitHub rulesets, protection, approval requirements, check enforcement,
and merge-queue behavior are `NOT_OBSERVED`, not absent. Historical active
review/reconstruction effort, ambiguity, rework, and change/merge latency are
also `NOT_MEASURED`: local commits do not establish those values, and no values
were invented.

## Narrow prospective boundary

If access is restored, the smallest defensible governed boundary is a pull
request that changes at least one already authoritative research object:

* frozen protocol or preregistration content;
* canonical dataset, analysis, retained-classification, or cohort-conclusion
  content;
* the publication-state manifest or publication-bound manuscript sources; or
* an explicitly frozen investigation artifact whose own contract prohibits
  mutation or requires an amendment.

Generated PDFs, ordinary documentation, tests, implementation scripts,
dependency housekeeping, and workflow maintenance do not qualify merely
because they are in this repository. Supporting files qualify only when the
same pull request changes an object in the boundary and they are evidence needed
to evaluate that exact mutation.

## Semantics and natural observations

No controlled VALID, bounded NULL, or changed-head test was run. Such tests
require the unavailable canonical StateGate executable/proof contract and can
only establish semantics, not workflow value.

Recent commits associated by their commit subjects with PRs 121, 124, 125, 128,
132, and 133 appear to involve frozen protocols, analysis freezes, calibration
evidence, or readiness packages. They are candidate natural changes only. They
were not admitted as observations because the PR head/base identities, workflow
runs, review reconstruction effort, proof artifacts, added latency, false
blocks/allows, and merge delay could not be inspected. The natural-observation
count is therefore zero. No PR was manufactured.

## Benefit, friction, and counterfactual

No incremental StateGate benefit was observed. Setup stopped before integration,
so added CI latency, maintenance cost, false blocks, false allows, duplicated
controls, corrections, and ambiguity removed are all `NOT_MEASURED`. The
observed friction is the inability to retrieve and pin StateGate or configure
repository-host enforcement; this is an environment/repository-permission
blocker, not evidence that StateGate intrinsically has excessive friction.

The counterfactual cannot be adjudicated empirically with zero eligible
observations. The existing workflow already records exact CI identity for the B2
audit and performs deterministic validation and freshness checks. A small
conventional path classifier plus evidence-export script could likely preserve
head/base/workflow/check metadata, but that is an explicitly untested inference.
It must not be attributed uniquely to StateGate. Whether StateGate adds useful
determination semantics or load-bearing enforcement remains unobserved.

## Evidence routing and next decision

This committed record is the only evidence artifact produced; no canonical
StateGate proof artifact exists. Posting it to StateGate Issue 66 and creating
or updating Issue 134's pull request were blocked by the same missing GitHub
authentication/network path. The intended evidence classification is exactly
`SAME_OWNER_INTERNAL_CONSUMER_EVIDENCE`.

The evidence does not currently justify a claim of value or progression based
on this consumer. Additional internal-consumer testing is justified only after
access permits the blocked audit inputs, immutable StateGate pin, exact PR-state
execution, proof retrieval, and at least one naturally occurring consequential
change. This determination should be superseded rather than rewritten if those
conditions are later met.
