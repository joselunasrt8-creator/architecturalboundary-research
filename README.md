# Architectural Boundary Research

Developing reproducible methods for discovering, evaluating, and validating architectural boundaries across independently designed software systems.

This repository is an **empirical research environment**. It contains protocols, preregistrations, execution instruments, evidence artifacts, datasets, analyses, and publication outputs used to test architectural claims rather than assume them.

Its role is deliberately different from a product runtime or authority system:

```text
Candidate architectural claim
        ↓
Prospective investigation
        ↓
Empirical evidence
        ↓
Retained / revised / rejected conclusion
```

ABR does not grant execution authority, determine legitimacy for another system, or make a Continufy component necessary merely because that component belongs to the same research ecosystem.

## Mission

Determine whether proposed architectural boundaries are:

- architectural invariants;
- conditional invariants;
- domain-specific patterns;
- implementation artifacts; or
- unsupported by evidence.

A valid outcome may simplify, weaken, or reject a proposed architecture.

## Research Lifecycle

```text
Protocol
  ↓
Investigation
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
Analysis
  ↓
Retained Classification
  ↓
Canonical Cohort Conclusion
```

Current B2 lifecycle state: BOR, SRF, DER, MSR, Comparative Dataset, Analysis, Retained Classification, Canonical Cohort Conclusion, and publication-readiness audit are complete. The canonical cohort outcome is `indeterminate`; publication readiness does not strengthen that outcome or authorize formalization.

## Reference Execution v1.0 Boundary

This repository applies frozen methodologies to bounded investigations of real systems and preserves reviewable research artifacts. It owns its protocol executions, empirical evidence, datasets, analyses, retained classifications, cohort conclusions, and producer-owned promotion packages.

It does not create canonical theory, mutate an upstream methodology or Structology definition during execution, grant implementation or execution authority, decide execution legitimacy for another repository, or convert evidence into formalization authority.

The producer/consumer boundary is:

```text
Empirical Evidence
  → Producer-Owned Promotion Package
  → Consumer-Owned Admissibility and Promotion Decision
```

Observation, derivation, measurement, analysis, and decision artifacts remain distinct. A Minimal Promotion Package may reference this chain, but it neither duplicates the canonical evidence nor performs a downstream decision.

The artifacts under `investigations/structology-transfer-audit-rehearsal-1/` are a pre-reference instrument-harness rehearsal only. Its validity is `BLOCKED`, its transfer outcome is `NOT_REACHED`, and it is not Pilot Execution #1 or a Reference Execution.

The repository-owned [Reference Execution v1.0 freeze/readiness record](docs/reference-execution/v1.0/freeze-readiness-record.md) assesses clean `main` commit `dc636f2ec0161b3554605489857cf19142818a43` and records `BLOCKED`. Issue #106 later materialized a deterministic [Architectural Investigation Instrument v1 candidate](instrument/architectural-investigation/v1/README.md), but the [superseding instrument freeze record](docs/reference-execution/v1.0/architectural-investigation-instrument-v1-freeze-record.md) records `INSTRUMENT_SPECIFICATION_REVISION_REQUIRED`. The [Issue #107 readiness review](docs/reference-execution/v1.0/architectural-investigation-instrument-v1-readiness-review-issue-107.md) and [Issue #108 readiness adjudication](docs/reference-execution/v1.0/architectural-investigation-instrument-v1-readiness-adjudication-issue-108.md) preserve the unresolved calibration/readiness boundary. The blocked Issue #84 package remains `BLOCKED` / `NOT_REACHED`; no substantive rerun is authorized.

## Continufy Ecosystem Research Role

ABR can test claims about Continufy components, their boundaries, and their relationships, but it does not presuppose a fixed Continufy pipeline.

```text
Proposed ecosystem topology
        ↓
Prospective tests
        ↓
Observed relationships
        ↓
Retain / specialize / remove / reorder
```

This means an investigation may legitimately conclude that:

- two repositories should remain independent;
- one repository is optional to a production path;
- a proposed handoff has no measurable value;
- responsibilities belong in a different component;
- multiple components collapse into a smaller primitive set; or
- the proposed topology is unsupported.

