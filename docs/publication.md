# Publication Build and Release Artifacts

This repository uses a deterministic, repository-first publication pipeline for buildable LaTeX papers under `papers/`.

The repository is the canonical source for all future research manuscripts. Overleaf must not be used to originate new manuscripts or to re-establish a canonical source outside version control. External editors may only hold non-canonical review copies; authoritative manuscript changes must return as repository commits before publication.

## Paper discovery

A paper is buildable when it contains a `main.tex` file somewhere under `papers/`, excluding hidden or template paths whose path components begin with `.` or `_`. The build entry point discovers `papers/**/main.tex` in sorted path order, builds each discovered paper independently, and does not hard-code paper names. Future papers are included automatically once their manuscript directory contains `main.tex`.

Paper directories that only contain planning or placeholder material, such as a README without `main.tex`, are not compiled and are not treated as build failures. The repository template at `papers/_template/` is intentionally excluded from builds until copied to a real paper directory.


## Repository-first authoring workflow

New research manuscripts must be created in this repository:

1. Copy `papers/_template/` to `papers/<paper-id>/`.
2. Edit `README.md`, `main.tex`, `references.bib`, and `sections/*.tex` in the copied repository directory.
3. Keep section-level manuscript text in repository files so review diffs, validation, and publication builds operate on the same object.
4. Run `python3 scripts/build_papers.py` to build the paper deterministically.
5. Run `python3 scripts/validate.py` before opening a PR.

Every new paper must include:

- `main.tex`
- section files under `sections/`
- `references.bib`
- `README.md`

Overleaf must never become the canonical source again. If authors use Overleaf or another external editor for comments or review, the external copy is disposable and non-authoritative; only committed repository files define the manuscript.

## Required TeX tools and packages

Local and CI builds require these executable tools:

- `pdflatex`
- `bibtex`

The GitHub Actions workflow installs the following Ubuntu TeX Live packages as the minimal repository CI set for the current manuscripts:

- `latexmk`
- `texlive-bibtex-extra`
- `texlive-fonts-recommended`
- `texlive-latex-base`
- `texlive-latex-extra`
- `texlive-latex-recommended`

The manuscripts currently use common LaTeX packages including `amsmath`, `amssymb`, `array`, `booktabs`, `enumitem`, `fontenc`, `geometry`, `graphicx`, `hyperref`, `inputenc`, `lmodern`, `longtable`, and `microtype`.

## Local build commands

Build every discovered paper and emit PDFs into `releases/papers/`:

```bash
python3 scripts/build_papers.py
```

Run full repository validation, including the publication build:

```bash
python3 scripts/validate.py
```

The build script exits non-zero if any paper fails to compile or if required TeX tools are unavailable. It prints one result block per paper and a final summary with pass, fail, warning, and discovery counts.

## Bibliographies, references, and warnings

Each paper is built independently with this sequence:

1. `pdflatex -halt-on-error -interaction=nonstopmode`
2. `bibtex` when the paper directory contains one or more `.bib` files
3. two additional `pdflatex` passes to resolve bibliography and cross-reference state

Compilation failures are fatal. Publication warnings are surfaced separately from fatal errors, including:

- missing bibliography references reported by BibTeX
- duplicate labels
- undefined citations
- undefined references
- rerun-needed cross-reference state

## CI workflow

The executable workflow is `.github/workflows/validate.yml`. On every push and pull request targeting `main`, CI:

1. checks out the repository
2. installs Python dependencies
3. installs TeX Live publication dependencies
4. runs repository validation, including LaTeX publication readiness
5. runs registry, dataset, and report entry-point checks
6. builds publication PDFs
7. uploads `releases/papers/*.pdf` as the `publication-pdfs` workflow artifact
8. checks whitespace with `git diff --check`

## Release artifact locations

Generated paper PDFs are emitted to:

```text
releases/papers/
```

The generated PDFs are build artifacts and should be regenerated from source for each release or CI run.
