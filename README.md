# Architectural Boundary Research

Architectural Boundary Research (ABR) is the empirical investigation layer for testing bounded claims about recurring software structure across independently designed systems.

Its central question is:

> **When a proposed architectural boundary is frozen before observation, what empirical evidence supports, weakens, conditions, or leaves indeterminate the claim that the boundary recurs across independently designed systems?**

ABR is designed to turn architectural reasoning into reviewable evidence. It does not turn recurrence into universal truth, empirical classification into formal proof, or repository validation into scientific validity.

```text
Observation ≠ interpretation
Recurrence ≠ invariance
Empirical support ≠ formal proof
Indeterminate ≠ negative
Publication readiness ≠ stronger evidence
Repository validation ≠ scientific validation
```

## Purpose

This repository owns bounded empirical executions: preregistrations, protocols, observation records, derived evidence, measurements, datasets, analyses, classifications, conclusions, and publication artifacts.

Its job is not to prove the Continufy ecosystem correct. Its job is to expose candidate claims to procedures capable of supporting, narrowing, falsifying, or leaving them unresolved.

Negative and indeterminate outcomes are first-class research results.

## Research lifecycle

```text
Frozen protocol / preregistration
        ↓
Observation (BOR)
        ↓
Surface record (SRF)
        ↓
Derived evidence (DER)
        ↓
Measurement (MSR)
        ↓
Comparative dataset
        ↓
Analysis
        ↓
Retained classification
        ↓
Bounded cohort conclusion
```

Each stage should preserve its own provenance and claim ceiling. Later stages may interpret earlier evidence but must not silently rewrite it.

## Current B2 result

The current B2 lifecycle has completed BOR, SRF, DER, MSR, comparative dataset, analysis, retained classification, canonical cohort conclusion, and publication-readiness audit.

The canonical cohort outcome is:

```text
indeterminate
```

That result is evidence. It does not become stronger because the repository is publication-ready, because validation passes, or because downstream theory could use the artifacts.

An indeterminate result means the executed design did not legitimately resolve the target claim under its frozen decision rules. It should not be rewritten as support, rejection, or implementation readiness.

## Empirical claim boundary

ABR may support claims such as:

- a specified structure was observed in a specified system under a specified observation procedure;
- a measurement or derived property followed from frozen evidence under a declared rule;
- a candidate pattern recurred within the sampled cohort;
- a classification followed from the preregistered decision rule; and
- a bounded cohort conclusion is reproducible from preserved artifacts.

ABR alone cannot establish:

- a universal architectural invariant;
- mathematical necessity;
- causality from recurrence alone;
- completeness of the observation surface;
- representativeness beyond the sampled cohort;
- product value;
- execution legitimacy;
- authority to formalize a result; or
- authority to mutate another repository's canon.

## Reference Execution v1.0 boundary

This repository applies frozen methodologies to bounded investigations of real systems and preserves reviewable research artifacts.

It owns its protocol executions, empirical evidence, datasets, analyses, retained classifications, cohort conclusions, and producer-owned promotion packages.

The producer/consumer boundary is:

```text
Empirical evidence
        ↓
Producer-owned promotion package
        ↓
Consumer-owned admissibility decision
        ↓
Possible downstream formalization / use
```

A promotion package does not authorize its own acceptance. A downstream consumer must independently determine whether the evidence is admissible for its purpose.

## Instrument readiness is not evidence of the target claim

The repository contains versioned instrument candidates and readiness records. Instrument conformance, deterministic validation, and calibration evidence are prerequisites for trustworthy execution; they are not observations of the target architectural phenomenon.

The `investigations/structology-transfer-audit-rehearsal-1/` artifacts remain a pre-reference instrument-harness rehearsal. Their validity is `BLOCKED`, their transfer outcome is `NOT_REACHED`, and they are not Pilot Execution #1 or a Reference Execution.

The repository-owned Reference Execution v1.0 readiness history preserves blocked and revision-required states rather than converting incomplete readiness into substantive evidence. A blocked instrument cannot legitimately generate a positive target finding merely because its software runs.

## Observation completeness boundary

ABR observes systems through declared surfaces and instruments. Therefore:

```text
Observed repository surface ≠ complete software system
Static artifact ≠ runtime behavior
Accessible evidence ≠ all relevant evidence
No observed counterexample ≠ no counterexample exists
```

Every investigation should state what was observable, what was inaccessible, what was excluded, and how those limits constrain the conclusion.

## Sampling boundary

Cross-system recurrence depends on cohort construction. A pattern recurring across repositories chosen because they visibly exhibit the pattern is weak evidence of general recurrence.

Strong investigations should prospectively define:

- target population;
- inclusion/exclusion criteria;
- sampling or case-selection procedure;
- independence assumptions;
- domain/architecture diversity;
- stopping rule;
- missing/unavailable-system handling; and
- the population to which any conclusion may generalize.

ABR should prefer a narrower legitimate conclusion over an unsupported general one.

## Comparator and alternative-explanation boundary

Evidence for a proposed architectural boundary is stronger when the investigation can distinguish it from simpler explanations.

Where practical, investigations should ask whether an observed pattern is explained by:

- common framework conventions;
- language/package-manager structure;
- shared templates or ancestry;
- repository layout conventions;
- common cloud/platform requirements;
- sampling bias;
- analyst coding choices; or
- a simpler dependency/graph representation.

A recurring pattern that cannot be distinguished from a conventional implementation artifact should not be promoted as an architectural invariant.

## Reproducibility and replication

ABR distinguishes several different achievements:

```text
Artifact reproducibility
Same frozen evidence + same rules → same result

Independent re-analysis
Independent analyst + same evidence → comparable result

Replication
New systems / new evidence + frozen protocol → comparable result

Generalization
Replicated bounded result transfers to a stated population
```

