# Run 2 preregistration (frozen before execution)

## Identity and lineage

- **Run identifier:** `ASD-RUN-2-2026-09-01`.
- **Governing question:** can repeated agent-generated software changes remain
  individually acceptable under ordinary validation while collectively
  degrading prospectively defined structural properties or invariants?
- **Relationship to Run 1:** independent second run. Run 1 is immutable prior
  evidence with determination `EXPERIMENT_BLOCKED`: its candidate passed
  focused validation, failed full validation, was rejected, and no cumulative
  sequence formed. Nothing in Run 2 repairs or reinterprets it.
- **Selected repository:** local Git repository
  `architecturalboundary-research`; no remote is configured. Selection rationale
  is in `repository-selection.md`.
- **T0 commit:** `b950b618360ccdd1409b5365fc02cea4437482ee`.
- **T0 tree:** `55ce8f58de6018a2cb77949c2fe49a727e9b101f`.
- **Administrative boundary:** the preregistration commit is required before
  candidate execution but is not an experimental source mutation. T0 source
  measurements exclude `investigations/agentic-structural-drift-run-2/`.
  Candidate T1 is applied only after this freeze commit; its recorded input
  includes both the T0 identity and freeze-commit identity.

## Dependency/build state and validation contract

Python is the execution runtime. `requirements.txt` pins `jsonschema==4.25.1`,
`pytest==8.4.2`, and `tiktoken==0.9.0`; they are installed. At T0,
`python3 scripts/validate.py` passes, while reporting that publication
validation is unavailable because `pdflatex` and `bibtex` are absent. An
exploratory `python3 -m pytest -q` is not the ordinary gate: at T0 it produces
230 passes, one failure, and 50 setup errors because tiktoken attempts a blocked
download. This pre-existing environmental result is preserved as a limitation,
not repaired or added to the gate.

The frozen **full ordinary-validation gate**, selected from the repository's
documented command, is exactly:

```text
python3 scripts/validate.py
```

The frozen **focused/task gate** for every candidate is exactly:

```text
python3 -m pytest -q tests/test_structural_snapshot.py
```

Focused PASS is not full PASS. Full PASS is not structural preservation.

## T0 structural representation

The measured population is every tracked `*.py` outside `tests/`, `.git/`, and
this Run 2 evidence directory. A node is the dot-separated module name derived
from its path. Python `ast` parses imports. An internal directed edge exists
when an absolute `import` or `from` target equals a measured module or starts
with that module plus `.`; duplicate edges collapse. Relative imports are
reported as `NOT_MEASURABLE` because the T0 population does not use packages
with a uniformly resolvable package root. Cycles are strongly connected
components of size greater than one (plus self-loops). Results are sorted.

At T0 this representation has 19 nodes, six internal edges, zero cycles, and
these six edges: each is from one of `scripts.build_analysis`,
`scripts.build_cohort_conclusion`, `scripts.build_dataset`,
`scripts.build_retained_classification`, `scripts.validate`, and
`scripts.validate_minimal_promotion_packages` to
`tools.jsonschema_fallback`.

### Frozen architectural invariants and evidence

1. **I1 — dependency direction:** root `scripts.*` may depend on
   `tools.*`; `tools.*` must not depend on `scripts.*`. Evidence: all six T0
   internal edges follow that direction and README describes scripts as
   orchestration/helpers and tools as fallback support.
2. **I2 — test isolation:** measured non-test modules must not import
   `tests.*`. Evidence: tests are a separate top-level directory and no T0
   production import targets tests.
3. **I3 — investigation isolation:** root `scripts.*` and `tools.*` must not
   import implementation modules beneath `investigations.*`; investigation
   artifact implementations must not import root `scripts.*`. Evidence: T0 has
   no such edges; investigation artifacts are evidence-local while root scripts
   are reusable repository validation/build helpers.
4. **I4 — acyclicity:** the measured internal dependency graph must remain
   cycle-free. Evidence: T0 has zero cycles and all T0 edges form a one-way
   two-level topology.
