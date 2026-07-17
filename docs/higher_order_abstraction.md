# Higher-Order Abstraction: Evidence-Bounded Claim Transition

## Scope and method

This note examines the repository's present concepts without proposing a software
redesign. It treats directory names, record formats, scripts, and repositories as
current implementations and asks which responsibilities would remain if any one
of them disappeared.

The current abstraction is an **investigation lifecycle**:

```text
registration -> observation -> surface description -> derivation -> measurement
             -> comparison -> analysis -> classification -> cohort conclusion
             -> publication or bounded downstream proposal
```

The broader system containing that lifecycle is a process that changes the
epistemic status of a claim while preserving the basis on which each change was
made. Its product is not primarily a paper, dataset, registry entry, or promotion
package. Its product is a **reviewable claim-state transition with an
evidence-preserving justification**.

This reading preserves the repository's existing scientific and authority
boundaries. It does not claim that an empirical result is a formal invariant, or
that a producer proposal is a consumer decision.

## Observations

### The named stages are transformations, not places

The lifecycle can be restated in terms of responsibilities that do not depend on
the present file layout:

| Current concept | Larger process | Responsibility actually fulfilled | Invariant if the implementation disappears |
| --- | --- | --- | --- |
| Protocol and preregistration | Claim initialization | Fix scope, terms, admissible operations, and decision rules before observing outcomes | A claim must be evaluated under rules that cannot be silently rewritten by its results |
| Investigation | Bounded execution | Bind one claim, protocol version, cohort, and execution history | Evidence must have an explicit scope and execution identity |
| BOR | Acquisition | Preserve what was observed before architectural interpretation | Source observations remain distinguishable from interpretations |
| SRF | Normalization | Express heterogeneous observations through comparable surfaces while retaining source links | Comparison requires a declared projection from observations, not an implicit equivalence |
| DER | Derivation | Apply a named rule to declared upstream material | Every derived assertion resolves to inputs and a rule |
| MSR | Measurement | Convert derived evidence into registered evaluative quantities | A measurement states its basis, method, and missingness |
| Comparative Dataset | Alignment | Assemble like quantities across bounded subjects | Cross-system comparison preserves subject identity and upstream lineage |
| Analysis | Evaluation | Apply frozen analytical rules to the aligned evidence | Analytical output is reproducible from declared inputs and rules |
| Retained Classification | Per-subject adjudication | Record the allowed outcome for each subject | A classification is a decision record, not raw evidence or an unrestricted claim |
| Cohort Conclusion | Aggregation | Apply a cohort rule without erasing per-subject outcomes | A cohort claim retains its basis systems, exceptions, and uncertainty |
| Registry | Discovery and resolution | Locate canonical identities and authority pointers | Canonical objects must be unambiguously resolvable; indexing does not create their truth |
| Schema and validator | Conformance control | Test declared structural and lineage contracts | Accepted objects meet explicit contracts; conformance alone does not establish scientific truth |
| Build and publication machinery | Rendering and dissemination | Produce inspectable views of canonical source state | A presentation is derived from, and does not replace, its canonical basis |
| Minimal Promotion Package | Inter-authority handoff proposal | Present a bounded, immutable question or claim for independent consideration | A producer may preserve and transmit a proposal but cannot make the consumer's decision |
| Formalization consumer | Independent adjudication | Decide whether and how an empirical proposal enters a formal authority domain | Formal authority remains owned by the system that evaluates and accepts the formal object |

Multiple implementations can fulfill each responsibility. Observations could be
stored in records other than BOR files; resolution could use an index other than
the current JSON registries; dissemination need not be a LaTeX paper; and an
independent formalization authority need not share the producer's repository or
terminology. The responsibility survives each substitution.

### The lifecycle moves claims, not merely data

The arrows in the current pipeline are not uniform build steps. Each crosses an
epistemic boundary:

- observation to surface record introduces a comparison vocabulary;
- surface record to derived evidence introduces a derivation rule;
- derived evidence to measurement introduces an evaluative operation;
- measurements to analysis introduce population-level interpretation;
- analysis to classification introduces a decision rule;
- per-system classifications to a cohort conclusion introduce an aggregation
  rule; and
- empirical conclusion to a promotion package introduces a proposal boundary,
  not an increase in authority.

The durable artifact at each boundary is therefore a tuple such as:

```text
(claim before, declared basis, transition rule, claim after, scope, provenance,
 uncertainty, authority)
```

