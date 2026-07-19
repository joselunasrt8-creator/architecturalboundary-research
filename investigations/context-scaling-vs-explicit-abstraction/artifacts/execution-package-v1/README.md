# Context-Abstraction Execution Package v1

This is a deterministic **pre-execution** package for the authoritative [preregistration](../../preregistration.md). It contains no model request, response, observation, result, or empirical dataset.

## Status

`NULL`. The repository supplies neither the frozen verbatim source corpus needed to construct `SP01`–`SP08` nor a candidate target registry from which the twenty-four eligible targets can be selected. The package deliberately records null fields instead of compressing, summarizing, substituting, or inventing those preregistered objects.

Run `python3 execution_package.py` to obtain the machine-readable readiness result. The command is offline and read-only. `hash-manifest.json` covers immutable package inputs; a hash manifest cannot include itself without a recursive preimage.

## Contents

- Source, target, answer-key, and scope-rubric registries record the explicit blockers.
- Prompt bindings and condition permutations materialize the immutable Section 8 controls.
- `execution_package.py` provides the offline literal evaluator and readiness validator.
- `audit-manifest-schema.json` defines the only allowable predeclared audit fields.

No file in this directory authorizes invocation.
