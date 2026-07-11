# B2-Run-2 Publication Readiness Audit

Audit date: 2026-07-11
Repository: `/workspace/architecturalboundary-research`
Objective: freeze B2 as the reference execution and determine whether B2 is complete enough to publish without altering Protocol v1.0 or scientific conclusions.

## Determination

**BLOCKED.** B2-Run-2 is not publication-ready as a fixed, inspectable scientific artifact. The current repository contains a B2 manuscript skeleton and some completed analysis/classification text, but the primary registered evidence chain is absent or placeholder-filled: BOR, SRF, ESM, DER, MSR, and Comparative Dataset are not complete enough to support the manuscript's conclusions.

This audit did **not** modify Protocol v1.0, scientific content, conclusions, evidence tables, or manuscript claims. It created only this audit report.

## Path consistency verification

Review concern checked: whether this audit used `papers/b2/` while the canonical post-restructure path should be `papers/paper-b2/`. In the current checkout audited here, `papers/b2/` exists, `papers/paper-b2/` does not exist, `scripts/validate.py` requires `papers/b2/main.tex`, `README.md` states that the B2 manuscript was moved to `papers/b2/`, and `investigations/b2-governance-cohort/README.md` states that the manuscript source currently lives in `papers/b2/`. Therefore this report's `papers/b2/` references match the canonical discoverable B2 manuscript path in this branch. If another branch standardized on `papers/paper-b2/`, this audit must be replayed after that branch is merged or checked out; no path translation was inferred silently.

## Artifact completion matrix

| # | Object | Canonical path | Status | Evidence supporting status | Missing fields/files | Completion requires |
|---|---|---|---|---|---|---|
| 1 | Protocol registration I1-I5 | `papers/b2/b2_05_protocol_registration.tex` | **PARTIAL** | I1-I5 sections are present, including admitted evidence, tolerance, measurement vector, and deterministic I5 decision function. | Cohort versions/doc snapshots and concrete degrees-of-freedom list remain TODOs; registration is embedded in manuscript only, not accompanied by a frozen machine-readable registration artifact. | Structural work; data work; scientific judgment for DoF enumeration. |
| 2 | Registration freeze | `papers/b2/b2_11a_registration_freeze.tex` | **PARTIAL** | A registration-freeze section exists and states that remaining work is limited to evidence/artifact closure and publication preparation. | Freeze date/source version are not concretely recorded; section itself lists unresolved closure requirements, including remaining TODOs and final PDF export. | Structural work; data work. |
| 3 | Baseline Observation Records (BOR) | `papers/b2/b2_07_baseline_observation_records.tex`; expected machine-readable artifacts under `investigations/b2-governance-cohort/` or equivalent | **PARTIAL** | BOR manuscript section exists with per-system placeholder row IDs. | BOR observations are TODO placeholders; evidence IDs are TODO placeholders; no B2 BOR JSON/CSV artifact was found; source reference bundle pointer is missing; completeness check is unresolved. | Data work; structural work; scientific judgment for observations. |
| 4 | Surface Record Files / Source Reference Files (SRF) | Expected B2 SRF files under `investigations/b2-governance-cohort/` or equivalent; referenced from `papers/b2/b2_07_baseline_observation_records.tex` | **MISSING** | Only schema/template-level SRF files exist outside the B2 execution; B2 BOR section asks for SRF pointers. | Per-source version, retrieval date, hashing scheme, source snapshots, and B2 SRF artifact files are absent. | Data work; structural work. |
| 5 | Derived Evidence Records (DER) | `papers/b2/b2_09_derived_object_registry.tex`; expected machine-readable artifacts under `investigations/b2-governance-cohort/` or equivalent | **PARTIAL** | DER manuscript section exists with per-system placeholder row IDs. | DER type/object/BOR references are TODO placeholders; schema version/export pointer missing; no B2 DER JSON/CSV artifact found. | Data work; structural work; scientific judgment for derivations. |
| 6 | Measurement Summary Records (MSR) | `papers/b2/b2_10_measurement_registry.tex`; expected machine-readable artifacts under `investigations/b2-governance-cohort/` or equivalent | **PARTIAL** | MSR manuscript section exists with per-system placeholder row IDs. | Measurement names, values, DER references, schema version/export pointer, tool versions/lockfiles, and rerun instructions are TODO placeholders; no B2 MSR JSON/CSV artifact found. | Data work; analysis execution; structural work. |
| 7 | Comparative Dataset | `papers/b2/b2_11_comparative_dataset.tex`; expected machine-readable dataset under `datasets/` or `investigations/b2-governance-cohort/` | **PARTIAL** | Comparative Dataset manuscript section exists. Later analysis references DER-001--DER-009 rows and measurement vectors. | Main comparative table still says fields are blocked/unpopulated and contains TODO(R/L/E); schema/export pointer and traceability map are missing; no B2 dataset CSV/JSON found. | Data work; analysis execution; structural work. |
| 8 | Analysis | `papers/b2/b2_12_analysis.tex` | **PARTIAL** | Analysis applies I4/I5 mechanically and reports 1 Supports, 8 Violates, 0 Indeterminate, cohort outcome Violates. | Analysis depends on comparative/MSR/DER/BOR identifiers that are not populated as registered evidence; therefore traceability is unresolved. | Analysis execution after data closure; structural trace repair. |
| 9 | Retained Classification | `papers/b2/b2_14_retained_classification.tex`; registry expected at `registry/retained_classifications.json` | **PARTIAL** | Manuscript retained-classification section lists per-DER outcomes and cohort outcome Violates/Unsupported. | `registry/retained_classifications.json` is empty; classification table depends on unresolved dataset/MSR trace; duplicate LaTeX label exists for `sec:retained-classification`. | Structural work; data work; analysis execution after trace closure. |
| 10 | Threats to validity | `papers/b2/b2_13_threats_to_validity.tex` | **PARTIAL** | Threats section exists and covers internal, construct, external, selection, observer, expectancy, and reproducibility threats. | Selection rationale, observer-bias mitigation, and replication package pointers remain TODOs. | Structural work; scientific judgment. |
| 11 | B2 manuscript | `papers/b2/main.tex` plus `papers/b2/b2_01_abstract.tex` through `papers/b2/b2_16_conclusion.tex` | **PARTIAL** | All `\input{...}` targets in `main.tex` exist; manuscript sections are present. | Many TODOs remain, including abstract result/artifact pointers, citations, evidence sources, traceability, ESM, BOR, DER, MSR, dataset, threats, and conclusion trace completeness; `pdflatex` unavailable in environment; duplicate label exists. | Structural work; data work; analysis execution; scientific judgment for unresolved narrative claims. |
| 12 | Publication artifacts | `releases/`, `scripts/publish.py`, `scripts/build.py`, expected PDF/replication package | **MISSING** | Publication/build scripts exist only as placeholders; `releases/README.md` exists. | No final PDF, no release bundle, no frozen replication package, no hashes/manifest, no configured publication pipeline. | Structural work; build execution after B2 closure. |

