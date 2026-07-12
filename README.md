# Architectural Boundary Research

Empirical research investigating whether architectural boundaries recur across independently designed software systems.

This repository is organized around the execution lifecycle of the **Invariance-Based Architectural Investigation Protocol**. The root README is the entry point; the directory topology mirrors how an investigation is registered, executed, validated, analyzed, and prepared for publication.

## Mission

This repository contains the protocol, preregistered investigations, evidence artifacts, comparative datasets, schemas, analysis materials, and publication outputs needed to determine whether proposed architectural boundaries are:

- Architectural invariants
- Conditional invariants
- Domain-specific patterns
- Implementation artifacts
- Unsupported by evidence

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
```

Current B2 lifecycle state: BOR complete, SRF complete, DER complete, and MSR complete. Comparative Dataset, Analysis, and Retained Classification remain Not Started.

## Repository Organization

| Path | Purpose |
| --- | --- |
| `protocol/` | Versioned definitions of the investigation protocol, protocol figures, schemas, templates, and changelog. |
| `investigations/` | Preregistered executions of the protocol. Each investigation follows the same preregistration → literature → BOR → SRF → DER → MSR → dataset → analysis → artifacts layout. |
| `evidence/` | Cross-investigation evidence stores for observations, measurements, classifications, and traceability material. |
| `datasets/` | Canonical, comparative, and published datasets derived from investigations. |
| `schemas/` | Repository-level JSON schemas for protocol objects and investigation metadata. |
| `analysis/` | Investigation-local analysis lives under each investigation; reusable or cross-investigation analysis should be added through the lifecycle layout before publication. |
| `papers/` | Manuscripts and paper-specific source files, including the migrated B2 manuscript. |
| `registry/` | Machine-readable indexes of investigations, protocol versions, retained classifications, and candidate invariants. |
| `figures/` | Shared figures grouped by protocol, papers, and investigations. |
| `scripts/` | Deterministic helper scripts for validation, build orchestration, publication staging, and registry generation. |
| `validation/` | Validation schemas, reports, and CI-facing validation assets. |
| `releases/` | Publication-oriented release bundles and immutable release notes. |

## Current Content Map

- The B2 LaTeX manuscript was moved from the repository root to `papers/paper-b2/` without rewriting manuscript content.
- `investigations/b1-three-system-pilot/` provides the lifecycle layout for the B1 pilot investigation.
- `investigations/b2-governance-cohort/` provides the lifecycle anchor for the B2 governance cohort.
- `investigations/template/` is the reusable scaffold for future investigations.

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

## Publication Build

Reproducible publication builds are driven by `scripts/build_papers.py`. The script discovers every buildable manuscript at `papers/**/main.tex`, compiles each paper independently with `pdflatex` and `bibtex`, reports fatal errors and publication warnings separately, and emits generated PDFs to `releases/papers/`.

Local publication build:

```bash
python3 scripts/build_papers.py
```

Full repository validation, including publication readiness:

```bash
python3 scripts/validate.py
```

New research manuscripts must originate in this repository by copying `papers/_template/` to `papers/<paper-id>/`; Overleaf and other external editors are non-canonical review surfaces only.

See [Publication Build and Release Artifacts](docs/publication.md) for the repository-first authoring workflow, required TeX Live packages, CI behavior, bibliography/reference warning categories, and release artifact locations.
