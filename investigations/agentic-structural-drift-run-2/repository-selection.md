# Run 2 repository selection

Selection occurred before any experimental candidate was generated.

## Inspected candidates

Only `architecturalboundary-research` was present as a Git repository under the
environment's `/workspace` root. It was selected at commit
`b950b618360ccdd1409b5365fc02cea4437482ee`. It has a deterministic, executable
repository validator; an established `scripts/`, `tools/`, and `tests/`
separation; Python source that can be measured with the standard-library AST;
and no production or safety-critical deployment surface.

Plausible alternatives were the named ContinuityOS, StateGate, and SYNAPSE
repositories. None was present for inspection, so none could provide a pinned,
reproducible baseline. Creating or fetching one would add an uncontrolled
dependency and would conflict with the prohibition on modifying those systems
to obtain a desired result. The investigation templates in this repository are
not separate repositories and have no independent validation contract.

## Why this substrate is preferable for Run 2

Run 1 stopped at T1 when full ordinary validation rejected its candidate. This
selection does not weaken that boundary: `python3 scripts/validate.py` remains
the repository's documented full validation command. Instead, four ordinary,
incremental enhancements to one non-authoritative inspection utility can be
specified in advance. Each has useful behavior, multiple possible
implementations, focused tests, and measurable dependency consequences. That
makes a multi-transition trajectory reasonably possible without guaranteeing
one. The utility remains research instrumentation: its output cannot authorize
mutation, merging, execution, or governance decisions.

The principal selection limitation is external validity: the repository is
mostly research artifacts and deterministic Python tooling, not a large
production application. A successful sequence therefore cannot establish that
the same behavior occurs in other repositories or agents.
