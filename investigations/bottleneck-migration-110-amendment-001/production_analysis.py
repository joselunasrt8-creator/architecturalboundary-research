#!/usr/bin/env python3
"""Frozen, repository-aware prospective inference for Amendment 001."""
from __future__ import annotations

import hashlib
import json
import random
from collections import defaultdict

from inference_core import exact_repository_symmetry_signflip, holm, primary_endpoint_conjunction

SEED = 11020260901

def _q(values, probability):
    values = sorted(values)
    return values[min(len(values) - 1, max(0, int(probability * (len(values) - 1))))]

def validate(records):
    required = {"pair_id", "condition", "repository_id", "task_class", "difficulty",
                "accepted", "active_minutes", "time_to_valid_minutes", "time_to_valid_event",
                "eligible", "binding_stages", "manipulation"}
    if not isinstance(records, list) or not records:
        raise ValueError("nonempty records required")
    pairs = defaultdict(list)
    for record in records:
        if not isinstance(record, dict) or set(record) != required:
            raise ValueError("malformed record")
        if record["condition"] not in ("LOW", "HIGH") or not isinstance(record["time_to_valid_event"], bool):
            raise ValueError("invalid value")
        if record["active_minutes"] <= 0 or record["time_to_valid_minutes"] < 0:
            raise ValueError("nonpositive active time or negative event time")
        pairs[record["pair_id"]].append(record)
    for pair in pairs.values():
        if sorted(row["condition"] for row in pair) != ["HIGH", "LOW"]:
            raise ValueError("incomplete pair")
        identity = {(row["repository_id"], row["task_class"], row["difficulty"]) for row in pair}
        if len(identity) != 1:
            raise ValueError("pair mismatch")
    if len({pair[0]["repository_id"] for pair in pairs.values()}) < 2:
        raise ValueError("clustered inference requires at least two repositories")
    return pairs

def rmst(rows, tau=480):
    """Tie-correct Kaplan–Meier restricted mean; events precede same-time censor removal."""
    grouped = defaultdict(lambda: [0, 0])
    for row in rows:
        time = min(row["time_to_valid_minutes"], tau)
        event = row["time_to_valid_event"] and row["time_to_valid_minutes"] <= tau
        grouped[time][0 if event else 1] += 1
    at_risk = len(rows)
    survival = 1.0
    previous = 0.0
    area = 0.0
    for time in sorted(grouped):
        if time > tau:
            break
        events, censored = grouped[time]
        area += survival * (time - previous)
        if events:
            survival *= 1.0 - events / at_risk
        at_risk -= events + censored
        previous = time
    return area + survival * (tau - previous)

def _effects(pairs, pair_ids, swapped_repositories=frozenset()):
    low, high = [], []
    for pair_id in pair_ids:
        rows = {row["condition"]: row for row in pairs[pair_id]}
        if rows["LOW"]["repository_id"] in swapped_repositories:
            rows["LOW"], rows["HIGH"] = rows["HIGH"], rows["LOW"]
        low.append(rows["LOW"])
        high.append(rows["HIGH"])
    throughput = lambda rows: sum(row["accepted"] for row in rows) * 480 / sum(row["active_minutes"] for row in rows)
    yield_difference = sum(row["accepted"] for row in high) / len(high) - sum(row["accepted"] for row in low) / len(low)
    low_rmst = rmst(low)
    if low_rmst <= 0:
        raise ValueError("relative RMST effect undefined when LOW RMST is zero")
    return yield_difference, throughput(high)-throughput(low), rmst(high)/low_rmst-1

def _hierarchical_sample(by_repository, rng):
    """Sample repositories first, then intact paired templates within each selected repository."""
    repositories = sorted(by_repository)
    sample = []
    for _ in repositories:
        repository = rng.choice(repositories)
        pair_ids = by_repository[repository]
        sample.extend(rng.choice(pair_ids) for _ in pair_ids)
    return sample

