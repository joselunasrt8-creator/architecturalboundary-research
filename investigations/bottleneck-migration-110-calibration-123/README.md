# Issue #123 outcome-blind calibration adjudication

This record evaluates whether the final empirical cohort for Issue #110 can be
frozen. It does **not** execute Issue #110, inspect an Issue #110 outcome,
generate a study candidate, or authorize execution.

## Determination

`FINAL_N_NOT_YET_FREEZABLE`

`BOTTLENECK_EXPERIMENT_NOT_READY`

The repository contains only synthetic nuisance regimes. No permissible
external data or non-study pre-study calibration record supplies defensible
bounds for any of the eight required nuisance quantities. In addition, no
permissible evidence and independent sign-off justify either independence of
repository clusters under the intended sampling frame or joint central sign
symmetry of the three-endpoint repository score vector under the global null.
Simulation behavior is not evidence for either assumption.

Because both gates fail, the frozen power engine was not rerun and no design
was selected. This preserves the Amendment 001 distinction between the actual
blocked task-template order randomization and the separately assumed
repository-score sign-flip inference. More task pairs or Monte Carlo draws
cannot repair a lack of independent repository clusters.

## Smallest legitimate next action

Before exposing any study task or outcome, register and independently sign off
one outcome-blind calibration package that (1) uses archived external data or
non-study tasks, (2) records source identifiers, hashes, dates, accessed
variables, estimators, conservative bounds, and exclusions for all eight
nuisance quantities, and (3) supplies a sampling-frame argument for repository
independence and a methodologically reviewed argument or diagnostic calibration
for **joint** three-endpoint central sign symmetry. The package must not access
candidate qualification, acceptance, binding, migration, or condition
contrasts from Issue #110. Only after that package passes the frozen contract
may the unchanged power engine and mechanical sample-size rule be run.

## Claim scopes

No candidate or frozen N exists. Consequently this adjudication supports no
primary bounded bottleneck-migration claim, repository interaction claim,
task-class interaction claim, or broader external-validity claim.

The files in the protocol, preflight, analysis-freeze, and Amendment 001
directories are immutable inputs. `artifact-bindings.json` binds their merged
commits and trees and the production/power interfaces. `calibration-readiness.json`
records each unavailable calibration item without inventing a bound.
`adversarial-validation.json` records the fail-closed falsification attempts.

AI output is a proposal, not execution authority.
