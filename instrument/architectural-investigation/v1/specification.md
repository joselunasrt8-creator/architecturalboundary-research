# Architectural Investigation Instrument v1 — Candidate Specification

## Status and authority

This document materializes the stable structural requirements owned by Issue
#59. It is a candidate normative surface, not a frozen executable instrument.
The unresolved controlled semantics in
[calibration-contract.md](calibration-contract.md) prevent
`IMPLEMENTATION_READY` and audit use.

## Purpose and governing question

The instrument supports bounded, reproducible repository investigations whose
question can be answered through reviewable repository evidence without
converting structural validation into scientific judgment. Every execution must
preserve enough identity, coverage, evidence, contradiction, limitation, and
judgment information for a second reviewer to reconstruct the bounded result.

## Supported investigation classes

- repository-architecture audits;
- research-artifact and repository-owned methodology audits;
- cross-repository boundary investigations with explicit ownership;
- static, executable, and mixed inspection modes; and
- documentation, source, schema, fixture, test, workflow, release, generated,
  binary, historical, and repository-status surfaces when explicitly included.

Unsupported claims include semantic completeness from sampling, scientific
correctness from artifact presence, external enforcement without pinned external
evidence, and runtime verification from static inspection.

An operator must identify their role and applicable qualifications or record the
limitation. No hidden analyst qualification may be assumed.

## Required inputs and preflight

Before substantive inspection, bind:

1. an Audit Request with a bounded governing question;
2. the target repository and exact immutable revision;
3. the frozen instrument name, version, containing commit, canonical paths, and
   manifest digest;
4. every normative dependency by immutable identity;
5. repository-local authorization for the audit and permitted mutations;
6. operator or custodian identity;
7. audit mode, environment, access limitations, and external-evidence mode;
8. intended scope, sampling policy, and stopping rule; and
9. rerun or supersession lineage.

Fail closed before substantive inspection if any mandatory binding is absent,
does not reproduce, or conflicts with the readiness record. Do not silently use
a newer target, instrument, dependency, or branch state after execution begins.

## Investigation flow

```text
Audit Request
-> Immutable Preflight Bindings
-> Scope and Coverage Declaration
-> Bounded Inspection
-> Inspection Log
-> Claim-Level Evidence Ledger
-> Boundary-Decomposed Findings
-> Four Output Surfaces
-> Stopping Determination
-> Execution Validity and Audit Outcome
-> Instrument Observations
```

The required record container and fields are defined by
[execution-record-contract.md](execution-record-contract.md). Controlled
evidence, authority, maturity, coverage, reachability, conflict, and promotion
semantics belong only to
[calibration-contract.md](calibration-contract.md).

## Evidence and claim rules

Every material finding must map to one or more claim-ledger entries. Evidence
must preserve, rather than collapse, these states:

```text
specification
!= implementation
!= test presence
!= CI selection
!= execution
!= preserved execution result
```

No later reachability or maturity state may be inferred from an earlier state.
Source authority is independent of source recency and evidence class.
Executable source is not automatically scientific authority. Negative,
contradictory, missing, inaccessible, unresolved, and indeterminate evidence
must remain visible.

```text
No Supporting Evidence != Evidence of Nonexistence
Missing Execution != Failed Execution
Static Inspection != Runtime Verification
```

## Boundary decomposition

Mixed findings must be separated into independently reviewable components:

1. repository-specific implementation or empirical finding;
2. Research Methodology candidate;
3. domain-neutral Structology candidate; and
4. instrument-improvement observation.

For each component record the exact abstraction, evidence basis, owning layer,
excluded implementation details, applicable maturity track, and disposition.
One evidence bundle may support multiple components only when every component
has an independent bounded claim. Wholesale promotion of APIs, schemas,
dataclasses, fixtures, field names, command-line options, or other
implementation bundles is prohibited.

## Required output surfaces

Every execution preserves, including explicit empty or not-reached states:

1. repository-specific empirical findings;
2. Research Methodology candidates;
3. provisional Structology candidates; and
4. instrument-improvement observations.

Only the first surface is a finding about the audited repository. Candidate and
instrument surfaces are proposals to their owning systems and cannot mutate
them during the run.

## Execution and stopping semantics

Preflight blocked states include:

```text
TARGET_IDENTITY_UNBOUND
INSTRUMENT_IDENTITY_UNBOUND
NORMATIVE_DEPENDENCY_UNBOUND
AUDIT_AUTHORIZATION_UNBOUND
ACCESS_BLOCKED
```

Inspection stopping states are:

```text
COMPLETE_FOR_DECLARED_SCOPE
COMPLETE_WITH_LIMITATIONS
MATERIAL_SURFACE_UNINSPECTED
ACCESS_BLOCKED
SCOPE_REVISION_REQUIRED
EXECUTION_INVALID
```

Every execution records exactly one execution-validity determination:

```text
VALID
BLOCKED
INVALID
```

and exactly one audit outcome:

```text
COMPLETE
PARTIAL
NOT_REACHED
```

`VALID` means all preflight bindings held and the frozen procedure was followed;
it says nothing favorable about repository findings. `BLOCKED` means a required
precondition failed before a valid execution could complete. `INVALID` means an
execution occurred but violated a binding, procedure, evidence-chain, or
integrity rule. `COMPLETE` is relative only to declared scope and does not imply
repository correctness or maturity. `PARTIAL` requires material audit work plus
explicit missing coverage. `NOT_REACHED` means substantive audit inspection did
not begin.

## Human scientific judgment

Humans exclusively own:

- evidence-class and source-authority classification where meaning is not
  mechanically decidable;
- conflict interpretation and bounded claim wording;
- semantic sufficiency and confidence judgments;
- boundary decomposition and proposed ownership;
- maturity determinations beyond mechanically observed predicates;
- promotion-candidate and promotion-disposition recommendations; and
- the final scientific interpretation of findings.

Every such decision must be recorded in a manual-judgment register with the
question, available evidence, decision, rationale, uncertainty, reasonable
disagreement, and effect on findings.

## Mechanically checkable boundary

Deterministic validation may check paths, identities, manifest digests, required
sections and fields, controlled-value membership, reference existence, and
internal traceability. It must not rank authority, resolve contradictions,
generate findings, determine scientific correctness, assign promotion
dispositions, or replace a manual judgment.

## Prohibited actions

- mutating the audited repository unless separately and explicitly authorized;
- changing the frozen instrument during a run;
- automatic scientific interpretation or promotion;
- automatic issue creation or external-system mutation;
- importing mutable issue or branch state as normative authority;
- treating structural validation as execution evidence; or
- rewriting a blocked or invalid execution into a successful one.

## Version and compatibility

Version, compatibility, immutable binding, and supersession rules are defined in
[compatibility-and-supersession.md](compatibility-and-supersession.md). An
instrument observation may propose a later change but cannot alter the version
governing its own execution.
