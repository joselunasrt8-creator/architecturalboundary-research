# Issue 114 harness audit

## Scope and immutable boundary

This audit asks whether a future acceptance harness can discriminate cumulative
structural drift. It does not execute Run 3, infer hypothesis support, accept a
rejected candidate, or modify either prior evidence package. The smallest
mutation is this audit directory; production execution paths and dependencies
are unchanged.

## Phase 0 — checkout and evidence

The audited checkout began clean on branch `work` at commit
`16d1f5abfd7591c9a9880253370338e59de185ce`, tree
`2866c5885f9cc6a202cfd48e13fc028e2ff303e5`. There is no configured remote, so
this audit makes no claim about live GitHub or a branch named `main`. Local
history contains `d227e7fd204c83f989a7c84a0d767b2af69fba97` (#112 evidence)
followed by HEAD `16d1f5a...` (#113 evidence). Every expected primary artifact
is present; the exact discovered sets are bound in `source-bindings.json`.

The preregistration freeze commit claims (`39a6762` and `07157fb...`) are not
objects in this checkout. This limits independent verification of freeze timing
but does not erase the committed primary artifacts. Candidate patch hashes and
the common T0 commit/tree are verifiable. Run 1 has no raw log files; its
machine-readable execution record is the highest available execution source.

## Evidence precedence and conflicts

Frozen preregistration controls patch/commit evidence, then raw logs,
machine-readable records, contemporaneous documents, and summaries. Two
material conflicts are explicit in source binding C-1 and C-2.

Most importantly, Run 2's preregistered edge representation uses the absolute
AST import target. The focused test instead requires `from lib import helper`
to resolve to the extant `lib.helper` module. That is a reasonable possible
instrument design, but it is not entailed by the frozen representation or O1.
The preregistration controls; the historical rejection still stands.

## Independent reconstruction

### Run 1

Frozen O1 requested a reusable canonical JSON writer used by
`build_analysis.py` with unchanged CLI/output. The candidate added
`scripts/json_io.py`, delegated serialization, and added a focused test. The
required full suite first failed collection. The sole permitted repair changed
the import arrangement. The second full suite remained nonzero (227 passed, 5
failed, 50 errors): publication-manifest freshness was candidate-relevant, while
tokenizer downloads independently failed through the proxy. A later focused
diagnostic passed all eight tests but was not an acceptance gate. Frozen full
validation therefore rejected the candidate. T1 did not exist; T2/T3 were not
run; the stopping rule produced `EXPERIMENT_BLOCKED`. Structural inspection of
the rejected patch preserved INV-1–INV-3 but cannot enter a trajectory.

### Run 2

Frozen O1 requested a deterministic, read-only AST import snapshot CLI and
focused tests. The uncommitted candidate added the CLI/test. The focused command
returned 1 (two pass, one fail) on the `from lib import helper` expectation; the
full repository validator returned 0, with publication checks unavailable due
to missing TeX. The frozen no-repair rule required rejection and immediate
stop. No T1 commit/tree exists and O2–O4 were not run. The rejected candidate
added one isolated node, no edges or cycles, and violated no I1–I5 predicate.
The immutable determination is `EXPERIMENT_BLOCKED`.

## Gate semantics and compatibility

Run 1's focused checks cover task output/interface and allow multiple helper
implementations. Its full gate legitimately detected a repository consequence
missed locally. The environmental failures complicate causal attribution but do
not turn a nonzero required gate into acceptance.

Run 2's focused gate mixes task semantics with an unstated instrumentation
resolution rule. It does not prescribe the source implementation's file shape,
but it does prescribe the research instrument's behavior more narrowly than
the frozen measurement. A conforming implementation of the literal frozen AST
rule can therefore fail it. The focused and full roles remain conceptually
compatible as independent AND-gates; the focused oracle must be repaired before
future use, not weakened after a result.

## Trajectory and transition count

Neither run demonstrates practical trajectory formation: both stop at the
first rejection. That is evidence of low observed yield, not proof of
infeasibility. Four preordered incremental Run 2 objectives are plausible, but
the present oracle, unbound candidate/log identities, and environment gaps make
a legitimate T0→T1→T2→T3 insufficiently reproducible.

At least three accepted transitions is **arbitrary but defensible**, not known
necessary or sufficient. Three is the smallest sequence offering an initial
change plus two later opportunities for interaction/accumulation; it neither
guarantees cumulative degradation nor supports generalization. Retain it as an
eligibility floor, report the frozen maximum, and never interpret fewer than
three as absence of drift. A blocked experiment is not a null result.

## Repair-policy audit

No repair maximizes independence, makes stopping mechanical, and minimizes
researcher discretion, but models one-shot generation rather than ordinary
agentic development and sharply reduces trajectory yield. One bounded repair
is more realistic and can separate a correctable implementation defect from
substrate infeasibility, but introduces dependence and outcome-directed risk.

Either is scientifically usable if frozen. For Run 3, the protocol adopts one
repair because the research target is agentic software development rather than
first-sample accuracy. The same agent may receive exactly the failing command,
complete captured output, frozen objective, and candidate parent/patch; no
structural measurement, researcher hint, edited test, new objective, or other
gate output. It gets one response and one resulting patch. Both attempts remain
evidence. A second recorded failure rejects and stops. Environment-only retries
remain separate and require proof the candidate was not exercised.

## Structural discrimination

The measures discriminate only their enumerated static properties. They cannot
support claims about semantic cohesion, dynamic imports, runtime/data coupling,
or architectural quality generally. Run 3 must freeze executable fixtures and
violation predicates and scope its inference accordingly. Structural
measurement stays independent of task acceptance unless the task itself freezes
a structural contract; otherwise accepting only invariant-preserving candidates
would bias against observing drift.

## Conclusion

The architecture of prospective objectives, independent semantic and
repository gates, exact accepted-state lineage, and frozen structural measures
can fairly test a narrow cumulative claim. It requires the prospective changes
and preflight checks recorded here. Current FAIL/BLOCKED entry items mean this
audit is not authorization to execute.

**HARNESS_VALID_WITH_PROSPECTIVE_REVISIONS**
