# Run 3 entry conditions

Status is evaluated at this audit's bound HEAD. `FAIL` means a prospective
artifact/rule is not yet frozen; `BLOCKED` means verification depends on absent
identity/environment evidence. Passing this audit does not authorize execution.

| # | Condition | Status | Direct evidence / mechanical completion check |
|---|---|---|---|
| 1 | Run 1 primary evidence bound | PASS | `evidence/source-bindings.json` Run 1 paths/hashes; evidence introduced by `d227e7f...`. |
| 2 | Run 2 primary evidence bound | PASS | Bindings include both raw logs, patch, transition, and structural JSON; evidence introduced by HEAD. |
| 3 | Conflicts resolved by precedence | PASS | Bindings C-1/C-2 identify both claims, controller, and effect. |
| 4 | Every focused assertion semantically justified | FAIL | Run 2 `from lib import helper` assertion is not entailed by the frozen representation; R1 preflight is not yet produced. |
| 5 | Objectives permit multiple legitimate implementations | PASS | Run 1 helper objective and Run 2 behavior objectives do not prescribe source algorithms; the oracle, not O1, created Run 2 narrowness. |
| 6 | Focused/full roles explicitly separated | PASS | `gate-analysis.json` defines semantic vs repository AND-gates. |
| 7 | Deterministic failure taxonomy exists | PASS | `failure-taxonomy.json` defines inclusion, exclusion, evidence, multi-label use, and precedence. |
| 8 | Environment reproducible or bounded | FAIL | Run 1 tokenizer/network failures and Run 2 missing TeX are documented; no frozen Run 3 environment/T0 double baseline exists. |
| 9 | Structural measurements prospectively defined | FAIL | Prior measures exist, but Run 3 predicates, controls, and observable scope have not been frozen. |
| 10 | Measurements discriminate the research question | FAIL | Existing measures discriminate only narrow static invariants; Run 3 must adopt R5 controls and constrain its claim before execution. |
| 11 | Repair policy frozen | FAIL | This audit proposes R4, but no Run 3 preregistration has frozen it. |
| 12 | Stopping rule frozen | FAIL | R5 proposes the rule; separate Run 3 preregistration is absent. |
| 13 | Transition count justified | PASS | Audit defines ≥3 as arbitrary but defensible: initial change plus two accumulation opportunities; it is neither sufficient nor no-drift evidence. |
| 14 | Candidate identity bindable to validation identity | FAIL | R2 is specified but not implemented/frozen for Run 3. Run 2 demonstrates the uncommitted-candidate limitation. |
| 15 | Accepted state bindable to next input | FAIL | R2 requires exact-tree lineage, but no Run 3 registration/execution substrate exists. |
| 16 | Preregistration freeze identities independently available | BLOCKED | Claimed Run 1/2 freeze commits are absent from the current object database; Run 3 must preserve its freeze object in reachable history. |
| 17 | Historical evidence unchanged | PASS | Audit writes only the Issue 114 directory; final tree comparison must continue to show no Run 1/2 diff. |
| 18 | Run 3 objectives frozen before execution | FAIL | No Run 3 preregistration/objective freeze was created by this audit. |
| 19 | Run 3 remains a separate action | PASS | No Run 3 directory, candidate, gate execution, or accepted state was created. |

## Entry result

Current entry status: **NOT AUTHORIZED — 10 PASS, 8 FAIL, 1 BLOCKED**.

The harness design is valid only with prospective revisions. All FAIL items and
the identity BLOCKED item must become PASS in a separately reviewed, reachable
Run 3 preregistration before candidate generation. Changing a gate, objective,
invariant, measure, environment exception, or repair transcript after generation
invalidates entry rather than curing it.

## Determination consistency

The audit is not blocked from judging design because both runs' primary evidence
and candidate hashes are present. It is not `HARNESS_VALID_FOR_RUN_3` because
the semantic oracle and reproducibility/identity conditions fail. The revisions
are precise, prospective, and preserve both gates rather than weakening them;
therefore the controlling audit determination is exactly:

**HARNESS_VALID_WITH_PROSPECTIVE_REVISIONS**
