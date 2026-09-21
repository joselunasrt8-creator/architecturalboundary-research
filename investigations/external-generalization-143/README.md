# Issue #143 — prospective external-cohort execution

## Bounded determination

This package executes the prospectively frozen cohort in
[`preregistration.json`](preregistration.json). The freeze is a distinct earlier
Git commit. It binds the three target identities, the existing Architectural
Investigation Instrument `1.0.0-candidate.2`, source classes, stopping and
missingness rules, terminal values, rerun procedure, and cohort decision rule.
No target was replaced and no rule was amended after execution began.

The exact supplied repository checkout was bound at
`30b9730f04fe0e0902a93af43941a9fa6fa8b7bf`. The environment could not fetch
GitHub (`CONNECT tunnel failed, response 403`), and contained neither a local
nor remote-tracking `main` ref. The freeze therefore identifies that commit as
the only available current-main proxy and makes no claim that hosted `main` was
verified. Issue #143's prompt supplied the operative acceptance criteria; live
issue text could not be independently acquired in this environment.

## Historical-evidence audit and instrument choice

The inspected checkout contains prior external or cross-system work, including
the B2 governance cohort, the Structology transfer rehearsal, and instrument
calibration exemplars. None is rewritten as prospective #143 evidence. The
reported prior `phpenv/phpenv` single-target pilot was explicitly excluded from
the cohort to avoid duplication; no artifact for that pilot was present in the
supplied checkout.

The closest existing instrument is the Architectural Investigation Instrument
because its specification includes cross-repository boundary investigations.
Candidate.2 is immutably identifiable, but the repository's Issue #108
adjudication states that it is not frozen, not implementation-ready, not
independently calibrated, not audit-authorized, and not legitimately bindable.
The study preserves this prerequisite failure instead of inventing a replacement
methodology.

## Frozen cohort and outcomes

| Target | Frozen commit | Identity | Terminal determination |
| --- | --- | --- | --- |
| `nvm-sh/nvm` | `ffec9fec724da725013d5b50e763908113983fc3` | sourced-shell Node.js version manager | `BLOCKED_BY_AUTHORITATIVE_BINDING` |
| `pyenv/pyenv` | `0b0335a3786ab5848738559a2e827e1c223adecf` | shim/plugin Python version manager | `BLOCKED_BY_AUTHORITATIVE_BINDING` |
| `php-build/php-build` | `8a5e7abbd6b9f096ef46f6545d5f24ff66b24450` | PHP source-build/definition tooling | `BLOCKED_BY_AUTHORITATIVE_BINDING` |

For each target the origin, commit object, and tree reproduced. The same frozen
binding predicates then failed before substantive inspection. Consequently,
documentation, implementation, tests, automation, releases, measurements,
vocabulary mappings, findings, and output surfaces are `NOT_REACHED`, not
missing or negative. Per-target records preserve the source manifest, binding
checks, stage path, missingness, judgment, burden, provenance boundary, and
terminal rationale.

## Reproducibility

The frozen rerun rule selected `nvm-sh-nvm`. Repeating identity and instrument
binding with the same inputs reproduced the repository commit/tree, execution
path, machine-readable binding fields, and
`BLOCKED_BY_AUTHORITATIVE_BINDING` terminal. No manual judgment changed the
result. This demonstrates reproducibility only of the pre-execution blocker; it
does not demonstrate a reproducible substantive ABR result.

## Cross-target synthesis

Exactly zero of three targets passed authoritative binding and zero reached
substantive instrument execution. Methodological transfer was therefore not
tested beyond the authority gate. No forced fit occurred because no target
vocabulary was mapped. The frozen rule for all targets blocked before valid
substantive execution yields exactly:

```text
GENERALIZATION_NOT_DEMONSTRATED
```

This is a legitimate bounded methodology-readiness result. It neither supports
nor refutes a structural proposition about any target. It says the current
repository state cannot supply the valid external executions needed to
demonstrate the generalization claim.

## Acceptance-criterion reconciliation

| Criterion | Evidence | Status |
| --- | --- | --- |
| Prospective 3–5 repository cohort frozen before outcomes | earlier preregistration commit and three immutable target commits | Satisfied |
| Existing instrument/version and rules frozen | preregistration instrument, binding, stop, missingness, adjudication, terminal, and rerun rules | Satisfied |
| Same instrument attempted for every frozen target | three records with identical authoritative-binding checks | Satisfied |
| Required per-target evidence preserved | target JSON source/binding/execution/missingness/judgment/terminal fields | Satisfied to reached preflight boundary |
| Every target has exactly one legal terminal | three `BLOCKED_BY_AUTHORITATIVE_BINDING` values | Satisfied |
| At least one legitimate rerun | `nvm-sh-nvm-rerun.json` | Satisfied for permitted preflight scope |
| Exactly one frozen-rule cohort determination | `result.json`: `GENERALIZATION_NOT_DEMONSTRATED` | Satisfied |
| Outcomes do not silently redesign or repair methodology | no instrument or external repository changes | Satisfied |
| Hosted main and live Issue #143 independently inspected | network blocked; exact supplied checkout and prompt criteria used | Not independently satisfied; disclosed limitation |
| Substantive external ABR result produced | stopped by authoritative binding on all targets | Not reached by design; legitimate blocked outcome |

The experimental acceptance criteria are complete at their frozen stopping
boundary. The environment limitation prevents a claim of independently
verifying hosted main or the live issue page, but does not alter the preserved
terminal result.

## Limitations and non-claims

- The repositories were available as pre-existing local Git objects; network
  state, present hosted ownership, and present hosted default branches were not
  re-queried. `nvm` lacked a preserved local default-branch symbolic ref, so its
  `master` label remains contextual while its commit and tree are bound.
- The cohort is small and concentrated in developer version/build tooling. Its
  implementations differ, but it does not represent all repository purposes.
- External target is not external adoption.
- Successful execution is not a useful result.
- Blocked execution is not a negative structural finding.
- Vocabulary fit is not structural truth.
- Cross-repository generalization is not universal validity.
- This study establishes no usefulness, economic value, or external user value.
