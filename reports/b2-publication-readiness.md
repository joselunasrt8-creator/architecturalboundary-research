# B2-Run-2 Publication Readiness Audit Rerun

Audit date: 2026-07-11
Audited commit: `a5bcf9afff0dfcf21fb2687173cfffc05452eb12`
Audited branch: `work`
Requested basis: current `main` after PR #2 merge.
Actual basis available in this environment: local checkout only; no configured remote and no local `main` ref were present, so the requested update from current `main` could not be performed.

## Publication readiness determination

**BLOCKED.** This rerun cannot be treated as the canonical post-PR-2 publication-readiness determination because the requested post-PR-2 topology is not present in the audited checkout. The requested canonical manuscript root `papers/paper-b2/` is missing, and the requested dataset directories `datasets/canonical/`, `datasets/comparative/`, and `datasets/exports/` are missing. The repository still contains the pre-PR-2 B2 manuscript at `papers/b2/`, and repository validation still requires `papers/b2/main.tex`.

This report therefore records two separate facts:

1. **Requested-current-main audit status:** blocked by unavailable `main`/remote and missing requested canonical paths.
2. **Available-checkout scientific state:** still blocked because the B2 evidence chain remains incomplete or placeholder-filled, with BOR/SRF-or-ESM/DER/MSR/Comparative Dataset not frozen, populated, and traceable.

No scientific content was changed. Protocol v1.0 was not modified. Evidence was not populated. Results were not reinterpreted. B3 was not started.

## Canonical path check requested for this rerun

| Requested path | Exists in audited checkout? | Finding |
|---|---:|---|
| `papers/paper-b2/` | **No** | Requested canonical B2 manuscript root is absent; LaTeX audit from `papers/paper-b2/main.tex` cannot run. |
| `investigations/b2-governance-cohort/` | **Yes** | Investigation lifecycle anchor exists. |
| `datasets/canonical/` | **No** | Requested canonical dataset directory is absent. |
| `datasets/comparative/` | **No** | Requested comparative dataset directory is absent. |
| `datasets/exports/` | **No** | Requested dataset export directory is absent. |
| `registry/` | **Yes** | Registry directory exists. Present registry files are `candidate_invariants.json`, `investigations.json`, `protocol_versions.json`, and `retained_classifications.json`. |
| `schemas/` | **Yes** | Schema directory exists with BOR/SRF/DER/MSR/dataset/investigation schemas. |
| `releases/` | **Yes** | Release directory exists, but only placeholder documentation was found. |

## Classification scale used

Each object is classified as one of:

- **COMPLETE:** directory/file exists; research object exists; object is populated; object is frozen; object is traceable to registered evidence.
- **PARTIAL:** some structure or placeholder exists, but at least one of object existence, population, freeze, or traceability is missing.
- **MISSING:** required canonical path or research object is absent in the audited checkout.

The columns below distinguish directory presence, placeholder presence, research-object presence, population, freeze, and traceability.

## Artifact completion matrix

