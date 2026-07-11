# Contributing

Contributions should preserve the research lifecycle topology and avoid mixing protocol definitions, investigation execution records, evidence, analysis, and publication artifacts.

## Contribution Rules

1. Add new investigations by copying `investigations/template/`.
2. Keep protocol changes versioned under `protocol/` and document them in `protocol/changelog.md`.
3. Keep evidence traceable to an investigation and protocol version.
4. Run `python3 scripts/validate.py` before proposing publication-facing changes.
