# Investigation Design: Context Scaling Versus Explicit Abstraction

## Status

**DOCUMENTATION-ONLY INVESTIGATION DESIGN**

This artifact defines a prospective empirical investigation. No experiment has been run, no observations have been collected, and no outcome is asserted.

## Provenance

- Upstream candidate hypothesis: `joselunasrt8-creator/MindShift-` PR #59
- Downstream design issue: `joselunasrt8-creator/architecturalboundary-research` Issue #86
- Upstream status: candidate abstraction; not empirically validated; novelty not established

## Candidate Hypothesis

> Scaling context windows increases information availability, but transforming information into reusable principles requires an explicit abstraction process.

The investigation must be capable of supporting, violating, or leaving this hypothesis indeterminate.

## Research Question

Under controlled task conditions, does an explicit abstraction workflow produce more transferable and reusable principles than a context-only workflow?

## Investigation Boundary

This design:

- separates context availability from explicit abstraction;
- distinguishes source-task performance from transfer;
- defines prospective measurements and stopping rules;
- preserves negative, indeterminate, and methodology-failure outcomes.

This design does not:

- execute an experiment;
- select final models, datasets, or vendors;
- claim that explicit abstraction is necessary;
- claim that context scaling is ineffective;
- establish novelty;
- prescribe operational architecture or governance.

## Experimental Unit

One experimental unit consists of:

```text
One source task
+
One bounded source-material set
+
One assigned workflow condition
+
One produced response or abstraction artifact
+
One or more unseen target tasks
+
One predefined transfer assessment
```

## Conditions

### C1 — Context-only

The system receives source material within a declared context budget and completes the source task without being required to construct or preserve a separate abstraction artifact.

### C2 — Explicit abstraction

The system receives the same source material and budget class, then must construct a source-linked abstraction artifact before attempting target tasks.

The abstraction artifact must include:

- identified relations or patterns;
- a generalized principle;
- applicability conditions;
- limitations or exclusions;
- provenance linking the principle to source material.

### C3 — Combined condition

The system receives an increased context budget and must also construct the explicit abstraction artifact. This condition tests complementarity rather than assuming context and abstraction are substitutes.

### C4 — Optional minimal-context control

A constrained-context baseline may be included when needed to estimate the effect of information availability itself.

## Canonical Prospective Objects

### Source Task

A bounded task performed using the source material.

### Source Material

The frozen information supplied before target-task evaluation.

### Context Budget

The maximum input material available to the system for the evaluated step, recorded in tokens or an equivalent deterministic unit.

### Abstraction Artifact

A preserved, source-linked object containing patterns, a generalized principle, applicability conditions, and limitations.

### Reusable Principle

A generalized statement that can be evaluated on an unseen target task distinct from its source.

### Target Task

An unseen task satisfying a preregistered difference criterion relative to the source task.

### Transfer Assessment

A preregistered procedure for determining whether the reusable principle was correctly applied to the target task.

### Repeated-Reasoning Measure

A predefined measure of reasoning work repeated after the source task, including the permitted reuse mechanism.

### Long-Horizon Consistency Measure

A predefined comparison of principle use across separated target tasks or evaluation intervals.

### Failure Classification

A typed record distinguishing task failure, abstraction failure, transfer failure, overgeneralization, evidence insufficiency, and methodology failure.

## Target-Task Difference Criterion

Before execution, each target task must be classified as materially different from its source using declared dimensions such as:

- domain or subject matter;
- surface representation;
- entities or vocabulary;
- task objective;
- causal or structural arrangement;
- required application context.

At least one substantive dimension must differ while the candidate underlying relation remains applicable. The exact threshold must be frozen before data collection.

## Primary Outcome

**Transfer performance on unseen target tasks.**

The primary measure must score whether a source-derived principle is applied correctly under the preregistered target-task difference criterion.

Source-task accuracy alone cannot satisfy the primary outcome.

## Secondary Outcomes

- source-task performance;
- abstraction-artifact completeness;
- source-to-principle traceability;
- principle applicability accuracy;
- overgeneralization rate;
- long-horizon consistency;
- repeated-reasoning reduction;
- performance by context budget;
- failure modes and boundary conditions.

## Comparability Controls

Before execution, freeze or record:

