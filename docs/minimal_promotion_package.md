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
2. reference the canonical empirical artifacts that support the proposal;
3. preserve immutable provenance for those references;
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

## Package eligibility rules

A Minimal Promotion Package is eligible to be created only when all of the following are true:

1. The producer repository has completed the canonical artifacts necessary for the package purpose.
2. Every referenced artifact is already repository-contained, canonical for its lifecycle stage, and stable enough to be referenced immutably.
3. The package can be expressed by references to existing artifacts rather than by copying BOR, SRF, DER, MSR, dataset, analysis, retained-classification, or cohort-conclusion content.
4. The proposal can be bounded to a specific investigation, cohort, artifact set, and package purpose.
5. The proposal can identify known limitations and uncertainty without converting them into downstream obligations.
6. The proposal can be replayed by resolving its artifact references and provenance metadata.
7. The package does not create candidate invariants, formal objects, theorems, registry entries, validators, workflows, or consumer-side decisions.

A package is not eligible merely because a manuscript is publication-ready, a retained classification exists, or an empirical pattern appears interesting.
Publication readiness may indicate that artifacts are organized for external reading, but it is not sufficient for formalization eligibility.

## Package-purpose taxonomy

A Minimal Promotion Package must declare exactly one package purpose.
The purpose constrains what the package may propose and what canonical artifacts it must reference.

| Purpose | Meaning | Required canonical artifact classes |
| --- | --- | --- |
| `formalization-consideration` | Proposes that the consumer inspect a bounded empirical result for possible downstream formalization. | BOR, SRF, DER, MSR, Comparative Dataset, Analysis, Retained Classification, and Cohort Conclusion when available for the claim scope. |
| `evidence-review` | Proposes that the consumer inspect whether the empirical trace is coherent enough to support later formalization consideration. | BOR, SRF, DER, MSR, Comparative Dataset, and Analysis for the reviewed scope. |
| `limitation-review` | Proposes that the consumer inspect a limitation, uncertainty, negative result, or non-retention outcome before any future formalization consideration. | The artifact classes that establish the limitation or uncertainty, including Analysis and Retained Classification when they exist. |
| `correction-notice` | Proposes that the consumer account for a producer-side correction to an earlier package or referenced artifact set. | The corrected package reference, correction record, and affected canonical artifacts. |
| `withdrawal-notice` | Declares that the producer no longer stands behind an earlier proposal while preserving its historical record. | The withdrawn package reference, withdrawal rationale, and affected canonical artifacts. |
| `supersession-notice` | Declares that a later package supersedes an earlier package without deleting the earlier package. | The superseded package reference, superseding package reference, and changed canonical artifact references. |

The taxonomy is intentionally limited to producer proposals and notices.
No purpose authorizes formalization or creates consumer-side acceptance semantics.

## Minimum required contents

A conforming Minimal Promotion Package must contain, at minimum:

1. **Package identity**: a stable package identifier, package purpose, producer repository identifier, creation date, and package version or revision identifier.
2. **Proposal summary**: a bounded statement of what the producer proposes for consumer inspection.
3. **Scope boundary**: the investigation, cohort, systems, lifecycle stages, and claim boundary covered by the proposal.
4. **Canonical artifact references**: repository-relative references to the existing canonical artifacts required by the package purpose.
5. **Provenance record**: immutable provenance for every referenced artifact, as defined in this contract.
6. **Replay instructions**: enough information for a reader to resolve the referenced artifacts and reproduce the evidence chain without relying on duplicated package content.
7. **Limitations**: explicit known limitations, exclusions, unresolved evidence gaps, and non-covered claims.
8. **Uncertainty statement**: explicit handling of missing, contested, low-confidence, or interpretation-sensitive evidence.
9. **Ownership statement**: producer-side ownership of the proposal and consumer-side ownership of any downstream decision.
10. **Correction, withdrawal, and supersession state**: whether the package is current, corrected, withdrawn, superseded, or superseding another package.
11. **Non-authority statement**: a declaration that the package is not a promotion decision, candidate invariant, formal object, theorem, or downstream authorization.

The package may include short human-readable descriptions of referenced artifacts, but those descriptions are navigational only.
The canonical source of empirical content remains the referenced artifact, not the package description.

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
2. the repository-relative path of each referenced artifact;
3. the artifact identifier when the artifact has one;
4. the lifecycle stage of each artifact;
5. the package creation date;
6. the package authoring or generation method, if any;
7. the commit, release, manifest, digest, or other immutable locator used to resolve each artifact; and
8. the package revision relationship to prior packages, corrections, withdrawals, or supersessions.

If an immutable locator is unavailable for a referenced artifact, the package must state that limitation explicitly and must not represent the reference as frozen.
Mutable branch names, local paths outside the repository, and external review surfaces are not sufficient provenance by themselves.

## Replay expectations

A reader must be able to replay the proposal by resolving the package's canonical artifact references, verifying the provenance locators, and following the repository's existing artifact lineage.
Replay means reconstructing the evidence chain used by the proposal; it does not mean recomputing downstream formalization results.

A package should support replay of:

1. the investigation and protocol context;
2. the BOR to SRF to DER to MSR evidence lineage when those artifacts are in scope;
3. the MSR to comparative-dataset projection when the dataset is in scope;
4. the dataset to analysis relation when analysis is in scope;
5. the analysis to retained-classification relation when retained classification is in scope; and
6. the retained-classification to cohort-conclusion relation when a cohort conclusion is in scope.

Replay expectations are referential.
They must not introduce new validators, workflows, automation, adapters, or synchronization requirements as part of this contract.

## Limitation requirements

Every package must contain a limitations section.
The section must identify known boundaries of the proposal, including:

- evidence gaps or unavailable observations;
- scope exclusions;
- non-generalized findings;
- unsupported interpretations;
- artifact stages that are absent, incomplete, corrected, or superseded;
- assumptions required to read the proposal; and
- claims that the package explicitly does not make.

A limitation must not be hidden by promotion language.
If a limitation affects formalization relevance, the package must state that the consumer owns any decision about whether the limitation is acceptable.

## Uncertainty handling

A package must preserve uncertainty rather than resolving it by assertion.
Uncertainty may include missing evidence, competing interpretations, measurement incompleteness, cohort-size constraints, domain specificity, negative results, or retained classifications that do not rise to formalization relevance.

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

## Correction policy

Corrections preserve history.
When a package contains an error that does not require withdrawing the proposal, the producer may issue a correction notice.
A correction notice must identify the corrected package, state the correction, identify affected artifact references or provenance, and indicate whether the corrected package remains current.

A correction must not silently rewrite the historical meaning of the original package.
If repository mechanics permit file edits, the corrected state must still preserve enough provenance to determine that a correction occurred.

## Withdrawal policy

Withdrawal means the producer no longer stands behind a prior proposal.
A withdrawal notice must identify the withdrawn package, state the withdrawal rationale, identify affected artifacts when relevant, and preserve the historical fact that the package existed.

Withdrawal does not delete downstream decisions and does not require a consumer to take any action.
The consumer owns any response to the withdrawal under its own authority.

## Supersession policy

Supersession means a later package replaces an earlier package for current producer-side proposal purposes.
A supersession notice must identify both the superseded and superseding packages, state the reason for supersession, and identify material changes in artifact references, scope, limitations, uncertainty, or provenance.

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
- a workflow trigger; or
- evidence that publication readiness equals formalization eligibility.

The package may help a consumer decide what to inspect, but the consumer's decision is separate, downstream, and outside the authority of this repository.
