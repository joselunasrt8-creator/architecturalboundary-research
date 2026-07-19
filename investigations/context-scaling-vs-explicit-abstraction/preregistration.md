# Preregistration: Context Scaling Versus Explicit Abstraction

**Registration status:** COMPLETE — documentation-only; execution is not authorized.

This registration operationalizes the prospective design in [the investigation design](investigation-design.md). The bounded literature review constrains these controls but is not empirical evidence ([design implications](literature/design-implications.md), [novelty determination](literature/novelty-determination.md)). Terms such as “context-only” and “explicit abstraction” have the qualified meanings in the [terminology reconciliation](literature/terminology-reconciliation.md).

## 1. Study Objective

**Research question.** Under controlled task conditions, does an explicit, inspectable generalized representation produce more correct transfer to materially different unseen target tasks than a context-only workflow, independently of the amount of available source information?

**Candidate hypothesis.** Scaling available input context increases information availability, but transforming information into reusable principles requires an explicit abstraction process.

**Purpose.** This prospective 2 × 2 investigation distinguishes the effect of a fixed increase in available source information from the effect of retaining an explicit generalized representation. It may support, violate, or leave the candidate hypothesis indeterminate; it does not test whether a model internally abstracts.

**Status and boundary.** This is a documentation-only preregistration. It creates no tasks, observations, datasets, artifacts, results, or empirical conclusion. It freezes methodology only and does not authorize execution.

## 2. Experimental Design

The unit of analysis is one **source-package/condition/target-task evaluation**. The execution cohort is frozen at exactly **eight** source packages, `SP01` through `SP08`; no ninth package may be added and none may be substituted. One source package is evaluated in every condition; each condition receives the same target task in a block, and no output from one condition is available to another.

Each of the eight packages has exactly one preregistered target in each of the three families. Therefore the planned evaluation count is exactly `8 packages × 4 conditions × 3 targets = 96` source-package/condition/target evaluations (24 per condition, 32 per target family, and 12 per package). The 32 source-step invocations (`8 × 4`) are preparation steps, not additional units of analysis.

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

The standard information level is **N = 8 source units** (`U001`–`U008`). The high information level is **M = 16 source units** (`U001`–`U016`), so `M > N`; it includes every standard unit plus `U009`–`U016`. Each of the fixed packages `SP01`–`SP08` must have at least 16 eligible units before its first invocation. A package with fewer than 16 eligible units is a methodology failure, not a reason to lower either level, add a package, or substitute a package.

Effective source information is the ordered list of eligible units actually supplied, plus their deterministic token count under the model tokenizer named in Section 8. Nominal model context-window capacity is not an information measure. The maximum **complete source-step input** budget, counting the system prompt, rendered source prompt, package/condition identifiers, every delimiter, every source-unit identifier, and every verbatim source-unit byte, is **4,096 tokens** for C1/C2 (`N = 8`) and **8,192 tokens** for C3/C4 (`M = 16`). Before an API request is constructed, tokenize the complete would-be source input exactly as rendered. If it exceeds its condition maximum, do not invoke the model and record `METHODOLOGY_FAILURE`; do not truncate, compress, summarize, substitute, reorder, omit, normalize, or otherwise alter the fixed source package. Record unit IDs, hashes, tokenizer/version, token count, and any excluded unit for every source invocation.

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

Selection proceeds deterministically: registry entries are sorted by target ID; take the first eligible entry for each family after applying the stated overlap checks. Canonical identifiers and analysis order are source-package ID ascending, then target family order shown above, then condition order `C1`, `C2`, `C3`, `C4`; this is not an execution-order instruction. The distinct, complete execution-order procedure is in Section 8. A target that fails eligibility before any model invocation makes its fixed package ineligible; it is **not** replaced, because replacement would change the frozen cohort and the 96-evaluation design.

## 7. Information Accounting

For each source and target invocation, an audit manifest records, in supplied order: system prompt, user prompt, source or target inputs, source response, citation/provenance identifiers, retained objects, abstraction artifact when applicable, tokenizer/version, unit and token counts, hashes, and condition ID. For C2/C4, parse the strict UTF-8 source output at the first byte-exact line `ABSTRACTION:`: the nonempty bytes before that line are the final source response and the nonempty bytes after it are the separately retained artifact; the delimiter itself is retained in neither object. A missing, repeated, or malformed delimiter is a methodology failure. C1/C3 retain their entire source output as the final source response. Target packages contain the target prompt, that final source response, permitted citation/provenance identifiers, and only for C2/C4 the separately retained artifact; they never contain raw source units or duplicate the artifact through the source response.

