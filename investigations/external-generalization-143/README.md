# Issue #143 — external-cohort execution record

## Bounded determination

This package preserves the attempted Issue #143 external-cohort execution and its observed pre-execution binding blockers. A post-run hosted audit found that the claimed preregistration commit `ccec06a23c0a97b424b0c4729f2e407f62858b26` is not present in the hosted repository and PR #146 contains only one hosted commit, which contains both the preregistration file and outcome artifacts.

Because Issue #143 requires the cohort and rules to be prospectively frozen before outcome observation, hosted history cannot verify the required preregistration/outcome separation. That defect cannot be repaired after outcomes have been observed. The cohort-level terminal determination is therefore:

```text
COHORT_INVALID
```

This invalidates the cohort as evidence for or against external generalization. It does not erase the recorded operational observation that the attempted executions encountered the same instrument authority/readiness blocker.

## Attempted cohort and observed blocker

| Target | Recorded commit | Recorded pre-execution terminal |
| --- | --- | --- |
| `nvm-sh/nvm` | `ffec9fec724da725013d5b50e763908113983fc3` | `BLOCKED_BY_AUTHORITATIVE_BINDING` |
| `pyenv/pyenv` | `0b0335a3786ab5848738559a2e827e1c223adecf` | `BLOCKED_BY_AUTHORITATIVE_BINDING` |
| `php-build/php-build` | `8a5e7abbd6b9f096ef46f6545d5f24ff66b24450` | `BLOCKED_BY_AUTHORITATIVE_BINDING` |

The records report that Architectural Investigation Instrument `1.0.0-candidate.2` was identifiable but failed the attempted authority/readiness binding gate before substantive target inspection. Documentation, implementation, tests, automation, releases, measurements, vocabulary mappings, findings, and output surfaces therefore remain `NOT_REACHED` in those records.

These per-target records are retained as audit history. Because the prospective freeze is not verifiable in hosted history, they must not be aggregated into a valid Issue #143 generalization result.

## Hosted audit correction

The original execution environment reported two local commits: a preregistration commit followed by an outcome commit. The hosted PR does not preserve that two-commit lineage. Hosted PR #146 has a single commit whose parent is the pre-study base, and that commit contains both preregistration and outcomes.

The correction does not manufacture a replacement preregistration commit. Doing so after observing outcomes would violate the experiment's prospective requirement.

Hosted CI also exposed two portability defects in the original tests:

- the test attempted to inspect the unavailable local preregistration commit;
- the target-reproduction test depended on Codex-local paths such as `/root/.nvm`.

The corrected tests validate repository-contained evidence and the invalidity disposition without depending on ephemeral external checkouts.

## Acceptance-criterion reconciliation

| Criterion | Status |
| --- | --- |
| 3–5 external repositories recorded | Recorded |
| Exact target commits recorded | Recorded |
| Existing methodology used without target-specific invention | Recorded |
| Binding failures remain visible | Preserved |
| Missingness remains `NOT_REACHED` | Preserved |
| Manual judgment recorded | Preserved |
| Reproducibility attempt recorded | Preserved as attempted preflight reproduction |
| Prospective freeze verifiably precedes outcomes | **Not satisfied in hosted history** |
| Exactly one bounded cohort determination | **`COHORT_INVALID`** |
| External-adoption/usefulness/economic claims avoided | Satisfied |

## Non-claims

- This package does not demonstrate external ABR generalization.
- It does not demonstrate that ABR fails to generalize.
- The recorded binding blocker is not a negative structural finding about any target.
- External target is not external adoption.
- Successful execution is not usefulness.
- Vocabulary fit is not structural truth.
- No economic value, external user value, decision influence, or universal validity is established.

A future Issue #143-style run must create and publish a verifiable preregistration identity before any target outcome is generated.