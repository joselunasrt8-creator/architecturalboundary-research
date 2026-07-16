# Minimal Promotion Package Contract

## Status and scope

This document defines the producer-side Minimal Promotion Package contract for `architecturalboundary-research`.
A Minimal Promotion Package is the smallest immutable research package this repository may use to propose bounded formalization work to `structural-analysis-foundations`.
The package is documentation- and evidence-referential: it references canonical artifacts already produced by this repository and does not duplicate their contents.

This contract does not define schemas, validators, package instances, registries, workflows, automation, adapters, synchronization behavior, candidate invariants, formal objects, or theorems.
It does not require or imply any change to SYNAPSE or to a downstream repository.

## Purpose

The purpose of a Minimal Promotion Package is to make a bounded, replayable, evidence-linked proposal that a consumer may inspect when deciding whether a research result is eligible for formalization consideration.
The package proposes; it does not authorize.

A package exists to:

1. identify the producer-owned proposal being made;
2. reference the canonical empirical artifacts that support, contradict, or leave indeterminate the proposal context;
3. preserve immutable source-commit and artifact-hash provenance for those references;
4. state limitations, uncertainty, corrections, withdrawal state, and supersession state; and
5. preserve the authority boundary between empirical research and downstream formalization decisions.

## Architectural invariants

The contract is governed by the following invariants:

- Empirical Evidence is not Canonical Authority.
- Promotion Package is not Promotion Decision.
- Publication Readiness is not Formalization Eligibility.
- Retained Classification is not Candidate Invariant.
- The producer owns the proposal.
- The consumer owns the decision.

A conforming package must preserve these invariants in its title, summary, referenced artifacts, limitations, and decision-language.
It must not state or imply that a recurring empirical result is already a formal object, theorem, accepted invariant, downstream registry entry, or authorized canonical boundary.

## Publication readiness boundary

Publication readiness is required review context when publication-state artifacts are available for the referenced investigation or cohort.
A package must state the applicable publication state and reference the publication or release manifest when one exists.

Publication readiness is not scientific support.
Publication readiness is not formalization eligibility.
A publication-ready artifact set may still yield an indeterminate or violating cohort outcome that blocks `candidate_invariant_review` and limits the package to the outcome-sensitive purposes defined below.

## Package eligibility rules

A Minimal Promotion Package is eligible to be created only when all of the following are true:

1. The producer repository has completed the canonical artifacts necessary for the package purpose.
2. Every referenced artifact is already repository-contained, canonical for its lifecycle stage, and stable enough to be referenced with a source commit SHA and artifact hash.
3. The package can be expressed by references to existing artifacts rather than by copying BOR, SRF, DER, MSR, dataset, analysis, retained-classification, or cohort-conclusion content.
4. The proposal can be bounded to a specific investigation, cohort, artifact set, package purpose, proposed foundation repository, proposed foundation surface, candidate claim, and excluded claims.
5. The proposal can identify known limitations and uncertainty without converting them into downstream obligations.
6. The proposal can be replayed by resolving its artifact references and provenance metadata.
7. The package does not create candidate invariants, formal objects, theorems, registry entries, validators, workflows, or consumer-side decisions.
8. The declared package purpose is permitted by the empirical outcome eligibility matrix in this contract.

A package is not eligible merely because a manuscript is publication-ready, a retained classification exists, or an empirical pattern appears interesting.
Publication readiness may indicate that artifacts are organized for external reading, but it is neither scientific support nor formalization eligibility.

## Package-purpose taxonomy

A Minimal Promotion Package must declare exactly one package purpose.
The purpose constrains what the package may propose and what canonical artifacts it must reference.
Package purpose is separate from package lifecycle status: correction, withdrawal, and supersession are represented by `package_status`, `supersession_lineage`, `correction_reason`, and `withdrawal_reason`, not as scientific review purposes.