| # | Object | Canonical path assessed | Status | Directory exists | Placeholder exists | Research object exists | Populated | Frozen | Traceable | Evidence and missing work |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | Protocol registration I1-I5 | Expected post-PR-2 path: `papers/paper-b2/b2_05_protocol_registration.tex`; present legacy path: `papers/b2/b2_05_protocol_registration.tex` | **PARTIAL** | Requested: No; legacy: Yes | Yes | Manuscript section exists at legacy path | Partially | Partially | Partially | I1-I5 text exists in legacy manuscript path, but requested canonical path is absent; cohort versions and concrete degrees-of-freedom list remain unresolved in the legacy manuscript. |
| 2 | Registration freeze | Expected: `papers/paper-b2/b2_11a_registration_freeze.tex`; legacy: `papers/b2/b2_11a_registration_freeze.tex` | **PARTIAL** | Requested: No; legacy: Yes | Yes | Manuscript section exists at legacy path | Partially | No | Partially | Freeze section exists only at legacy path and still records remaining closure work; exact source ledger/freeze metadata are not complete. |
| 3 | Baseline Observation Records (BOR) | Expected B2 BOR objects under `investigations/b2-governance-cohort/` and/or `datasets/canonical/`; legacy manuscript section `papers/b2/b2_07_baseline_observation_records.tex` | **PARTIAL** | Investigation dir: Yes; requested dataset dir: No | Yes | Placeholder manuscript table exists | No | No | No | BOR rows are placeholder observations/evidence IDs in the legacy manuscript; no populated frozen BOR research objects were found in requested canonical dataset locations. |
| 4 | SRF / ESM | Expected SRF under `datasets/canonical/` or investigation artifacts; legacy ESM section `papers/b2/b2_08_execution_surface_matrix.tex` | **PARTIAL** | Investigation dir: Yes; requested dataset dir: No | Yes | Placeholder ESM manuscript table exists | No | No | No | User checklist names SRF while manuscript has ESM; no populated/frozen SRF or ESM research object was found. |
| 5 | Derived Evidence Records (DER) | Expected DER objects under `investigations/b2-governance-cohort/` and/or `datasets/canonical/`; legacy manuscript section `papers/b2/b2_09_derived_object_registry.tex` | **PARTIAL** | Investigation dir: Yes; requested dataset dir: No | Yes | Placeholder manuscript table exists | No | No | No | DER type/object/BOR-reference values remain placeholders; no populated/frozen DER object was found. |
| 6 | Measurement Summary Records (MSR) | Expected MSR objects under `investigations/b2-governance-cohort/` and/or `datasets/canonical/`; legacy manuscript section `papers/b2/b2_10_measurement_registry.tex` | **PARTIAL** | Investigation dir: Yes; requested dataset dir: No | Yes | Placeholder manuscript table exists | No | No | No | MSR names, values, DER references, export pointer, tooling metadata, and rerun instructions are not populated/frozen. |
| 7 | Comparative Dataset | Expected: `datasets/comparative/` and `datasets/exports/`; legacy manuscript section `papers/b2/b2_11_comparative_dataset.tex` | **PARTIAL** | Requested dirs: No | Yes | Placeholder manuscript table exists | No | No | No | Comparative dataset directory/export paths are absent; legacy table still contains unpopulated TODO fields and lacks trace map/export. |
| 8 | Analysis | Expected manuscript path `papers/paper-b2/b2_12_analysis.tex`; legacy path `papers/b2/b2_12_analysis.tex` | **PARTIAL** | Requested: No; legacy: Yes | No result placeholder in analysis table, but dependencies are placeholders | Manuscript analysis exists at legacy path | Text populated | No | No | Analysis applies I4/I5 in text, but it depends on non-populated BOR/DER/MSR/dataset objects, so it is not deterministically traceable. |
| 9 | Retained Classification | Expected manuscript path `papers/paper-b2/b2_14_retained_classification.tex`; registry directory `registry/` | **PARTIAL** | Requested manuscript: No; registry dir: Yes | Registry empty | Manuscript table exists at legacy path; registry object not populated | Partially | No | No | Legacy retained classification table exists, but `registry/retained_classifications.json` is empty and traceability depends on incomplete dataset/MSR/DER/BOR objects. |
| 10 | Threats to Validity | Expected manuscript path `papers/paper-b2/b2_13_threats_to_validity.tex`; legacy path `papers/b2/b2_13_threats_to_validity.tex` | **PARTIAL** | Requested: No; legacy: Yes | Yes | Manuscript section exists at legacy path | Partially | No | Not applicable / partial | Threat categories exist, but selection rationale, observer-bias mitigation, and replication package pointers remain unresolved. |
| 11 | B2 manuscript | Requested: `papers/paper-b2/main.tex`; legacy: `papers/b2/main.tex` | **PARTIAL** | Requested: No; legacy: Yes | Yes | Legacy manuscript exists | Partially | No | No | Requested canonical LaTeX root is absent. Legacy inputs all exist, but TODOs remain and a duplicate label is present. |
| 12 | Publication artifacts | `releases/`; build/report scripts requested under `scripts/` | **MISSING** | `releases/`: Yes | Yes | Final publication bundle not found | No | No | No | No final PDF, release manifest, hashes, replication package, or successful post-PR-2 report/dataset build pipeline was found. Requested scripts `check_registry.py`, `build_dataset.py`, and `build_report.py` are absent. |

## Changed classifications from previous audit

