# Architectural Investigation Instrument v1 — Unresolved Calibration Contract

## Status and ownership

Issue #78 owns the controlled evidence, authority, maturity, coverage, conflict,
and promotion semantics consumed by the instrument and execution-record
contract. This file materializes the values and invariants that Issue #78 states
explicitly. It does not invent the missing per-value predicates or precedence
rules. Consequently it is an unresolved dependency, not an executable
calibration contract.

## Maturity tracks and declared states

Applicable tracks are `CONCEPTUAL_METHOD`, `DOCUMENTARY_SPECIFICATION`,
`OBSERVED_PRACTICE`, `EXECUTABLE_IMPLEMENTATION`, and
`TRANSFER_AND_REPRODUCTION`.

The declared conceptual/documentary state sequence is:

```text
CONCEPTUALIZED
DOCUMENTED
NORMATIVELY_SPECIFIED
EXAMPLE_INSTANTIATED
APPLIED_WITH_RECORD
REPEATED_WITH_RECORDS
TRANSFER_EVALUATED
INDEPENDENTLY_REPRODUCED
```

The declared executable-system state sequence is:

```text
ARTIFACT_PRESENT
MACHINE_VALIDATABLE
IMPLEMENTED
SELECTED_BY_REQUIRED_PATH
EXECUTED
EXECUTION_SUCCEEDED
RESULT_PRESERVED
REPEATED
TRANSFERRED
INDEPENDENTLY_REPRODUCED
```

A claim may use multiple applicable tracks, but each determination remains
separate. No combined label may hide a weak dimension.

## Evidence reachability

Executable reachability states are:

```text
ARTIFACT_PRESENT
ARTIFACT_PARSEABLE
ARTIFACT_DISCOVERABLE
ARTIFACT_REACHABLE_FROM_DECLARED_ENTRY_POINT
ARTIFACT_SELECTED_BY_REQUIRED_WORKFLOW
ARTIFACT_EXECUTED
EXECUTION_SUCCEEDED
RESULT_PRESERVED
RESULT_BOUND_TO_REVISION
```

Methodological reachability states are:

```text
METHOD_DECLARED
METHOD_DOCUMENTED
METHOD_NORMATIVELY_SPECIFIED
METHOD_INSTANTIATED
METHOD_APPLIED
APPLICATION_RECORD_PRESERVED
APPLICATION_BOUND_TO_REVISION
METHOD_REPEATED
TRANSFER_EVALUATED
INDEPENDENTLY_REPRODUCED
```

A later state may never be inferred from an earlier state.

## Declared evidence classes

```text
NORMATIVE_SPECIFICATION
NORMATIVE_BOUNDARY_DECLARATION
PROCEDURAL_DOCUMENTATION
DESCRIPTIVE_DOCUMENTATION
IMPLEMENTATION_SOURCE
MACHINE_VALIDATABLE_CONTRACT
TEST_OR_FIXTURE
WORKFLOW_CONFIGURATION
EXECUTION_RECORD
GENERATED_ARTIFACT
REPOSITORY_METADATA
HISTORICAL_RECORD
EXTERNAL_PINNED_EVIDENCE
DIRECT_OBSERVATION
INFERENCE
ABSENCE_OR_MISSING_EVIDENCE
CONTRADICTORY_EVIDENCE
```

Issue #78 requires, but does not supply, each class's support capability,
incapability, direct/inferential status, revision-binding requirement, execution
implication, and conflict rule.

## Declared source-authority classes

```text
DECLARED_CANONICAL
NORMATIVE_SUPPORTING
IMPLEMENTATION_AUTHORITATIVE
WORKFLOW_AUTHORITATIVE
REPOSITORY_STATUS_AUTHORITATIVE
HISTORICAL_ONLY
DESCRIPTIVE_ONLY
EXTERNAL_RESOLVED
EXTERNAL_UNRESOLVED
NONAUTHORITATIVE_EXAMPLE
UNKNOWN
```

Evidence class and source authority are independent. The Issue #78 prose calls
this a twelve-level vocabulary but enumerates eleven values; that contradiction
is unresolved. `UNKNOWN` cannot authorize imputed capability.

## External-evidence modes

```text
REPOSITORY_LOCAL_ONLY
PINNED_EXTERNAL_EVIDENCE
EXTERNAL_REFERENCE_UNRESOLVED
EXTERNAL_EVIDENCE_BLOCKED
```

External evidence remains owned by its producer. Unavailable external evidence
is not a conformance failure and cannot be replaced by consumer inference.

## Coverage contract

Every execution records total, inspected, sampled, uninspected, and inaccessible
artifacts by class; unresolved external references; current-revision coverage;
historical depth; remote-governance coverage; binary/generated coverage; and
claim-surface coverage.

Declared measures are:

```text
Artifact-Class Coverage
Artifact-Count Coverage
Canonical-Surface Coverage
Claim-Surface Coverage
Execution-Surface Coverage
External-Evidence Coverage
Historical-Depth Coverage
```

A percentage summarizes inventory only and never semantic completeness.

## Promotion predicates and dispositions

A promotion candidate requires a bounded abstraction, excluded
repository-specific details, a recorded evidence basis, and justified owner.
Provisional promotion additionally requires conceptual coherence, documented
evidence, complete boundary decomposition, visible contradictions, and no
disqualifying implementation dependence. Promotion eligibility additionally
requires normative specification, satisfied evidence predicates, a preserved
application or execution, repeated or transferred evidence appropriate to the
claim, bounded contradictions, resolved ownership/authority, and independent
review.

Declared dispositions are:

```text
UNSUPPORTED
OBSERVED_CANDIDATE
PROVISIONAL
PROMOTION_ELIGIBLE
DEFERRED_PENDING_EVIDENCE
REJECTED
```

Eligibility is not promotion, acceptance, formalization, or canon.

## Validator execution capability

Where validators are inspected, keep these capability states separate:

```text
SYNTAX_ONLY
STATIC_SEMANTIC
SOURCE_INTROSPECTING
IMPORT_EXECUTING
RUNTIME_EXECUTING
EXTERNAL_DEPENDENCY_EXECUTING
MUTATION_CAPABLE
```

Presence or source inspection cannot establish observed execution.

## Legitimacy-oriented additions

Issue #78's ContinuityOS calibration comment adds legitimacy-claim maturity,
canonical-source conflict, declared-failure versus observed-containment, and
external-sovereignty coverage states. Their values and the missing integration
crosswalk are recorded in
[unresolved-normative-gaps.md](unresolved-normative-gaps.md). They cannot be
applied until their relationship to the general tracks is resolved.

## Conflict invariants

```text
Evidence Class != Source Authority
Method Maturity != Implementation Maturity
Coverage Percentage != Semantic Completeness
Example != Preserved Application Record
Promotion Candidate != Promotion Eligible
Promotion Eligible != Promoted
```

The required precedence rules for documentation versus implementation,
canonical versus supporting, current versus historical, local versus external,
and examples versus normative specifications remain undefined. A reviewer must
not silently supply them.
