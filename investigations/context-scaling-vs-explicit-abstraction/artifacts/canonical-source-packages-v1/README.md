# Canonical Source Packages v1

This directory is the Issue #96 construction boundary for `SP01` through `SP08`. It is separate from the merged `execution-package-v1` validator framework.

## Current state

- Option B corpus-selection protocol: **READY**
- Selection execution: **COMPLETE**
- Selection result: **NULL**
- `SP01`–`SP08` construction: **NOT_STARTED**

`source-selection-freeze.json` remains byte-identical to its merged PR #98 version. It pins the repository corpus to commit `ba18a99ab6276948aebf74f4240e5de75a30d62d` and freezes path discovery, ordering, eligibility, unit, provenance, duplicate, budget, leakage, first-eight assignment, and fail-closed rules.

`canonical_source_constructor.py` reads the pinned Git tree and pinned prompt bindings directly, produces the complete `candidate-review-ledger.json`, and validates those artifacts against `hash-manifest.json`. The execution reviewed all 81 path-eligible candidates in canonical order. Only four documents met every frozen eligibility rule, including the requirement for at least sixteen meaningful verbatim units:

- `docs/higher_order_abstraction.md`
- `docs/minimal_promotion_package.md`
- `docs/publication.md`
- `docs/reference-execution/v1.0/freeze-readiness-record.md`

The protocol requires eight eligible documents and explicitly returns `NULL` when fewer qualify. Therefore no assignments or package files were produced, and the execution-package source registry remains unchanged. Run the deterministic verification with:

```bash
python3 investigations/context-scaling-vs-explicit-abstraction/artifacts/canonical-source-packages-v1/canonical_source_constructor.py --check
```

## Boundary

This milestone may construct and freeze canonical source packages only after the frozen selection gate returns `READY`. It does not authorize target construction, answer keys, scope rubrics, abstraction generation, model invocation, experiment execution, or empirical evidence collection.
