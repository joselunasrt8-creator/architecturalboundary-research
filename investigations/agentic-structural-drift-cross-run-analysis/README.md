# Issue #109 cross-run analysis (Runs 1–3)

## Boundary and exact determination

This package is a bounded analysis of immutable evidence. It did not execute or
design Run 4, modify Runs 1–3, change a historical gate or classification,
accept a rejected candidate, or change any Issue #109 determination. Direct
GitHub issue retrieval was unavailable in this checkout (no remote or GitHub
credentials), so issue-level claims are limited to the checked-in artifacts
that bind themselves to Issues #109, #110, and #114. Repository artifacts—not
prompt summaries—control this analysis.

**Exact final determination: `CROSS_RUN_ANALYSIS_SUPPORTS_110_HANDOFF`.** Issue
#109 should pause for an independent #110 handoff; this is neither support nor
non-support for structural drift and is not proof of #110.

## Primary answer: why no accepted T1 formed

No single cause explains all three runs:

1. **Run 1:** the candidate passed eight focused/local checks, but the required
   full pytest gate remained nonzero after its one repair. Publication-manifest
   freshness was a candidate-relevant repository consequence. Independent
   tokenizer/proxy errors also kept the suite nonzero. The candidate was
   rejected, so T1 did not form.
2. **Run 2:** full ordinary validation passed, but the focused gate failed and
   the frozen no-repair rule rejected the candidate. Issue #114 later classified
   that exact assertion prospectively as `HARNESS_MISMATCH`; the focused oracle
   required an import-resolution behavior not entailed by the frozen objective
   and representation. The historical rejection remains immutable.
3. **Run 3:** the corrected entry boundary was **19 PASS / 0 FAIL / 0 BLOCKED**.
   Both immutable O1 candidates passed scope and failed the prospectively frozen
   oracle. The sole repair fixed canonical whitespace but still omitted the
   required `nodes` list. Exact identity, coverage, and raw output support the
   frozen `TASK_FAILURE` classification. Ordinary validation was not reached.

Thus the repeated surface result—generated patch, no accepted T1—arose from a
repository-wide validity failure with independent environment noise, a harness
mismatch, and a genuine task-contract failure. Repetition of
`EXPERIMENT_BLOCKED` is low observed trajectory yield, not a shared causal
mechanism and not a negative hypothesis result.

## Cross-run failure pattern and H1–H8

The comparable reconstruction is in `cross-run-matrix.json`; evidence-backed
ratings and the explicit rating standard are in `failure-analysis.json`.

| Explanation | Assessment | Bounded conclusion |
| --- | --- | --- |
| H1 candidate capability | `PARTIAL_SUPPORT` | Directly supported in Run 3, not a common explanation for Runs 1–2. |
| H2 harness mismatch | `SUPPORT` | Directly established for Run 2 by Issue #114; no retroactive acceptance. |
| H3 repository/system constraint | `SUPPORT` | Run 1 exposed a legitimate manifest-freshness consequence missed locally. |
| H4 environment | `PARTIAL_SUPPORT` | Contributed independently in Run 1, but did not solely control it or Runs 2–3. |
| H5 stopping sensitivity | `PARTIAL_SUPPORT` | Policies censored further attempts; likely eventual acceptance is not established. |
| H6 task-contract difficulty | `SUPPORT` | Ordinary implementation success and precise independent task semantics discriminated differently. |
| H7 substrate effect | `PARTIAL_SUPPORT` | One research repository is an external-validity confounder; no comparative effect is estimated. |
| H8 bottleneck migration | `PARTIAL_SUPPORT` | Pattern warrants a candidate hypothesis only; major rival explanations remain. |

The **strongest supported observation** is that code generation occurred in all
three runs, yet acceptance yield was zero because independently defined notions
of correctness did not all align or pass. The **strongest counter-hypothesis**
is that the pattern is produced by protocol/substrate heterogeneity—especially
Run 2's known harness mismatch, strict stopping, Run 1 environment noise, and a
single research repository—rather than migration of a general engineering
bottleneck.

## Counterfactual boundary

`counterfactual-analysis.json` labels every statement as `OBSERVED`,
`SUPPORTED_INFERENCE`, `SPECULATION`, or `NOT_DETERMINABLE`. Removing a gate
never retroactively creates a legitimate T1: it would change an immutable
AND-contract after observing the result. Run 1 would still fail without its
focused diagnostic; Run 2 would still fail without ordinary validation; and
Run 3 would still fail without ordinary validation. Run 3's outcome without
the focused oracle is not determinable because the ordinary gate never ran.
There is no preserved evidence that one more repair in any run likely would
have passed every gate.

