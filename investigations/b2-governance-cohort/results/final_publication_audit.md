# Program B2 Final Publication Audit

Audit date: 2026-07-11

Scope: Program B2 (`investigations/b2-governance-cohort` and `papers/paper-b2`). This report treats Protocol v1.0, BOR, SRF, DER, MSR, Comparative Dataset, Literature Review, and Operational Definitions as frozen unless a reproducibility defect is identified.

Determination: **BLOCKED**

Reason: Protocol-required BOR, SRF, DER, MSR, and Comparative Dataset machine-readable artifacts are present, but Analysis and Retained Classification remain not started and the manuscript still contains unresolved publication-readiness TODOs. Under the user's stop rule, classification execution is not run or expanded in this audit.

## 1. Protocol Conformance Report

### Required artifact checklist

| Required output | Repository evidence | Status | Completeness finding |
|---|---|---:|---|
| Protocol Registration | `investigations/b2-governance-cohort/preregistration/i1_i5_registration.json`; index at `investigations/b2-governance-cohort/preregistration.md`; manuscript section `papers/paper-b2/b2_05_protocol_registration.tex` | Complete enough for audit | Registration artifact exists. |
| BOR | Nine JSON files under `investigations/b2-governance-cohort/bor/*.bor.json`; manuscript section `papers/paper-b2/b2_07_baseline_observation_records.tex` | Present, but manuscript extract incomplete | Machine-readable BOR files exist. Manuscript BOR section still contains TODO placeholders. |
| SRF | Nine JSON files under `investigations/b2-governance-cohort/srf/*.srf.json`; manuscript section `papers/paper-b2/b2_08_execution_surface_matrix.tex` | Present, but manuscript extract incomplete | Machine-readable SRF files exist. Manuscript SRF/ESM section still contains TODO placeholders. |
| DER | Nine JSON files under `investigations/b2-governance-cohort/der/*.der.json`; manuscript section `papers/paper-b2/b2_09_derived_object_registry.tex` | Complete | Machine-readable DER files exist for all nine systems. |
| MSR | Nine JSON files under `investigations/b2-governance-cohort/msr/*.msr.json`; manuscript section `papers/paper-b2/b2_10_measurement_registry.tex` | Complete | Machine-readable MSR files exist for all nine systems. |
| Comparative Dataset | Manuscript section `papers/paper-b2/b2_11_comparative_dataset.tex`; dataset export at `investigations/b2-governance-cohort/dataset/b2-governance-cohort-i4.dataset.json`; schema at `schemas/dataset.schema.json` | Complete | The machine-readable export exists and is freshness-checked as a deterministic projection of the nine canonical MSRs. |
| Analysis | Manuscript section `papers/paper-b2/b2_12_analysis.tex` | Not started | The upstream Comparative Dataset exists, but no analysis execution or cohort outcome is accepted by this audit. |
| Threats to Validity | Manuscript section `papers/paper-b2/b2_13_threats_to_validity.tex` | Present, but publication-incomplete | Section exists but has unresolved TODOs for selection rationale, observer-bias mitigation, and replication package. |
| Retained Classification | Manuscript section `papers/paper-b2/b2_14_retained_classification.tex`; registry file `registry/retained_classifications.json` | Not started | No retained classification is independently accepted by this audit. |

### Missing or incomplete exact sections

1. `papers/paper-b2/b2_12_analysis.tex`
   - Analysis remains a deferred placeholder and does not issue cohort outcomes.
2. `papers/paper-b2/b2_14_retained_classification.tex`
   - Retained Classification remains not started for accepted lifecycle purposes.
3. `papers/paper-b2/b2_13_threats_to_validity.tex`
   - Selection rationale, observer-bias mitigation, and replication package pointers remain TODO.

Protocol conformance result: **blocked before analysis/classification acceptance**.

## 2. Evidence Integrity Report

### Checks performed

- Verified that each BOR observation's `source_reference` resolves to an evidence source declared in the same BOR file.
- Verified that each SRF `observation_refs` entry resolves to a BOR observation in the referenced BOR file.
- Searched publication manuscript sections for unresolved TODO / blocked markers.
- Inspected DER, MSR, and Comparative Dataset repository directories for machine-readable artifacts.

### Integrity findings

| Integrity condition | Finding |
|---|---|
| Every observation traces to cited primary evidence | No broken BOR `source_reference` values were found in the JSON BOR files. |
| Every derivation references BOR observations | Validated by repository DER contract checks. |
| Every measurement references DER objects | Validated by repository MSR contract checks. |
| No interpretation appears inside BOR | No classification fields were found in BOR constraints, and BOR files identify themselves as baseline-observation-only records. This audit did not rewrite BOR text. |
| No unsupported claims exist | **Blocked for publication.** Analysis and retained-classification stages remain not started; this audit therefore does not certify any cohort outcome. |

### Inconsistencies and reproducibility defects

1. Analysis and retained-classification sections remain outside the completed lifecycle and must not be treated as accepted cohort outcomes.
2. Remaining manuscript TODOs outside the canonical dataset path must be resolved before publication readiness is claimed.

