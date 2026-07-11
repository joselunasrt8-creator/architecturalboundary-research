# B2 Publication-Readiness Audit

A B2 publication-readiness audit is valid only when it is bound to an exact
repository commit. An unverified local checkout is not an auditable object and
must produce `NULL_NOT_AUDITED` rather than a scientific readiness determination.

The manual GitHub Actions workflow `.github/workflows/b2-publication-readiness.yml`
checks out `main` with full history, records the repository, branch, commit SHA,
workflow run ID, and timestamp, verifies canonical paths, runs repository
validators, runs the B2 audit script, and uploads the resulting report artifact.

The first version does not commit changes, open pull requests, populate evidence,
modify Protocol v1.0, reinterpret conclusions, or begin B3.

## Audit Contract

The audit script classifies each required artifact as `COMPLETE`, `PARTIAL`, or
`MISSING`. For each artifact it distinguishes whether the path exists, placeholder
text exists, a research object exists, the object is populated, the object is
frozen, and the object is traceable.

If canonical preconditions fail, the workflow emits `NULL_NOT_AUDITED`, fails,
and does not create a scientific readiness determination. If preconditions pass,
the report records exact blockers, an ordered closure sequence, commands executed,
and one final determination: `READY`, `BLOCKED`, or `NULL_NOT_AUDITED`.