## Verification findings

### Traceability of conclusions to registered evidence

**Fail / blocked.** The conclusion and analysis report a cohort-level **Violates** outcome from DER/MSR/dataset rows, but the underlying BOR, DER, MSR, and Comparative Dataset sections contain TODO placeholders or missing machine-readable artifacts. Because the evidence chain is not populated, every conclusion is not currently traceable to registered evidence.

### I5 applied exactly as preregistered

**Partially verifiable.** The analysis text uses the registered I5 branches: missing -> Indeterminate; all five components equal 1 -> Supports; otherwise -> Violates; cohort precedence Indeterminate > Violates > Supports. However, exact application cannot be fully certified because the Comparative Dataset and MSR source records used to compute the vectors are not complete/frozen.

### No unresolved placeholder presented as a result

**Fail.** Multiple TODO placeholders remain in result-bearing manuscript sections, including the abstract, BOR, ESM, DER, MSR, Comparative Dataset, Threats, and Conclusion. The abstract still says results should be inserted after BOR/DER/MSR are populated, while later sections present a cohort result.

### Retained classifications match comparative dataset

**Blocked.** The retained-classification table matches the analysis table's reported vectors/outcomes at the narrative level, but the Comparative Dataset section still contains unpopulated TODO(R/L/E) fields and lacks the traceability map/export. Therefore matching cannot be deterministically validated against a completed dataset artifact.

### Manuscript does not claim more than the evidence supports

**Blocked / likely overclaim in current state.** The manuscript claims a deterministic cohort outcome and retained status, but the registered evidence artifacts needed to support those claims are incomplete or absent. The scientific conclusion may be conservative in wording, but it is not publication-ready until trace closure exists.

### Internal links and LaTeX inputs resolve

**Partial.** All `\input{...}` targets referenced by `papers/b2/main.tex` exist. A duplicate LaTeX label `sec:retained-classification` appears in both methodology and retained-classification files. Full LaTeX compilation could not be executed because `pdflatex` is not installed in this environment.

### No scientific content silently changed during repository restructuring

**Not fully verifiable from current working tree alone.** The B2 README states the LaTeX files were moved from the repository root into `papers/b2/`. This audit found no evidence of additional scientific edits made during this audit. Establishing that no prior restructuring changed scientific content requires comparing against the pre-move commit or archived B2-Run-1/B2-Run-2 source, which is not part of this audit's permitted mutation scope.

## Exact blockers

