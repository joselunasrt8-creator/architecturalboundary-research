# Issue #110 Prospective Amendment 001

This separately versioned package implements `ISSUE-110-PROSPECTIVE-AMENDMENT-001` after the prospective analysis freeze. It does **not** rewrite protocol v1.0.0, execute Issue #110, select tasks, generate candidates, inspect empirical outcomes, or authorize execution.

## Historical identity and amendment boundary

`artifact-bindings.json` records the canonical merged commit, Git subtree, current subtree, blob, and SHA-256 identity for every file in the protocol, preflight, and analysis-freeze inputs. Those trees are immutable historical inputs. `amendment.json` records each original rule, defect, prospective revision, scientific justification, and interpretive effect, and affirms that no Issue #110 outcome informed this amendment.

## Production machinery

`power-engine.py` is a fixed-seed (`11020260901`) Monte Carlo sensitivity engine. It executes 10,000 replicates for every combination of four candidate designs and three prospective nuisance regimes (120,000 total). It models paired LOW/HIGH assignments, repository clusters, task class, difficulty, within-pair correlation, repository/task heterogeneity, attrition, environment loss, censoring, acceptance yield, throughput, time to valid, and conjunctive migration. `power-results.json` is machine-readable and binds the exact engine and canonical configuration by SHA-256. Its values are synthetic prospective assumptions, never nuisance estimates or empirical findings.

`production_analysis.py` freezes fail-closed executable interfaces for repository-outer/pair-inner hierarchical bootstrap inference, paired acceptance yield, throughput, tie-grouped Kaplan-Meier restricted-mean time-to-valid with right censoring, sharp-null repository-cluster randomization tests, repository-by-task stratification, difficulty retention, interactions, Holm correction, uncertainty intervals, binding stages, migration conjunction, domain dependence, and determination precedence. It refuses fewer than 10,000 bootstrap draws rather than silently substituting a simpler method.

## Manipulation and future contract

`manipulation-check.json` operationalizes a runnable candidate before execution and freezes checks A–D. `results-schema-amendment.json` requires content hashes, build/gate timestamps, S05 entry, configuration identity, and AI-use stages. A failed check maps only to `BOTTLENECK_MIGRATION_INDETERMINATE`; it cannot count for or against migration.

## Calibration, N, and readiness

`nuisance-calibration-contract.json` separates external data, synthetic assumptions, pre-study calibration, and prohibited empirical Issue #110 outcomes. Legitimate bounds are not currently available. Therefore `sample-size-freeze-rule.json` freezes the deterministic future selection procedure but reports exactly `FINAL_N_NOT_YET_FREEZABLE`; no 256, 576, or 1,024-execution design is automatically selected. Primary, repository-interaction, task-class-interaction, and broader-validity requirements remain separate and cluster-aware.

`synthetic-validation.json` labels all fifteen validation scenarios unmistakably non-empirical. `readiness-impact.json` reports remaining conditions individually. Amendment implementation is complete, but repositories, templates, final N, environment, instruments, oracles, randomization, operators/adjudicators, AI configuration/isolation, and separate authorization remain blocked.

Run:

```bash
python investigations/bottleneck-migration-110-amendment-001/power-engine.py
python -m unittest discover investigations/bottleneck-migration-110-amendment-001 -p 'test_issue110_amendment001.py'
```

**Exact amendment determination: `AMENDMENT_001_COMPLETE`. Current Issue #110 readiness: `BOTTLENECK_EXPERIMENT_NOT_READY`. Neither determination authorizes empirical execution.**
