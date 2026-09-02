#!/usr/bin/env python3
"""Deterministic structured Monte Carlo power engine for Amendment 001."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from pathlib import Path

from inference_core import exact_repository_signflip, finite_signflip_capability, primary_endpoint_conjunction

ROOT = Path(__file__).resolve().parent
SEED = 11020260901
REPLICATES = 10_000
DESIGNS = ((64, 4), (128, 4), (288, 6), (512, 8))
REGIMES = (
    {"name":"favorable", "baseline":.40, "baseline_throughput":.80, "yield_effect":.20, "pair_correlation":.60,
     "repository_sd":.05, "task_sd":.10, "difficulty_effect":.08, "timing_cv":.35,
     "time_ratio":.70, "attrition":.05, "censoring":.05, "environment_failure":.02,
     "repository_interaction_sd":.10},
    {"name":"moderate", "baseline":.40, "baseline_throughput":.80, "yield_effect":.15, "pair_correlation":.35,
     "repository_sd":.10, "task_sd":.20, "difficulty_effect":.12, "timing_cv":.55,
     "time_ratio":.70, "attrition":.10, "censoring":.15, "environment_failure":.05,
     "repository_interaction_sd":.10},
    {"name":"conservative", "baseline":.40, "baseline_throughput":.80, "yield_effect":.10, "pair_correlation":.10,
     "repository_sd":.15, "task_sd":.30, "difficulty_effect":.16, "timing_cv":.80,
     "time_ratio":.70, "attrition":.25, "censoring":.25, "environment_failure":.10,
     "repository_interaction_sd":.10},
)

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()

def _normal_cdf(value):
    return .5 * (1 + math.erf(value / math.sqrt(2)))

def _wilson(successes, trials):
    z = 1.95996398454
    proportion = successes/trials
    denominator = 1+z*z/trials
    center = (proportion+z*z/(2*trials))/denominator
    half_width = z*math.sqrt(proportion*(1-proportion)/trials+z*z/(4*trials*trials))/denominator
    return [round(center-half_width, 6), round(center+half_width, 6)]

def _weighted_rmst(observations, tau=480):
    """Kaplan–Meier RMST for (time, event, frequency) prospective cell observations."""
    grouped = {}
    for time, event, frequency in observations:
        key = min(time, tau)
        grouped.setdefault(key, [0, 0])[0 if event and time <= tau else 1] += frequency
    at_risk = sum(sum(counts) for counts in grouped.values())
    survival, previous, area = 1.0, 0.0, 0.0
    for time in sorted(grouped):
        events, censored = grouped[time]
        area += survival*(time-previous)
        if events:
            survival *= 1-events/at_risk
        at_risk -= events+censored
        previous = time
    return area+survival*(tau-previous)

def _simulate_cell(pairs, repositories, regime, rng, replicates):
    primary_hits = interaction_hits = retained_total = censored_total = 0
    capability = finite_signflip_capability(repositories)
    tasks, difficulties = 4, 2
    cells = repositories * tasks * difficulties
    for _ in range(replicates):
        repository_main = [rng.gauss(0, regime["repository_sd"]) for _ in range(repositories)]
        repository_interaction = [rng.gauss(0, regime["repository_interaction_sd"]) for _ in range(repositories)]
        task_main = [rng.gauss(0, regime["task_sd"]) for _ in range(tasks)]
        yield_weighted = throughput_weighted = migration_weighted = 0.0
        retained = 0
        repository_effects = [[] for _ in range(repositories)]
        repository_variances = [[] for _ in range(repositories)]
        primary_endpoint_effects = []
        all_low_survival, all_high_survival = [], []
        retention = (1-regime["attrition"]) * (1-regime["environment_failure"])
        for repository in range(repositories):
            expected = pairs/repositories * retention
            n = max(0, round(rng.gauss(expected, math.sqrt(max(expected*(1-retention), .01)))))
            if not n:
                continue
            retained += n
            # Balanced task/difficulty cells contribute explicitly to the aggregate paired variance.
            baselines = [min(.95, max(.05, regime["baseline"] + repository_main[repository]
                         + task_main[task] + regime["difficulty_effect"]*(-.5 if difficulty == 0 else .5)))
                         for task in range(tasks) for difficulty in range(difficulties)]
            paired_variance = max(.0001, sum(2*p*(1-p)*(1-regime["pair_correlation"])
                                             for p in baselines)/len(baselines)/n)
            effect = regime["yield_effect"] + repository_interaction[repository]
            repository_effect = rng.gauss(effect, math.sqrt(paired_variance))
            yield_weighted += n*repository_effect
            repository_effects[repository].append(repository_effect)
            repository_variances[repository].append(paired_variance)
            throughput_effect = rng.gauss(.20, .08+regime["timing_cv"]/math.sqrt(n))
            throughput_weighted += n*throughput_effect
            migration_weighted += n*rng.gauss(.35, .15/math.sqrt(n))
            # Repository-specific censored survival observations match the production cluster statistic.
            low_survival, high_survival = [], []
            sigma = math.sqrt(math.log1p(regime["timing_cv"]**2))
            for difficulty in range(difficulties):
                frequency = max(1, n//difficulties)
                difficulty_shift = regime["difficulty_effect"]*(-.5 if difficulty == 0 else .5)
                low_time = rng.lognormvariate(math.log(240*(1+difficulty_shift))-sigma*sigma/2, sigma)
                high_time = rng.lognormvariate(math.log(240*(1+difficulty_shift)*regime["time_ratio"])-sigma*sigma/2, sigma)
                def observe(event_time):
                    censor_time = rng.uniform(60, 480) if rng.random() < regime["censoring"] else 480
                    return min(event_time, censor_time), event_time <= censor_time
                low_observed, low_event = observe(low_time)
                high_observed, high_event = observe(high_time)
                censored_total += frequency*((not low_event)+(not high_event))
                low_survival.append((low_observed, low_event, frequency))
                high_survival.append((high_observed, high_event, frequency))
            low_rmst = _weighted_rmst(low_survival)
            repository_time_relative_change = _weighted_rmst(high_survival)/low_rmst-1
            primary_endpoint_effects.append((repository_effect, throughput_effect, repository_time_relative_change))
            all_low_survival.extend(low_survival)
            all_high_survival.extend(high_survival)
        retained_total += retained
        if retained < max(12, repositories*2):
            continue
        mean_yield = yield_weighted/retained
        time_relative_change = _weighted_rmst(all_high_survival)/_weighted_rmst(all_low_survival)-1
        point_effects = (mean_yield, throughput_weighted/retained, time_relative_change)
        migration_hit = migration_weighted/retained >= .20
        null_result = exact_repository_signflip(primary_endpoint_effects) if capability["eligible"] else None
        endpoint_conjunction = (capability["eligible"]
                                and primary_endpoint_conjunction(point_effects, regime["baseline_throughput"], null_result["holm"]))
        production_rejection = endpoint_conjunction and migration_hit
        primary_hits += production_rejection

        # Defined omnibus condition-by-repository Wald test (df = repositories-1, alpha=.05).
        estimates = [sum(values)/len(values) for values in repository_effects]
        variances = [sum(values)/len(values)**2 for values in repository_variances]
        weights = [1/max(value, 1e-9) for value in variances]
        pooled = sum(weight*estimate for weight,estimate in zip(weights,estimates))/sum(weights)
        wald = sum(weight*(estimate-pooled)**2 for weight,estimate in zip(weights,estimates))
        # Wilson-Hilferty approximation to the chi-square upper-tail decision.
        df = repositories-1
        z = ((wald/df)**(1/3)-(1-2/(9*df)))/math.sqrt(2/(9*df))
        interaction_hits += 1-_normal_cdf(z) < .05
    return {
        "production_aligned_primary_power": round(primary_hits/replicates, 6),
        "production_aligned_primary_power_95_wilson": _wilson(primary_hits, replicates),
        "design_eligible_for_primary_inference": capability["eligible"],
        "finite_null_capability": capability,
        "ineligibility_reason": None if capability["eligible"] else "Holm-corrected alpha is unattainable with this repository count regardless of pair count",
        "repository_interaction_wald_power": round(interaction_hits/replicates, 6),
        "repository_interaction_wald_power_95_wilson": _wilson(interaction_hits, replicates),
        "repository_interaction_test": "omnibus condition-by-repository inverse-variance Wald, alpha=0.05",
        "mean_retained_pairs": round(retained_total/replicates, 3),
        "mean_censored_arm_observations": round(censored_total/replicates, 3),
    }

def run(replicates=REPLICATES, seed=SEED):
    if replicates < 10_000:
        raise ValueError("production run requires at least 10,000 replicates per design/regime")
    configuration = {
        "seed": seed,
        "inference_core_sha256": hashlib.sha256((ROOT/"inference_core.py").read_bytes()).hexdigest(),
        "production_inference_rule": "exact repository sign flips; three-endpoint Holm alpha 0.05; frozen effect-threshold conjunction",
        "replicates_per_design_regime": replicates,
        "designs": [{"pairs": pairs, "executions": 2*pairs, "repositories": repositories,
                     "task_classes": 4, "difficulty_bands": 2} for pairs,repositories in DESIGNS],
        "regimes": REGIMES,
        "model_features": ["paired LOW/HIGH", "repository random intercepts and condition interactions",
                           "task random effects", "difficulty fixed effect", "within-pair correlation",
                           "attrition", "explicit right-censored survival observations", "acceptance yield",
                           "throughput", "time to valid", "conjunctive migration"],
    }
    rng = random.Random(seed)
    results = []
    for pairs, repositories in DESIGNS:
        for regime in REGIMES:
            results.append({"pairs": pairs, "executions": 2*pairs, "repositories": repositories,
                            "regime": regime["name"], "replicates_executed": replicates,
                            **_simulate_cell(pairs, repositories, regime, rng, replicates)})
    return {
        "schema_version": "1.2",
        "artifact_role": "PROSPECTIVE_ASSUMPTION_SENSITIVITY_NOT_EMPIRICAL_DATA",
        "seed": seed,
        "replicates_per_design_regime": replicates,
        "total_replicates_executed": replicates*len(results),
        "engine_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "inference_core_sha256": configuration["inference_core_sha256"],
        "configuration_sha256": hashlib.sha256(canonical(configuration)).hexdigest(),
        "configuration": configuration,
        "results": results,
        "final_n": "FINAL_N_NOT_YET_FREEZABLE",
        "reason": "Regime nuisance values are synthetic assumptions; no permissible outcome-blind calibration bounds have been frozen.",
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(ROOT/"power-results.json"))
    parser.add_argument("--replicates", type=int, default=REPLICATES)
    arguments = parser.parse_args()
    Path(arguments.output).write_text(json.dumps(run(arguments.replicates), indent=2, sort_keys=True)+"\n")

if __name__ == "__main__":
    main()
