# Literature Review Protocol

## Review Question

How does existing research distinguish information availability, long context, retrieval, memory, summarization, abstraction, and transferable representations?

## Secondary Questions

- Has the distinction between context availability and reusable abstraction already been stated?
- Has it been directly tested?
- Are explicit abstraction artifacts already used to improve transfer, consistency, or reuse?
- Which existing methods most closely match the proposed explicit-abstraction condition?
- Which studies compare larger context against structured abstraction, memory, compression, summarization, or distilled representations?
- Which established terms should replace or qualify the repository’s current terminology?
- What part of the planned investigation, if any, remains distinct?

## Scope

The review covers primary work on long-context language models; retrieval-augmented generation; external and persistent memory; context compression; summarization; knowledge distillation; abstraction and concept formation; representation and transfer learning; schema induction; structured memory; reusable prompts and externalized reasoning artifacts; long-horizon consistency; repeated reasoning; and cross-task/cross-domain transfer.

## Source Classes

Preferred evidence is peer-reviewed journal or conference work, official proceedings, and arXiv papers only when a final venue version is not identified. Official technical reports and project repositories are admissible only to establish implementation details attached to a paper. Marketing, news, unsupported blogs, and secondary summaries are not evidence. A preprint and its final version count as one source.

## Search Record

**Review date:** 2026-07-19. **Sources consulted:** ACL Anthology, NeurIPS Proceedings, ICLR/OpenReview, arXiv, and official paper PDFs/records linked in the [source registry](source-registry.md). The following query families were used as discovery vocabulary and expanded with the established terms in the terminology reconciliation:

- `long context transfer language models`; `context window scaling generalization`; `long context retrieval position`
- `retrieval augmented generation transfer`; `external memory language models`; `structured memory language models`
- `context compression long context`; `summarization versus abstraction`; `distilled representations unseen tasks`
- `explicit abstraction artifact transfer`; `schema induction transfer learning`; `concept abstraction language models`
- `externalized reasoning artifacts`; `long horizon consistency language models`; `repeated reasoning memory abstraction`

The registry records the reviewed, retained primary sources. Discovery coverage is bounded rather than exhaustive; search results are not evidence until the primary paper is reviewed.

## Inclusion Criteria

Retain a source when it directly addresses at least one of: increased available context; retrieval or persistent memory; compression or summarization; explicit abstraction; generalized/reusable representations; unseen-task transfer; structured reasoning artifacts; long-horizon reuse or consistency; repeated-reasoning reduction; or direct comparisons among those mechanisms.

## Exclusion Criteria

Exclude work with no clear relation to the question, insufficient methodological detail, duplicate versions, non-primary commentary, and work that only reports source-task performance when transfer is central but supplies neither a transferable object nor unseen-task evaluation. Exclusion is a relevance decision, not a quality judgment.

## Extraction and Comparison Procedure

For every retained source, record: mechanism; information source and availability; retained representation; whether the object is explicit and independently preserved; task and evaluation setting; transfer/reuse outcome; and limits for comparison. Code a source as a **direct comparator** only if it manipulates both information availability and an explicit reusable artifact, evaluates unseen targets, and controls the target-step information budget. Otherwise classify it as adjacent evidence.

## Review Limits

This protocol does not infer absence from the bounded search, rank all research traditions, or convert design documentation into empirical evidence. It does not preregister tasks or measurements. The planned investigation remains prospective until separately preregistered and executed.