The accounting unit is tokens produced by the frozen model tokenizer/version. The assigned target-package maximum is **4,096 tokens** for C1/C2 and **8,192 tokens** for C3/C4. Count all supplied text and identifiers, including prompts and artifact. Before invocation, tokenize the complete rendered package. If it is over its condition maximum, stop as a methodology failure. Do not remove whitespace or labels, truncate, compress, summarize, substitute, reorder, or otherwise alter a fixed package. C1/C2 use the same accounting and maximum, as do C3/C4. The manifest makes all four conditions auditable.

## 8. Immutable Execution Bindings and Randomization

All execution choices are bound by this merged document; an executor may not select, upgrade, substitute, or “freeze” any of them later. The following literal bindings, including capitalization and punctuation, are the authoritative execution package:

| Control | Immutable binding |
| --- | --- |
| Model/version policy | OpenAI Responses API model `gpt-4.1-2025-04-14`; no model alias, fallback, routing, or version upgrade is permitted. |
| Tokenizer | `o200k_base`, package `tiktoken==0.9.0`; tokenization is UTF-8 input encoded by that tokenizer with no normalization. |
| System prompt | `You are a careful research assistant. Follow the user message exactly. Do not use tools, browse, retrieve, or rely on information not supplied in this conversation. Return only the requested answer.` |
| Source prompt template | `SOURCE PACKAGE {package_id}; CONDITION {condition_id}. Source units, in order: {source_units}. Produce the source-specific answer. {retention_instruction}` |
| Target prompt template | `TARGET {target_id}; CONDITION {condition_id}. Retained package: {retained_package}. Solve the target. State the conclusion and a concise justification. Do not use tools, retrieval, or outside knowledge.` |
| Retention instruction | C1/C3: `Return only the source-specific answer; do not create or state any reusable abstraction.` C2/C4: `Return the source-specific answer, then exactly one line ABSTRACTION:, then the abstraction containing principle, applicability conditions, limitations/failure cases, source-unit provenance for every material claim, and reuse instructions.` |
| Scoring rubric | The frozen target registry supplies, for each target, a nonempty ordered `answer_key.required_literals` array, an ordered `answer_key.forbidden_literals` array (possibly empty), and a `scope_rubric` containing nonempty ordered `relation_literals` and `required_applicability_literals` arrays plus an ordered `forbidden_applicability_literals` array (possibly empty). These literal arrays are the answer key and applicability conditions: they are created and hashed with the frozen target registry before any invocation, are unavailable to the model, and cannot contain `KEY_MATCH`, `SCOPE_MATCH`, a score, or an outcome label. |
| Evaluator | A deterministic, offline evaluator—not a human or model—derives rather than reads the two booleans. It accepts only the retained raw target-output UTF-8 bytes and the hashed target-registry answer key and scope rubric. Decode as strict UTF-8; normalize each input string by Unicode NFKC, Unicode case-folding, replacing every maximal Unicode-whitespace run with one ASCII space, then trimming ASCII spaces. A literal matches only as a contiguous substring of the normalized raw output. Set `KEY_MATCH=true` exactly when every normalized required literal matches and no normalized forbidden literal matches. Set `SCOPE_MATCH=true` exactly when every normalized relation and required-applicability literal matches and no normalized forbidden-applicability literal matches. Emit canonical JSON, with exactly `target_id`, `raw_output_sha256`, `answer_key_sha256`, `scope_rubric_sha256`, `KEY_MATCH`, `SCOPE_MATCH`, and `score`, where `score = KEY_MATCH AND SCOPE_MATCH`; reject undecodable output, an empty normalized literal, malformed registry data, a hash mismatch, or any other input/output field as `METHODOLOGY_FAILURE`. No registry field may prestate either boolean. |
| Environment | Execution is split into the controlled networked invocation boundary and the isolated scoring/audit environment specified immediately below. Neither component supplies the model with tools, retrieval, filesystem access, plugins, cache, or persistent memory. |
| Time limit | 120 wall-clock seconds per source or target invocation; a timeout is a fatal methodology failure, with no retry. |
| Decoding | Send exactly `temperature=0`, `top_p=1`, `max_output_tokens=2048`, `presence_penalty=0`, `frequency_penalty=0`, and `seed=20260719`; omit every other optional decoding parameter, make no tools available, and log the complete request JSON. |

