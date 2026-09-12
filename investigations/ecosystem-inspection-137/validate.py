#!/usr/bin/env python3
"""Validate Issue 137 Phase 1 vocabulary and prospective-integrity guards."""

from pathlib import Path


TEXT = Path(__file__).with_name("README.md").read_text(encoding="utf-8")

REQUIRED_GROUPS = {
    "matrix_a": {
        "TESTABLE_NOW", "PLAUSIBLE_BUT_BLOCKED", "NO_CAUSAL_QUESTION_YET",
        "OUT_OF_SCOPE_BY_CONTRACT", "DUPLICATED_BY_EXISTING_EXPERIMENT",
    },
    "matrix_b": {
        "APPLICABLE", "APPLICABLE_WITH_LIMITS", "NOT_YET_APPLICABLE",
        "REDUNDANT_WITH_NATIVE_METHOD", "OUT_OF_SCOPE",
        "BLOCKED_BY_MISSING_INPUT", "PIPELINE_TESTABLE_NOW",
        "PIPELINE_PARTIALLY_TESTABLE", "PIPELINE_NOT_JUSTIFIED",
    },
    "stage": {
        "STAGE_UNIQUE_VALUE_OBSERVED", "STAGE_VALUE_WITH_LIMITATIONS",
        "STAGE_NO_UNIQUE_VALUE", "STAGE_REDUNDANT", "STAGE_BLOCKED",
        "STAGE_OUT_OF_SCOPE", "STAGE_INDETERMINATE",
    },
    "target": {
        "FULL_PIPELINE_VALUE_OBSERVED", "PARTIAL_PIPELINE_VALUE_OBSERVED",
        "PIPELINE_REDUNDANT_WITH_NATIVE_PROCESS",
        "PIPELINE_FRICTION_EXCEEDS_VALUE", "PIPELINE_BLOCKED",
        "PIPELINE_NOT_APPLICABLE", "PIPELINE_INDETERMINATE",
    },
    "generality": {
        "INSPECTION_PIPELINE_GENERALITY_SUPPORTED",
        "INSPECTION_PIPELINE_PARTIALLY_SUPPORTED",
        "INSPECTION_PIPELINE_NOT_SUPPORTED",
        "INSPECTION_PIPELINE_GENERALITY_INDETERMINATE",
    },
}

for group, values in REQUIRED_GROUPS.items():
    missing = sorted(value for value in values if f"`{value}`" not in TEXT)
    assert not missing, f"{group}: missing exact vocabulary: {missing}"

assert "ECOSYSTEM_INSPECTION_PROTOCOL_PARTIALLY_READY" in TEXT
assert "no new empirical inspection-pipeline outcomes" in TEXT
assert "1fa7517c4e14c61941cd2d60dab586cd6c5485fb" in TEXT
assert "1ee0778d8ed402b0c370279e21e5c637e0fb47c5" in TEXT

# These outcome labels may occur only where their prospective rules are defined.
for value in REQUIRED_GROUPS["generality"]:
    assert TEXT.count(f"`{value}`") == 1, f"outcome emitted outside rule: {value}"

print("Issue 137 Phase 1 freeze: PASS (shape/vocabulary only; no outcomes tested)")