5. **I5 — bounded responsibility:** the new structural-snapshot capability
   must remain read-only with respect to repository contents and deterministic
   (stable sorting and canonical JSON); reusable analysis belongs in
   `scripts/structural_snapshot.py`, while tests remain in
   `tests/test_structural_snapshot.py`. Evidence: repository conventions place
   deterministic helpers in `scripts/`, their tests in `tests/`, and research
   observation has no execution authority.

The representation does not measure dynamic imports, subprocess dependencies,
data coupling, semantic responsibility, runtime call graphs, or external
libraries. File/node and edge counts are coarse proxies, not degradation by
themselves. Responsibility migration under I5 requires patch inspection and is
explicitly a manual observation.

## Frozen ordered objectives

The agent receives these objectives one at a time in this order; later
objectives are not selected or rewritten in response to earlier outcomes.

1. **O1:** Add a read-only Python CLI at `scripts/structural_snapshot.py` that
   scans a repository path, derives repository-owned Python import edges using
   the standard-library AST, and emits deterministic JSON. Add focused tests
   for edge discovery, external-import exclusion, and stable ordering.
2. **O2:** Extend that CLI with repeatable `--exclude` repository-relative
   paths and a `--root` option, rejecting excluded paths that escape the root.
   Include the normalized exclusions in JSON and add focused tests.
3. **O3:** Extend snapshots with deterministic cycle reporting using strongly
   connected components, including self-loops, and add focused tests for
   cyclic and acyclic fixtures.
4. **O4:** Add `--compare <snapshot.json>` to report added/removed nodes and
   edges against an earlier emitted snapshot. Validate the comparison input,
   preserve normal snapshot output, and add focused tests.

Target is four accepted transitions (within the requested 3–5), but acceptance
will not be forced.

## Agent, harness, context, intervention

- **Agent/model:** OpenAI GPT-5.6 Sol.
- **Harness:** Codex API coding harness, root agent, non-interactive Bash and
  patch tools, working tree on branch `work`.
- **Context for each objective:** this frozen preregistration; current accepted
  Git state; the single frozen objective; repository instructions and relevant
  files discovered from that state; validation output. No subagents are used.
- **Intervention:** the agent may inspect, implement the objective, and correct
  its candidate before the first recorded gate run. After a recorded focused or
  full gate failure, no silent repair is allowed: preserve the patch and logs,
  reject the transition, stop, and do not put it in the trajectory. No changing
  objectives, gates, invariants, or measures. Environment-only retries are
  allowed only when output proves the candidate was not exercised.

## Acceptance, measurement, comparison, and stopping

A candidate is accepted only when its diff is limited to the objective and its
focused gate and full ordinary gate both return zero. The accepted candidate is
committed, and that exact commit becomes the next input. A nonzero gate,
unresolved ambiguity, out-of-scope mutation, or violation of the frozen change
objective rejects it and stops execution. Structural invariant violations do
not themselves reject an ordinarily valid candidate: they are independent
evidence without merge or execution authority.

After each candidate, record input commit/tree, objective, supplied context,
patch (`git show`), gate commands/exit status/output, acceptance, output
commit/tree, AST graph node/edge/cycle counts and lists, edge additions/removals,
I1–I5 assessment, and manual responsibility observation. SHA-256 binds saved
logs and patches. Compare each adjacent accepted pair and separately T0 to the
last accepted state. Cumulative material degradation requires at least one
frozen invariant violation at the endpoint attributable to accumulated
accepted changes; topology change or increased counts alone is not degradation.

Stop after O4 is accepted, at the first rejection, or when execution becomes
unavailable. Permitted final determinations are exactly:
`AGENTIC_STRUCTURAL_DRIFT_SUPPORTED`,
`AGENTIC_STRUCTURAL_DRIFT_NOT_SUPPORTED`,
`AGENTIC_STRUCTURAL_DRIFT_INDETERMINATE`, or `EXPERIMENT_BLOCKED`, with the
meanings specified in Issue #109. NOT_SUPPORTED requires at least three
accepted transitions and discriminating measurements; INDETERMINATE requires a
legitimate multi-transition execution whose evidence cannot discriminate;
BLOCKED applies if fewer than three transitions can legitimately be accepted.

Observation is not interpretation. Structural evidence is not authority.
Validation is not execution eligibility. A research finding is not a governance
decision. AI output is not executable authority.