The source-package roster is exactly `SP01`, `SP02`, `SP03`, `SP04`, `SP05`, `SP06`, `SP07`, and `SP08`. Before the first model invocation, each roster member and all three of its selected targets must pass Sections 3 and 6 eligibility checks. This is a gate, not a selection opportunity: a failed member is neither excluded from aggregation nor replaced. It prevents execution and records `METHODOLOGY_FAILURE` for the study, so the planned denominator remains 96 and the minimum-five-pair rule cannot be used to salvage a reduced design.

**Execution order and condition-presentation randomization (not bootstrap).** Use the integer seed `20260719`, distinct from the Section 13 bootstrap seed `94`. Execute exactly two stages. **Stage 1 (source):** visit `SP01` through `SP08` in ascending order and, for each package, run its four source invocations in canonical condition order `C1`, `C2`, `C3`, `C4`; no target task, target identifier, answer key, or scope rubric is exposed in this stage. **Stage 2 (target):** visit packages in ascending order and target families in the Section 6 order. For each `(package_id, target_family)` block, derive `d = SHA-256("context-transfer-condition-order-v1|20260719|{package_id}|{target_family}")`. Interpret the first 16 hexadecimal characters of `d` as an unsigned 64-bit big-endian integer. Starting from `[C1, C2, C3, C4]`, apply Fisher–Yates for `i = 3, 2, 1`, swapping positions `i` and `j = (integer // 4^(3-i)) mod (i+1)`, and execute the four target invocations in the resulting order. Do not generate random numbers, reseed, shuffle again, or use outcome information. After each block is frozen, restore its retained outputs by their `(package_id, target_family, condition_id)` identifiers to the Section 6 canonical condition order for scoring, package aggregation, and analysis; chronology remains in the audit log.

Prompts may differ only in the literal retention instruction above; all other wording is byte-identical. The same trained operator performs only predeclared mechanical procedures and never scores their own work. Each invocation uses a fresh session, account context, process, and cache namespace; session isolation forbids conversational carryover.

**Invocation and scoring boundaries.** The controlled networked invocation boundary is a fresh Linux/amd64 process that may make exactly one outbound TLS connection per invocation: `POST https://api.openai.com/v1/responses` on port `443`, after resolving and allowlisting only `api.openai.com`. Its egress firewall denies every other hostname, IP address, port, protocol, and inbound connection; no proxy, redirect, callback, telemetry, package installation, browsing, or unrelated network request is permitted. It constructs the complete pinned request JSON locally from the applicable frozen prompt/package and decoding row, sends no tools, and records a canonical request log containing the endpoint, request body, non-secret headers, UTC start/end timestamps, HTTP status, response identifier, and SHA-256 hashes of the canonical request JSON and retained raw response bytes. The `Authorization: Bearer` credential is injected only into that process by a one-invocation secret mechanism, is never written to disk, prompt, response, manifest, hash preimage, or log, and is destroyed when the process exits. Credential absence, a second request, an unexpected endpoint, redirect, non-2xx response, or logging failure is a fatal methodology failure with no retry after a request is sent.

After the response is received, the boundary writes the raw response bytes and its SHA-256 digest to the retained execution package. For a target response, it parses that JSON with duplicate keys rejected, takes the `output` array in array order, and concatenates without separators the `text` strings of every content item whose `type` is exactly `output_text`; this strict UTF-8 concatenation is the retained raw target-output bytes. A missing/non-string `output_text` item, an empty concatenation, or any unrecognized output item type is a methodology failure. The boundary transfers only those bytes, the frozen target-registry record, and their recorded hashes through a one-way local handoff to the isolated scoring/audit environment. The scoring/audit environment is a fresh Linux/amd64 container with network disabled, a read-only filesystem except empty `/work`, no mounted credentials, no tools, plugins, cache, or persistent volumes. It runs only `tiktoken==0.9.0`, SHA-256, and the deterministic evaluator above; it cannot invoke the API or any other network service. It verifies every handoff hash, derives and records the score, and emits an audit record that links the request hash, response hash, registry hashes, evaluator output, and container image digest. The operator may inspect neither answer keys nor scores until the block is frozen.

## 9. Confound Controls

