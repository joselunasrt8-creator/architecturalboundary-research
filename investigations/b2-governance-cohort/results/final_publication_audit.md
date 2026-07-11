# Program B2 Final Publication Audit

Audit date: 2026-07-11

Scope: Program B2 (`investigations/b2-governance-cohort` and `papers/paper-b2`). This report treats Protocol v1.0, BOR, SRF, DER, MSR, Comparative Dataset, Literature Review, and Operational Definitions as frozen unless a reproducibility defect is identified.

Determination: **BLOCKED**

Reason: Protocol-required DER and MSR deliverables are not complete machine-readable artifacts, and the manuscript still contains explicit TODO / blocked placeholders in required evidence-pipeline sections. Under the user's stop rule, classification execution is not re-run or expanded in this audit.

## 1. Protocol Conformance Report

### Required artifact checklist

| Required output | Repository evidence | Status | Completeness finding |
|---|---|---:|---|
| Protocol Registration | `investigations/b2-governance-cohort/preregistration/i1_i5_registration.json`; index at `investigations/b2-governance-cohort/preregistration.md`; manuscript section `papers/paper-b2/b2_05_protocol_registration.tex` | Complete enough for audit | Registration artifact exists. |
| BOR | Nine JSON files under `investigations/b2-governance-cohort/bor/*.bor.json`; manuscript section `papers/paper-b2/b2_07_baseline_observation_records.tex` | Present, but manuscript extract incomplete | Machine-readable BOR files exist. Manuscript BOR section still contains TODO placeholders. |
| SRF | Nine JSON files under `investigations/b2-governance-cohort/srf/*.srf.json`; manuscript section `papers/paper-b2/b2_08_execution_surface_matrix.tex` | Present, but manuscript extract incomplete | Machine-readable SRF files exist. Manuscript SRF/ESM section still contains TODO placeholders. |
| DER | Placeholder README at `investigations/b2-governance-cohort/der/README.md`; manuscript section `papers/paper-b2/b2_09_derived_object_registry.tex` | **Incomplete** | Required DER records are not present as machine-readable frozen artifacts; the manuscript DER table contains TODO object types, descriptions, BOR references, schema, and artifact pointer. |
| MSR | Placeholder README at `investigations/b2-governance-cohort/msr/README.md`; manuscript section `papers/paper-b2/b2_10_measurement_registry.tex` | **Incomplete** | Required MSR records are not present as machine-readable frozen artifacts; the manuscript MSR table contains TODO measurement names, values, DER references, schema, and artifact pointer. |
| Comparative Dataset | Manuscript section `papers/paper-b2/b2_11_comparative_dataset.tex`; dataset directory index at `investigations/b2-governance-cohort/dataset/README.md` | **Incomplete** | The manuscript contains a metric extract, but the cohort-level R/L/E fields, traceability map, schema, and export pointer remain TODO / blocked. No machine-readable export was identified in the B2 dataset directory. |
| Analysis | Manuscript section `papers/paper-b2/b2_12_analysis.tex` | Present, but dependent on incomplete upstream artifacts | Analysis text exists and applies I4/I5 to a comparative table, but its upstream DER/MSR/comparative dataset artifacts are incomplete. |
| Threats to Validity | Manuscript section `papers/paper-b2/b2_13_threats_to_validity.tex` | Present, but publication-incomplete | Section exists but has unresolved TODOs for selection rationale, observer-bias mitigation, and replication package. |
| Retained Classification | Manuscript section `papers/paper-b2/b2_14_retained_classification.tex`; registry file `registry/retained_classifications.json` | Present, but dependent on incomplete upstream artifacts | Classification text and registry exist, but classification is not independently accepted by this audit because required upstream DER/MSR/comparative dataset completion is blocked. |

### Missing or incomplete exact sections

1. `papers/paper-b2/b2_09_derived_object_registry.tex`
   - Incomplete DER schema declaration.
   - DER table rows retain TODO object types, object descriptions, and BOR trace references.
   - Full DER artifact pointer remains TODO.
2. `investigations/b2-governance-cohort/der/README.md`
   - This is a structural placeholder and explicitly does not provide DER records.
3. `papers/paper-b2/b2_10_measurement_registry.tex`
   - Incomplete MSR schema declaration.
   - MSR table rows retain TODO measurement names, values, and DER trace references.
   - Full MSR artifact pointer remains TODO.
4. `investigations/b2-governance-cohort/msr/README.md`
   - This is a structural placeholder and explicitly does not provide MSR records.
5. `papers/paper-b2/b2_11_comparative_dataset.tex`
   - Dataset schema/export pointer remains TODO.
   - Cohort-level R/L/E field table remains TODO and is explicitly marked blocked pending I4/I5.
   - Traceability map remains TODO.
6. `papers/paper-b2/b2_13_threats_to_validity.tex`
   - Selection rationale, observer-bias mitigation, and replication package pointers remain TODO.

Protocol conformance result: **blocked before classification acceptance**.

## 2. Evidence Integrity Report

### Checks performed

- Verified that each BOR observation's `source_reference` resolves to an evidence source declared in the same BOR file.
- Verified that each SRF `observation_refs` entry resolves to a BOR observation in the referenced BOR file.
- Searched publication manuscript sections for unresolved TODO / blocked markers.
- Inspected DER and MSR repository directories for machine-readable artifacts.

### Integrity findings