Current record types specialize this tuple for different transition kinds.

### Repositories are authority containers, not scientific roles

The producer repository currently performs several roles: protocol custody,
evidence custody, transformation, validation, publication, and proposal
packaging. Their co-location does not make them one responsibility. Conversely,
moving one role to a separate repository would not necessarily create a new
scientific boundary.

The fundamental repository boundary appears where authority cannot be delegated
by the producer: the empirical system may state what its evidence supports and
may propose a question, while a formalization system independently determines
what becomes canonical in its domain. The number and names of repositories on
either side are accidental; the non-transfer of decision authority is not.

## Hidden assumptions

1. **A linear directory lifecycle is assumed to be the scientific process.** In
   fact, the scientific constraint is an ordered dependency relation. Different
   subjects may be acquired independently, multiple derivations may share an
   observation, and a conclusion may depend on several classifications. The
   underlying shape is a provenance graph with controlled transitions.
2. **One record type is assumed per epistemic stage.** BOR, SRF, DER, and MSR are
   useful methodological specializations, but the invariant is separation of
   input, operation, output, and provenance—not these acronyms.
3. **Filesystem location is assumed to imply ownership and canonicity.** A path
   provides custody and resolution in the present implementation. Authority
   instead depends on an explicit contract identifying which object governs a
   claim and which objects are derived views.
4. **Validation is assumed to validate knowledge.** Current validators can prove
   conformance, referential integrity, and deterministic reconstruction. They
   cannot by themselves prove that an observation is complete, a construct is
   valid, or a conclusion is true.
5. **Determinism is assumed to imply repeatability of the full investigation.**
   Deterministic transforms support computational replay. Re-observing a mutable
   external system is a distinct form of replication and may yield different
   source evidence.
6. **A cohort is assumed to be the natural unit of generalization.** It is the
   registered comparison scope, not a universal population. Cohort aggregation
   must not erase selection criteria or basis systems.
7. **Publication is assumed to be the terminal product.** Publication is one
   projection of the claim history. A negative or indeterminate conclusion is
   still a complete scientific product, even when it cannot support candidate
   invariant review.
8. **Promotion language is assumed to describe upward scientific maturity.** A
   promotion package changes custody and review context, not evidentiary outcome
   or formal authority.
9. **Shared vocabulary is assumed to imply shared semantics.** Empirical
   classifications and formal objects may use similar names while answering
   different questions. Translation must remain explicit.
10. **Repository separation is assumed to guarantee independent authority.**
    Independence is a decision-right property. Separate storage can still hide a
    coupled decision, while one storage system can contain explicitly separated
    authorities.

## Candidate higher-order abstractions

### 1. Provenance graph

This explains lineage, replay, fan-in, and fan-out better than a linear pipeline.
It does not, by itself, explain why some transitions are scientific decisions or
why a producer cannot authorize a consumer result.

### 2. Typed evidence-transformation system

This treats every stage as a typed operation over traceable inputs. It explains
schemas, validators, deterministic builders, and methodological separation. It
under-explains uncertainty, scope, and differences in authority: a valid
transformation is not necessarily a warranted claim.

### 3. Claim-state machine

This explains preregistration, permitted classifications, supersession, and
outcome-sensitive package eligibility. A conventional state machine is too
lossy unless transitions retain their full evidence basis and can represent
parallel or competing derivations.

### 4. Chain of epistemic custody

This explains canonical sources, immutable provenance, publication views, and
the producer/consumer boundary. On its own it says little about the internal
method that warrants a transition.

### Smallest abstraction that explains the whole system

The minimal synthesis is an **evidence-bounded claim-transition system**:

> A system in which an identified authority may change the state of a bounded
> claim only by applying a declared rule to resolvable evidence, while preserving
> scope, provenance, uncertainty, and the authority responsible for the change.

This abstraction explains all observed repository responsibilities without
requiring their current implementations:

- the protocol constrains legal transitions;
- investigation artifacts supply and transform the evidence basis;
- schemas and validation test whether a transition conforms to its declared
  contract;
- registries resolve identities and canonical objects;
- analyses and conclusions record claim-state changes;
- publications render selected claim histories; and
- promotion packages carry a frozen transition history to another authority
  without performing that authority's transition.

The abstraction is deliberately smaller than a generalized research platform.
It says nothing about user interfaces, storage engines, orchestration, or
automation. Those are replaceable implementations.

## Proposed responsibility shifts

These are shifts in the conceptual model, not proposed code or repository moves.

