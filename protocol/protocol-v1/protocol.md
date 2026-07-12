# Invariance-Based Architectural Investigation Protocol v1

This directory contains the versioned protocol definition and supporting assets for protocol v1.

## Lifecycle

1. Registration
2. Baseline Observation Records (BOR)
3. Surface Record Files (SRF)
4. Derived Evidence Records (DER)
5. Measurement Summary Records (MSR)
6. Comparative Dataset
7. Analysis
8. Retained Classification
9. Publication artifacts

## SRF to DER Contract

Protocol v1 freezes the SRF to DER boundary before any investigation may treat DER execution as complete. A Derived Evidence Record (DER) is a machine-readable object that derives an evidence claim from one or more already-valid Surface Record Files (SRF). Observation and derivation remain separate: an SRF records observed execution surfaces and their BOR observation references, while a DER records only the bounded derivation made from those declared upstream SRF surfaces or observations.

SRF existence is not DER validity. A DER is valid only when all of the following are true:

1. The DER declares `object_type` as `DerivedEvidenceRecord`, `schema_version` as the DER schema version, a unique `id`, the `protocol_version`, and the `investigation_id`.
2. The DER lists one or more `source_srf_ids` from the same investigation. Protocol v1 permits one SRF to produce zero, one, or multiple DER objects; one DER may reference one or multiple SRFs when every referenced SRF belongs to the same investigation.
3. The DER lists one or more `source_surface_ids` and one or more `source_observation_refs`. Empty upstream reference sets are invalid.
4. Every referenced SRF ID, surface ID, and observation reference resolves to the declared upstream SRF objects; unknown upstream identifiers are invalid.
5. The DER records a `derivation_rule` with a `registered_derivation_reference` that resolves to an existing repository protocol or preregistration source before use. Unregistered derivation rules are invalid.
6. The DER records a `derived_claim` and must not introduce unsupported facts that cannot be traced to its declared SRF surfaces or BOR observation references.
7. The DER records `provenance` for the repository objects used to construct it.
8. DER identifiers must be unique within an investigation.
9. A DER whose `investigation_id` differs from its referenced SRF objects is invalid.

The DER stage may be explicitly not yet executed for an investigation. In that state, placeholder DER directories do not count as completed DER execution, and validation must not fabricate DER records. If DER JSON files are present, they are subject to the schema and lineage contract above.

Current Protocol v1 enforcement status: BOR to SRF is the currently enforced lifecycle boundary. SRF to DER is the next frozen contract. DER execution for the current B2 governance cohort is not yet populated and not yet completed.