| Purpose | Meaning | Required canonical artifact classes |
| --- | --- | --- |
| `candidate_invariant_review` | Proposes that the consumer inspect a supported empirical result for possible downstream treatment as a candidate invariant. | BOR, SRF, DER, MSR, Comparative Dataset, Analysis, Retained Classification, Cohort Conclusion, and applicable publication-state artifacts. |
| `bounded_formal_question` | Proposes a narrow formal question arising from supported, indeterminate, or violating empirical evidence without asserting a candidate invariant. | The canonical artifacts establishing the question boundary, including Retained Classification and Cohort Conclusion when available. |
| `counterexample_review` | Proposes consumer inspection of empirical evidence that violates or counters a possible invariant or formal claim. | The artifacts establishing the violation, negative evidence, basis systems, and cohort conclusion. |
| `vocabulary_alignment` | Proposes terminology or concept-boundary alignment between producer empirical vocabulary and consumer formal vocabulary without asserting formal acceptance. | The artifacts establishing terminology usage, classification context, and proposal boundary. |
| `model_obligation` | Proposes that the consumer inspect whether a formal model would need to account for an observed empirical obligation, gap, or constraint. | The artifacts establishing the obligation, missing measurements, indeterminate evidence, or negative evidence. |
| `indeterminate_evidence_review` | Proposes consumer inspection of an indeterminate empirical outcome, including why the evidence does not support candidate-invariant review. | Analysis, Retained Classification, Cohort Conclusion, basis systems, missing measurement summary, indeterminate evidence summary, and relevant upstream lineage. |

The taxonomy is intentionally limited to producer proposals.
No purpose authorizes formalization or creates consumer-side acceptance semantics.

## Outcome-sensitive eligibility

A package must bind its purpose to the empirical result recorded in the canonical retained classification and cohort conclusion.
The `cohort_outcome` field controls which purposes are eligible.

| `cohort_outcome` | Eligible package purposes | Prohibited package purposes |
| --- | --- | --- |
| `supports` | `candidate_invariant_review` may be eligible, but only within the registered scope; `bounded_formal_question`, `vocabulary_alignment`, and `model_obligation` may also be eligible when bounded by the evidence. | Any purpose that exceeds the registered scope, omits contrary evidence, or treats support as consumer acceptance. |
| `indeterminate` | `indeterminate_evidence_review`, `bounded_formal_question`, `vocabulary_alignment`, and `model_obligation` may be eligible when the package preserves uncertainty. | `candidate_invariant_review` is never supported by an indeterminate cohort outcome. |
| `violates` | `counterexample_review` and `bounded_formal_question` may be eligible when the package preserves negative evidence and known counterexamples. | `candidate_invariant_review` is never supported by a violating cohort outcome. |

An indeterminate or violating result must not be repackaged under a generic formalization purpose.
A supported result may propose `candidate_invariant_review` only for the registered claim scope and only when the complete outcome evidence remains visible.

## Current B2 constraint

For the current B2 governance cohort, the canonical cohort conclusion records `cohort_outcome = indeterminate`.
Therefore a B2 Minimal Promotion Package may support `indeterminate_evidence_review` and may support bounded secondary purposes such as `bounded_formal_question`, `vocabulary_alignment`, or `model_obligation` when each is explicitly bounded by the B2 evidence.
A B2 package must not declare `candidate_invariant_review` unless a future canonical cohort conclusion supersedes the current indeterminate outcome with a supported outcome under the registered scope.

## Minimum required field model

A conforming Minimal Promotion Package must name and populate, or explicitly mark as not applicable with rationale, at least the following fields:

1. `package_id`
2. `package_version`
3. `package_status`
4. `package_purpose`
5. `source_repository`
6. `source_commit_sha`
7. `created_at`
8. `hash_algorithm`
9. `protocol_version`
10. `investigation_id`
11. `registration_ref_and_hash`
12. `decision_rule_ref`
13. `cohort_rule_ref`
14. `source_artifact_refs_and_hashes`
15. `retained_classification_ref_and_hash`
16. `cohort_conclusion_ref_and_hash`
17. `per_system_classification_summary`
18. `cohort_outcome`
19. `basis_systems`
20. `missing_measurement_summary`
21. `supporting_evidence_summary`
22. `indeterminate_evidence_summary`
23. `negative_evidence_summary`
24. `known_limitations`
25. `replication_status`
26. `replay_status`
27. `validation_commands`
28. `publication_state`
29. `proposed_foundation_repository`
30. `proposed_foundation_surface`
31. `candidate_claim`
32. `excluded_claims`
33. `non_authority_statement`
34. `supersession_lineage`
35. `correction_reason`
36. `withdrawal_reason`

