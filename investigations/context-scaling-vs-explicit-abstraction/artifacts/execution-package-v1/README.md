# Context-Abstraction Execution Package v1

This is a deterministic **pre-execution** package for the authoritative [preregistration](../../preregistration.md). It contains no model request, response, observation, result, or empirical dataset.

## Status

`NULL`. The repository supplies neither the frozen verbatim source corpus needed to construct `SP01`–`SP08` nor a candidate target registry from which the twenty-four eligible targets can be selected. The package deliberately records null fields instead of compressing, summarizing, substituting, or inventing those preregistered objects.

Run `python3 execution_package.py` to obtain the machine-readable readiness result. The command is offline and read-only. `hash-manifest.json` covers immutable package inputs; a hash manifest cannot include itself without a recursive preimage.

Readiness is staged. `SOURCE_STAGE_READY` validates the frozen source/target rosters, prompts, source-input budgets, governed hashes, condition order, scorer binding, and source-audit capability without requiring any future source output. `TARGET_STAGE_READY` additionally requires the retained Stage-1 responses, C2/C4 abstraction artifacts, target-package accounting, and target-audit capability. Overall `READY` requires target-stage readiness.

## Contents

- Source, target, answer-key, and scope-rubric registries record the explicit blockers.
- Prompt bindings and condition permutations materialize the immutable Section 8 controls.
- `execution_package.py` provides the offline literal evaluator and readiness validator.
- `hash-manifest-anchor.json` binds the governed manifest to the repository commit immediately preceding the anchor's one-time introduction, preventing post-freeze manifest regeneration from preserving readiness.
- `audit-manifest-schema.json` defines strict, closed nested records for the honest pre-execution `NULL` determination and for execution-bound audit entries; it rejects missing, mistyped, or undeclared audit data.

No file in this directory authorizes invocation.
