# Readiness and Immutable-Binding Contract

## `IMPLEMENTATION_READY` review

An independent readiness review may determine `IMPLEMENTATION_READY` only when:

```text
all required normative surfaces complete
and every candidate.1 gap mapped to resolved evidence
and #77 execution-record mapping complete
and #78 semantics complete
and calibration fixture structurally valid
and two qualified independent reviews agree
    or a qualified adjudication preserves and resolves disagreement
and no material contradiction remains unresolved
and structural validators/tests pass
```

The determination is a preserved human review conclusion. A validator may check
the listed records but cannot emit scientific readiness on its own.

## Freeze predicate

Instrument v1 is frozen only when `IMPLEMENTATION_READY` is already supported
and a freeze record binds:

- exact name and version;
- full containing Git commit;
- canonical path set and Git blob for every path at that commit;
- deterministic manifest SHA-256 and Git blob;
- aggregate content digest reproduced from the containing commit;
- normative dependency identities;
- compatibility and supersession lineage; and
- exactly one freeze determination.

The containing commit must contain the exact package bytes. A working-tree hash,
base commit, branch, tag name, issue state, or future-commit promise cannot
substitute.

## Drift and amendment

Any path, digest, dependency, semantic, fixture, or review drift after freeze
requires a new version or explicit correction record. The old version and every
execution bound to it remain immutable historical evidence.

## Execution eligibility

Freeze makes an instrument identity bindable; it does not authorize its use. A
fresh audit separately requires an authorized Audit Request, target commit,
operator/custodian, permitted commands/mutations, environment, coverage,
stopping rule, and any external evidence. Failure of any binding yields
`BLOCKED` / `NOT_REACHED` before substantive inspection.

## Candidate.2 state

Candidate.2 has deterministic working-tree content but no second independent
calibration review, so it cannot reach `IMPLEMENTATION_READY`. It also has no
containing commit, so it cannot freeze in the current worktree.