The field model is a documentation contract, not a schema.
A package may add fields, but it must not omit these fields or obscure their meaning through aliases.

## Target and claim boundaries

Every package must expose the consumer-facing proposal surface explicitly:

- `proposed_foundation_repository` identifies the downstream repository or authority surface being asked to inspect the proposal.
- `proposed_foundation_surface` identifies the bounded area, module, theory surface, vocabulary surface, or review surface within that repository.
- `candidate_claim` states the producer's bounded claim or question for the declared package purpose.
- `excluded_claims` states claims the producer is not making, including any stronger invariant, theorem, proof, or authority claim.

The proposal summary and scope boundary do not substitute for these fields.
The target and claim boundaries are required to prevent a package from being read as a broad request for downstream formalization.

## Canonical artifact reference rules

A package references existing canonical artifacts; it does not embed, regenerate, summarize as replacement, or reinterpret them.
References must be repository-relative and specific enough to resolve the artifact being relied on.
When a referenced artifact is itself derived from earlier artifacts, the package may reference the downstream canonical artifact and its lineage rather than duplicating the full upstream content.

The following artifact classes may be referenced when relevant to the declared purpose:

- preregistration and protocol sources;
- Baseline Observation Records (BOR);
- Surface Record Files (SRF);
- Derived Evidence Records (DER);
- Measurement Summary Records (MSR);
- Comparative Dataset artifacts;
- Analysis artifacts;
- Retained Classification artifacts;
- Cohort Conclusion artifacts; and
- publication or release manifests that identify immutable publication state.

A package must not copy BOR observations, SRF surfaces, DER claims, MSR measurements, dataset rows, analysis results, retained-classification decisions, or cohort conclusions into itself as substitute canonical content.

## Immutable provenance requirements

A Minimal Promotion Package must preserve immutable provenance for the package and for each referenced artifact.
At minimum, provenance must identify:

1. the producer repository;
2. the source commit SHA for the producer repository state that emitted the package;
3. the repository-relative path of each referenced artifact;
4. the artifact identifier when the artifact has one;
5. the lifecycle stage of each artifact;
6. the hash algorithm used for artifact hashes;
7. the artifact hash for each referenced artifact;
8. the package creation date;
9. the package authoring or generation method, if any;
10. the release, manifest, or other immutable locator used to resolve publication state when applicable; and
11. the package revision relationship to prior packages, corrections, withdrawals, or supersessions.

If a source commit SHA or artifact hash is unavailable for a referenced artifact, the package must state that limitation explicitly and must not represent the reference as frozen.
Mutable branch names, local paths outside the repository, and external review surfaces are not sufficient provenance by themselves.

## Replay expectations

A reader must be able to replay the proposal by resolving the package's canonical artifact references, verifying the source commit SHA and artifact hashes, and following the repository's existing artifact lineage.
Replay means reconstructing the evidence chain used by the proposal; it does not mean recomputing downstream formalization results.

A package should support replay of:

1. the investigation and protocol context;
2. the BOR to SRF to DER to MSR evidence lineage when those artifacts are in scope;
3. the MSR to comparative-dataset projection when the dataset is in scope;
4. the dataset to analysis relation when analysis is in scope;
5. the analysis to retained-classification relation when retained classification is in scope;
6. the retained-classification to cohort-conclusion relation when a cohort conclusion is in scope; and
7. the publication or release manifest relation when publication state is available.

Replay expectations are referential.
They must not introduce new validators, workflows, automation, adapters, or synchronization requirements as part of this contract.

## Complete outcome evidence requirement

A package must present a complete outcome summary for the declared scope.
It must not cherry-pick favorable evidence or omit outcome categories that change the interpretation of the proposal.

A conforming package must not omit:

- supporting systems;
- indeterminate systems;
- violating systems;
- basis systems;
- missing measurements;
- negative evidence; or
- known counterexamples.

If a category has no members, the package must state that the category is empty rather than omitting it.
If a category is not applicable to the declared purpose, the package must state why it is not applicable.

## Limitation requirements

Every package must contain a limitations section.
The section must identify known boundaries of the proposal, including:

