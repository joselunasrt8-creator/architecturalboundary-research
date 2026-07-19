# Terminology Reconciliation

Repository terms are retained only with the following qualifications. These mappings prevent a local label from implying a settled or universally shared construct.

| Repository term | Established/qualified term | Reconciliation |
| --- | --- | --- |
| Context scaling | **Available input context** or **context-length condition** | Capacity, supplied tokens, and effective use are distinct. Record the actual frozen source-unit selection and target-step token accounting, not only a model context-window limit (S1–S3). |
| Information availability | **Conditioned information available at inference** | Includes supplied context, retrieved text, and memory only when their visibility and selection policy are declared (S4–S6). |
| Explicit abstraction | **Explicit, inspectable generalized representation** | “Abstraction” is broad. For this investigation it must mean the specified source-linked principle, applicability conditions, limitations, and provenance—not any chain-of-thought or summary (S11–S15). |
| Reusable principle | **Generalized representation evaluated for transfer** | Reuse must be operationalized through preregistered unseen target tasks; textual reuse alone is insufficient (S10–S11). |
| Context-only | **No independently retained generalized artifact condition** | It does not mean the model performs no internal abstraction. It constrains only the retained transfer package. |
| Memory | **Persistent/external memory with a read/write policy** | Memory is not synonymous with a context window or an abstraction artifact. Retention, retrieval, and update policies are separate interventions (S1, S6, S14). |
| Summarization/compression | **Lossy or learned context compression** | A shorter representation is not automatically generalized, transferable, inspectable, or source-traceable (S7–S8). |
| Externalized reasoning artifact | **Visible intermediate trace, reflection, plan, or skill** | Such artifacts may be useful, but they differ in semantics and may carry feedback, tool state, or iterative history (S12–S15). |
| Long-horizon consistency | **Stability of application across separated evaluations** | It requires an explicit interval and repeated target evaluations; it is not implied by long-context processing. |
| Repeated-reasoning reduction | **Change in predefined repeated work under a fixed reuse policy** | Output length is not a measure of reasoning work. Tool calls, prompts, retrieval, and iterations must be controlled or reported. |

## Required Language

Use “candidate hypothesis,” “prospective explicit generalized representation,” and “bounded literature determination.” Do not write that context cannot abstract, that explicit artifacts are necessary, or that this is the first comparison. The design’s C1/C3 boundary concerns retained objects, not unobserved model computation.
