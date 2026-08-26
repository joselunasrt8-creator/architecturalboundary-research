# Validation Record

This record distinguishes preflight commands from package validation. Target
commands were limited to identity checks; target tests and validators were not
run.

## Preflight commands and observed outcomes

| Command | Context | Outcome |
| --- | --- | --- |
| `git status --short --branch` | execution host | Clean `main` at preflight start |
| `git rev-parse HEAD` | execution host | `d10c0329f5fa871d131d4879ae6684865bf2f2fc` |
| `git ls-tree HEAD docs/reference-execution/v1.0/freeze-readiness-record.md` | execution host | Blob `92bcefb29d907b958a2ff2f54f796faf8701c713` |
| `git ls-tree -r HEAD` plus instrument-term search | execution host | No frozen local Architectural Investigation Instrument located |
| `git ls-remote ... HEAD refs/heads/main` | target remote | Both resolved to `7cc919bebe799b5c9086d4ef58968947c761d00a` |
| `git checkout --detach 7cc919b...` | temporary target clone | Detached checkout succeeded |
| `git rev-parse HEAD` | temporary target clone | `7cc919bebe799b5c9086d4ef58968947c761d00a` |
| `git rev-parse HEAD^{tree}` | temporary target clone | `fb1682fd84f677e1b51fd6e6f8987bba1e2b7753` |
| `git status --short --branch` | temporary target clone | Clean detached checkout |
| `git ls-files` and count | temporary target clone | 105 tracked paths inventoried; no semantic claim made |

## Package validation outcomes

| Command / check | Outcome |
| --- | --- |
| Required-artifact shell existence check against all 15 manifest paths | `PASS` |
| `python3 -m json.tool investigations/structural-analysis-foundations-audit-1/execution-package-manifest.json` | `PASS` |
| Repository-local Markdown-link validation through `scripts/validate.py` | `PASS` |
| Explicit `CL-001` through `CL-003`, `MJ-001` through `MJ-003`, and `PIO-001` definition checks | `PASS` |
| Unresolved drafting-sentinel scan across the package | `PASS` — none found |
| `python3 scripts/validate.py` | `PASS`; repository topology, registries, canonical artifact freshness, and local links passed; publication validation reported unavailable because `pdflatex` and `bibtex` are absent |
| `python3 -m pytest -q` | `NOT_RUN` with system Python because `pytest` was not installed |
| `/tmp/abr-issue84-venv/bin/python -m pip install -r requirements.txt` | `PASS`; exact pinned dependencies installed in a temporary validation environment |
| `/tmp/abr-issue84-venv/bin/python scripts/validate.py` | `PASS` with the same disclosed TeX-toolchain limitation |
| First sandboxed `/tmp/abr-issue84-venv/bin/python -m pytest -q` | Environment-limited: `210 passed`, `1 failed`, `50 errors`; all non-passing cases arose when tiktoken could not resolve `openaipublic.blob.core.windows.net` to load the pinned `o200k_base` data |
| Approved-network rerun of `/tmp/abr-issue84-venv/bin/python -m pytest -q` | `PASS` — `261 passed in 138.49s` |
| Target `git rev-parse HEAD`, `git rev-parse HEAD^{tree}`, and `git status --short --branch` after package assembly | `PASS`; pinned commit and tree unchanged; detached inspection copy clean |
| `git diff --check` | `PASS` |
| Worktree path review | `PASS`; changes are confined to this package and its investigations index entry |

## Validation boundary

The missing TeX tools affect the host repository's publication-build check, not
the blocked audit-package paths. The full Python test suite passed after its
pinned tokenizer data became reachable. None of these validations executed or
validated the target repository; they validate the execution host and package
only.