Retrieval, external memory, persistent memory, context compression, and summarization outside the treatment are prohibited in all conditions. Evaluator feedback is unavailable until all outputs and scores for a block are frozen. Retries, self-reflection loops, tool use, adaptive prompting, hidden-state reuse, and reuse of prior outputs are prohibited. The model receives no network, filesystem, plugins, or tools. Any unequal treatment, including an unavailable control, is a methodology failure unless a separate preregistration explicitly crosses and freezes it before execution.

## 10. Outcome Measures

All scores use the target-task evaluation as the unit of analysis. Missing values are never imputed; an ineligible, stopped, or unscorable unit is excluded from numerical aggregation and reported with its reason. Exact score ties remain ties and receive no arbitrary ordering.

### Primary outcome

**Transfer correctness** is `1` when the frozen deterministic evaluator finds that the target answer reaches the correct task conclusion and applies the source-derived relation within its stated scope; otherwise `0`. Aggregate as the mean across eligible target evaluations within condition, then report paired condition differences by identical source package and target. Higher is better; it is not evidence of necessity or internal abstraction.

### Secondary outcomes

- **Source-task correctness:** binary rubric score per source response; aggregate as a condition mean. It is descriptive and cannot replace transfer correctness.
- **Artifact compliance:** binary C2/C4 audit of all five required artifact elements; aggregate as compliant proportion. C1/C3 are not applicable, not zero.
- **Provenance coverage:** number of material artifact claims with valid source-unit mappings divided by all material claims, calculated over every produced C2/C4 artifact before the compliance filter; malformed artifacts receive `0` and are separately reported. Aggregate as a mean.
- **Overgeneralization rate:** target answers that assert or apply a `relation_literal` while failing a required applicability literal or matching a forbidden applicability literal under the Section 8 evaluator are overgeneralizations. This evaluator-side target-specific scope rubric is frozen independently of every condition and applies identically to C1–C4; it does not require C1/C3 to retain applicability artifacts. Divide by eligible target answers and aggregate as a condition proportion. Lower is better.
- **Cross-target consistency:** for each source package/condition, proportion of applicable targets receiving mutually consistent principle application; aggregate as a condition mean.
- **Repeated-work count:** count of permitted model invocations after a source step (always one per target); aggregate as a mean and interpret only as an audit control, not reasoning effort.

### Diagnostic outcomes

Record target-package token count, retained-object inventory, source-unit availability, scorer agreement, exclusion count, and typed failure category. Aggregate as distributions/counts by condition. These diagnose comparability and never change the primary outcome.

## 11. Methodology Failures

The following are fatal: contamination between conditions; unequal accounted information within a context level; abstraction leakage; malformed or missing C2/C4 artifact; missing/invalid provenance; missing audit manifest; nonreproducible package hash or environment; unlogged operator intervention; target-overlap violation; forbidden tool, memory, retry, feedback, reflection, or hidden-state reuse; unavailable raw-source withholding; or a violated stopping rule. Mark the affected unit `METHODOLOGY_FAILURE`; if it affects a factorial contrast, no hypothesis classification may be issued for that contrast. A methodology failure is not a hypothesis failure and may not be recoded as an unfavorable result.

## 12. Stopping Rules

Before any invocation, stop the study as `METHODOLOGY_FAILURE` if any one of the eight fixed packages or its three fixed targets fails eligibility. Per trial, stop before scoring on any fatal condition in Section 11 or an over-budget package. Per condition, stop remaining trials for that condition when two fatal trial failures occur or when a controlled variable cannot be held fixed. Stop the study when any condition stops, when an execution package cannot be reproduced from hashes, or after all **96** preregistered evaluations (eight packages × three targets × four conditions) have completed—whichever occurs first. Tooling failures trigger one recorded rerun only if no model invocation occurred; otherwise they invalidate that invocation. There is no discretionary stopping, extension, replacement, or rerun after observing outcomes.

## 13. Planned Analysis

The analysis dataset first restores Stage-2 outputs to canonical order. For every package `p` and condition `c`, define its package score `S[p,c]` as the arithmetic mean of its three binary target scores, in the fixed family order (structural diagnosis, constraint-aware recommendation, causal explanation). A package is eligible for a contrast only if all three target scores exist for both conditions; no target-level sign flips, imputation, or partial-package averages are permitted. Thus the planned primary and each factorial contrast have the eight package-level paired differences as their permutation units.