## 3. Retained Classification Table

Classification execution is **not accepted by this audit** because Analysis and Retained Classification remain not started. The table below records only the classifications already stated in the manuscript, without adding new evidence, new outcomes, or new hypotheses.

| Boundary | DER | System | Manuscript protocol outcome | Manuscript status label | Audit status |
|---|---|---|---|---|---|
| B2-BND-001 | DER-001 | Kubernetes RBAC/Admission | Violates | Unsupported | Not independently accepted; upstream artifacts incomplete |
| B2-BND-001 | DER-002 | Kubernetes RBAC/Admission | Supports | Unsupported | Not independently accepted; upstream artifacts incomplete |
| B2-BND-001 | DER-003 | HashiCorp Vault | Violates | Unsupported | Not independently accepted; upstream artifacts incomplete |
| B2-BND-001 | DER-004 | AWS IAM | Violates | Unsupported | Not independently accepted; upstream artifacts incomplete |
| B2-BND-001 | DER-005 | Google Zanzibar | Violates | Unsupported | Not independently accepted; upstream artifacts incomplete |
| B2-BND-001 | DER-006 | Istio AuthorizationPolicy | Violates | Unsupported | Not independently accepted; upstream artifacts incomplete |
| B2-BND-001 | DER-007 | Envoy ext_authz | Violates | Unsupported | Not independently accepted; upstream artifacts incomplete |
| B2-BND-001 | DER-008 | OpenFGA | Violates | Unsupported | Not independently accepted; upstream artifacts incomplete |
| B2-BND-001 | DER-009 | Cedar / AVP | Violates | Unsupported | Not independently accepted; upstream artifacts incomplete |

## 4. Cohort Summary

Because the protocol conformance audit is blocked, this section separates already-recorded manuscript content from audit conclusions.

### Observations

- BOR JSON files exist for nine cohort members.
- SRF JSON files exist for nine cohort members.
- DER, MSR, and comparative dataset machine-readable exports exist for the nine-system cohort.

### Derived Findings

- No new derived findings are introduced by this audit.
- No new derived findings are introduced from the completed Comparative Dataset in this audit.

### Interpretation

- The audit cannot certify cohort synthesis as publication-ready because Analysis and Retained Classification remain not started.
- Any already-written manuscript interpretation must remain separated from the completed Comparative Dataset until a bounded Analysis stage is executed.

### Conclusions

- **No new scientific conclusion is added.**
- Publication readiness is blocked by artifact completeness and traceability defects, not by a newly discovered contrary observation.

## 5. Threats to Validity Review

The threats section is directionally appropriate but not publication-complete.

| Threat area | Audit finding |
|---|---|
| Internal validity | Existing text covers extraction/transcription error, pipeline drift, and trace breakage. The DER/MSR/Comparative Dataset machine-readable chain is now present and freshness-checked, but analysis-stage trace claims remain unexecuted. |
| Construct validity | Existing text covers operationalization mismatch, proxy measurement error, and schema pressure. No unsupported strengthening is recommended. |
| External validity | Existing text correctly restricts findings to the selected governance/authorization cohort and admitted representations. |
| Reproducibility | Existing text identifies source stability, tooling determinism, and inter-analyst agreement; replication package pointer remains TODO. |
| Selection bias | Section acknowledges non-random sampling but the selection rationale remains TODO. |
| Observer bias | Section acknowledges risk, but double-coding / reconciliation procedure remains TODO. |
| Protocol limitations | The current audit preserves the protocol-execution boundary: classification cannot be publication-certified before a separate Analysis and Retained Classification stage. |

## 6. Publication Readiness Report

| Publication item | Status | Issue |
|---|---:|---|
| Terminology consistency | Needs review | DER/MSR/dataset identifiers are machine-readable, but downstream analysis/classification text is not accepted in this audit. |
| Figure numbering | Not fully audited | No figure-number defect was established in this audit. |
| Table numbering | Needs review | Several tables are present, but unresolved TODO tables prevent final numbering/readiness certification. |
| Citations | Needs review | BOR evidence sources are cited in JSON; publication citation completeness remains outside this dataset synchronization. |
| References | Needs review | Bibliography was not validated as complete because publication is blocked earlier. |
| Appendix references | Needs review | Appendix/cross-link completeness was not certified because required artifacts are incomplete. |
| Cross-links | Needs review | Analysis and classification sections remain not started for accepted lifecycle purposes. |
| Protocol references | Present | Protocol references exist for the completed BOR/SRF/DER/MSR/Comparative Dataset pipeline. |
| Classification consistency | Blocked | Retained Classification remains not started. |

## Final determination

**BLOCKED**

Objective blocking issues required before publication:

1. Keep Analysis and Retained Classification marked not started until those stages are explicitly executed.
2. Resolve remaining manuscript TODO / blocked placeholders without adding unsupported evidence.
3. Complete the threats-to-validity TODOs for selection rationale, observer-bias mitigation, and replication package pointer.