## Structural-drift question remains unresolved

Every run has zero accepted transitions. Rejected-candidate structural
observations are not trajectory states. Run 3 correctly measured only T0 and
withheld structural measurement of rejected candidates. There is no adjacent
accepted T0→T1 comparison, no cumulative comparison, and no minimum trajectory.
Accordingly, the evidence supports neither presence nor absence of structural
drift, cannot assess cumulative preservation, and does not change any historical
`EXPERIMENT_BLOCKED` determination.

The following separations remain controlling:

- generated code ≠ task success;
- task success ≠ repository validity;
- repository validity ≠ structural preservation;
- structural preservation ≠ cumulative structural preservation;
- validation ≠ authority;
- blocked experiment ≠ negative hypothesis result;
- repeated observation ≠ general law; and
- Issue #109 evidence ≠ Issue #110 proof.

## Bottleneck-migration status

The proposed observation is promoted only to **`CANDIDATE_HYPOTHESIS`**. The
bounded cohort supplies repeated generated artifacts and distinct acceptance
failures, but it did not operationalize “abundant,” estimate acceptance
probability, compare baselines, or isolate multi-constraint satisfaction from
harness, environment, repair, task, and substrate effects. It therefore does
not meet the stated standard for `SUPPORTED_WITHIN_BOUNDED_COHORT` and cannot
be generalized beyond these runs.

## Run 4 decision

**`ISSUE_109_SHOULD_PAUSE_FOR_110`.** Run 4 was neither designed nor executed.
Another Issue #109 attempt is not justified merely as “try again.” Before it
can be reconsidered, independent work must resolve whether acceptance yield
remains low with prospectively aligned semantics, valid oracles, environment
readiness, explicit repository consequences, comparable repair budgets, and
bound candidate identities. A later Run 4 would need to name a structural
uncertainty that another accepted trajectory can discriminate.

## Bounded Issue #110 handoff

### Transferable observations

- Each run generated a candidate artifact; none established T1.
- Focused success did not imply repository validity (Run 1), and repository
  validity did not imply focused acceptance (Run 2).
- A corrected prospective oracle discriminated two Run 3 candidates, including
  one after repair.
- Gate order and repair limits censored later evidence.

### Non-transferable observations

- The three blocks do not prove Issue #110, abundance, causal migration, model
  incapability, or a general engineering law.
- Run 2's failed assertion cannot be treated as candidate task failure.
- Rejected-candidate structural findings cannot become accepted trajectory data.
- Nothing here supports or refutes structural drift or modifies #110's
  independently specified hypothesis.

### Candidate variables and possible measurements

- **Variables:** objective entailment clarity, oracle validity/independence,
  number and diversity of candidates, repair budget, gate order, repository
  consequences, environment readiness, task semantic precision, repository
  type, and context supplied.
- **Measurements:** candidates generated per fixed budget; focused/full/joint
  pass rates; first-failure gate; repair-to-acceptance curve; error-category
  transitions; time/tokens to first all-gates pass; inter-rater entailment
  agreement; environment-only failure rate; and cross-repository yield.
- **Confounders:** known-oracle exposure, post-hoc gate edits, correlated gates,
  candidate selection, stopping censoring, model/harness changes, task
  heterogeneity, repository familiarity, and unavailable dependencies.
- **External validity:** one model/harness family, one research repository,
  three O1 attempts, heterogeneous protocols, and no human or alternative-model
  control.

Issue #110 must independently preregister and test what “abundant” means,
whether multi-constraint satisfaction is actually the rate-limiting variable,
how it compares with generation capacity and baselines, and whether the effect
replicates across tasks and repositories. It must be able to reject bottleneck
migration rather than absorb every blocked outcome as confirmation.

## Artifact map and immutability checks

- `cross-run-matrix.json`: all fourteen requested fields per run.
- `failure-analysis.json`: H1–H8 ratings and path-level evidence.
- `counterfactual-analysis.json`: labeled observed facts and inferences.
- `hypothesis-assessment.json`: candidate-hypothesis decision and standard.
- `run4-decision.json`: pause decision and the uncertainty required for future
  reconsideration.

Historical identities were checked against the execution records and Run 3's
pre-execution binding report. Final validation additionally verifies that the
Git diff contains only this new directory; therefore no historical evidence,
Run 4 artifact, or Issue #109 determination was mutated.