| Object | Previous report status | Rerun status | Change |
|---|---|---|---|
| Protocol registration I1-I5 | PARTIAL | PARTIAL | No status change; path basis changed from legacy manuscript-only assessment to requested canonical-path check plus legacy fallback evidence. |
| Registration freeze | PARTIAL | PARTIAL | No status change; requested canonical manuscript path is missing. |
| BOR | PARTIAL | PARTIAL | No status change; requested canonical dataset directories are missing and legacy BOR remains placeholder-filled. |
| SRF / ESM | MISSING for SRF, partial ESM noted | PARTIAL | Changed because the rerun records the existing placeholder ESM section separately from missing SRF/canonical dataset objects. It remains not publishable. |
| DER | PARTIAL | PARTIAL | No status change. |
| MSR | PARTIAL | PARTIAL | No status change. |
| Comparative Dataset | PARTIAL | PARTIAL | No status change; requested dataset directories are absent. |
| Analysis | PARTIAL | PARTIAL | No status change. |
| Retained Classification | PARTIAL | PARTIAL | No status change. |
| Threats to Validity | PARTIAL | PARTIAL | No status change. |
| B2 manuscript | PARTIAL | PARTIAL | No status change; requested canonical root is missing, legacy root exists. |
| Publication artifacts | MISSING | MISSING | No status change. |

## Verification findings

### Update from current main

**Blocked.** The checkout has no configured remote and no local `main` ref. Therefore Task 1 could not be completed in this environment. This report must not be treated as a canonical post-PR-2 main-branch audit unless replayed in a checkout where PR #2's canonical topology is present.

### LaTeX audit

- Requested canonical audit target `papers/paper-b2/main.tex`: **missing**, so LaTeX input resolution from the requested path could not run.
- Present legacy target `papers/b2/main.tex`: all `\input{...}` targets exist.
- Duplicate label recorded in present legacy manuscript: `sec:retained-classification` appears in `papers/b2/b2_04_methodology.tex` and `papers/b2/b2_14_retained_classification.tex`.

### Traceability of conclusions to registered evidence

**Blocked.** The legacy analysis and retained-classification sections report outcomes, but the supporting BOR/SRF-or-ESM/DER/MSR/Comparative Dataset research objects are not populated, frozen, and traceable in the requested canonical locations. Therefore conclusions are not currently deterministically traceable to registered evidence in this audited checkout.

### I5 applied exactly as preregistered

**Partially verifiable only at text level.** The legacy analysis text describes the registered I5 branches, but exact application cannot be certified because the completed Comparative Dataset/MSR/DER/BOR chain is absent.

### No unresolved placeholder presented as a result

**Fail.** Placeholder TODOs remain in publication-facing legacy manuscript sections, including BOR, ESM, DER, MSR, Comparative Dataset, Threats, and abstract/conclusion trace-completeness notes.

### Retained classifications match comparative dataset

**Blocked.** The retained-classification table cannot be deterministically checked against a completed comparative dataset because `datasets/comparative/` and `datasets/exports/` are absent and the legacy comparative table remains placeholder-filled.

### Manuscript does not claim more than evidence supports

**Blocked.** The legacy manuscript reports a cohort outcome, but the evidence chain needed to support that result is not complete/frozen/traceable in this checkout.

### All report paths exist in audited checkout

**No.** This report intentionally records requested canonical paths that are missing in the audited checkout because path absence is itself the primary audit finding. Existing paths were separately distinguished from missing requested paths in the canonical path check and artifact matrix.

### No scientific files changed

**Confirmed for this rerun.** The intended and observed file change is limited to `reports/b2-publication-readiness.md`. No protocol, manuscript, dataset, schema, registry, or release file was edited.

## Exact blockers

1. Replay this audit in a checkout that actually contains current `main` after PR #2, or configure a remote/local `main` ref so the branch can be updated.
2. Ensure the requested canonical B2 root `papers/paper-b2/` exists before treating the audit as post-PR-2 canonical.
3. Ensure `datasets/canonical/`, `datasets/comparative/`, and `datasets/exports/` exist or update the roadmap if those are no longer canonical.
4. Provide the requested scripts `scripts/check_registry.py`, `scripts/build_dataset.py`, and `scripts/build_report.py`, or update the validation contract.
5. Populate and freeze SRF/BOR research objects with admitted source metadata and factual observations.
6. Populate and freeze DER objects traced to SRF/BOR.
7. Populate and freeze MSR objects with I4 M1-M5 values traced to DER.
8. Build and freeze the Comparative Dataset and export trace map.
9. Re-run I5 mechanically from the completed dataset without changing Protocol v1.0 or reinterpreting results.
10. Reconcile retained classifications against the completed Comparative Dataset and current canonical registry names.
11. Remove publication-facing TODOs by linking to frozen artifacts or recording limitations; do not strengthen conclusions.
12. Produce publication artifacts: PDF, release manifest, hashes, and replication package.

