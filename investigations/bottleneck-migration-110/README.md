# Issue #110 Investigation: Bottleneck Migration Under Abundant AI Implementation

## Metadata

| Field | Value |
| --- | --- |
| Investigation ID | `bottleneck-migration-110` |
| Issue reference | [#110](https://github.com/joselunasrt8-creator/architecturalboundary-research/issues/110) |
| Protocol version | `protocol-v1` |
| Status | `PREREGISTRATION_PHASE` |
| Created | 2026-09-01 |
| Last updated | 2026-09-01 |
| Authorization boundary | None; this investigation is in design/readiness phase only |
| Execution status | `NOT_EXECUTED` |

## Purpose

This investigation asks whether the primary constraint on successful software change migrates away from implementation toward upstream/downstream stages when AI substantially reduces implementation scarcity.

The governing question is:

> As AI reduces the scarcity of software implementation, where do the binding constraints on reliable software development migrate?

This investigation **does not assume** bottleneck migration is true. It preserves migration as one of multiple falsifiable hypotheses.

## Relationship to Issue #109

Issue #109 investigates a specific failure mode: whether locally acceptable agentic transitions can collectively degrade system architecture.

This investigation (#110) asks the broader question: does the binding engineering constraint itself migrate as implementation becomes cheaper?

**Explicit dependency model:**

```
#109 evidence
    ↓
possible input to #110 interpretation
    ↓
#110 conclusion
```

**NOT:**

```
#109 architecture
    ↓
#110 proof
```

Evidence from #109 may inform this investigation, but #109 must not be treated as predetermined support or a prerequisite for #110. Negative/null #109 results do not block #110.

## Investigation Structure

The investigation package contains:

| Artifact | Purpose |
| --- | --- |
| `preregistration.md` | Frozen research question, design, and acceptance criteria before execution |
| `research-question.json` | Machine-readable research question and hypotheses |
| `stage-model.json` | Prospectively frozen workflow stage decomposition |
| `measurement-model.json` | Every proposed metric with construct, observable, unit, collection, interpretation, and confounders |
| `failure-taxonomy.json` | Prospectively frozen failure classification prior to observation |
| `task-cohort-design.json` | Bounded task population: selection criteria, count, comparability |
| `experimental-design.json` | Condition A vs. B contrast, instrumentation, and procedural freezing |
| `counter-hypotheses.json` | H0–H6 and alternative explanations preserved as live alternatives |
| `instrumentation.json` | Evidence collection mechanism: automated vs. manual, timing, storage |
| `determination-rules.json` | Prospective decision rule for bottleneck migration determination |
| `readiness-assessment.md` | Full readiness evaluation against acceptance criteria |
| `BLOCKED_EXECUTION_BOUNDARY.md` | Explicit identification of where execution authorization must occur |

## Governance

**Preregistration freezing:** All artifacts in this directory must be committed and versioned before canonical evidence collection begins. No retrospective redefinition of stages, metrics, or determination rules is permitted.

**Contamination controls:** This investigation must not:
- inspect or modify Issue #109 Run 3 unreleased artifacts;
- use #109 candidate-generation transcripts to tune #110 design before their legitimate release;
- modify ContinuityOS, MindShift, StateGate, SYNAPSE, or other repositories unless strictly necessary;
- import #109 conclusions as proof of bottleneck migration;
- use subjective practitioner impressions as baseline observations.

**Evidence preservation:** All measurements, decision points, negative findings, and unresolved questions remain explicit and visible.

## Entry Points

- **Executives and reviewers:** Start at `readiness-assessment.md` and `BLOCKED_EXECUTION_BOUNDARY.md`
- **Protocol and methodology:** See `preregistration.md`, `stage-model.json`, and `determination-rules.json`
- **Measurement design:** See `measurement-model.json` and `instrumentation.json`
- **Hypotheses and alternatives:** See `counter-hypotheses.json` and `research-question.json`

## Status

**Current phase:** Preregistration design and readiness evaluation.

**Expected actions:**
1. Freeze all preregistration artifacts.
2. Conduct internal and external readiness review.
3. Determine exact execution authorization boundary.
4. Return readiness determination: `BOTTLENECK_EXPERIMENT_READY` or `BOTTLENECK_EXPERIMENT_NOT_READY`.

**Execution:** Will not begin unless preregistration is frozen and readiness determination explicitly permits it.