- evidence gaps or unavailable observations;
- scope exclusions;
- non-generalized findings;
- unsupported interpretations;
- artifact stages that are absent, incomplete, corrected, or superseded;
- assumptions required to read the proposal;
- claims that the package explicitly does not make; and
- any publication-readiness constraints that affect review context but do not establish scientific support.

A limitation must not be hidden by promotion language.
If a limitation affects formalization relevance, the package must state that the consumer owns any decision about whether the limitation is acceptable.

## Uncertainty handling

A package must preserve uncertainty rather than resolving it by assertion.
Uncertainty may include missing evidence, competing interpretations, measurement incompleteness, cohort-size constraints, domain specificity, negative results, known counterexamples, or retained classifications that do not rise to formalization relevance.

Uncertainty must be represented as part of the proposal context and must not be converted into a candidate invariant, theorem obligation, or downstream acceptance criterion.
Where uncertainty depends on a canonical artifact, the package must reference that artifact rather than restating the evidence in full.

## Ownership

The producer repository owns:

- creation of the package;
- correctness of package references to producer artifacts;
- package limitations and uncertainty statements;
- corrections, withdrawals, and supersession notices; and
- the bounded proposal semantics.

The consumer owns:

- whether to inspect the package;
- whether the package is admissible for downstream consideration;
- whether any formalization work is accepted, rejected, deferred, or scoped differently;
- any downstream canonical objects, if created under consumer authority; and
- the consumer-side decision record.

No producer package may require the consumer to accept a promotion, create a formal object, or preserve the producer's terminology as canonical authority.

## Package status and lifecycle fields

Package status is separate from package purpose.
A package must use `package_status` and lifecycle fields to represent correction, withdrawal, and supersession state.
Allowed package-status meanings are:

- `current`: the producer currently stands behind the package;
- `corrected`: a later package version or append-only correction record corrects the package;
- `withdrawn`: the producer no longer stands behind the package;
- `superseded`: a later package replaces the package for current producer-side proposal purposes; and
- `superseding`: the package replaces an earlier package for current producer-side proposal purposes.

`supersession_lineage` records superseded and superseding package identifiers.
`correction_reason` records why a correction exists or states that no correction applies.
`withdrawal_reason` records why withdrawal exists or states that no withdrawal applies.

## Correction policy

A package version is immutable after emission.
A historical emitted package must not be edited, even when repository mechanics technically allow it.

Correction must occur through either:

1. a new package version that references the corrected package and states the correction; or
2. an append-only correction record that references the corrected package and states the correction.

A correction notice must identify the corrected package, state the correction, identify affected artifact references or provenance, and indicate whether the corrected package remains current, corrected, superseded, or withdrawn.
A correction must not silently rewrite the historical meaning of the original package.

## Withdrawal policy

Withdrawal means the producer no longer stands behind a prior proposal.
A withdrawal notice must identify the withdrawn package, state the withdrawal rationale in `withdrawal_reason`, identify affected artifacts when relevant, and preserve the historical fact that the package existed.

Withdrawal does not delete downstream decisions and does not require a consumer to take any action.
The consumer owns any response to the withdrawal under its own authority.

## Supersession policy

Supersession means a later package replaces an earlier package for current producer-side proposal purposes.
A supersession notice must identify both the superseded and superseding packages in `supersession_lineage`, state the reason for supersession, and identify material changes in artifact references, scope, limitations, uncertainty, outcome evidence, target surface, claim boundary, or provenance.

Supersession does not invalidate the historical existence of the superseded package.
It also does not imply downstream acceptance of the superseding package.

## Non-authority semantics

A Minimal Promotion Package has no authority to authorize promotion.
It must be read as a producer-side proposal or notice only.

Specifically, a package is not:

- a promotion decision;
- a consumer acceptance record;
- a candidate invariant;
- a formal object;
- a theorem;
- a proof obligation;
- a registry entry in a downstream authority;
- a synchronization contract;
- a workflow trigger;
- evidence that publication readiness equals scientific support; or
- evidence that publication readiness equals formalization eligibility.

The package may help a consumer decide what to inspect, but the consumer's decision is separate, downstream, and outside the authority of this repository.
