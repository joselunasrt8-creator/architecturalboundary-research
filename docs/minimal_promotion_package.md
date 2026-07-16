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

The immutable identity rule is: an emitted (`package_id`, `package_version`) may be referenced forever, may acquire append-only lifecycle records, and may derive a non-current, corrected, withdrawn, or superseded effective status, but it must never be rewritten, reused for different content, or erased from historical lineage.

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

The lifecycle model uses a single status enum plus lineage and reason fields.
This contract chooses a single enum because each package-version view must have exactly one producer-side lifecycle classification for deterministic replay, while `supersession_lineage`, `correction_reason`, and `withdrawal_reason` carry the orthogonal explanatory details without creating conflicting state combinations.
Multiple orthogonal status booleans are prohibited because they could allow ambiguous combinations such as simultaneously `current` and `withdrawn`.

The stored package document records `package_status` as `status_at_emission`.
After emission, that stored value must not be mutated.
Later correction, withdrawal, or supersession is represented only by independent append-only lifecycle records.
The current producer-side lifecycle state is `effective_status`, derived by applying the immutable package's `status_at_emission` and all applicable append-only lifecycle records in lineage order.
When this contract refers to lifecycle transitions, it refers to transitions in derived `effective_status`, not edits to the stored historical package document.

Allowed status enum values for both `status_at_emission` and derived `effective_status` are:

- `current`: the producer currently stands behind this package version as an active proposal version for its lineage;
- `corrected`: this package version has been corrected by a later package version or by an append-only correction lifecycle record;
- `withdrawn`: the producer no longer stands behind this package version;
- `superseded`: a distinct package lineage has replaced this package version for current producer-side proposal purposes; and
- `superseding`: this package version replaces one or more earlier package versions from distinct package lineages for current producer-side proposal purposes.

Allowed transitions are append-only derived `effective_status` transitions from `current` to one of `corrected`, `withdrawn`, or `superseded`.
A newly emitted correction version normally records `status_at_emission = current` unless it also supersedes another package lineage, in which case it records `status_at_emission = superseding`.
A newly emitted superseding package records `status_at_emission = superseding`.
A package whose derived `effective_status` is `superseding` may later derive `corrected`, `withdrawn`, or `superseded` status from a later append-only lifecycle record if later history requires it.

Terminal states are `withdrawn` and `superseded`: once a package version derives either effective state, it must not later derive `current` or `superseding`.
`corrected` is terminal for the corrected historical version: the corrected version remains addressable with its original `status_at_emission`, but the producer's active proposal for that same lineage moves to the later correction version or to the correction lifecycle record.

Prohibited effective-status transitions are:

- from `withdrawn` to any other status;
- from `superseded` to any other status;
- from `corrected` back to `current` or `superseding`;
- from `current` directly to another `current` without a new version or lifecycle record;
- from `superseding` to `current` merely to remove supersession context; and
- any transition that changes package purpose, candidate claim, evidence references, or provenance without preserving the prior (`package_id`, `package_version`).

`supersession_lineage` records superseded and superseding package identifiers and versions.
`correction_reason` records why a correction exists or states that no correction applies.
`withdrawal_reason` records why withdrawal exists or states that no withdrawal applies.
These fields explain derived lifecycle state; they do not mutate historical package documents, create independent authority, create registry entries, create synchronization behavior, or create consumer decisions.

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


## Structured artifact reference model

A structured artifact reference is the reusable documentation-level object used whenever a package names a producer artifact as evidence, lineage, publication context, or proposal context.
It defines semantics only and does not define JSON, serialization, validation tooling, registries, or package instances.

The model applies to references to Protocol, Registration, BOR, SRF, DER, MSR, Comparative Dataset, Analysis, Retained Classification, Cohort Conclusion, and Publication Manifest artifacts.
Each artifact reference must have deterministic meaning for the following conceptual fields:

| Conceptual field | Semantics |
| --- | --- |
| artifact class | The bounded class of the referenced artifact, chosen from Protocol, Registration, BOR, SRF, DER, MSR, Comparative Dataset, Analysis, Retained Classification, Cohort Conclusion, or Publication Manifest. The class describes the role of the referenced artifact; it does not create a new schema or registry class. |
| repository-relative path | The path from the producer repository root to the referenced artifact. It must not be an absolute local path, mutable workspace path, or external-only URL. |
| artifact identifier | The artifact's own stable identifier when the artifact defines one. If the artifact has no internal identifier, the package must use the not-applicable convention and rely on repository-relative path, source commit, and artifact hash for determinism. |
| source commit | The producer repository commit SHA at which the referenced artifact content is resolved. Branch names, tags without commit resolution, and working-tree state are not substitutes for this field. |
| lifecycle stage | The artifact's producer-owned stage at the referenced commit, such as registered, canonical, corrected, superseded, withdrawn, release-candidate, or released when those terms are applicable to that artifact class. Lifecycle stage is descriptive provenance and must not imply consumer acceptance. |
| hash algorithm | The named digest algorithm used to compute the artifact hash. The name must be specific enough that a future schema can distinguish algorithms without reinterpretation. |
| artifact hash | The digest of the referenced artifact content at the source commit under the stated hash algorithm. The hash binds the reference to content, not to mutable filesystem state. |
| lineage role | The reason the artifact is included in the package lineage, such as protocol source, registration source, observation input, surface record, derived evidence, measurement summary, dataset projection, analysis result, retained classification, cohort conclusion, publication-state binding, correction context, supersession context, withdrawal context, or limitation evidence. |
| required-for-purpose flag | A deterministic yes/no statement indicating whether the reference is required for the declared `package_purpose`. Required references are part of the minimum evidence chain for the purpose; non-required references provide context, limitation evidence, lineage explanation, or publication-state binding. |

A package may contain multiple references to the same artifact class when the declared purpose requires them, for example per-system BOR, SRF, DER, or MSR artifacts.
Each reference remains independently content-addressed by its source commit, path, algorithm, and hash.
A structured artifact reference does not make upstream provenance a runtime dependency: it preserves replayable provenance while leaving package consumption, formalization, and downstream admissibility under consumer authority.

## Package reference semantics

A package reference is a documentation-level reference to one immutable emitted package version or to a package lineage when historical precision is intentionally not required.
A package reference that cites evidence, correction, withdrawal, supersession, or historical state must identify the immutable pair (`package_id`, `package_version`).
A lineage-only package reference may use `package_id` alone only when the statement concerns the continuing producer-side proposal lineage rather than a specific emitted package version.

A content-addressed reference identifies content by digest.
For package content, the digest binds the referenced emitted package document or lifecycle record to the hash algorithm and computed hash recorded with the reference.
For artifact content, the digest binds the referenced artifact content to the structured artifact reference.
Digest semantics are content semantics: a matching digest means the bytes used for replay match the recorded reference under the stated algorithm; it does not mean the scientific interpretation is correct, the package is accepted, or the consumer must act.

A repository reference identifies the producer repository and source commit used to resolve package and artifact paths.
Repository references provide provenance and replay context; they do not create synchronization, mutable dependency, external registry membership, or downstream runtime dependency.

Immutable package identity remains (`package_id`, `package_version`).
Content-addressed and repository references strengthen replay and provenance for that identity, but they do not replace it.
If identity and digest disagree, the package must be treated as unresolved until the producer records a correction, withdrawal, or supersession; a consumer must not infer a corrected identity from digest data alone.

## Replay status

Replay means reconstructing the proposal's evidence chain from repository-contained references, source commits, artifact hashes, and lineage metadata.
Replay does not mean recomputing downstream formalization results, reproducing consumer decisions, or independently replicating empirical observations outside the repository.

`replay_status` must use one of the following documentation-level finite states:

| State | Semantics |
| --- | --- |
| `replayable` | The package records sufficient repository, commit, path, hash, lifecycle, lineage, and validation-command semantics for a reader to reconstruct the evidence chain for the declared purpose. |
| `replay_not_attempted` | The package has not been replayed by the producer or package author, even though the recorded metadata may be sufficient. The absence of an attempt must not be represented as success. |
| `replay_blocked` | Replay was attempted or assessed and cannot proceed because a required reference, commit, artifact, hash, lineage link, or command precondition is unavailable or inconsistent. The blocking reason must be stated. |
| `partially_replayable` | Some required evidence-chain segments can be replayed and others cannot. The package must identify replayable and non-replayable segments and must not summarize the package as fully replayable. |
| `replay_unavailable` | Replay is unavailable because the package purpose or historical state lacks necessary repository-contained artifacts or immutable provenance. The unavailability reason must be stated. |

