# Preregistration: Context Scaling Versus Explicit Abstraction

**Registration status:** COMPLETE — documentation-only; execution is not authorized.

This registration operationalizes the prospective design in [the investigation design](investigation-design.md). The bounded literature review constrains these controls but is not empirical evidence ([design implications](literature/design-implications.md), [novelty determination](literature/novelty-determination.md)). Terms such as “context-only” and “explicit abstraction” have the qualified meanings in the [terminology reconciliation](literature/terminology-reconciliation.md).

## 1. Study Objective

**Research question.** Under controlled task conditions, does an explicit, inspectable generalized representation produce more correct transfer to materially different unseen target tasks than a context-only workflow, independently of the amount of available source information?

**Candidate hypothesis.** Scaling available input context increases information availability, but transforming information into reusable principles requires an explicit abstraction process.

**Purpose.** This prospective 2 × 2 investigation distinguishes the effect of a fixed increase in available source information from the effect of retaining an explicit generalized representation. It may support, violate, or leave the candidate hypothesis indeterminate; it does not test whether a model internally abstracts.

**Status and boundary.** This is a documentation-only preregistration. It creates no tasks, observations, datasets, artifacts, results, or empirical conclusion. It freezes methodology only and does not authorize execution.

## 2. Experimental Design

The unit of analysis is one **source-package/condition/target-task evaluation**. One source package is evaluated in every condition; each condition receives the same target task in a block, and no output from one condition is available to another.

| Workflow | Standard context | High context |
| --- | --- | --- |
| Context only | C1 | C3 |
| Explicit abstraction | C2 | C4 |

- **C1 — context only, standard:** receives source units `U001`–`U008`; produces a source-specific answer; at transfer retains only that answer and source citation identifiers.
- **C2 — explicit abstraction, standard:** receives the identical `U001`–`U008`; produces a source-specific answer and a compliant abstraction artifact; at transfer retains both.
- **C3 — context only, high:** receives source units `U001`–`U016`; produces a source-specific answer; at transfer retains only that answer and source citation identifiers.
- **C4 — explicit abstraction, high:** receives the identical `U001`–`U016`; produces a source-specific answer and a compliant abstraction artifact; at transfer retains both.

No condition may be redefined by prompt wording, compression, extra context, or a different retained-object policy after this registration. Raw source material is unavailable during every target evaluation.

## 3. Source Information Manipulation

A **source unit** is one immutable, consecutively numbered record in the pre-execution source registry, consisting of one source identifier, verbatim source content, and a content hash. Unit boundaries are paragraph boundaries in the frozen source corpus; a heading is attached to the following paragraph, and tables, lists, and code blocks each constitute one unit. Empty blocks and metadata not needed to interpret a unit are excluded.

The canonical order is ascending registry sequence number (`U001`, `U002`, ...), assigned before condition execution by source-document order, then ascending paragraph/block order within document. Segmentation is performed once with those rules and is not rerun per condition. Inclusion requires a nonempty, in-scope unit with its identifier, source location, and hash. Exclude duplicate content (retain only the first canonical occurrence), boilerplate, navigation, evaluator material, target material, and any text added after the source registry freeze.

The standard information level is **N = 8 source units** (`U001`–`U008`). The high information level is **M = 16 source units** (`U001`–`U016`), so `M > N`; it includes every standard unit plus `U009`–`U016`. A source package with fewer than 16 eligible units is ineligible and is a methodology failure, not a reason to lower either level.

Effective source information is the ordered list of eligible units actually supplied, plus their deterministic token count under the model tokenizer named in the execution package. Nominal model context-window capacity is not an information measure. Record unit IDs, hashes, tokenizer/version, token count, and any excluded unit for every source invocation; no truncation is permitted at the source step.

## 4. Explicit-Abstraction Artifact

C2 and C4 must preserve one separately delimited, source-linked artifact before any target task is exposed. It must contain all of the following:

1. a generalized principle expressed independently of the source’s wording;
2. applicability conditions that state when the principle may be used;
3. limitations and explicit failure cases that state when it must not be used or is expected to fail;
4. provenance mapping every material claim to one or more source-unit IDs; and
5. reuse instructions that permit application to a materially different unseen target without raw source access.

The artifact is compliant only if an auditor can identify all five elements and verify each material claim’s provenance. It must be reusable across the preregistered target-task families, not written as an answer to one target. A summary, copied passage, compressed text, source-specific answer, chain-of-thought, or task-specific notes is rejected even if short or source-linked. A malformed artifact stops its unit before target evaluation and is a methodology failure.

## 5. Context-Only Boundary

