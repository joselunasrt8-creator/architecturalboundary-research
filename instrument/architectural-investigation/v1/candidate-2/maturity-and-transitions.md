# Maturity and Transition Predicates

## Claim-type to track mapping

| Claim type | Required track | Optional additional track |
| --- | --- | --- |
| Concept, method, procedure, documentary contract | `CONCEPTUAL_METHOD` or `DOCUMENTARY_SPECIFICATION` | `OBSERVED_PRACTICE`, `TRANSFER_AND_REPRODUCTION` |
| Observed human or repository practice | `OBSERVED_PRACTICE` | `CONCEPTUAL_METHOD`, `TRANSFER_AND_REPRODUCTION` |
| Code, schema, validator, fixture, test, workflow, runtime behavior | `EXECUTABLE_IMPLEMENTATION` | `TRANSFER_AND_REPRODUCTION` |
| Cross-context generality, transfer, or reproduction | `TRANSFER_AND_REPRODUCTION` | The originating conceptual or executable track |
| Mixed claim | Every applicable track separately | None may be collapsed into an aggregate label |

Manual judgment selects the claim type and records the rationale. The validator
may check that a selected track is allowed but may not select it.

## Conceptual and documentary predicates

Every later state requires every earlier applicable predicate plus the new
evidence shown here.

| State | Minimum evidence predicate |
| --- | --- |
| `CONCEPTUALIZED` | Bounded concept statement, owner, scope, and evidence basis recorded |
| `DOCUMENTED` | `CONCEPTUALIZED` plus revision-bound descriptive or procedural documentation |
| `NORMATIVELY_SPECIFIED` | `DOCUMENTED` plus a bound `NORMATIVE_SPECIFICATION` from an identified normative owner, with conflicts bounded |
| `EXAMPLE_INSTANTIATED` | `NORMATIVELY_SPECIFIED` plus an example explicitly marked nonauthoritative and traceable to the specification |
| `APPLIED_WITH_RECORD` | Applicable method steps performed and a revision-bound application record preserving inputs, judgments, and outcome |
| `REPEATED_WITH_RECORDS` | At least two distinct bound applications under the same specified method; differences and failures preserved |
| `TRANSFER_EVALUATED` | A declared different context, transfer question, mapping, contrary evidence, and bounded transfer determination |
| `INDEPENDENTLY_REPRODUCED` | A qualified reviewer independent of authorship repeats the applicable method from frozen inputs and preserves comparison/disagreement |

## Executable-system predicates

| State | Minimum evidence predicate |
| --- | --- |
| `ARTIFACT_PRESENT` | Revision-bound artifact path/blob directly observed |
| `MACHINE_VALIDATABLE` | `ARTIFACT_PRESENT` plus bound contract and validator capability; validation not yet implied |
| `IMPLEMENTED` | Revision-bound source implements the bounded capability; static inference limitations recorded |
| `SELECTED_BY_REQUIRED_PATH` | Bound workflow or entry point selects the artifact/capability for the declared required path |
| `EXECUTED` | Direct or preserved execution record binds revision, command, environment, inputs, and invocation |
| `EXECUTION_SUCCEEDED` | `EXECUTED` plus bound success predicate and observed result satisfying it |
| `RESULT_PRESERVED` | `EXECUTION_SUCCEEDED` plus immutable result identity, timestamp, provenance, and revision linkage |
| `REPEATED` | At least two distinct preserved executions with declared equivalence conditions and all failures retained |
| `TRANSFERRED` | Execution in a declared different context with mapping, scope, and transfer limitations preserved |
| `INDEPENDENTLY_REPRODUCED` | Qualified independent operator reproduces from frozen inputs and records comparison/disagreement |

Test presence cannot satisfy selection. Selection cannot satisfy execution.
Execution cannot satisfy success. Success cannot satisfy preservation.
Repetition, transfer, and independent reproduction are independent predicates.

## Methodological reachability transitions

`METHOD_DECLARED`, `METHOD_DOCUMENTED`, `METHOD_NORMATIVELY_SPECIFIED`,
`METHOD_INSTANTIATED`, `METHOD_APPLIED`, `APPLICATION_RECORD_PRESERVED`,
`APPLICATION_BOUND_TO_REVISION`, `METHOD_REPEATED`, `TRANSFER_EVALUATED`, and
`INDEPENDENTLY_REPRODUCED` are cumulative only when the corresponding evidence
predicate above is satisfied. A worked example stops at `METHOD_INSTANTIATED`.

## Missing and contradictory evidence

- Missing required evidence caps the claim at the highest earlier state whose
  predicates are fully supported.
- Bounded search failure is not proof of nonexistence outside that search.
- Contrary evidence makes the affected transition `CONTESTED`; it cannot be
  crossed until a manual review bounds or resolves the contradiction.
- An `UNKNOWN` authority item cannot satisfy a normative or ownership predicate.
- A failed execution is evidence of execution and failure, not success.
- An inaccessible external dependency produces a blocked/unresolved state, not
  local conformance failure.

## Instrument lifecycle predicates

| State | Predicate |
| --- | --- |
| `CANDIDATE` | Versioned surfaces and declared owner exist; gaps may remain; no execution identity or authority |
| `DRAFT` | Every required normative section is materialized and internally reviewable; calibration or independent review may remain |
| `SPECIFICATION_REVISION_REQUIRED` | Any normative definition, compatibility rule, calibration requirement, identity predicate, or required review is missing or contradicted |
| `IMPLEMENTATION_READY` | All normative gaps resolved; #77/#78 mappings semantically complete; calibration fixture passes two qualified independent reviews or documented adjudication; structural validation passes; no containing-commit or freeze claim is implied |
| `FROZEN` | `IMPLEMENTATION_READY` plus exact version, containing commit, canonical paths/blobs, manifest/content digests reproduced from that commit, supersession record, and freeze determination |

Transitions are monotonic only for the same version and evidence set. New
contradictory evidence can require a new revision; it never rewrites historical
state. `IMPLEMENTATION_READY` is a human, evidence-bound review determination,
not a validator output. `FROZEN` still does not authorize an audit.
