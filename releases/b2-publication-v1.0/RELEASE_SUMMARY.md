# Program B2 Canonical Publication Release Summary

## Release identity

- Release name: Program B2 canonical publication release candidate
- Intended release tag: `b2-publication-v1.0`
- Release branch prepared in this workspace: `work`
- Canonical investigation: `b2-governance-cohort`
- Canonical manuscript source: `papers/paper-b2/main.tex`
- Publication-state manifest: `releases/publication-state-manifest.json`
- Publication-readiness audit: `docs/publication_readiness_audit.md`

## Current state

This repository state is publication-ready but not yet publication-closed. The final published release still requires successful validation on the final `main` commit, successful CI PDF generation and artifact upload, creation of the permanent annotated tag exactly once on that verified `main` SHA, and GitHub Release publication.

Prepared artifact classes:

- Protocol and protocol-version references recorded in the publication-state manifest.
- B2 preregistration, BOR, SRF, DER, MSR, comparative dataset, analysis, retained classification, and cohort conclusion records recorded in the publication-state manifest.
- Registry references recorded in the publication-state manifest.
- B2 manuscript frozen source files under `papers/paper-b2/`.
- Reproducibility and publication pipeline documentation.
- Publication-readiness audit report with final determination `READY`.

## Scientific-state invariant

Release preparation did not change protocol text, evidence records, measurements, analysis outputs, retained classifications, cohort conclusions, or scientific interpretation.

## Tagging contract

The intended canonical immutable release object is the future annotated git tag `b2-publication-v1.0` created exactly once against the final CI-verified `main` commit. Any local tag with this name before final `main` validation is provisional and must not be pushed or treated as the permanent release tag.

Generated mutable build outputs under `releases/papers/*.pdf` remain excluded from `releases/publication-state-manifest.json` so repeated local or CI builds cannot perturb canonical manifest validation.

## Validation summary

Deterministic repository validation, registry checks, dataset freshness checks, analysis freshness checks, retained-classification freshness checks, cohort-conclusion freshness checks, publication-state manifest freshness checks, whitespace checks, and the Python test suite passed in this workspace.

Local PDF compilation was attempted through `scripts/build_papers.py`, but this container does not include `pdflatex` or `bibtex`. Installing the documented TeX Live dependency set was blocked by the container APT proxy returning HTTP 403 responses. Therefore rendered publication state remains pending until GitHub Actions installs TeX Live, builds the PDFs, verifies non-empty PDF artifacts, and uploads the `publication-pdfs` artifact.