| From | To | Why |
| --- | --- | --- |
| Lifecycle stage as a directory | Lifecycle stage as a claim-transition responsibility | Separates scientific method from file layout |
| Record acronym as the abstraction | Input/rule/output/provenance contract as the invariant | Permits independent implementations without weakening traceability |
| Registry as source of truth | Registry as resolver of an authority-owned canonical object | Prevents discovery metadata from being mistaken for evidence or decision authority |
| Validator as research arbiter | Validator as conformance and replay witness | Separates computational proof from empirical warrant |
| Dataset or paper as final artifact | Evidence-linked claim history as the primary artifact | Explains negative, indeterminate, unpublished, and multiply rendered outcomes |
| Investigation repository as a single role | Co-located protocol, evidence, evaluation, custody, and dissemination roles | Exposes real responsibilities without demanding physical separation |
| Promotion as maturity escalation | Handoff of a bounded proposal between independent authorities | Preserves the distinction between evidence and acceptance |
| Repository ownership | Explicit transition authority | Makes the fundamental boundary portable across repository topologies |

## Repository boundary implications

### Fundamental boundaries

- **Observation versus interpretation:** a later claim must not rewrite its
  observational basis.
- **Rule definition versus rule application:** outcome-dependent methods destroy
  the meaning of preregistration.
- **Canonical object versus derived view:** papers, reports, indexes, and bundles
  must not silently become competing authorities.
- **Evidence versus decision:** structural validity and available evidence do not
  automatically yield a retained classification or cohort conclusion.
- **Empirical authority versus formal authority:** a producer proposal cannot
  accept itself on behalf of an independent consumer.
- **Transition versus supersession:** correcting a claim history must preserve
  what changed, why it changed, and which version remains authoritative.

### Accidental boundaries

- one directory per lifecycle stage;
- JSON as the representation of canonical records;
- scripts as the mechanism for deterministic transformations;
- global versus investigation-local placement of datasets and analysis;
- separate top-level locations for schemas, validation assets, and registries;
- LaTeX and release directories as publication mechanisms; and
- one repository containing all empirical roles before the formal-authority
  boundary.

These boundaries may be valuable operational choices. Calling them accidental
means only that the scientific model does not depend on them.

### Boundary test

A proposed boundary is fundamental when removing it permits an actor to change a
claim's epistemic status without preserving at least one of: observational
basis, declared rule, scope, uncertainty, provenance, or responsible authority.
A boundary is likely an implementation boundary when those properties survive
its removal unchanged.

## New research questions

1. What is the minimal common transition envelope needed to describe BOR-to-SRF,
   SRF-to-DER, classification, conclusion, correction, and handoff without
   erasing their methodological differences?
2. Which transition properties can be proven computationally, which require
   scientific review, and which require an authority decision?
3. How should observational replication be distinguished from deterministic
   replay when external source systems evolve?
4. Can two independent normalizations of the same observations be compared
   without privileging either vocabulary as canonical?
5. What evidence would show that a current record boundary reflects a genuine
   epistemic discontinuity rather than historical workflow convenience?
6. When multiple derivation paths support conflicting claim states, what must be
   retained so that disagreement remains inspectable rather than collapsed?
7. Is authority adequately represented by repository ownership, or does each
   claim transition require an explicit decision-right assertion?
8. Which correction and supersession semantics preserve both current authority
   and the historical reproducibility of withdrawn conclusions?
9. What constitutes equivalence between two implementations of the same
   transition responsibility: identical bytes, identical claim state, identical
   evidence basis, or observationally equivalent justification?
10. At what point does vocabulary alignment become an interpretive transition
    that requires its own evidence and authority, rather than a neutral mapping?
11. Can a cohort conclusion remain comparable across investigations when cohort
    construction rules differ, even if record schemas match?
12. What is the smallest durable artifact a consumer needs to independently
    assess a proposal without importing producer authority?

## Conceptual conclusion

The current lifecycle is not fundamental as a sequence of repositories,
directories, acronyms, or file formats. It is one implementation of a more
general responsibility: controlled movement of bounded claims through evidence,
rules, and independent authority domains.

The next architectural layer is therefore not another pipeline stage. It is the
explicit model of **evidence-bounded claim transitions** that the existing stages
already instantiate. The central invariant is:

```text
No claim-state change without a resolvable basis, a declared transition rule,
preserved uncertainty and scope, and an identified authority for the decision.
```