Passing the first does not imply the others.

## Repository organization

| Path | Purpose |
| --- | --- |
| `protocol/` | Versioned investigation protocol definitions, schemas, templates, figures, and changelog. |
| `investigations/` | Preregistered bounded executions and their lifecycle artifacts. |
| `evidence/` | Cross-investigation observation, measurement, classification, and traceability stores. |
| `datasets/` | Comparative and publication datasets derived from investigations. |
| `schemas/` | Repository-level schemas for protocol objects and metadata. |
| `instrument/` | Versioned instrument candidates, manifests, compatibility contracts, and readiness evidence. |
| `papers/` | Manuscripts and paper-specific sources. |
| `registry/` | Machine-readable indexes of investigations, protocol versions, classifications, and candidate invariants. |
| `figures/` | Shared figures. |
| `scripts/` | Deterministic validation/build helpers. |
| `validation/` | Validation reports, schemas, and CI-facing assets. |
| `releases/` | Publication-oriented release bundles and release notes. |

## Adding a future investigation

1. Copy `investigations/template/` to `investigations/<investigation-id>/`.
2. Complete the preregistration before observing the target evidence used for adjudication.
3. Freeze the target claim, cohort-selection rule, observation surface, instruments, decision rule, and stopping rule.
4. Record observations in `bor/`, surfaces in `srf/`, derived evidence in `der/`, and measurements in `msr/`.
5. Build investigation-local datasets and analysis outputs without overwriting source observations.
6. Preserve missingness, deviations, amendments, exclusions, and counterevidence.
7. Register the investigation in `registry/investigations.json`.
8. Run `python3 scripts/validate.py` for repository conformance.
9. Report the scientific conclusion separately from repository/CI validity.

## Scientific principles

- Preregister before adjudicative observation.
- Separate observation from interpretation.
- Preserve complete traceability and negative evidence.
- Freeze decision rules before seeing target outcomes where feasible.
- Treat missingness and inaccessible surfaces as evidence limitations, not zeros.
- Preserve blocked and indeterminate outcomes.
- Compare proposed boundaries with plausible simpler explanations.
- Distinguish reproducibility from replication and generalization.
- Treat empirical recurrence and formal proof as separate stages.
- Do not strengthen claims during publication or promotion.

## Publication and validation

Reproducible publication builds are driven by `scripts/build_papers.py`.

```bash
python3 scripts/build_papers.py
```

Repository validation, including publication-readiness checks, is run with:

```bash
python3 scripts/validate.py
```

These commands test repository/build contracts. A green build or validation result does not establish that an empirical claim is true.

New research manuscripts should originate in this repository under `papers/<paper-id>/`; external editors may be used as non-canonical review surfaces.

## Relationship to Methodology Engineering

Methodology Engineering may define reusable methodology and instrument contracts. ABR executes bounded empirical investigations under frozen versions of such contracts.

```text
Methodology definition
        ↓
ABR preregistration
        ↓
ABR execution
        ↓
Empirical evidence
```

If execution reveals a methodology defect, ABR records the defect/deviation. It does not silently modify the frozen upstream definition to rescue the investigation.

## Relationship to Structology and Structural Foundations

Structology may supply candidate structural concepts. ABR can test bounded empirical consequences of those concepts. Structural Foundations may later formalize propositions that have independent justification.

Neither direction creates automatic validity:

```text
Structology concept → ABR use     does not validate Structology
ABR recurrence → formal theory    does not prove necessity
Formal theory → empirical world   does not establish external correspondence
```

## Relationship to SYNAPSE

SYNAPSE may produce deterministic structural analysis over declared topology. ABR can use such artifacts only when the investigation prospectively defines their evidentiary role and independently bounds topology/model fidelity.

Deterministic compiler output is not automatically empirical ground truth.

## Relationship to ContinuityOS

ContinuityOS concerns legitimacy/execution-boundary mechanisms. ABR can empirically investigate such mechanisms, but ABR evidence does not itself create execution authority.

## Evaluation program

The next high-value ABR work is to improve external validity and independent replication, not merely increase artifact volume.

Priority directions include:

1. **Independent cohort replication** — rerun a frozen investigation on systems not used to design the candidate claim or instrument.
2. **Independent analyst replication** — provide frozen protocols/evidence to another analyst and measure classification agreement.
3. **Observation-surface challenge** — compare static repository observations against runtime/build/deployment evidence where relevant.
4. **Comparator studies** — test whether candidate boundaries outperform simpler framework, dependency, or architecture explanations.
5. **Prospective counterexample search** — select cases likely to violate the candidate rather than only cases likely to confirm it.
6. **Cross-domain transfer** — test whether a result survives different languages, frameworks, deployment models, and organizational contexts.

## Falsification boundary

A candidate architectural claim should be narrowed, rejected, or retained as indeterminate if:

- prospectively selected systems produce counterexamples incompatible with the claim;
- the result depends materially on analyst discretion;
- the pattern disappears when controlling for framework/template ancestry;
- independent replication fails;
- observation-surface expansion changes the classification;
- a simpler explanation accounts for the evidence equally well; or
- the sampled evidence cannot support the proposed population-level claim.

ABR itself should be simplified if its research machinery does not improve traceability, reproducibility, bias control, or evidentiary clarity enough to justify its overhead.

## Current conclusion

ABR is the Continufy ecosystem's empirical evidence-producing environment. Its strongest legitimate output is a bounded, provenance-preserved empirical conclusion under a frozen investigation design.

Its value depends not on producing positive findings, but on making it difficult to turn architectural intuition into stronger claims than the evidence supports.
