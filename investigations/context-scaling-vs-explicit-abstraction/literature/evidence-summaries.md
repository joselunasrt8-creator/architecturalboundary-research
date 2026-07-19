# Evidence Summaries

These summaries report only what the retained primary sources establish in their own evaluation settings. They are not evidence for the candidate hypothesis or the planned investigation’s outcome.

## Information availability and long context

- **S1 (Transformer-XL)** introduces recurrence over prior segments to make information from earlier segments available beyond a fixed segment window. It is evidence that architectural memory can extend accessible history; it does not compare a larger context with an independently preserved, human-readable abstraction artifact on unseen target tasks.
- **S2 (Longformer)** changes attention sparsity to process long documents. It concerns computational access to longer inputs, not whether available information is transformed into reusable principles.
- **S3 (Lost in the Middle)** shows that long-context QA performance can depend on the position of relevant information. It supports treating nominal context capacity and effective use of supplied information as different variables.

## Retrieval, memory, and compression

- **S4 (RAG)** and **S5 (RETRO)** retrieve external text at inference. Their retrieved evidence changes available information and model conditioning. Retrieval selection is not the same intervention as preserving a source-derived generalized principle with declared applicability and limitations.
- **S6 (MemGPT)** manages a virtual context with external memory and retrieval-like paging. It is close to the planned retention boundary, but it evaluates an agent-memory mechanism rather than the planned factorial contrast with equal target-step packages.
- **S7 (LLMLingua)** compresses prompts to reduce token cost while preserving downstream task performance. Compression may be extractive or task-oriented and should not be called abstraction unless the retained object is evaluated for generalization, scope, and provenance.
- **S8 (AutoCompressors)** learns compressed soft-prompt representations of context. It is a representation-compression method; the retained representation is not an inspectable source-linked principle.

## Transfer and abstract representations

- **S9 (knowledge distillation)** transfers behavior from teacher to student through training. It is relevant to compact representations but differs from a within-run external artifact available at target time.
- **S10 (feature transfer)** directly studies when learned neural features transfer between tasks. It provides established transfer terminology and warns that transfer depends on task distance and representation level; it does not test language-model context budgets.
- **S11 (probabilistic program induction)** demonstrates compositional concept representations supporting generalization in a constrained domain. It is evidence that explicit structured representations can support generalization, not evidence that an LLM should externalize such a representation.

## Externalized reasoning and reusable artifacts

- **S12 (chain-of-thought)** supplies or elicits intermediate natural-language reasoning. The trace is explicit but is not necessarily a reusable principle, and its evaluation is primarily problem-solving rather than frozen source-to-unseen-target transfer.
- **S13 (ReAct)** makes reasoning/action traces available to an agent alongside observations. It joins an explicit trace with environment interaction, so tool state and observations are additional mechanisms absent from the planned design.
- **S14 (Reflexion)** retains verbal reflections over attempts. It is adjacent evidence for textual self-generated memory, but reflection content, feedback, and iteration are confounded with retention.
- **S15 (Voyager)** stores and retrieves executable skills across tasks. It most closely motivates reusable external artifacts, but its embodied environment, curriculum, retrieval policy, and code skills differ materially from the proposed source-linked principle artifact.

## Synthesis Bound

The selected literature establishes multiple mechanisms for increasing available information, selecting it, compressing it, retaining it, and externalizing intermediate artifacts. It does not, within this bounded corpus, supply evidence of the exact proposed four-condition comparison: fixed incremental source information crossed with a separately preserved, source-linked generalized principle; raw source withheld at transfer; equal target-step accounting; and preregistered unseen-target transfer evaluation.