**Research relationship ≠ runtime dependency.**

**Evidence of internal coherence ≠ evidence of external value.**

**Same-owner validation ≠ independent replication.**

ABR therefore serves as a candidate falsification layer for the wider Continufy research program, not as a mechanism for confirming the ecosystem by construction.

## Repository Organization

| Path | Purpose |
| --- | --- |
| `protocol/` | Versioned definitions of the investigation protocol, protocol figures, schemas, templates, and changelog. |
| `investigations/` | Preregistered executions of the protocol. |
| `evidence/` | Cross-investigation evidence stores for observations, measurements, classifications, and traceability material. |
| `datasets/` | Canonical, comparative, and published datasets derived from investigations. |
| `schemas/` | Repository-level JSON schemas for protocol objects and investigation metadata. |
| `analysis/` | Investigation-local and reusable analysis material. |
| `instrument/` | Versioned repository-owned audit-instrument candidates, manifests, compatibility contracts, and readiness boundaries. Presence does not imply freeze or execution authority. |
| `papers/` | Manuscripts and paper-specific source files. |
| `registry/` | Machine-readable indexes of investigations, protocol versions, retained classifications, and candidate invariants. |
| `figures/` | Shared figures grouped by protocol, papers, and investigations. |
| `scripts/` | Deterministic helper scripts for validation, build orchestration, publication staging, and registry generation. |
| `validation/` | Validation schemas, reports, and CI-facing validation assets. |
| `releases/` | Publication-oriented release bundles and immutable release notes. |

## Adding a Future Investigation

1. Copy `investigations/template/` to `investigations/<investigation-id>/`.
2. Complete `preregistration.md` before execution.
3. Record observations in `bor/`, surfaces in `srf/`, derived evidence in `der/`, and measurements in `msr/`.
4. Build investigation-local datasets in `dataset/` and analysis outputs in `analysis/`.
5. Place figures and publication artifacts in `figures/` and `artifacts/`.
6. Register the investigation in `registry/investigations.json`.
7. Run `python3 scripts/validate.py` before publication or release.

## Scientific Principles

- Preregister before execution.
- Separate observation from interpretation.
- Preserve complete traceability.
- Prefer evidence over intuition.
- Promote only recurring patterns to Candidate Architectural Invariants.
- Treat empirical recurrence and formal proof as separate stages of the research program.
- Treat null, negative, simplifying, and topology-reducing results as valid outcomes.
- Do not infer commercial value from repository conformance.

## Evidence Boundary

ABR can establish conclusions only within the scope and evidence of its registered investigations.

A green validation suite, completed investigation, publication-ready manuscript, or internally replicated result does not by itself establish:

- universal architectural truth;
- production necessity;
- execution legitimacy;
- independent external replication;
- customer value;
- willingness to pay; or
- commercial viability.

Those require appropriately designed evidence beyond repository conformance.

## Publication Build

Reproducible publication builds are driven by `scripts/build_papers.py`.

```bash
python3 scripts/build_papers.py
python3 scripts/validate.py
```

New research manuscripts must originate in this repository by copying `papers/_template/` to `papers/<paper-id>/`; external editors are non-canonical review surfaces only.

See [Publication Build and Release Artifacts](docs/publication.md) for the repository-first authoring workflow and release artifact requirements.

## Architectural Boundary Research Overview

The visual material under `assets/images/slides/` is explanatory material. Any diagram depicting a Continufy pipeline is a historical or candidate research model, not evidence that the depicted topology is mandatory, optimal, or production-valid.

### Research Focus

![Research Focus](assets/images/slides/boundaryresearch.jpeg)

### Research Workflow

![Research Workflow](assets/images/slides/howwediscover.jpeg)

### Evidence Before Theory

![Evidence Before Theory](assets/images/slides/evidencebeforetheory.jpeg)

### Why Evidence Comes First

![Why Evidence Comes First](assets/images/slides/whyevidencecomesfirst.jpeg)

### Candidate Continufy Research Topology

![Research Pipeline](assets/images/slides/pipeline.png)
