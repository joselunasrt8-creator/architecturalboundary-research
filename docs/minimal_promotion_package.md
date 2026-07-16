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

## Immutable package identity

Package identity is deterministic, repository-scoped, and version-qualified.
The `package_id` value is unique within this producer repository across all Minimal Promotion Packages and lifecycle records, regardless of package purpose, investigation, target repository, lifecycle state, or historical status.
No two unrelated proposal lineages may reuse the same `package_id`.

The identifier syntax is documentation-level and intentionally schema-free: `package_id` must be a stable ASCII lowercase slug composed only of `a-z`, `0-9`, and hyphen characters, must begin with a letter, must end with a letter or digit, and must contain enough semantic context to avoid collision within this repository.
A package identifier must not encode mutable lifecycle state, mutable publication state, mutable branch names, or consumer decisions.

Identity has two levels:

1. `package_id` identifies the continuing producer-side proposal lineage.
2. The ordered pair (`package_id`, `package_version`) identifies one immutable emitted package version.

For deterministic replay, artifact verification, and historical citation, identity is the pair (`package_id`, `package_version`).
`package_id` alone is a lineage locator and must not be used to cite a historical package version when multiple versions exist.

Corrections preserve `package_id` when the producer is correcting the same proposal lineage.
The correction emits a new `package_version` under the same `package_id`, or records an independent append-only lifecycle record that names the corrected (`package_id`, `package_version`).
A correction must not allocate a new `package_id` unless the corrected material changes the proposal into a different lineage rather than correcting the existing one; in that case the old lineage must be withdrawn or superseded rather than silently replaced.

Supersession does not preserve `package_id` when the new package is the producer's preferred replacement proposal lineage.
A superseding package uses a distinct `package_id` and records the relationship to the superseded (`package_id`, `package_version`) in `supersession_lineage`.
If the producer only corrects errors while preserving the same proposal lineage, the change is a correction, not supersession.

The immutable identity rule is: an emitted (`package_id`, `package_version`) may be referenced forever, may acquire append-only lifecycle records, and may be made non-current, corrected, withdrawn, or superseded, but it must never be rewritten, reused for different content, or erased from historical lineage.

## Version semantics

`package_version` identifies an immutable emission within a `package_id` lineage.
Version syntax is documentation-level and schema-free: versions must use `v` followed by a non-negative integer sequence separated by dots, such as `v1`, `v1.1`, or `v2.0`.
Numeric ordering is semantic, not lexical: `v1.10` follows `v1.9`.
A package lineage must not reuse a version value once emitted.

Version increments are producer-owned and must be monotonic within a `package_id` lineage:

- the first emitted package version for a lineage is `v1`;
- a correction that preserves the same proposal lineage increments the version under the same `package_id`;
- a correction increment must identify the corrected prior version and explain the correction in `correction_reason`;
- a withdrawal does not modify the withdrawn package version and does not require a new package version; withdrawal is represented by an append-only lifecycle record unless the producer also emits a new explanatory package version;
- supersession starts a distinct `package_id` lineage and therefore starts its own version sequence at `v1`; and
- no version increment may be used to change a historical package without preserving the prior version as an addressable historical package.

Major/minor meaning is intentionally not assigned in this documentation contract because no schema or release-management automation is introduced here.
The only required interpretation is deterministic ordering and immutable historical addressability.

The relationship between version and immutable identity is strict: (`package_id`, `package_version`) names a single emitted package version; later correction, withdrawal, or supersession records may alter current producer preference but never alter the contents, provenance, or historical meaning of that version.

## Lifecycle model

The lifecycle model uses a single `package_status` enum plus lineage and reason fields.
This contract chooses a single enum because each emitted package version must have exactly one current producer-side lifecycle classification for deterministic replay, while `supersession_lineage`, `correction_reason`, and `withdrawal_reason` carry the orthogonal explanatory details without creating conflicting state combinations.
Multiple orthogonal status booleans are prohibited because they could allow ambiguous combinations such as simultaneously `current` and `withdrawn`.

Allowed `package_status` values are:

- `current`: the producer currently stands behind this package version as an active proposal version for its lineage;
- `corrected`: this package version has been corrected by a later package version or by an append-only correction lifecycle record;
- `withdrawn`: the producer no longer stands behind this package version;
- `superseded`: a distinct package lineage has replaced this package version for current producer-side proposal purposes; and
- `superseding`: this package version replaces one or more earlier package versions from distinct package lineages for current producer-side proposal purposes.

Allowed transitions for an emitted package version are append-only transitions from `current` to one of `corrected`, `withdrawn`, or `superseded`.
A newly emitted correction version normally starts as `current` unless it also supersedes another package lineage, in which case it starts as `superseding`.
A newly emitted superseding package starts as `superseding`.
A `superseding` package may later transition to `corrected`, `withdrawn`, or `superseded` by append-only lifecycle record if later history requires it.

Terminal states are `withdrawn` and `superseded`: once a package version enters either state, it must not return to `current` or `superseding`.
`corrected` is terminal for the corrected historical version: the corrected version remains addressable, but the producer's active proposal for that same lineage moves to the later correction version or to the correction lifecycle record.

Prohibited transitions are:

