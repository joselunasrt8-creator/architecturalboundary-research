# Issue #110: frozen bottleneck-migration protocol

## Status and authorization

**Readiness: `BOTTLENECK_EXPERIMENT_NOT_READY`.** This package is a prospective
protocol, version 1.0.0. It contains no study results and reports no support or
rejection for Issue #110. No empirical execution occurred. Protocol design is
authorized; task execution, AI invocation, candidate generation, study-gate
execution, deployment, and data collection are not. A human must separately
authorize execution after every entry condition in `entry-conditions.json` is
satisfied.

## Question and design

The primary question is: **As implementation capacity increases, does the
binding constraint on reliable software-development throughput move away from
code production toward other stages?** Every frozen rule is machine-readable:

| Artifact | Frozen content |
| --- | --- |
| `protocol.json` | scope, artifact links, exclusions, and source boundary |
| `hypotheses.json` | target and live H0–H8 alternatives |
| `bottleneck-definition.json` | time, failure, rework, throughput, and coordination criteria |
| `workflow-stages.json` | twelve stages and clock/transition rules |
| `experimental-contrast.json` | randomized paired LOW/HIGH implementation contrast |
| `cohort-design.json` | repositories, task classes, difficulty bands, inclusion and allocation |
| `measurements.json` | primary, secondary, and diagnostic observables |
| `failure-taxonomy.json` | ordered, adjudicated failure classes |
| `stopping-rule.json` | execution/study caps and evidence lock |
| `analysis-plan.json` | estimands, stratification, intervals, interactions, and artifact checks |
| `determination-rules.json` | exclusive future outcome categories and precedence |
| `entry-conditions.json` | environment, authorization, and readiness gate |

## Operational bottleneck definition

A longest stage is only a time concentration. A stage binds only when it meets
both the candidate threshold and the marginal constraint criterion frozen for
a bottleneck type. Failure and throughput are primary; time, rework, and
coordination are secondary. Cohort binding must replicate in at least two
repositories and two task classes without an opposite interaction.

Migration requires all of the following: implementation binds in LOW; it stops
binding in HIGH; a named non-implementation stage newly binds; the HIGH
manipulation is realized; and harness, measurement, task mix, and environment
checks do not explain the pattern. Thus implementation remaining binding,
proportional speedup, repository-specific effects, artifacts, limitations, and
insufficient evidence are independently admissible.

## Implementation abundance and contrast

The blocked paired crossover compares the same frozen task and 120-minute
implementation cap. LOW provides one qualified human with ordinary
non-generative tools and at most two candidates. HIGH provides the same
qualification pool plus a frozen AI coding agent/configuration and up to four
isolated candidates. AI help outside implementation is prohibited in both
conditions. Assigned abundance is therefore increased implementation tooling
and doubled candidate capacity—not a label inferred from a successful result.
It is realized only when HIGH produces at least two runnable candidates in 70%
of eligible executions, has median time to first runnable candidate no more
than 70% of LOW, and preserves the frozen agent configuration and caps.

## Cohort and measurement

Before assignment, freeze 64 task templates: four repositories × four task
classes × two difficulty bands × two templates. Each template runs from a reset
commit in both conditions (128 planned executions). The repositories span at
least two domains and two toolchain families. The task classes are localized
defect repair, cross-module feature, dependency/API adaptation, and
structural/refactoring change; both moderate and difficult bands remain.
No post-outcome substitution is allowed. Valid failures, nulls, difficult
implementation, and negative cases remain in analysis. No Continufy component
is required.

Primary measurements are all-gates-valid throughput, acceptance yield, binding
status, time to an all-gates-valid result, and first-failure stage. Secondary
records include per-stage elapsed/active/wait time, attempts, candidate count,
gate results, rework count/origin, cycle time, stage proportions, handoffs, and
coordination. Diagnostics isolate instrumentation burden, environment events,
harness/oracle validity, tool usage, gate censoring, and identities.

## Live counter-hypotheses

- **H0:** no binding-bottleneck migration.
- **H1:** implementation remains dominant under higher capacity.
- **H2:** stages accelerate proportionally without relative migration.
- **H3:** measurement overhead produces the appearance.
- **H4:** difficulty or task mix produces the appearance.
- **H5:** any migration is repository/domain specific.
- **H6:** validation or harness artifacts produce the appearance.
- **H7:** environment readiness or availability produces the appearance.
- **H8:** candidate multiplicity creates offsetting coordination/review load.

These alternatives remain live and may overlap; none has been assessed.

## Issue #109 handoff boundary

The cross-run package is a design input only. Transferable bounded observations
are: every run generated a candidate but none formed an accepted T1; focused
success did not entail repository validity; repository validity did not entail
focused acceptance; a corrected prospective oracle discriminated Run 3
candidates; and gate order and repair limits censored evidence. Transferable
candidate variables are task-contract precision, oracle validity, repository
consequences, repair budget, gate order, environment readiness, candidate
capacity, context supplied, and acceptance yield.

Not transferable are any claim that abundance was present, bottleneck migration
occurred, AI or a model was incapable, structural drift was supported/refuted,
or a general software-engineering law holds. The heterogeneous three-run,
one-repository record supplies neither a baseline effect nor a causal contrast.
Run 2's failed assertion is not candidate task failure, rejected candidates are
not accepted trajectory states, and zero yield is not itself evidence of a
shared causal mechanism. The present definitions and thresholds were therefore
frozen independently rather than fit to the #109 outcomes.

## Failure, stopping, and future determination

Failures distinguish instrumentation, invalid harness/oracle, environment,
specification, context, architecture, implementation, review, focused,
repository, structural, coordination, governance, stopping censoring, and
unattributable causes. Two blinded adjudicators and, if needed, a third classify
first failure and terminal cause; detection stage and rework origin remain
separate.

An execution ends at all-gates-valid acceptance or the first frozen time,
candidate, repair, safety, or wall-clock cap. The study never stops because a
favored effect appears. Integrity/authorization failures, inability to realize
the contrast, or common artifacts can administratively stop it. No extra
attempt, reordered gate, or discretionary repair is permitted.

Future data produce exactly one category, in precedence order:

1. `EXPERIMENT_BLOCKED` for administrative/integrity/common-artifact stops or
   inadequate classifiable coverage;
2. `BOTTLENECK_MIGRATION_INDETERMINATE` for failed manipulation, inadequate
   precision/power, or outcome-sensitive artifact/environment imbalance;
3. `BOTTLENECK_MIGRATION_DOMAIN_DEPENDENT` for discriminating heterogeneous
   repository/task-class migration;
4. `BOTTLENECK_MIGRATION_SUPPORTED` only when every replicated migration,
   minimum-throughput/yield, and artifact-control condition passes; or
5. `BOTTLENECK_MIGRATION_NOT_SUPPORTED` when the study is adequate but the
   support rule fails, including implementation dominance, proportional
   acceleration, precise null, or opposite results.

## Readiness gate

The scientific definitions are frozen, but repositories/tasks, images, oracle
reviews, instrumentation calibration, randomization manifest, synthetic-data
analysis rehearsal, and separate execution authorization are outstanding.
Accordingly the exact present determination is:

**`BOTTLENECK_EXPERIMENT_NOT_READY`**