| Integrity condition | Finding |
|---|---|
| Every observation traces to cited primary evidence | No broken BOR `source_reference` values were found in the JSON BOR files. |
| Every derivation references BOR observations | **Not validated / blocked.** The DER artifact is incomplete and lacks resolved BOR trace references in the manuscript extract; no machine-readable DER records were identified. |
| Every measurement references DER objects | **Not validated / blocked.** The MSR artifact is incomplete and lacks resolved DER trace references in the manuscript extract; no machine-readable MSR records were identified. |
| No interpretation appears inside BOR | No classification fields were found in BOR constraints, and BOR files identify themselves as baseline-observation-only records. This audit did not rewrite BOR text. |
| No unsupported claims exist | **Blocked.** Analysis and retained-classification sections rely on DER/MSR/comparative dataset claims whose upstream machine-readable artifacts are incomplete. The audit therefore cannot certify unsupported-claim absence. |

### Inconsistencies and reproducibility defects

1. The manuscript analysis references MSR ID ranges (`MSR-001--MSR-081`) and DER IDs (`DER-001--DER-009`), while the MSR and DER manuscript sections still use placeholder IDs such as `MSR-K8S-001` and `DER-K8S-001` and TODO traces.
2. The comparative dataset table contains concrete M1--M9 values, but the dataset section also states the R/L/E fields remain blocked pending I4/I5 registration. This creates a publication inconsistency that must be resolved without inventing evidence.
3. The repository contains machine-readable BOR and SRF artifacts, but no equivalent machine-readable DER, MSR, or comparative dataset export was identified for B2.

## 3. Retained Classification Table

Classification execution is **not accepted by this audit** because Protocol Conformance Phase 1 found incomplete required artifacts. The table below records only the classifications already stated in the manuscript, without adding new evidence, new outcomes, or new hypotheses.

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
- DER, MSR, and comparative dataset machine-readable exports were not identified.

### Derived Findings

- No new derived findings are introduced by this audit.
- Existing manuscript-derived findings depend on incomplete DER/MSR/comparative dataset artifacts.

### Interpretation

- The audit cannot certify the cohort synthesis as publication-ready while upstream trace artifacts remain incomplete.
- The already-written manuscript interpretation that the strict RLE invariant is unsupported must remain marked as dependent on completing the evidence pipeline, unless the authors decide that the manuscript tables themselves are the frozen DER/MSR/dataset artifacts and update traceability accordingly.

### Conclusions

- **No new scientific conclusion is added.**
- Publication readiness is blocked by artifact completeness and traceability defects, not by a newly discovered contrary observation.

## 5. Threats to Validity Review

The threats section is directionally appropriate but not publication-complete.

| Threat area | Audit finding |
|---|---|
| Internal validity | Existing text covers extraction/transcription error, pipeline drift, and trace breakage. Trace breakage is currently active for DER/MSR/comparative dataset artifacts. |
| Construct validity | Existing text covers operationalization mismatch, proxy measurement error, and schema pressure. No unsupported strengthening is recommended. |
| External validity | Existing text correctly restricts findings to the selected governance/authorization cohort and admitted representations. |
| Reproducibility | Existing text identifies source stability, tooling determinism, and inter-analyst agreement; replication package pointer remains TODO. |
| Selection bias | Section acknowledges non-random sampling but the selection rationale remains TODO. |
| Observer bias | Section acknowledges risk, but double-coding / reconciliation procedure remains TODO. |
| Protocol limitations | The current audit shows a protocol-execution limitation: classification cannot be publication-certified when DER/MSR/dataset artifacts are placeholders or internally inconsistent. |

## 6. Publication Readiness Report

| Publication item | Status | Issue |
|---|---:|---|
| Terminology consistency | Blocked | DER/MSR identifiers differ between manuscript sections and analysis/classification tables. |
| Figure numbering | Not fully audited | No figure-number defect was established in this audit. |
| Table numbering | Needs review | Several tables are present, but unresolved TODO tables prevent final numbering/readiness certification. |
| Citations | Needs review | BOR evidence sources are cited in JSON, but manuscript references and trace pointers are incomplete in DER/MSR/dataset sections. |
| References | Needs review | Bibliography was not validated as complete because publication is blocked earlier. |
| Appendix references | Needs review | Appendix/cross-link completeness was not certified because required artifacts are incomplete. |
| Cross-links | Blocked | Analysis references sections and IDs that do not resolve to completed DER/MSR records. |
| Protocol references | Present, but blocked | Protocol references exist, but execution artifacts do not yet satisfy the required pipeline. |
| Classification consistency | Blocked | Existing classification table depends on incomplete DER/MSR/comparative dataset traceability. |

## Final determination

**BLOCKED**

Objective blocking issues required before publication:

1. Complete or identify the frozen DER artifact with schema, DER IDs, object types, object descriptions, and BOR trace references.
2. Complete or identify the frozen MSR artifact with schema, MSR IDs, measurement names, values, and DER trace references.
3. Complete or identify the frozen Comparative Dataset export/schema and traceability map to MSR/DER/BOR.
4. Resolve manuscript TODO / blocked placeholders in required evidence-pipeline sections without adding unsupported evidence.
5. Reconcile DER/MSR identifier inconsistencies across DER, MSR, comparative dataset, analysis, and retained classification sections.
6. Complete the threats-to-validity TODOs for selection rationale, observer-bias mitigation, and replication package pointer.
