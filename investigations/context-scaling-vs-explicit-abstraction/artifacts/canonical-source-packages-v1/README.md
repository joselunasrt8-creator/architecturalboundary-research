# Canonical Source Packages v1

This directory is the Issue #96 construction boundary for `SP01` through `SP08`. It is separate from the merged `execution-package-v1` validator framework.

## Current state

- Option B corpus-selection protocol: **READY**
- Selection execution: **NOT_EXECUTED**
- Selection result: **NULL**
- `SP01`–`SP08` construction: **NOT_STARTED**

`source-selection-freeze.json` pins the repository corpus to one commit and freezes path discovery, ordering, eligibility, unit, provenance, duplicate, budget, leakage, first-eight assignment, and fail-closed rules. It contains no candidate manifest or source assignment.

`canonical_source_selector.py` is the deterministic reference implementation. Tests exercise it only with synthetic candidate-review records. This pull request does not enumerate or evaluate the real pinned corpus; that work belongs to the following reviewed milestone.

## Boundary

This milestone may construct and freeze canonical source packages only. It does not authorize target construction, answer keys, scope rubrics, abstraction generation, model invocation, experiment execution, or empirical evidence collection.
