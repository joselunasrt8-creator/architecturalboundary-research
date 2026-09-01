# Issue 114 — acceptance-harness audit

This directory audits the Issue #109 harness from the exact checkout bound in
`evidence/source-bindings.json`. Both merged evidence packages are present. The
audit neither executes Run 3 nor changes the immutable Run 1/Run 2 evidence.

The controlling determination is:

**HARNESS_VALID_WITH_PROSPECTIVE_REVISIONS**

The acceptance architecture (prospective objectives, independently required
focused and full gates, candidate/state lineage, frozen structural measures,
and a minimum cumulative trajectory) is methodologically usable. Run 2 exposed
a semantic-oracle mismatch and both runs expose identity/environment gaps that
must be corrected prospectively. The revised protocol is specified in
`protocol-revisions.md`; the current entry checklist is not an authorization.

Documents:

- `audit.md`: evidence reconstruction and conclusion.
- `gate-analysis.json`: machine-readable semantic and compatibility audit.
- `failure-taxonomy.json`: deterministic failure classification.
- `protocol-revisions.md`: prospective-only protocol.
- `run-3-entry-conditions.md`: objective entry checks.
- `evidence/source-bindings.json`: paths, hashes, Git identities, and conflicts.

Harness validity is not hypothesis support. Audit completion is not Run 3
authorization, and no candidate patch is accepted product code.