def analyze(records, bootstrap_replicates=10_000, seed=SEED):
    if bootstrap_replicates < 10_000:
        raise ValueError("hierarchical cluster bootstrap requires >=10,000 replicates")
    pairs = validate(records)
    pair_ids = sorted(pairs)
    by_repository = defaultdict(list)
    for pair_id in pair_ids:
        by_repository[pairs[pair_id][0]["repository_id"]].append(pair_id)
    for pair_ids_in_repository in by_repository.values():
        pair_ids_in_repository.sort()
    point = _effects(pairs, pair_ids)
    all_low = [row for pair in pairs.values() for row in pair if row["condition"] == "LOW"]
    low_throughput = sum(row["accepted"] for row in all_low)*480/sum(row["active_minutes"] for row in all_low)
    if low_throughput <= 0:
        raise ValueError("relative throughput threshold undefined when cohort LOW throughput is zero")
    throughput_relative_change = point[1]/low_throughput
    bootstrap_rng = random.Random(seed)
    bootstrap = [_effects(pairs, _hierarchical_sample(by_repository, bootstrap_rng))
                 for _ in range(bootstrap_replicates)]
    intervals = [[round(_q([draw[index] for draw in bootstrap], .025), 6),
                  round(_q([draw[index] for draw in bootstrap], .975), 6)] for index in range(3)]

    # Separate cluster-score inference, not the task-template/order randomization distribution.
    repositories = sorted(by_repository)
    repository_effects = [_effects(pairs, by_repository[repository]) for repository in repositories]
    null_result = exact_repository_symmetry_signflip(repository_effects)
    endpoint_conjunction = primary_endpoint_conjunction(point, low_throughput, null_result["holm"])

    strata = defaultdict(list)
    for pair_id, pair in pairs.items():
        strata[(pair[0]["repository_id"], pair[0]["task_class"])].append(pair_id)
    interactions = {f"{key[0]}::{key[1]}": round(_effects(pairs, value)[0], 6)
                    for key, value in sorted(strata.items())}
    return {
        "schema_version": "1.2",
        "resampling_unit": "repository_then_paired_template_hierarchical_cluster",
        "bootstrap_replicates": bootstrap_replicates,
        "null_assignments_enumerated": null_result["assignments_enumerated"],
        "seed": seed,
        "effects": {"acceptance_yield_difference": point[0], "throughput_absolute_difference": point[1],
                    "throughput_relative_change": throughput_relative_change, "rmst_relative_change": point[2]},
        "intervals_95": {"acceptance_yield": intervals[0], "throughput": intervals[1], "rmst": intervals[2]},
        "right_censoring_method": "tie-grouped Kaplan-Meier restricted mean through 480 minutes",
        "null_test": "repository-score symmetry sign flip; separate inferential assumption, not experiment randomization",
        "cluster_inference_assumption": "independent repository score vectors are jointly sign-symmetric under the null",
        "stratum_effects": interactions,
        "holm": null_result["holm"],
        "primary_endpoint_evidentiary_conjunction": endpoint_conjunction,
        "input_sha256": hashlib.sha256(json.dumps(records, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
    }

def manipulation_check(records):
    pairs = validate(records)
    high = [row for pair in pairs.values() for row in pair if row["condition"] == "HIGH" and row["eligible"]]
    low = [row for pair in pairs.values() for row in pair if row["condition"] == "LOW" and row["eligible"]]
    if not high or not low:
        raise ValueError("eligible LOW and HIGH required")
    a = sum(row["manipulation"]["runnable_candidate_count"] >= 2 for row in high) / len(high) >= .70
    median = lambda rows: _q([row["manipulation"]["time_to_first_runnable_minutes"] for row in rows], .5)
    b = median(high) <= .70 * median(low)
    c = all(row["manipulation"]["ai_configuration_frozen"] for row in high)
    d = all(row["manipulation"]["ai_use_stage_ids"] == ["S05"] for row in high)
    return {"A_candidate_abundance": a, "B_time_ratio": b, "C_configuration_frozen": c,
            "D_implementation_only": d, "passed": a and b and c and d,
            "failure_consequence": "BOTTLENECK_MIGRATION_INDETERMINATE" if not (a and b and c and d) else None}

def determination(*, blocked=False, manipulation=True, adequate_power=True, domain=False, migration=False):
    if blocked: return "EXPERIMENT_BLOCKED"
    if not manipulation or not adequate_power: return "BOTTLENECK_MIGRATION_INDETERMINATE"
    if domain: return "BOTTLENECK_MIGRATION_DOMAIN_DEPENDENT"
    if migration: return "BOTTLENECK_MIGRATION_SUPPORTED"
    return "BOTTLENECK_MIGRATION_NOT_SUPPORTED"

def binding_migration(low_stages, high_stages):
    low, high = set(low_stages), set(high_stages)
    replacements = sorted(high - {"S05"})
    return {"implementation_low": "S05" in low, "implementation_high": "S05" in high,
            "replacement_high": replacements,
            "migration": "S05" in low and "S05" not in high and bool(replacements)}