- from `withdrawn` to any other status;
- from `superseded` to any other status;
- from `corrected` back to `current` or `superseding`;
- from `current` directly to another `current` without a new version or lifecycle record;
- from `superseding` to `current` merely to remove supersession context; and
- any transition that changes package purpose, candidate claim, evidence references, or provenance without preserving the prior (`package_id`, `package_version`).

`supersession_lineage` records superseded and superseding package identifiers and versions.
`correction_reason` records why a correction exists or states that no correction applies.
`withdrawal_reason` records why withdrawal exists or states that no withdrawal applies.
These fields explain lifecycle state; they do not create independent authority, registry entries, synchronization behavior, or consumer decisions.

## Historical lineage and immutability

History is append-only.
Historical package versions must never disappear from the documentation lineage, even when corrected, withdrawn, or superseded.

Correction lineage records a directed relationship from the correcting package version or correction lifecycle record to each corrected (`package_id`, `package_version`).
The corrected version remains preserved for audit and replay, and the correction states the affected fields, artifacts, provenance, or limitations without rewriting the corrected version.

Withdrawal lineage records a directed relationship from the withdrawal lifecycle record to each withdrawn (`package_id`, `package_version`).
Withdrawal preserves the historical fact that the proposal existed, the evidence it referenced, and any downstream decisions already made outside this repository.
Withdrawal never erases history and never deletes evidence.

Supersession lineage records a directed relationship from each superseding (`package_id`, `package_version`) to each superseded (`package_id`, `package_version`).
Supersession changes the producer's preferred current lineage only; it does not invalidate the superseded package as a historical object, modify its evidence, or imply consumer acceptance of the superseding package.

Package versions are immutable.
Corrections never rewrite history.
Withdrawals never erase history.
Supersession changes preferred lineage only.
Historical evidence remains preserved through repository-relative artifact references, source commit SHAs, artifact hashes, and release or publication manifests when applicable.

## Lifecycle records architecture

Corrections, withdrawals, and supersessions are independent lifecycle records, not package instances.
This contract chooses independent lifecycle records for lifecycle notices because a notice changes producer standing or lineage metadata, not the empirical package content itself.
Representing a lifecycle notice as a package instance is prohibited because it would blur Package ≠ Decision, risk treating lifecycle notices as new proposals, and create ambiguity about whether withdrawal or supersession has its own evidence package.

A lifecycle record must identify the affected (`package_id`, `package_version`), lifecycle action, reason, authoring context, source commit SHA, and any affected artifact references when relevant.
It must not duplicate or replace the affected package, must not create a registry entry, and must not become a consumer decision.
When a lifecycle action also accompanies changed proposal content, the changed proposal content is emitted separately as a new immutable package version or distinct superseding package lineage, and the independent lifecycle record links the old and new immutable identities.

## Correction policy

A package version is immutable after emission.
A historical emitted package must not be edited, even when repository mechanics technically allow it.

Correction must occur through either:

1. a new package version that preserves `package_id`, increments `package_version`, references the corrected version, and states the correction; or
2. an append-only correction lifecycle record that references the corrected (`package_id`, `package_version`) and states the correction.

A correction notice must identify the corrected package version, state the correction, identify affected artifact references or provenance, and indicate whether the corrected package version remains current, corrected, superseded, or withdrawn.
A correction must not silently rewrite the historical meaning of the original package.

## Withdrawal policy

Withdrawal means the producer no longer stands behind a prior proposal.
A withdrawal notice must identify the withdrawn (`package_id`, `package_version`), state the withdrawal rationale in `withdrawal_reason`, identify affected artifacts when relevant, and preserve the historical fact that the package existed.

Withdrawal does not delete package history, erase evidence, delete downstream decisions, or require a consumer to take any action.
The consumer owns any response to the withdrawal under its own authority.

## Supersession policy

Supersession means a distinct later package lineage replaces an earlier package lineage for current producer-side proposal purposes.
A supersession notice must identify both the superseded and superseding (`package_id`, `package_version`) pairs in `supersession_lineage`, state the reason for supersession, and identify material changes in artifact references, scope, limitations, uncertainty, outcome evidence, target surface, claim boundary, or provenance.

Supersession does not invalidate the historical existence of the superseded package, does not preserve `package_id`, and does not rewrite the superseded package version.
It also does not imply downstream acceptance of the superseding package.

## Documentation audit and schema-readiness assessment

This documentation revision determines immutable identity, version semantics, lifecycle semantics, and lineage semantics without introducing schemas, validators, package instances, registries, workflows, automation, adapters, synchronization, candidate invariants, formal objects, or B2 conclusion changes.
The remaining schema-readiness ambiguities are mechanical rather than architectural:

- exact field names for future lifecycle records beyond the already required `supersession_lineage`, `correction_reason`, and `withdrawal_reason`;
- exact timestamp format for lifecycle records;
- exact hash canonicalization rules for future machine validation; and
- exact storage location for future package-version documents and independent lifecycle records, if a later effort chooses to create them.

Readiness determination: `SCHEMA_READY_WITH_REVISIONS`.
The contract is architecturally complete for identity, versioning, lifecycle, lineage, and immutability, but future schema work must still make mechanical representation choices without reinterpreting the architecture.

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
