# Canonical B2 Minimal Promotion Package v1.0

This release directory makes the producer-owned Canonical B2 Minimal Promotion
Package available to downstream repositories as an immutable, repository-local
artifact.

## Canonical artifact

- File: `b2-governance-cohort-indeterminate-evidence-review-v1.0.json`
- Package identity: `b2-governance-cohort-indeterminate-evidence-review`, `v1.0`
- Producer repository: `architecturalboundary-research`
- Producer evidence commit: `b6a837e916fdf18ebed35896de223cc2429d61e7`
- Canonical producer path: `investigations/b2-governance-cohort/promotion-packages/b2-governance-cohort-indeterminate-evidence-review-v1.0.json`
- Package content digest: `4fb1e08a8a0489d6715ab30e9c52ee96d269d7dd7c1d7b918d38f10800832cca`
- Digest canonicalization: RFC 8785-style deterministic JSON (UTF-8, sorted
  keys, compact separators), with `package_content_digest.digest` represented
  as an empty string to avoid a self-referential digest.

The JSON file is an exact byte-for-byte copy of the canonical package produced
by Issue #49. It is not regenerated, normalized, extended, or reinterpreted.
`SHA256SUMS` records the SHA-256 digest of the distributed file bytes; this
transport checksum is distinct from the package's embedded canonical-content
digest.

Downstream consumers may copy this JSON file into a repository-local immutable
snapshot and cite its package identity, version, provenance, and digest. The
copy must not be treated as a consumer admissibility review, promotion
decision, or formalization authorization. No consumer-owned fields are included
in the producer package.
