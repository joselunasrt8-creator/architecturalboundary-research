# Papers

Publication manuscripts and paper-specific source files. Manuscripts should reference investigation evidence rather than duplicate execution records.

## Repository-first authorship

New research papers must originate in this repository. Overleaf, local editor exports, shared drives, or other external writing environments may be used only as non-canonical review or collaboration surfaces; they must never become the source of truth for manuscript text, bibliography state, or publication build inputs.

The canonical manuscript object is the reviewed repository tree under `papers/<paper-id>/`. A manuscript change is publication-ready only when the repository source builds with `python3 scripts/build_papers.py` and passes repository validation.

## Standard paper structure

Create new papers by copying `papers/_template/` to `papers/<paper-id>/` and editing the copied files in the repository:

```text
papers/<paper-id>/
├── README.md
├── main.tex
├── references.bib
└── sections/
    ├── abstract.tex
    ├── introduction.tex
    ├── methodology.tex
    ├── evidence.tex
    ├── analysis.tex
    └── conclusion.tex
```

Every new paper must include `main.tex`, section files under `sections/`, `references.bib`, and `README.md`. The build system discovers new papers automatically from `papers/**/main.tex`; no registry update is required for discovery.

Existing migrated manuscripts may retain their current layout for backward compatibility, but new manuscripts should use the template structure.
