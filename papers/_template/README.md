# Repository-First Paper Template

Use this directory as the starting point for every new research manuscript.

## Canonical-source rule

The repository is the canonical source of the manuscript. Do not originate the manuscript in Overleaf or treat Overleaf as an authoritative source. If a collaboration copy is ever exported elsewhere, changes must return to this repository as reviewed commits before they become canonical.

## Required structure

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

## Creating a paper

1. Copy this directory to `papers/<paper-id>/`.
2. Replace template placeholders in `README.md`, `main.tex`, `references.bib`, and `sections/*.tex`.
3. Keep manuscript sections as repository files so diffs, validation, and builds operate on the same object.
4. Run `python3 scripts/build_papers.py` to build the manuscript.
5. Run `python3 scripts/validate.py` before opening a PR.

## Build behavior

The `_template` directory is intentionally excluded from publication builds. A copied paper directory is discovered automatically by `scripts/build_papers.py` once it lives outside `_template` and contains `main.tex`.
