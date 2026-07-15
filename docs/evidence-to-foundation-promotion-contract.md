# Evidence-to-Foundation Promotion Contract

Status: Planning / methodology audit

## Objective

Define the canonical boundary between `architecturalboundary-research` and `structural-analysis-foundations`.

This contract determines how retained empirical findings become candidate formal research objects while preserving provenance, traceability, and scientific review. The boundary originates from the research methodology: the question is not how to formalize a theorem, but when empirical evidence is sufficiently supported to be promoted into a formal research object.

## Repository Boundary

`architecturalboundary-research` owns the empirical side of the boundary. It records protocol executions, evidence artifacts, datasets, retained classifications, cohort conclusions, and promotion nominations that remain grounded in empirical provenance.

`structural-analysis-foundations` owns the downstream formal side of the boundary. It may accept a promoted candidate as a formal research object only after the promotion contract records the empirical basis, provenance, review state, and ownership transfer expectations.

Promotion does not itself create a theorem, proof obligation, SYNAPSE implementation, or mathematical formalization. It creates a reviewed bridge object between empirical evidence and downstream formal research.

## Candidate Runtime

```text
Real Systems
        ↓
BOR
        ↓
SRF
        ↓
DER
        ↓
MSR
        ↓
Comparative Dataset
        ↓
Retained Classification
        ↓
Candidate Structural Invariant
        ↓
Promotion Contract
        ↓
Structural Analysis Foundations
        ↓
Formal Research Object
```

## Eligibility Questions

A promotion review must answer the following questions before any downstream formal ownership is claimed:

- What research artifacts are eligible for promotion?
- What metadata must accompany a promotion?
- What evidence is required before promotion?
- What remains in `architecturalboundary-research`?
- What becomes owned by `structural-analysis-foundations`?
- How are rejected or deferred candidates represented?
- How is provenance preserved across repositories?

## Promotion Object Schema

A promotion object should be repository-independent and include, at minimum:

- `promotion_id`: stable identifier for the promotion nomination.
- `source_repository`: repository that owns the empirical record.
- `target_repository`: repository that may own downstream formalization work.
- `candidate_invariant_id`: retained or candidate invariant being nominated.
- `source_protocol_version`: protocol version used to produce the empirical record.
- `source_investigations`: investigation identifiers contributing evidence.
- `source_artifacts`: BOR, SRF, DER, MSR, dataset, analysis, retained-classification, and cohort-conclusion references required to replay the empirical basis.
- `evidence_threshold`: review rule used to decide whether the candidate is promotable.
- `provenance_manifest`: immutable source pointers, content hashes where available, and release or commit references.
- `review_status`: one of `proposed`, `accepted`, `rejected`, or `deferred`.
- `review_record`: reviewer, date, rationale, and unresolved limitations.
- `ownership_boundary`: explicit statement of what remains empirical and what may be formalized downstream.
- `replay_expectations`: validation commands, release references, and audit steps needed to reproduce the promotion basis.

## Provenance Requirements

Promotion requires source-preserved evidence. A candidate should not be promoted from narrative summary alone.

The promotion record should preserve:

- the protocol version and preregistration that governed the investigation;
- the full artifact chain from BOR through retained classification and, when available, cohort conclusion;
- stable references to comparative datasets and generated analysis outputs;
- source-system version identifiers or release references used during evidence collection;
- validation commands and outputs used to establish repository consistency;
- known limitations, exclusions, deferred evidence, and rejected interpretations.

## Traceability Model

Traceability is unidirectional from empirical evidence to formal candidate. Downstream formal work may cite the promotion object, but it must not rewrite the empirical record.

A compliant promotion path is:

```text
promotion_id
  ├─ candidate_invariant_id
  ├─ protocol_version
  ├─ investigation_id[]
  ├─ artifact_reference[]
  ├─ dataset_reference[]
  ├─ retained_classification_reference
  ├─ cohort_conclusion_reference?
  ├─ review_record
  └─ downstream_formal_object_reference?
```

The empirical repository remains the source of truth for evidence artifacts. The foundations repository may own formal definitions, proof attempts, counterexamples, and theory-local metadata after acceptance.

## Ownership Boundary

### Remains in `architecturalboundary-research`

- Protocol definitions and protocol versions.
- Preregistrations and investigation records.
- BOR, SRF, DER, and MSR artifacts.
- Comparative datasets and analysis outputs.
- Retained classifications and cohort conclusions.
- Promotion nominations, review records, rejection records, and deferred-candidate records.
- Provenance manifests and replay/audit instructions for empirical claims.

### Becomes eligible for `structural-analysis-foundations`

- Accepted candidate formal research objects.
- Formal terminology derived from, but not overwriting, empirical terms.
- Formalization plans, proof obligations, proof attempts, and counterexamples.
- Theory-local acceptance, rejection, or refinement decisions.
- Links back to the immutable empirical promotion object.

## Acceptance, Rejection, and Deferral Workflow

1. A retained classification or cohort conclusion identifies a candidate structural invariant.
2. A promotion nomination records the required schema fields and provenance manifest.
3. Review verifies eligibility, traceability, evidence sufficiency, and replay expectations.
4. The nomination is marked:
   - `accepted` when it may become a downstream formal research object;
   - `rejected` when the evidence or provenance is insufficient;
   - `deferred` when additional empirical work is required before review can conclude.
5. Accepted nominations may be referenced by downstream implementation issues in `structural-analysis-foundations`.
6. Rejected and deferred nominations remain in `architecturalboundary-research` as methodological audit records.

## Replay and Audit Expectations

A promotion must be auditable without relying on downstream formal work. Reviewers should be able to:

- locate every cited source artifact;
- verify that retained classifications follow the registered protocol rules;
- rebuild or validate generated datasets when deterministic scripts are available;
- inspect known limitations and unresolved threats to validity;
- confirm that no theorem development, mathematical formalization, SYNAPSE implementation, or automatic promotion occurred as part of the empirical promotion record.

## Non-goals

- No theorem development.
- No mathematical formalization.
- No SYNAPSE implementation.
- No automatic promotion.
- No changes to existing research protocol.