Replay status is package-context metadata.
It does not create validators, automation, or synchronization requirements, and it does not authorize consumer formalization.

## Replication status

Replication means an empirical confirmation activity beyond repository replay.
It must be distinguished from replay, because repository replay verifies the recorded evidence chain while replication evaluates whether comparable observations or conclusions can be obtained through another empirical effort.

`replication_status` must use one of the following documentation-level finite states:

| State | Semantics |
| --- | --- |
| `not_replicated` | No independent empirical replication is claimed. Repository replay may still be available. |
| `replication_not_attempted` | Replication has not been attempted, and the package makes no replication claim. |
| `internal_replication_partial` | The producer has performed a bounded repeat or extension within the producer repository or method family, but it is not independent external replication. Scope and limits must be stated. |
| `independently_replicated` | An empirically independent effort has replicated the relevant observation or conclusion under stated scope. The package must reference the evidence without converting it into consumer authority. |
| `replication_failed` | A replication attempt produced negative or non-confirming evidence. The failed scope and relationship to the package claim must be stated as negative evidence or limitation. |
| `replication_blocked` | Replication cannot currently proceed because required access, measurements, artifacts, systems, or method details are unavailable. The blocker must be stated. |
| `replication_unavailable` | Replication is not possible for the declared scope, for example because the observed system state no longer exists. The reason must be stated. |

Terminology is deterministic:

- repository replay is reconstruction of the producer evidence chain from immutable repository references;
- consumer replay is a consumer's own reconstruction of that same producer evidence chain under consumer authority;
- independent empirical replication is a new empirical effort that does not merely resolve producer references; and
- external replication is independent empirical replication performed outside the producer repository or producer-controlled process.

A package must not label repository replay as replication.
A package must not label consumer replay as external replication.
Replication evidence may inform review context, but it does not establish formalization eligibility or downstream acceptance.

## Validation command semantics

`validation_commands` describes commands relevant to checking the package or referenced artifacts.
It is documentation metadata only and does not prescribe tooling, create automation, require CI execution, or define validators.

Each validation command entry must have deterministic semantics for:

| Conceptual field | Semantics |
| --- | --- |
| command | The exact shell command or command sequence as documented for human or CI execution. |
| working directory | The repository-relative directory from which the command is expected to run. |
| expected exit status | The expected numeric process exit status for success, usually zero unless the command intentionally demonstrates failure behavior. |
| scope | The artifact, package field, repository area, publication state, or evidence-chain segment the command is intended to check. |
| canonicality | Whether the command is canonical for repository acceptance or non-canonical supporting context. Non-canonical commands may inform review but must not replace canonical validation. |
| execution context | Whether the command is intended for CI, local execution, or both. CI/local distinction records context only and does not create a workflow requirement. |

A validation command may be unavailable, non-canonical, or local-only if the package states that status deterministically.
Validation-command documentation must not hide replay blockers, missing artifacts, or failed checks.

## Publication-state binding

A package binds publication state by referencing the existing publication-state manifest as a structured artifact reference with artifact class `Publication Manifest`, repository-relative path `releases/publication-state-manifest.json`, a source commit, lifecycle stage, hash algorithm, artifact hash, lineage role `publication-state binding`, and required-for-purpose status determined by the package purpose and available publication artifacts.
If a release summary or publication-readiness audit is also referenced, each is a separate structured artifact reference with its own path, commit, hash, lifecycle stage, and lineage role.

The publication-state binding records the producer's publication-readiness context for the referenced investigation or cohort.
It does not copy publication-state manifest content into the package and does not create a new publication manifest.
If the manifest is not applicable or unavailable for the package scope, the package must use the not-applicable convention and state the deterministic reason.

Publication readiness is not formalization eligibility.
Publication readiness is not scientific support.
A publication-ready artifact set may be useful review context, but `cohort_outcome`, complete outcome evidence, limitations, replay status, replication status, and consumer authority continue to govern package interpretation.

## Evidence summary structure

Evidence summaries must be structured by conceptual category rather than prose-only narrative.
The categories below define documentation semantics only and do not define JSON.
Each category must identify the relevant systems, artifacts, measurements, lineage references, and interpretation limits at the level needed to prevent cherry-picking.

