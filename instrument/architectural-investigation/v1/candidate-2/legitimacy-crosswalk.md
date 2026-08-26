# Legitimacy and Authority Crosswalk

## Non-transfer invariant

| Observed state | What it establishes | What it does not establish |
| --- | --- | --- |
| Capability present | A bounded artifact or mechanism exists | Selection, execution, effectiveness, authority |
| Evidence admissible | An item may support a bounded claim | Truth, sufficiency, ownership, permission |
| Structural validation passed | Required structure and deterministic identities conform | Scientific correctness, execution eligibility |
| Repository finding supported | A bounded claim is evidence-supported for the audited revision | Authorization to fix, mutate, promote, or generalize |
| Candidate recommended | Review by the proposed owner may be warranted | Acceptance, promotion, formalization, canon |
| Instrument frozen | Exact procedure identity can be bound | Audit authorization or target mutation authority |
| Audit request authorized | Named scope/operator/actions are permitted | Favorable findings or scientific truth |

```text
Capability != Evidence
Evidence != Validation
Validation != Execution Eligibility
Recommendation != Authority
Instrument Freeze != Audit Authorization
```

## Legitimacy maturity crosswalk

| Legitimacy state | Required general track/evidence | Authority boundary |
| --- | --- | --- |
| `NORMATIVE_INVARIANT` | `NORMATIVELY_SPECIFIED` with `NORMATIVE_SPECIFICATION` and `DECLARED_CANONICAL` | Declared invariant only; no enforcement implied |
| `RUNTIME_LOCAL_ENFORCEMENT` | `IMPLEMENTED` through `RESULT_PRESERVED` for a bounded local path | Local run only; bypass and repository-wide reach unresolved |
| `REPOSITORY_WIDE_ENFORCEMENT` | Every declared required path selected and revision-bound successful results preserved with complete path coverage | Repository scope only; infrastructure/external paths unresolved |
| `INFRASTRUCTURE_ENFORCEMENT` | Pinned infrastructure configuration, selection, and execution evidence from its owner | External ownership retained |
| `EXTERNALLY_VERIFIED_ENFORCEMENT` | `EXTERNAL_PINNED_EVIDENCE` plus independent verification record and resolved external authority | Verification scope only; no universal legitimacy |
| `NON_BYPASS_CLOSURE` | All declared normal, administrative, external, and break-glass paths covered; `EXTERNAL_BYPASS_EXCLUDED` directly supported | Cannot be inferred from repository-only evidence or implemented guards |

## Canonical-source conflict crosswalk

| State | Instrument treatment |
| --- | --- |
| `SINGLE_CANONICAL_SOURCE` | Bind source/owner/revision; projections remain nonauthoritative unless declared |
| `MULTIPLE_COMPATIBLE_PROJECTIONS` | Preserve source-to-projection lineage and compatibility evidence |
| `SPLIT_OPERATIVE_AUTHORITY` | Mark affected claims `CONTESTED`; require decomposition or owning-governance resolution |
| `DECLARED_CANONICAL_BUT_NOT_CONSUMED` | Separate normative specification from observed selection/implementation |
| `CANONICAL_SOURCE_UNRESOLVED` | Use unknown/unresolved authority and fail closed for normative transitions |

## Failure-containment reachability

`FAILURE_RESPONSE_DECLARED`, `INTERCEPTION_POINT_IDENTIFIED`,
`ENFORCEMENT_IMPLEMENTED`, `ENFORCEMENT_SELECTED`, `FAILURE_OBSERVED`,
`RESULT_PRESERVED`, and `EXTERNAL_BYPASS_EXCLUDED` map in order to normative
declaration, static structure, implementation, required-path selection, direct
execution observation, preserved revision-bound result, and external/bypass
coverage. No later state follows from an earlier one.

## External sovereignty coverage

| State | Required evidence |
| --- | --- |
| `REPOSITORY_CONTROLLED` | Bound local source/configuration and owner declaration |
| `EXTERNALLY_CONFIGURED` | Pinned external configuration identity; no execution implied |
| `EXTERNALLY_ATTESTED` | Bound external owner attestation with scope and timestamp |
| `EXTERNALLY_VERIFIED` | Independent verification record bound to external identity |
| `BREAK_GLASS_ONLY` | Normative restriction plus observed/verified path coverage; label alone is insufficient |
| `UNRESOLVED` | Missing/unbound external evidence; no positive sovereignty claim |

The crosswalk classifies evidence and maturity; it never authorizes an execution,
mutation, governance decision, or legitimacy claim outside the bounded record.