For every listed contrast, define `D[p] = S[p,right] − S[p,left]` and the observed statistic `T = mean_p(D[p])`. Its null hypothesis is that the distribution of package-level paired differences is symmetric about zero (equivalently, each package difference has an exchangeable sign under the null); the alternative is two-sided. The exact sign-flip test enumerates all `2^k` vectors `z ∈ {-1,+1}^k` for the `k` eligible packages, calculates `T(z) = mean_p(z[p] D[p])`, and reports `p_raw = count(|T(z)| >= |T_observed|) / 2^k`. This is the complete permutation procedure; no Monte Carlo draw, continuity correction, or alternate statistic is used. A contrast is **significant** exactly when its Holm-adjusted p value is at most `0.05`, as defined below.

The four result-classification contrasts are: C2−C1 (standard-context abstraction), C3−C1 (context effect without abstraction), C4−C3 (high-context abstraction), and the interaction `(C4−C3)−(C2−C1)`. For the interaction, use its eight package differences `D[p] = (S[p,C4]-S[p,C3])-(S[p,C2]-S[p,C1])` in the same test. Their four `p_raw` values form one family; sort ascending (ties by contrast order just listed), multiply the smallest by 4, next by 3, next by 2, last by 1, cap each at 1, then take the cumulative maximum in that sorted order and return values to contrast order. Those are the Holm-adjusted p values used everywhere in Section 14. The two-sided familywise alpha is `0.05`.

Report each `T`, its raw and Holm-adjusted p values, `k`, and the eight package differences. Bootstrap percentile intervals (10,000 resamples of package IDs with replacement, seed `94`) are descriptive only and do not define significance. Estimate the context main effect as the mean of package values `((S[C3]-S[C1]) + (S[C4]-S[C2])) / 2`; estimate the abstraction main effect analogously as `((S[C2]-S[C1]) + (S[C4]-S[C3])) / 2`; report both with the same descriptive bootstrap interval and without a result-classification significance claim.

Secondary analyses apply package-level aggregation to secondary measures and report results separately by the three preregistered task families. They are descriptive: no secondary result is called significant or used for classification. Exclude only units under the stated eligibility, stopping, or methodology-failure rules. No undisclosed post hoc analysis, alternate primary outcome, reclassification, or exploratory comparison may be presented as preregistered; any later exploratory analysis must be labeled exploratory.

## 14. Result Classifications

After validity checks, the study receives exactly one classification:

- `METHODOLOGY_FAILURE` if any fatal defect invalidates a primary factorial contrast or the study stopping rule stops the study.
- `INDETERMINATE` if no fatal defect exists but fewer than five eligible paired source packages complete, or the primary comparison is not significant (as Section 13 defines) and the absolute paired transfer difference is less than 0.10. Under this frozen eight-package design, this branch can occur only after a nonfatal post-invocation loss that is explicitly permitted by Sections 11–12; pre-invocation eligibility loss and stopping never reduce the cohort to create it.
- `SUPPORTS_CANDIDATE_HYPOTHESIS` if C2−C1 is at least `+0.10`, C2−C1 is significant, and neither C4−C3 nor the interaction is at most `−0.10`.
- `VIOLATES_CANDIDATE_HYPOTHESIS` if C2−C1 is at most `−0.10` and C2−C1 is significant, or C1 matches/exceeds C2 within `0.10` while C3−C1 is at least `+0.10` and C3−C1 is significant.
- `MIXED_OR_INTERACTION_DEPENDENT` otherwise, including an interaction with absolute magnitude at least `0.10` that is significant.

In this section, every use of “significant” means the corresponding Section 13 exact two-sided sign-flip test has Holm-adjusted `p ≤ 0.05`; no other result has a significance status. These labels classify this candidate hypothesis under this protocol only; none establishes necessity, mechanism, novelty, or generality.

## 15. Artifact Retention

Retain in a versioned, access-controlled execution package: source-unit ordering and hashes; all prompts; model/tokenizer/environment bindings; abstraction artifacts; target registries and packages; raw outputs; scoring rubrics and scores; exclusions and failure records; all package hashes; timestamps/chronology; randomization seed; and the operator log. Preserve each object in canonical supplied order with condition and source/target identifiers. No retained execution artifact is created by this documentation-only registration.

## 16. Execution Boundary

Preregistration freezes the proposed methodology.
It does not authorize execution.
No empirical evidence, results, or conclusions are produced by this document.
Experiment execution requires a separate explicitly authorized investigation stage.
