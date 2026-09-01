# Agentic structural drift Run 3 execution

## Determination

**EXPERIMENT_BLOCKED**

Run 3 began only after all corrective bindings and the 19 PASS / 0 FAIL / 0
BLOCKED entry boundary were verified. The historical T0 identity and its frozen
structural baseline were independently reproduced byte-for-byte.

O1 produced one candidate and used the single permitted transcript-bound repair.
Both immutable candidates passed the scope gate and failed the frozen focused
semantic oracle. Attempt 1 emitted non-canonical JSON whitespace. The repaired
candidate corrected that failure but still omitted the required `nodes` list.
Under the frozen stopping rule the repaired candidate was rejected, ordinary
validation was not reached, no T1 formed, and O2–O4 were not exposed or attempted.
The failure classification is `TASK_FAILURE` because the exact candidate was
exercised and violated frozen output requirements.

No rejected candidate was structurally measured. There are consequently no
adjacent or cumulative T1 measurements. The zero accepted transitions do not
constitute evidence that drift was absent; they fail the minimum three-transition
observation floor and require `EXPERIMENT_BLOCKED`.

## Evidence layout

- `pre-execution-verification.json`: canonical identity, binding checks, and entry counts.
- `execution-record.json`: run-level chain and determination.
- `generation/`: exact candidate prompt, repair input, and response records.
- `transitions/O1/attempt-*`: immutable patches, gate logs, identities, and decisions.
- `structural/T0.json`: reproduced historical baseline; administrative verification only.

## Interpretation boundary

The frozen instrument observes only repository-owned static absolute-import
nodes, edges, enumerated violations, SCCs/self-loops, and set deltas. It does not
measure dynamic imports, runtime calls or dependencies, data coupling, semantic
cohesion, or general architectural quality. Because no accepted transition
formed, none of the structural-drift counter-hypotheses can be discriminated.