| Category | Semantics |
| --- | --- |
| supporting evidence | Observations, measurements, classifications, or cohort conclusions that support the package's bounded claim or question within the registered scope. Supporting evidence must state its basis systems and must not omit contrary or missing evidence. |
| indeterminate evidence | Evidence that does not support a definitive supporting or negative interpretation because measurements, observations, or classification criteria are incomplete, mixed, or insufficient. Indeterminacy must be preserved rather than resolved by assertion. |
| negative evidence | Observations, measurements, classifications, or conclusions that contradict, violate, or weaken the package's bounded claim or question. Negative evidence must remain visible even when the declared purpose is not counterexample review. |
| missing measurements | Measurements or observations required for stronger interpretation but absent, unavailable, incomplete, or not collected. Missing measurements must identify affected systems or artifact classes when known. |
| known limitations | Scope boundaries, methodological limits, unavailable artifacts, non-generalized findings, lifecycle constraints, and assumptions that limit interpretation or downstream relevance. |
| known counterexamples | Specific systems, artifacts, observations, or external facts that counter the package's claim or possible stronger claims. Counterexamples must be distinguished from general negative evidence when they identify concrete contrary instances. |

Every category must be populated, declared empty, or declared not applicable using the not-applicable convention.
A package must not merge categories in a way that hides complete outcome evidence or changes the cohort outcome interpretation.

## Not-applicable convention

A field or category that is intentionally absent must be represented by the exact documentation-level value `not_applicable` plus a rationale that explains why the field is not applicable to the declared package purpose, artifact class, lifecycle state, or evidence context.
The rationale must be specific enough that another reader can distinguish intentional absence from omission, unavailable data, failed replay, or unknown status.

`not_applicable` must not be used for unknown, missing, blocked, unavailable, unattempted, or failed information when a finite state or limitation category exists for that condition.
For example, replay failure must use `replay_blocked`, not `not_applicable`; absent replication attempts must use a replication status, not `not_applicable`; and an artifact without an internal identifier may use `not_applicable` only for the artifact identifier while still recording path, commit, algorithm, and hash.

This convention preserves deterministic interpretation without defining schemas.
Future schemas may encode the same semantics mechanically, but they must not reinterpret intentional absence as missing data.

## Documentation audit and schema-readiness assessment

This documentation revision determines immutable identity, version semantics, lifecycle semantics, lineage semantics, structured artifact reference semantics, package reference semantics, replay status, replication status, validation-command semantics, publication-state binding, evidence-summary categories, and the not-applicable convention without introducing schemas, validators, package instances, registries, workflows, automation, adapters, synchronization, candidate invariants, formal objects, investigation changes, B2 changes, or candidate-invariant status changes.
The revision remains compatible with the prior identity and lifecycle decisions: immutable package identity remains (`package_id`, `package_version`), lifecycle changes remain append-only producer records, source commits and artifact hashes preserve immutable provenance, and consumer authority remains separate from producer proposals.

Schema-readiness assessment:

- complete-outcome evidence remains required through explicit supporting, indeterminate, negative, missing-measurement, limitation, and counterexample categories;
- no cherry-picking remains required because empty and not-applicable categories must be explicit;
- replayability now has finite documentation states distinct from replication;
- immutable provenance is preserved by structured artifact references, package references, repository references, source commits, and digest semantics;
- producer ownership and consumer authority remain separated; and
- upstream provenance remains replay context rather than runtime dependency.

Remaining ambiguities are mechanical representation choices for a future schema effort, not semantic blockers:

- exact JSON object shapes, property names, and cardinality constraints for artifact references, package references, validation command entries, evidence categories, and not-applicable rationales;
- exact timestamp format for lifecycle records and package creation fields;
- exact digest canonicalization rules for future machine validation of text, JSON, TeX, and generated artifacts;
- exact enumeration spelling strategy if a future schema chooses different wire names while preserving these documented states; and
- exact storage location for future package-version documents and independent lifecycle records, if a later effort chooses to create them.

Readiness determination: `SCHEMA_READY_WITH_REVISIONS`.
The contract is semantically ready for future schema design, but schema work still requires mechanical representation decisions and digest canonicalization rules.
Those future decisions must preserve the documentation semantics defined here and must not reinterpret publication readiness as formalization eligibility or scientific support.

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
