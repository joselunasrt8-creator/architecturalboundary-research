# Conflict, Precedence, and Supersession Rules

## Claim-relative precedence

There is no global ranking that makes one artifact universally authoritative.
Apply precedence only within the bounded claim:

1. **Normative meaning:** the producer-declared canonical source at the bound
   revision governs; supporting documents cannot override it.
2. **Implementation structure:** bound implementation source governs what is
   present; documentation may describe intent but cannot replace source evidence.
3. **Required selection:** bound workflow or declared entry-point configuration
   governs selection; test/source presence does not.
4. **Observed execution/result:** a revision-, command-, environment-, input-,
   and result-bound execution record governs only that run; source/workflow
   configuration cannot prove it occurred.
5. **Repository status:** Git/repository metadata governs status facts only;
   issue closure or branch state cannot govern normative readiness.
6. **External semantics:** the external producer's bound source governs its own
   semantics; local interpretation cannot transfer ownership.
7. **Examples:** examples and fixtures never override normative specifications.

Recency is not authority. A later artifact wins only when the owning normative
surface explicitly declares supersession and preserves lineage.

## Contradiction procedure

When material evidence disagrees:

1. record every item and its claim-relative authority;
2. identify whether the items address the same claim, revision, scope, and
   execution;
3. preserve the contradiction even if it is later bounded;
4. mark the affected claim `CONTESTED` and cap maturity at the highest common
   uncontradicted state;
5. route semantic resolution to a manual judgment with rationale, uncertainty,
   reasonable-disagreement disclosure, and finding effect; and
6. prohibit `PROMOTION_ELIGIBLE` while a material contradiction is unresolved.

If scopes differ, decompose the claim rather than force precedence. If the owner
or canonical source cannot be resolved, use `UNKNOWN` or `EXTERNAL_UNRESOLVED`
and fail closed for any transition requiring authority.

## Supersession rules

A superseding record must have a new identity; identify the prior record and
exact scope superseded; bind both old and new revisions; state what changed and
why; preserve prior bytes/digests; and take effect prospectively only.

- A later readiness record does not change whether an earlier execution was
  valid under its then-bound instrument.
- A later frozen instrument does not migrate or reinterpret historical evidence.
- A correction distinguishes factual correction from changed methodology.
- Mutable branch, issue, or latest-release state is context, never supersession.
- An execution remains bound to its original instrument unless a separately
  authorized fresh execution receives a new execution ID.

## Historical #84 and #106 treatment

Issue #84 execution `AII-SAF-20260825-001` remains `BLOCKED` / `NOT_REACHED`.
Candidate.1 and the #106 materialization/freeze record remain historical
evidence with their original digests and revision-required determination.
Candidate.2 may cite them but cannot rewrite, upgrade, or call them successful.

## Later revisions

New evidence may produce a new candidate or frozen version. It must preserve
contrary evidence and explain compatibility. No new version may silently reuse
an old manifest identity or claim that validation under one version establishes
validity under another.