1. Populate or provide frozen BOR artifacts for every registered cohort member, including versioned evidence references and non-placeholder factual observations.
2. Provide B2 SRF/source-reference files with version/retrieval/hash metadata for every admitted source.
3. Populate/freeze ESM records or reconcile whether SRF vs ESM naming is intended; the manuscript currently uses ESM sections while the user checklist asks for SRF.
4. Populate/freeze DER artifacts with derivation type, derived object content, and BOR/SRF trace links.
5. Populate/freeze MSR artifacts with M1-M5 values, DER trace links, schema version/export pointer, and rerun/tooling metadata.
6. Populate/freeze the Comparative Dataset with R/L/E or I4 fields, traceability map, schema/export pointer, and machine-readable dataset artifact.
7. Re-run/confirm I4/I5 only after the dataset/MSR/DER/BOR chain is complete; do not reinterpret conclusions while closing trace gaps.
8. Reconcile retained classifications against the completed Comparative Dataset and update the empty `registry/retained_classifications.json` or explicitly document why manuscript-only classification is canonical.
9. Remove or resolve all TODO placeholders that are presented in publication-facing sections.
10. Complete threats-to-validity placeholders: selection rationale, observer-bias mitigation, replication package pointer.
11. Fix LaTeX duplicate label `sec:retained-classification` and verify all references after a real LaTeX build.
12. Configure/build publication artifacts: final PDF, release manifest, hashes, and replication package.

## Ordered closure sequence

1. **Freeze scope ledger:** record B2-Run-2 source commit, freeze date, canonical artifact directory, and artifact naming convention without changing Protocol v1.0.
2. **Close SRF/BOR evidence base:** add source-reference records and BOR factual observations for all nine cohort members.
3. **Close ESM/DER:** populate execution-surface and derived-evidence records from BOR/SRF only.
4. **Close MSR:** compute M1-M5 values solely from DER entries with trace back to admitted BOR evidence.
5. **Close Comparative Dataset:** export machine-readable dataset and trace map from MSR/DER/BOR identifiers.
6. **Re-execute registered I5 mechanically:** verify per-system and cohort outcomes from the completed dataset only.
7. **Reconcile retained classification:** ensure manuscript table and registry/dataset agree exactly.
8. **Resolve manuscript placeholders:** remove TODOs only by pointing to frozen artifacts or explicitly stating limitations; do not strengthen conclusions.
9. **Validate structure/build:** run repository validation, LaTeX build, reference checks, and artifact hash/manifest checks.
10. **Create publication bundle:** final PDF plus replication package and release manifest.

## Commands used

```sh
pwd && find .. -name AGENTS.md -print && rg --files -g '!**/.git/**' | sed -n '1,200p'
find papers -maxdepth 2 -type d | sort; test -d papers/b2 && echo 'exists: papers/b2' || echo 'missing: papers/b2'; test -d papers/paper-b2 && echo 'exists: papers/paper-b2' || echo 'missing: papers/paper-b2'; rg -n "papers/(b2|paper-b2)|paper-b2|B2 Paper|b2-governance" README.md papers investigations reports registry scripts validation analysis evidence datasets releases REPRODUCIBILITY.md CONTRIBUTING.md || true
find /workspace -name AGENTS.md -print; printf '\n--- b2 files ---\n'; find investigations/b2-governance-cohort papers/b2 -maxdepth 4 -type f | sort
for f in investigations/b2-governance-cohort/README.md papers/b2/*.tex papers/b2/README.md registry/*.json; do echo '---' $f; sed -n '1,220p' "$f"; done
printf '%s\n' '--- TODO/FIXME/placeholders ---'; rg -n "TODO|TBD|placeholder|Insert|pending|populate|MISSING|FIXME" papers/b2 investigations/b2-governance-cohort protocol registry analysis evidence datasets releases validation scripts README.md REPRODUCIBILITY.md; printf '\n--- b2 labels/inputs ---\n'; rg -n "\\label\{|\\input\{|\\ref\{" papers/b2; printf '\n--- artifact-ish files ---\n'; rg --files | rg '(^|/)(bor|srf|der|msr|dataset|analysis|classification|publication|artifact|comparative|baseline|surface|measurement|derived|retained|threat)' -i
python scripts/validate.py; python scripts/build.py; (cd papers/b2 && pdflatex -interaction=nonstopmode -halt-on-error main.tex)
printf '%s\n' '--- inputs ---'; rg -n -F '\input{' papers/b2/main.tex; printf '%s\n' '--- labels ---'; rg -n -F '\label{' papers/b2; printf '%s\n' '--- refs ---'; rg -n -F '\ref{' papers/b2
python - <<'PY'
from pathlib import Path
root=Path('papers/b2')
missing=[]
for line in (root/'main.tex').read_text().splitlines():
    if '\\input{' in line:
        name=line.split('\\input{',1)[1].split('}',1)[0]
        p=root/(name+'.tex')
        if not p.exists(): missing.append(str(p))
print('missing inputs:', missing if missing else 'none')
labels=[]
for p in root.glob('*.tex'):
    for i,l in enumerate(p.read_text().splitlines(),1):
        if '\\label{' in l:
            labels.append(l.split('\\label{',1)[1].split('}',1)[0])
from collections import Counter
print('duplicate labels:', [k for k,v in Counter(labels).items() if v>1] or 'none')
PY
```

## Confirmation of non-mutation

This audit created `reports/b2-publication-readiness.md` only. It did not edit Protocol v1.0, B2 manuscript content, schemas, registries, evidence, analysis, or classifications. No B3 work was started.
