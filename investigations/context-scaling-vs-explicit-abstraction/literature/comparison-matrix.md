# Comparison Matrix

`Yes` means the primary paper evaluates the feature in its own setting, not that it is equivalent to the prospective investigation. `—` means not a primary evaluated feature of the paper.

| Method family / sources | Increases or selects available information | Retains an explicit artifact | Artifact is a generalized, source-linked principle | Unseen-task transfer is central | Directly compares availability × explicit artifact under equal target budget | Relation to planned conditions |
| --- | --- | --- | --- | --- | --- | --- |
| Long context (S1–S3) | Yes | — | — | Limited/varies | No | Closest to the context factor, but not the abstraction factor. |
| Retrieval augmentation (S4–S5) | Yes | Retrieved documents/index | No | Benchmark dependent | No | Adjacent: dynamic evidence selection, not source-to-principle transformation. |
| Managed external memory (S6) | Yes | Yes | No | Agent task continuation | No | Adjacent: memory policy is an additional treatment. |
| Context compression (S7–S8) | Indirectly | Yes | Usually no | Downstream task dependent | No | Adjacent: compactness is not validated reusable abstraction. |
| Distillation/feature transfer (S9–S10) | Training-time | Learned representation | No inspectable artifact | Yes | No | Adjacent transfer tradition at a different intervention boundary. |
| Concept/program representations (S11) | No | Yes | Structured concept/program | Yes | No | Adjacent evidence for representation-mediated generalization. |
| Reasoning traces and agents (S12–S15) | Sometimes | Yes | Sometimes textual/skill-like, but not the specified artifact | Varies | No | Closest artifact tradition; feedback, tools, iteration, or retrieval confound comparison. |
| Proposed prospective investigation | Fixed `N` versus `M` source units | C2/C4 only | Yes: principle, conditions, limitations, provenance | Yes: preregistered targets | Intended, not yet executed | Prospective design only; no result exists. |

## Closest Existing Methods

The closest **information** comparators are long-context, retrieval, and memory methods (S1–S6). The closest **artifact** comparators are chain-of-thought, reflection, and skill-library methods (S12–S15). Compression and distillation (S7–S10) are closest to representation bottlenecks but do not make the planned inspectable artifact available as a controlled target-step input.

## Comparability Decision

No retained source is a direct comparator under the protocol’s definition. This is a bounded classification of the retained corpus, not a claim that no comparable study exists elsewhere. The planned design must therefore describe these as adjacent methods and test a clearly delimited comparison rather than claim priority.