C1 and C3 may retain exactly: (a) the final source-specific answer generated at the source step, and (b) source citation identifiers sufficient only to audit that answer. The answer may address the source task but may not contain a generalized principle, applicability conditions, limitations, failure cases, pattern inventory, summary for reuse, reusable instructions, or an abstraction-object wrapper.

C1/C3 must not retain, create, retrieve, or pass to transfer any reusable abstraction artifact, generalized principle, applicability table, extracted summary, note, plan, skill, memory record, or other retained abstraction object. This boundary concerns visible retained objects, not inaccessible internal computation. Any prohibited object or equivalent content in the transfer package is abstraction leakage and invalidates the affected comparison.

## 6. Target Tasks

Target tasks are selected before execution from a frozen registry using three families: **structural diagnosis**, **constraint-aware recommendation**, and **causal explanation**. Each source package has one target from each family, yielding three target evaluations per condition and source package.

Every target must be unseen: its full content, answer key, and evaluator rubric are unavailable during the source step and abstraction creation. A target is eligible only when it differs from its source on at least **three of five** dimensions—domain/subject matter, surface representation, entities/vocabulary, task objective, and causal/structural arrangement—while the registry records why the candidate relation remains applicable. It must have no duplicate, paraphrase, shared answer, shared source unit, or shared unique entity set with its source or another target in its block.

Selection proceeds deterministically: registry entries are sorted by target ID; take the first eligible entry for each family after applying the stated overlap checks. The fixed execution order is source-package ID ascending, then target family order shown above, then condition order `C1`, `C2`, `C3`, `C4`; condition presentation order is independently randomized once with a recorded seed, while scoring uses canonical order. A target that fails eligibility is excluded before execution and replaced only by the next eligible registry entry under this rule.

## 7. Information Accounting

For each source and target invocation, an audit manifest records, in supplied order: system prompt, user prompt, source or target inputs, source response, citation/provenance identifiers, retained objects, abstraction artifact when applicable, tokenizer/version, unit and token counts, hashes, and condition ID. Target packages contain the target prompt, final source response, permitted citation/provenance identifiers, and only for C2/C4 the compliant artifact; they never contain raw source units.

The accounting unit is tokens produced by the frozen model tokenizer/version. The assigned target-package maximum is **4,096 tokens** in every condition. Count all supplied text and identifiers, including prompts and artifact. When a package is over budget, apply this deterministic order: remove optional whitespace; then remove provenance display labels while retaining fixed identifiers; then stop as a methodology failure if still over budget. Do not summarize, compress, silently truncate substantive content, or add information. C1/C2 and C3/C4 use the same accounting and same 4,096-token maximum. The manifest makes all four conditions auditable.

## 8. Controlled Variables

Freeze before execution one model provider, model identifier/version, tokenizer/version, decoding parameters, system prompt, source prompt template, target prompt template, scoring rubric, evaluator identity/program, execution environment image, and time/compute limit. Prompts may differ only where the condition requires the C2/C4 artifact instruction or the C1/C3 prohibition; all other wording is byte-identical. The same trained operator performs only predeclared mechanical procedures and never scores their own work. Each invocation uses a fresh session, account context, process, and cache namespace; session isolation forbids conversational carryover.

## 9. Confound Controls

Retrieval, external memory, persistent memory, context compression, and summarization outside the treatment are prohibited in all conditions. Evaluator feedback is unavailable until all outputs and scores for a block are frozen. Retries, self-reflection loops, tool use, adaptive prompting, hidden-state reuse, and reuse of prior outputs are prohibited. The model receives no network, filesystem, plugins, or tools. Any unequal treatment, including an unavailable control, is a methodology failure unless a separate preregistration explicitly crosses and freezes it before execution.

## 10. Outcome Measures

All scores use the target-task evaluation as the unit of analysis. Missing values are never imputed; an ineligible, stopped, or unscorable unit is excluded from numerical aggregation and reported with its reason. Exact score ties remain ties and receive no arbitrary ordering.

### Primary outcome

**Transfer correctness** is `1` when a blinded scorer, using the frozen rubric, finds that the target answer reaches the correct task conclusion and applies the source-derived relation within its stated scope; otherwise `0`. Aggregate as the mean across eligible target evaluations within condition, then report paired condition differences by identical source package and target. Higher is better; it is not evidence of necessity or internal abstraction.

### Secondary outcomes

