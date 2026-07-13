# B2 Publication-Readiness Audit Contract

This document is stable explanatory documentation. It is not a generated readiness result and must not be treated as canonical release evidence.

## Canonical artifact

The canonical B2 publication-readiness determination is generated in CI at:

```text
reports/b2-publication-readiness.md
```

The CI workflow uploads that generated report as the workflow artifact named:

```text
b2-publication-readiness-audit
```

## Required canonical identity fields

Canonical audit evidence must include all of the following fields from the CI execution that generated the report:

- repository
- branch
- exact commit SHA
- workflow run ID
- workflow run URL
- timestamp
- final determination

Local executions may be useful for source-state diagnosis, but local reports are non-canonical and may use `LOCAL_UNVERIFIED` identity markers. Those markers must not appear in committed canonical documentation or in a CI-generated canonical audit artifact.

## READY boundary

The final CI audit may emit `READY` only after publication rendering has succeeded and the exact expected PDF set has been verified as present and non-empty. If source checks pass but rendered PDFs are absent or invalid, the audit reports source readiness without claiming final rendered-publication readiness.
