# Manual-Judgment Register

## `MJ-001` — Does issue closure supply the frozen instrument?

- **Question:** May closed issues #59, #77, and #78 be treated as the canonical
  frozen repository-local instrument?
- **Available evidence:** the issues are closed; the pinned host tree contains
  no versioned local instrument; the repository-owned readiness record says
  issue prose is not the instrument and requires a later tracked instrument plus
  `READY` freeze.
- **Decision made:** no.
- **Rationale:** issue lifecycle status does not provide the required immutable
  repository artifact identity or supersede the tracked `BLOCKED` record.
- **Uncertainty:** low; a later unobserved or untracked artifact may exist, but it
  is outside the pinned execution host.
- **Reasonable disagreement:** another reviewer could argue that issue closure
  signals intent, but that would not satisfy the explicit immutable-binding
  requirement.
- **Effect on final findings:** causes `CL-002`, `Execution Validity: BLOCKED`,
  and `Audit Outcome: NOT_REACHED`.

## `MJ-002` — Is target identity inventory substantive inspection?

- **Question:** Does cloning the target and listing tracked paths count as audit
  coverage?
- **Available evidence:** only Git identity, clean checkout, tree identity, and
  path inventory were observed; no contents were assessed under an instrument.
- **Decision made:** count these actions as preflight identity coverage only.
- **Rationale:** artifact presence is not specification, implementation, test
  selection, execution, or preserved result evidence.
- **Uncertainty:** low.
- **Reasonable disagreement:** a reviewer might call the path listing minimal
  static inspection; it still cannot support a substantive finding.
- **Effect on final findings:** target artifact-class coverage remains
  `NOT_REACHED`; `CL-001` remains identity-only.

## `MJ-003` — How should a blocked run be packaged?

- **Question:** Should the run omit downstream files or preserve them with
  explicit not-reached states?
- **Available evidence:** the request requires the full package and separate
  determinations, while also requiring fail-closed behavior.
- **Decision made:** preserve every required package surface, with no invented
  audit content and explicit `NOT_REACHED` records.
- **Rationale:** this makes the failed preflight reproducible without implying a
  completed or partial target audit.
- **Uncertainty:** moderate because the missing instrument provides no canonical
  blocked-package schema.
- **Reasonable disagreement:** another reviewer could prefer only a blocking
  record; the complete empty/not-reached surfaces are more directly reviewable
  against Issue #84's package checklist.
- **Effect on final findings:** package preservation can complete while the audit
  outcome remains `NOT_REACHED`.