- **Source-task correctness:** binary rubric score per source response; aggregate as a condition mean. It is descriptive and cannot replace transfer correctness.
- **Artifact compliance:** binary C2/C4 audit of all five required artifact elements; aggregate as compliant proportion. C1/C3 are not applicable, not zero.
- **Provenance coverage:** number of material artifact claims with valid source-unit mappings divided by all material claims; aggregate as a mean among compliant C2/C4 artifacts.
- **Overgeneralization rate:** target answers applying a relation outside recorded applicability conditions divided by eligible target answers; aggregate as a condition proportion. Lower is better.
- **Cross-target consistency:** for each source package/condition, proportion of applicable targets receiving mutually consistent principle application; aggregate as a condition mean.
- **Repeated-work count:** count of permitted model invocations after a source step (always one per target); aggregate as a mean and interpret only as an audit control, not reasoning effort.

### Diagnostic outcomes

Record target-package token count, retained-object inventory, source-unit availability, scorer agreement, exclusion count, and typed failure category. Aggregate as distributions/counts by condition. These diagnose comparability and never change the primary outcome.

## 11. Methodology Failures

The following are fatal: contamination between conditions; unequal accounted information within a context level; abstraction leakage; malformed or missing C2/C4 artifact; missing/invalid provenance; missing audit manifest; nonreproducible package hash or environment; unlogged operator intervention; target-overlap violation; forbidden tool, memory, retry, feedback, reflection, or hidden-state reuse; unavailable raw-source withholding; or a violated stopping rule. Mark the affected unit `METHODOLOGY_FAILURE`; if it affects a factorial contrast, no hypothesis classification may be issued for that contrast. A methodology failure is not a hypothesis failure and may not be recoded as an unfavorable result.

## 12. Stopping Rules

Per trial, stop before scoring on any fatal condition in Section 11 or an over-budget package. Per condition, stop remaining trials for that condition when two fatal trial failures occur or when a controlled variable cannot be held fixed. Stop the study when any condition stops, when an execution package cannot be reproduced from hashes, or after all preregistered source packages and their three targets have completed—whichever occurs first. Tooling failures trigger one recorded rerun only if no model invocation occurred; otherwise they invalidate that invocation. There is no discretionary stopping, extension, replacement, or rerun after observing outcomes.

## 13. Planned Analysis

The primary comparison is C1 versus C2 on paired transfer correctness at standard context. Report the paired mean difference and its exact two-sided paired permutation test at `α = 0.05`. Estimate context main effect as the average of `(C3 − C1)` and `(C4 − C2)`; estimate abstraction main effect as the average of `(C2 − C1)` and `(C4 − C3)`; interpret the interaction as `(C4 − C3) − (C2 − C1)`. Report each with paired mean difference and 95% bootstrap percentile interval (10,000 resamples, seed `94`).

Secondary analyses apply the same paired aggregation to the secondary measures and report results separately by the three preregistered task families. Family and secondary analyses are descriptive with Holm correction across the three secondary inferential comparisons; no subgroup is analyzed unless it is one of those families and has at least five eligible paired source packages. Exclude only units under the stated eligibility, stopping, or methodology-failure rules. No undisclosed post hoc analysis, alternate primary outcome, reclassification, or exploratory comparison may be presented as preregistered; any later exploratory analysis must be labeled exploratory.

## 14. Result Classifications

After validity checks, the study receives exactly one classification:

- `METHODOLOGY_FAILURE` if any fatal defect invalidates a primary factorial contrast or the study stopping rule stops the study.
- `INDETERMINATE` if no fatal defect exists but fewer than five eligible paired source packages complete, or the primary comparison is not significant and the absolute paired transfer difference is less than 0.10.
- `SUPPORTS_CANDIDATE_HYPOTHESIS` if the primary C2−C1 difference is at least `+0.10`, its exact test is significant, and neither the high-context abstraction contrast nor interaction reverses direction by `0.10` or more.
- `VIOLATES_CANDIDATE_HYPOTHESIS` if C2−C1 is at most `−0.10` with a significant exact test, or C1 matches/exceeds C2 within `0.10` while C3−C1 is at least `+0.10` and significant.
- `MIXED_OR_INTERACTION_DEPENDENT` otherwise, including a significant interaction of absolute magnitude at least `0.10` without a classification above.

These labels classify this candidate hypothesis under this protocol only; none establishes necessity, mechanism, novelty, or generality.

## 15. Artifact Retention

Retain in a versioned, access-controlled execution package: source-unit ordering and hashes; all prompts; model/tokenizer/environment bindings; abstraction artifacts; target registries and packages; raw outputs; scoring rubrics and scores; exclusions and failure records; all package hashes; timestamps/chronology; randomization seed; and the operator log. Preserve each object in canonical supplied order with condition and source/target identifiers. No retained execution artifact is created by this documentation-only registration.

## 16. Execution Boundary

Preregistration freezes the proposed methodology.
It does not authorize execution.
No empirical evidence, results, or conclusions are produced by this document.
Experiment execution requires a separate explicitly authorized investigation stage.
