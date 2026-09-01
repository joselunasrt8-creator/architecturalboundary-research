# Issue #110 prospective analysis freeze

This package resolves the highest-leverage *analysis-design* blockers without executing Issue #110. Every generated observation is marked `SYNTHETIC_REHEARSAL_ONLY`; it is fictional and cannot authorize empirical work.

## Frozen identities and preserved contract

`artifact-bindings.json` binds every committed byte in the protocol and preflight trees to commit `321f0c932937265accd76c0d6a69ca8232a2f7d9`. It preserves the LOW/HIGH paired crossover, binding definition, S01–S12, P1–P5, H0–H8/HM, five-category precedence, null/negative outcomes, Issue #109 non-circularity, and design-only authorization. Neither historical tree was edited.

## Estimands and computation

`estimands.json` defines the unit, numerator, denominator, pairing, missing/blocked/censored handling, aggregation, uncertainty, and meaningful effect for acceptance yield, throughput, time to valid, implementation/replacement binding, first failure, and interactions. Strata are reported before any cohort summary.

`results-schema.json` is the prospective record contract. `analysis.py` adds fail-closed semantic validation (complete LOW/HIGH pairs and invariant identities), computes deterministic summaries, applies the migration conjunction and frozen category precedence, and emits one allowed determination. Binding requires candidate and binding clauses plus a positive interval; a longest stage alone never qualifies.

Run:

```bash
python investigations/bottleneck-migration-110-analysis-freeze/analysis.py DATASET.json
python investigations/bottleneck-migration-110-analysis-freeze/simulate.py
python -m unittest discover investigations/bottleneck-migration-110-analysis-freeze -p 'test_*.py'
```

## Rehearsal

Thirteen numeric scenarios cover replicated migration, implementation dominance, proportional acceleration, precise null, opposite effect, repository/class specificity, failed manipulation, harness/environment artifacts, insufficient information, censoring, and non-global heterogeneity. `analysis-rehearsal-results.json` records expected and actual outcomes from the real analyzer.

## Precision and sample size

The 64-template/128-execution proposal is not prospectively justified across the frozen sensitivity regimes and has only two pairs per cell. Unknown baseline rates, paired correlation, heterogeneity and censoring mean no final N can honestly be frozen. The smallest current *candidate* for primary inference is 128 templates/256 executions under a defensible moderate regime. Interaction/external-validity claims require a separately sized candidate of at least 288 templates/576 executions, potentially 512/1024 conservatively. These are planning candidates, not authorization or a cost optimization.

## Amendment and boundary

`amendment-decision.json` proposes a separately identified amendment; it does not rewrite protocol v1.0.0. Production authorization still requires a complete 10,000-resample clustered bootstrap/mixed-survival implementation, the time-to-first-runnable manipulation check, outcome-blind nuisance calibration, cohort/environment/oracle/instrument/randomization freezes, and separate human authorization.

**Exact analysis-freeze determination: `ANALYSIS_FREEZE_COMPLETE`. Issue #110 remains `BOTTLENECK_EXPERIMENT_NOT_READY`. This determination does not authorize empirical execution.**
