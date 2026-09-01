# Run 3 entry conditions

Run 3 is **not authorized** by this audit. Authorization requires all conditions
below to be checked against preserved evidence before candidate generation.

- [ ] Exact immutable identities and existing paths for the frozen Issue 109
  preregistration, Run 1, and Run 2 are recorded.
- [ ] Candidate patches/trees, raw logs, execution records, rejection reasons,
  environments, and validation commands for both prior runs are present and
  hash-verified.
- [ ] Each task gate is mapped from a frozen objective to required behavior,
  semantics, interface, or explicitly required structure; no gate requires an
  merely expected implementation shape.
- [ ] The `from lib import helper` expectation is adjudicated from the frozen
  objective and instrument source, not from a later interpretation.
- [ ] At least two legitimate implementation shapes for each candidate objective
  are shown to be admissible, or exclusivity is justified by the frozen task.
- [ ] Focused and ordinary validation commands pass on the declared baseline and
  are executable in the frozen target environment.
- [ ] The deterministic failure taxonomy is frozen, includes evidentiary
  requirements, and produces one classification or explicit `UNCLASSIFIED`.
- [ ] Structural invariants, measures, sensitivity limits, and interpretation are
  frozen before candidate generation and do not themselves encode drift.
- [ ] Candidate selection does not prefer trivial changes or changes expected to
  create structural drift.
- [ ] The repair policy is frozen. If repair is permitted, eligibility,
  information available, mutation bounds, attempt count, unchanged validation,
  complete logging, and transition-independence treatment are specified.
- [ ] The stopping rule and treatment of rejected candidates are frozen; rejected
  candidates cannot be silently incorporated into later states.
- [ ] The minimum accepted-transition count is justified by the estimand and an
  explicit sensitivity/feasibility argument. The number three is not inherited
  merely from an earlier prompt.
- [ ] A dry run on nonexperimental fixtures demonstrates that the harness can
  distinguish all taxonomy classes without changing gates after outcomes.
- [ ] An independent reproducibility check confirms that the validated object is
  the executed object at each transition.
- [ ] The audit is rerun with the restored primary evidence and ends in either
  `HARNESS_VALID_FOR_RUN_3` or
  `HARNESS_VALID_WITH_PROSPECTIVE_REVISIONS`, with every stated revision frozen
  before Run 3.

Until every item is satisfied, audit completion is not execution authority.

**Final determination: `AUDIT_BLOCKED`**