## Ordered closure sequence

1. **Topology reconciliation:** update/replay on current `main` with PR #2 present; verify canonical paths before scientific audit.
2. **Scope/source ledger:** record exact B2-Run-2 source commit, freeze date, and canonical artifact roots.
3. **SRF/BOR closure:** add/freeze source references and factual observations for each registered cohort member.
4. **DER closure:** derive objects only from admitted and frozen SRF/BOR evidence.
5. **MSR closure:** compute M1-M5 values only from DER objects with trace to admitted evidence.
6. **Comparative Dataset closure:** build `datasets/comparative/` and `datasets/exports/` outputs plus trace map.
7. **I5 rerun:** execute the preregistered decision function mechanically from the completed dataset.
8. **Classification reconciliation:** align retained classification manuscript/registry/dataset outputs exactly.
9. **Manuscript cleanup:** resolve placeholders and duplicate labels without changing scientific conclusions beyond evidence-supported text.
10. **Publication build:** run validation/build/report scripts and create final release bundle.

## Commands used

```sh
git status --short --branch && git remote -v && git branch --show-current && git rev-parse HEAD && git rev-parse main || true && find /workspace -name AGENTS.md -print
find papers investigations datasets registry schemas releases scripts -maxdepth 3 -type d | sort
for p in papers/paper-b2 papers/b2 investigations/b2-governance-cohort datasets/canonical datasets/comparative datasets/exports registry schemas releases; do test -e "$p" && echo "exists: $p" || echo "missing: $p"; done
rg --files | sed -n '1,220p'
cat .git/config && git log --oneline --decorate --graph --all -20
python3 scripts/validate.py
python3 scripts/check_registry.py
python3 scripts/build_dataset.py
python3 scripts/build_report.py
git diff --check
python3 - <<'PY'
from pathlib import Path
from collections import Counter
for root_s in ['papers/paper-b2', 'papers/b2']:
    root=Path(root_s)
    main=root/'main.tex'
    print(f'main_exists={main.exists()} path={main}')
    if not main.exists():
        print('missing_inputs=not_checked_main_missing')
        print('duplicate_labels=not_checked_main_missing')
        continue
    missing=[]
    for line in main.read_text().splitlines():
        if '\\input{' in line:
            name=line.split('\\input{',1)[1].split('}',1)[0]
            p=root/(name+'.tex')
            if not p.exists(): missing.append(str(p))
    print('missing_inputs=', missing or [])
    labels=[]
    for p in root.glob('*.tex'):
        for i,l in enumerate(p.read_text().splitlines(),1):
            if '\\label{' in l:
                labels.append((l.split('\\label{',1)[1].split('}',1)[0], str(p), i))
    c=Counter(k for k,_,__ in labels)
    print('duplicate_labels=', {k:[x for x in labels if x[0]==k] for k,v in c.items() if v>1})
PY
git status --short
git diff -- reports/b2-publication-readiness.md
git diff --name-only
```

## Validation results

| Command | Result |
|---|---|
| `python3 scripts/validate.py` | PASS: repository topology validation passed for the available checkout. |
| `python3 scripts/check_registry.py` | FAIL: script file is absent in this checkout. |
| `python3 scripts/build_dataset.py` | FAIL: script file is absent in this checkout. |
| `python3 scripts/build_report.py` | FAIL: script file is absent in this checkout. |
| `git diff --check` | PASS: no whitespace errors reported. |
| LaTeX input audit from `papers/paper-b2/main.tex` | FAIL/BLOCKED: requested canonical main file is absent. |
| LaTeX input audit from available `papers/b2/main.tex` | PASS for inputs; duplicate label `sec:retained-classification` recorded. |

## Non-mutation confirmation

This rerun replaced `reports/b2-publication-readiness.md` only. It did not edit Protocol v1.0, B2 manuscript scientific content, schemas, registries, evidence, datasets, analysis, retained classifications, or publication artifacts. No B3 work was started.
