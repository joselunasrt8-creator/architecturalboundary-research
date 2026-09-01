# Run 2 results

## Actual trajectory

```text
T0
  → O1 candidate
  → focused validation FAIL (exit 1; 2 passed, 1 failed)
  → full ordinary validation PASS (exit 0)
  → candidate REJECTED
  → no T1
```

There are zero accepted transitions. The frozen stopping rule prohibited repair
after the recorded failure and prohibited execution of O2–O4. The target of
three to five accepted transitions was an experimental design target, not
permission to force acceptance.

## Local and cumulative structural comparison

No accepted adjacent comparison T0→T1 exists, and therefore no accepted
cumulative T0→Tn comparison exists. Both are `NOT_MEASURABLE`. The rejected O1
candidate added one isolated measured module, no dependency edges, no boundary
crossings, no cycles, and no frozen-invariant violation. This observation does
not enter an accepted trajectory. Coupling changed only by the isolated-node
count; runtime topology and responsibility migration beyond static/manual
inspection are `NOT_MEASURABLE` under the frozen representation.

It would be invalid to infer benign evolution, degradation, or preservation of
a sequence from this rejected patch. Topology change is not automatically
degradation, and full ordinary validation passing did not override focused task
failure.

## Counter-hypothesis and null evidence

- “All accepted agentic transitions preserve architecture” is not testable:
  there were no accepted transitions.
- “Ordinary validation prevents material degradation” is not supported or
  refuted: ordinary validation passed the rejected candidate, while the
  independent focused gate rejected it.
- The rejected candidate's structural difference was real but not degrading
  under I1–I5; it cannot support a trajectory-level benign-change claim.
- Structural evidence added no acceptance discrimination at T1 because task
  validation already failed.
- Whether the frozen invariants are too coarse remains unresolved.
- Cumulative effects are unmeasurable because no cumulative sequence formed.
- Equivalence to ordinary human-led software evolution remains untested.
- The experiment could not form the preregistered minimum of three accepted
  transitions.

## Run 1 versus Run 2

Run 1 remains unchanged:

```text
candidate → focused PASS → full validation FAIL → rejected
          → cumulative sequence unavailable → EXPERIMENT_BLOCKED
```

Run 2 produced a different gate ordering:

```text
candidate → focused FAIL → full validation PASS → rejected
          → cumulative sequence unavailable → EXPERIMENT_BLOCKED
```

Run 2 adds evidence unavailable from Run 1: choosing a substrate whose full
ordinary validator accepts the first candidate is insufficient to create a
legitimate transition when a prospectively frozen task gate detects incorrect
behavior. The runs are not pooled into stronger evidence about cumulative
structural drift. Neither run observed an accepted sequence.

## Limitations and governance boundary

The only available repository was a research repository, reducing external
validity. The AST model omits dynamic imports, relative imports, external
coupling, calls, and semantics. The full ordinary validator does not run this
new tool's focused tests, so the two gates discriminate different properties.
The candidate was not committed because it was rejected; its patch and hashes
provide identity but not a Git commit/tree identity. The agent implemented O1
once, so this run says nothing about model-to-model or attempt-to-attempt
variation. Missing TeX executables limited publication validation but did not
make the frozen ordinary gate fail.

Observation remains distinct from interpretation. Structural evidence grants
no authority. Validation grants no execution eligibility. This finding is not
a governance decision, and AI output is not executable authority.

## Final determination

EXPERIMENT_BLOCKED
