# Prospective protocol revisions for Run 3

These rules apply only to a separately authorized Run 3. They do not alter
either historical rejection.

## R1 — semantic-oracle derivation and adversarial preflight

**Current rule →** Freeze a focused test command with the objective.

**Observed failure mode →** Run 2's test required submodule expansion not
entailed by its frozen AST representation.

**Repository evidence →** `preregistration.md`, `t1-candidate.patch`, and the
focused raw log; conflict C-1 binds the discrepancy.

**Proposed prospective rule →** Before candidate generation, publish an oracle
table mapping every assertion to exact objective/contract text. For each
behavioral assertion, freeze at least two materially different conforming
fixtures/implementations and one nonconforming fixture; all conforming examples
must pass and every nonconforming example must fail. Resolve `ImportFrom`
semantics explicitly (including aliases, submodules, `*`, and relative imports)
or declare each case unmeasurable. Do not inspect a Run 3 candidate during this
preflight.

**Why discrimination improves →** The gate rejects semantic defects rather
than unstated instrument conventions. **Why validity is preserved →** Tests are
fixed before outcomes and include negative controls. **New risks →** Fixtures
may under-sample valid solutions. **Required validation →** Recorded fixture
matrix and independent entailment review with no unresolved assertion.

## R2 — exact identity chain

**Current rule →** Save patches/log hashes; commit only accepted states.

**Observed failure mode →** Run 2 has no candidate commit/tree, and neither
claimed freeze commit object is locally available.

**Repository evidence →** Both transition records and current object-database
checks.

**Proposed prospective rule →** Create an immutable candidate commit for each
attempt in an evidence-only ref/worktree. Record commit/tree, parent commit/tree,
patch SHA-256, environment fingerprint, command, exit, stdout/stderr SHA-256,
and `git diff --exit-code <candidate-tree>` immediately before and after each
gate. An accepted candidate commit (or a verified identical-tree acceptance
commit) is the sole parent/input for the next objective. Preserve freeze commit
objects in reachable history.

**Why discrimination improves →** Validated object equals classified object.
**Why validity is preserved →** Identity adds no acceptance leniency. **New
risks →** Administrative commits could contaminate measurement. **Required
validation →** Exclude only frozen evidence paths prospectively and verify tree
equivalence mechanically.

## R3 — gate roles and environment baseline

**Current rule →** Require focused and full commands; tolerate documented tool
limitations inconsistently across runs.

**Observed failure mode →** Run 1 mixed candidate and tokenizer failures; Run 2
full validation did not include the focused tests and lacked TeX.

**Repository evidence →** Run 1 execution record and Run 2 full raw log.

**Proposed prospective rule →** Freeze three separate decisions: scope/identity,
focused semantics, and full repository compatibility. All must pass. Before O1,
run every command twice on T0 in the frozen environment; require identical exit
and normalized output or freeze a narrowly enumerated non-candidate limitation.
A limitation may not mask a required check. No gate may be added, removed, or
reinterpreted after generation.

**Why discrimination improves →** Failure cause and gate role become explicit.
**Why validity is preserved →** Full validation is not weakened. **New risks →**
Strict reproducibility can block execution. **Required validation →** T0 logs,
tool versions/cache hashes, and a zero-exit full gate unless a preregistered
unavailable optional check is visibly non-fatal.

## R4 — one transcript-bound repair

**Current rule →** Run 1 allowed one repair; Run 2 allowed none.

**Observed failure mode →** Both first transitions stopped; policies are not
comparable and no trajectory formed.

**Repository evidence →** Both frozen intervention/stopping rules.

**Proposed prospective rule →** After the first candidate-related gate failure,
permit exactly one repair response from the same agent. Supply only the frozen
objective, candidate identity/patch, exact failing command, and complete frozen
output. Withhold structural results, researcher diagnosis, later objectives,
and edited tests. Commit the repair as a second candidate, rerun all gates in
the frozen order, preserve both attempts, and reject/stop on any further
failure. Retry without consuming repair only when output proves non-exercise.

**Why discrimination improves →** It models bounded feedback while retaining a
mechanical limit. **Why validity is preserved →** No discretionary hint or gate
change occurs. **New risks →** Attempts are dependent and the transcript may
leak implementation expectations. **Required validation →** Hash the exact
prompt/transcript and report attempt-level and transition-level results.

## R5 — cumulative measurement and stopping

**Current rule →** Three accepted transitions are required, with broad static
AST/manual measures.

**Observed failure mode →** No accepted comparisons; some claimed properties
are explicitly unmeasurable.

**Repository evidence →** Both results and structural artifacts.

**Proposed prospective rule →** Freeze 3 as the minimum and 4 as the maximum,
with all objectives ordered before execution. Measure every candidate for
evidence, but form adjacent/cumulative comparisons only from accepted states.
For every invariant freeze an executable predicate, positive/negative control,
observable domain, and materiality threshold. Do not reject an ordinarily valid
candidate for independent structural degradation unless the objective itself
prospectively makes that structure a task constraint. Fewer than three accepted
transitions is `EXPERIMENT_BLOCKED`, never no-drift evidence.

**Why discrimination improves →** Accumulation and limits are mechanically
distinguished. **Why validity is preserved →** Objectives, measures, and
thresholds cannot chase outcomes. **New risks →** Three remains a small sample
and narrow measures limit external validity. **Required validation →** Fixture
controls, deterministic repeat measurements, and identity-chain verification.

## Exact fair-chance protocol

Freeze repository/T0/environment; ordered O1–O4; semantic oracle matrix; focused
and full commands; scope rule; structural predicates/controls; one
transcript-bound repair; three-transition floor/four-transition ceiling; and
the taxonomy in this audit. For each objective: generate candidate commit →
bind identity → run scope/focused/full gates → optionally perform the single
bounded repair and rerun all gates → reject and stop on failure, otherwise
record structural evidence → accept exact tree → use it as next input. Do not
show structural outcomes before acceptance. Compare T0 with each accepted state
and the endpoint; constrain conclusions to frozen observables.
