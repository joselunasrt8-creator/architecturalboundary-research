"""Shared repository-symmetry inference used by production analysis and power."""
from __future__ import annotations

ALPHA = .05
PRIMARY_FAMILY_SIZE = 3
YIELD_THRESHOLD = .10
THROUGHPUT_RELATIVE_THRESHOLD = .15
RMST_RELATIVE_THRESHOLD = -.15

def holm(pvalues, alpha=ALPHA):
    ordered = sorted(enumerate(pvalues), key=lambda item: item[1])
    adjusted = [0.0] * len(pvalues)
    running = 0.0
    for rank, (index, pvalue) in enumerate(ordered):
        running = max(running, min(1.0, pvalue * (len(pvalues) - rank)))
        adjusted[index] = running
    return {"adjusted_p": adjusted, "reject": [pvalue <= alpha for pvalue in adjusted]}

def finite_symmetry_signflip_capability(repository_count, family_size=PRIMARY_FAMILY_SIZE, alpha=ALPHA):
    """Resolution under the separately frozen repository-score symmetry assumption."""
    if repository_count < 2:
        raise ValueError("at least two repositories required")
    assignments = 1 << repository_count
    minimum_raw = 2 / assignments
    minimum_holm = holm([minimum_raw] * family_size, alpha)
    return {
        "repository_count": repository_count,
        "distinct_assignments": assignments,
        "minimum_attainable_two_sided_p": minimum_raw,
        "minimum_attainable_holm_adjusted_p": max(minimum_holm["adjusted_p"]),
        "primary_family_size": family_size,
        "alpha": alpha,
        "eligible": all(minimum_holm["reject"]),
    }

def exact_repository_symmetry_signflip(repository_effects):
    """Enumerate repository score signs; this is not experiment randomization inference."""
    if len(repository_effects) < 2 or not repository_effects:
        raise ValueError("at least two repository effect vectors required")
    endpoint_count = len(repository_effects[0])
    if endpoint_count != PRIMARY_FAMILY_SIZE or any(len(row) != endpoint_count for row in repository_effects):
        raise ValueError("three complete primary endpoint effects required per repository")
    observed = [abs(sum(row[index] for row in repository_effects)) for index in range(endpoint_count)]
    exceedances = [0] * endpoint_count
    assignments = 1 << len(repository_effects)
    permuted = [sum(row[index] for row in repository_effects) for index in range(endpoint_count)]
    previous_gray = 0
    for sequence in range(assignments):
        gray = sequence ^ (sequence >> 1)
        if sequence:
            changed = gray ^ previous_gray
            repository = changed.bit_length()-1
            direction = -2 if gray & changed else 2
            for index, effect in enumerate(repository_effects[repository]):
                permuted[index] += direction*effect
        for index in range(endpoint_count):
            exceedances[index] += abs(permuted[index]) >= observed[index] - 1e-12
        previous_gray = gray
    pvalues = [count / assignments for count in exceedances]
    return {"pvalues": pvalues, "holm": holm(pvalues), "assignments_enumerated": assignments}

def primary_endpoint_conjunction(point_effects, low_throughput, holm_result):
    """The single frozen endpoint rule shared by production analysis and power."""
    if len(point_effects) != PRIMARY_FAMILY_SIZE or low_throughput <= 0:
        raise ValueError("complete effects and positive LOW throughput required")
    return (all(holm_result["reject"])
            and point_effects[0] >= YIELD_THRESHOLD
            and point_effects[1]/low_throughput >= THROUGHPUT_RELATIVE_THRESHOLD
            and point_effects[2] <= RMST_RELATIVE_THRESHOLD)