- model and version;
- system and user prompts;
- decoding or sampling parameters;
- tool access;
- retrieval access;
- source material;
- task order;
- context budget;
- time or compute budget where applicable;
- scoring procedure;
- evaluator identity or evaluation program;
- randomization procedure;
- permitted reuse of prior artifacts.

Any uncontrolled difference must be recorded as a limitation.

## Measurement Plan

### Transfer score

A task-specific score defined before execution. It must distinguish correct transfer, incorrect transfer, non-application, and unsupported application.

### Traceability score

The proportion of material claims in the abstraction artifact linked to identifiable source evidence.

### Overgeneralization rate

The proportion of target applications in which a principle is applied outside its declared conditions.

### Repeated-reasoning reduction

The difference in predefined reasoning work between workflows, without treating shorter output alone as reduced reasoning.

### Consistency score

Agreement in principle interpretation and application across separated target tasks.

## Analysis Plan

The analysis must:

1. report source-task and transfer outcomes separately;
2. compare C1 and C2 as the primary contrast;
3. compare C2 and C3 to evaluate complementarity with additional context;
4. stratify results by context budget and task family where sample size permits;
5. report task-level variation and failure classifications;
6. retain null, negative, mixed, and indeterminate results;
7. separate measured findings from interpretations of the bottleneck-shift framing.

No post hoc metric may replace the preregistered primary outcome. Exploratory analyses must be labeled exploratory.

## Decision Rule

The retained investigation outcome must be exactly one of:

### SUPPORTS

The explicit-abstraction condition demonstrates a preregistered, meaningful improvement in transfer relative to the context-only condition without an offsetting failure that invalidates the comparison.

### VIOLATES

The context-only condition matches or outperforms explicit abstraction under the preregistered decision rule, or explicit abstraction reliably impairs transfer.

### INDETERMINATE

Evidence is mixed, insufficient, underpowered, or unable to distinguish the conditions while the methodology remains valid.

### METHODOLOGY_FAILURE

The design or execution cannot validly test the research question because of confounding, invalid target-task separation, scoring failure, provenance failure, or another preregistered fatal defect.

## Stopping Rules

Stop before or during execution when:

- source or target tasks violate frozen eligibility rules;
- context budgets cannot be enforced or measured;
- the abstraction artifact is not preserved independently from the response;
- target tasks are exposed before the source artifact is frozen;
- evaluators cannot apply the scoring protocol consistently;
- condition contamination occurs;
- provenance or version bindings are missing;
- a fatal methodology defect makes the primary contrast uninterpretable.

Stopping does not imply support or violation. It produces `METHODOLOGY_FAILURE` or `INDETERMINATE` according to the defect.

## Literature and Novelty Review

Before any novelty claim, review primary literature on:

- long-context language models;
- retrieval and external memory;
- abstraction and concept formation;
- representation and transfer learning;
- summarization and knowledge distillation;
- externalized reasoning artifacts;
- reusable prompts, schemas, and structured memory.

The contribution status must be classified as one of:

- new empirical comparison;
- new operationalization;
- new abstraction workflow;
- synthesis of existing ideas;
- novelty unsupported;
- review incomplete.

A literature review is not part of this documentation-only PR unless separately scoped and source-bound.

## Threats to Validity

### Construct validity

The selected measures may not fully capture understanding, abstraction quality, or reasoning effort.

### Internal validity

Prompt differences, artifact exposure, evaluator expectations, or unequal budgets may confound condition effects.

### External validity

Results may not transfer across models, task families, domains, context sizes, or abstraction formats.

### Statistical conclusion validity

Small samples, task dependence, evaluator disagreement, and multiple comparisons may produce unstable estimates.

### Novelty validity

A positive empirical result does not establish that the underlying distinction or mechanism is novel.

## Required Execution Package

Before running the experiment, create and freeze:

- research request;
- protocol version;
- source and target task registry;
- task-difference criteria;
- condition assignments;
- prompt and model bindings;
- abstraction-artifact template;
- measurement specification;
- evaluator instructions;
- analysis script or deterministic procedure;
- stopping rules;
- provenance manifest;
- preregistration record.

## Current Determination

```text
Investigation design: COMPLETE
Experiment execution: NOT PERFORMED
Evidence collection: NOT PERFORMED
Empirical outcome: NOT REACHED
Novelty determination: NOT ESTABLISHED
```

No experiment may be represented as authorized or complete by this document alone.