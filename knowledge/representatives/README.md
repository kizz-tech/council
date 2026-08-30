# Representative Lens Library

## Purpose and boundary

This document defines a source-bound library for composing Council lenses when
a consequential question needs more than one genuinely countervailing
analysis. It is a methodology for preserving attribution, source fidelity, and
meaningful disagreement. It is not a directory of authorities, a simulation of
real people, a voting mechanism, or a claim that a larger roster is better.

The canonical chain is:

```text
source work
  → atomic position
  → representation unit
  → roster slot
  → run manifest
  → evaluated output
```

Each arrow is a distinct relationship. Skipping an arrow turns a name, a
prompt, or a model label into unsupported authority.

Names are provenance anchors: they help a reader locate a work, a version, and
an attributable position. A name is never authority by itself and never a
license to impersonate a person. A run must not ask a model to write in a
person's voice, use first-person claims on their behalf, invent quotations, or
infer private motives, traits, or current beliefs. Where exact words matter,
quote the source with an exact locator; otherwise use an attributed paraphrase.

This boundary also aligns with OpenAI's policy against impersonating people or
organizations without consent or legal right. That policy is product-specific;
the broader method requirement here is source fidelity and transparent
attribution, not a claim that every use of a name is unsafe.

## Concepts and types

The library deliberately distinguishes five representation types.

| Type | What it represents | Appropriate use | What it must not claim |
| --- | --- | --- | --- |
| `person` | A bounded set of positions attributable to one person in named works and a stated time window | A historically consequential or otherwise uniquely attributable position is decision-relevant | That the agent is the person, knows their unrecorded views, or represents every view they have held |
| `joint_authors` | A bounded set of positions attributable to named coauthors in jointly authored works | The jointly expressed position is decision-relevant and cannot be safely split into individual views | That each coauthor separately holds every joint position or that the runtime may simulate any author |
| `school` | A family of related methods, concepts, or arguments with documented variants | The shared intellectual structure matters more than one author | That the school is homogeneous or that one member speaks for all others |
| `functional_lens` | A constructed task function, such as evidence auditor, safety red-team, systems/operations analyst, or affected-party impact analyst | The decision needs a function rather than historical attribution | That it is a person's belief or that a role label creates independent evidence |
| `source_corpus` | A bounded, versioned set of works without a claim to personhood or school membership | Direct evidence is sufficient or a person/school cannot meet the admission gate | That a collection of texts has a unified worldview |

`source_corpus` is the safe fallback for a useful single work, uncertain
attribution, or evidence that cannot support a person-level representation.

## Orthogonal axes

Use the following axes independently. None is a proxy for another.

| Axis | Meaning | Examples |
| --- | --- | --- |
| Decision function | What contribution the slot is intended to make | framing, causal analysis, empirical audit, option generation, implementation risk, values/trade-off, red-team |
| Claim mode | What kind of proposition is being represented | empirical, theoretical, normative, design/operational, experiential |
| Position structure | The decision-relevant content | proposition, assumptions, mechanism, method, recommendation, expected discriminator |
| Scope | Boundary conditions | domain, population, geography, time, stakes, uncertainty, affected parties |
| Intellectual lineage | Dependence among ideas and sources | shared source roots, school, citation path, coauthorship, institution, funding, known internal dissent |
| Source fidelity | Whether attribution is supportable | primary/authorized source coverage, locator quality, version status, unresolved conflict |
| Counterweight | How a position can be tested or limited | competing mechanism, empirical exception, value conflict, scope condition, implementation failure path |
| Runtime configuration | What actually happened in an experiment | source pack, prompt, model/version, seed, context visibility, topology, evaluator |
| Observed output diversity | What was measured after the run | unique supported claims, source-root overlap, semantic overlap, dissent retained, error profile |

Identity, popularity, citations, institutional status, or model agreement are
not diversity axes. They may be recorded as narrowly relevant provenance or
conflict information, but they are not evidence weights.

## Admission and retyping gate

Admit a `person` only when all of the following are true:

1. The candidate has **two or more primary or authorized works** with stable
   locators and a meaningful relationship to the decision question.
2. The record contains **at least three locator-bound atomic positions**:
   a central proposition, a mechanism or decision rule, and a scope condition,
   revision, or limitation. Each position must identify its exact source work
   and passage, section, page, timestamp, or immutable revision.
3. At least one counterweight is recorded: a distinct-lineage challenge,
   empirical exception, self-stated caveat, or a documented gap explaining why
   a credible counterweight could not be located.
4. The candidate adds a decision-relevant claim, method, scope condition, or
   source lineage not already represented.
5. The time window and scope of the attributed positions are explicit.

Admit a `school` only with canonical source work, a lineage/variant map, and a
recorded internal or external challenge. Admit a `functional_lens` only with a
clear role, task boundary, and source-backed method or evaluation standard.
Admit `source_corpus` whenever the source is useful but the stronger
attribution conditions are not met.

Admission status determines roster eligibility. `admitted` units may be bound
by a `library_bound` or `hybrid` slot. A `qualified_counterweight` is retained
for bounded challenge and source-pack use but is counterweight-only: it must
not occur in `representation_ids`. A `source_corpus` may be bound as a corpus,
never promoted by that binding to a person, school, or unified worldview. A
roster cannot override this gate; eligibility changes only through a reviewed
representation revision.

Exclude or retype a candidate when direct evidence is absent, the contribution
is only prestige, the proposed view is a slogan rather than a position, the
candidate duplicates an existing lineage without adding a material difference,
or representation would require invented speech or private inference. Preserve
an exclusion reason. Multiple reports, biographies, interviews, and derivative
commentary about the same underlying work do not count as independent support.

There is no global prestige score or composite “representativeness” score.
Selection is a coverage and falsifiability decision, recorded in the roster
manifest.

## Semantic model and the 0.2.0-alpha.2 projection

The normative machine contract for this release is the standard-library-only
repository validator in `tools/council_dist.py`. The JSON Schemas under
`schemas/` are reviewable documentary projections of its record shapes; this
release does not claim that a Draft 2020-12 engine executes them. The validator
enforces the represented field constraints plus cross-record checks such as
global ID uniqueness, manifest-declared family membership, source-reference
integrity, admission-aware roster bindings, index hashes, and release cutoff.
Negative tests guard constraints that have previously drifted. The versioned
`knowledge/representatives/library.json` is the single release declaration for
the library version, research cutoff, and family set; changing any of those is
a reviewed library-contract revision. Each family record materializes a
deliberately compact projection:

- `primary_sources`: the schema's historical field name for admitted evidence
  bindings—exactly two for non-corpus units in v0.2 and one or more for a
  `source_corpus`—each with `id`, `title`, integer `year`, HTTPS `locator`,
  and exact `evidence_locator`. A binding may support the attributed position
  or bound it with direct empirical evidence; it is not automatically a work by
  the named person and never counts as an independent lineage merely because
  the URL differs;
- `positions`: neutral `statement`, one or more local `source_ids`, and
  `scope`;
- `representations`: identity/type/status, lens, decision functions, lineage
  IDs, the type-appropriate source bindings, exactly three positions and questions,
  counterweights, misuse risks, evidence boundary, and confidence.

The richer fields below are the semantic design target for future source
registries, roster manifests, and evaluated outputs. They are not claimed to be
present or validated in every 0.2.0-alpha.2 family file. Promoting one requires a new
schema version, migration, tests, and an ADR; documentation alone cannot add a
machine-enforced guarantee.

The 0.2.0-alpha.2 index therefore reports both the number of bindings and the number of
unique locators. The current projection contains 138 bindings over 134 unique
HTTPS locators; neither number is a count of independent works or independent
views.

### Future `source_work`

| Field | Semantics |
| --- | --- |
| `source_id` | Stable internal identifier for one work/version, not for an author or a URL collection |
| `canonical_locator` | DOI, canonical URL, standard identifier, or immutable repository revision; no tracking, credentials, or private paths |
| `title`, `author_or_owner`, `published_at`, `revised_at`, `accessed_at` | Bibliographic/version facts, not quality ratings |
| `source_class` | For example: primary research, official documentation, official implementation, institutional report, recognized-expert primary, secondary analysis |
| `authority_scope` | Predicate-specific authority, such as empirical, documented feature, normative, implementation, interpretive, or experiential |
| `evidence_locator` | Exact page, section, paragraph, timestamp, table, figure, or commit where a claim is supported |
| `atomic_extract` | Short accurate paraphrase or permitted exact quotation; never a generated imitation |
| `source_root_id` | Earliest known material source root for dependence analysis; link revisions rather than collapsing them |
| `limitations` | Scope, population, version, conflict, access, or freshness limits |

### Future `atomic_position`

| Field | Semantics |
| --- | --- |
| `position_id` | Stable identifier for one testable proposition, not an entire worldview |
| `question_ids` | The exact questions for which the position is admissible |
| `claim_mode` | `direct_assertion`, `constrained_reconstruction`, or `run_inference`; these must never be merged |
| `proposition` | Neutral attributed paraphrase of the claim |
| `assumptions`, `mechanism`, `method`, `decision_implication` | The content needed to test or apply the position |
| `scope` | Time, domain, affected parties, conditions, and exclusions |
| `evidence_ids` | One or more `source_work` IDs with precise locators |
| `discriminator` | Evidence, observation, or decision consequence that would distinguish this position from a counterweight |
| `known_limits` | Uncertainty, revision, contested interpretation, or non-applicability |

### Future full `representation_unit`

| Field | Semantics |
| --- | --- |
| `representation_id`, `type`, `label` | Stable identity and one of the five types above |
| `attributed_name` | Optional provenance label only; no runtime persona instruction is derived from it |
| `position_ids`, `source_ids`, `lineage_ids` | Explicit evidence and dependence bindings |
| `functional_role` | The contribution expected in a council run, bounded to the decision function |
| `selection_reason` | The uncovered axis, counterweight, or source lineage this unit adds |
| `counterweight_ids` | Competing unit or position IDs plus relation: contradicts, limits scope, offers a competing value, or exposes a failure mode |
| `fidelity_status` | `pass`, `partial`, `retype_required`, or `retired`; never a prestige judgment |
| `does_not_speak_for` | Persons, groups, periods, or claims that must not be inferred from this unit |
| `last_verified`, `known_limits` | Freshness and unresolved limitations |

### Future full `roster_slot`

| Field | Semantics |
| --- | --- |
| `slot_id` | Identifies one contribution in one manifest, not a permanent authority position |
| `representation_id` | Exact unit/version used |
| `decision_function` | The task contribution expected from this slot |
| `coverage_axes` | The claimed material differences that justify inclusion |
| `counterweight_slots` | Required challenges or scope checks for the slot |
| `lineage_cluster` | Dependency grouping used to prevent duplicate counting |
| `source_pack_id` | The bounded evidence visible to the slot |
| `runtime_independence_vector` | Actual separation from other slots; see below |
| `stop_condition` | When the slot has done enough work or must escalate uncertainty |

### Future `run_manifest`

A run manifest makes a bounded experiment reproducible:

`manifest_id, revision, cutoff, question_set, decision_stakes, candidate_pool,
inclusion_exclusion_log, slots, axis_coverage_map, lineage_map, source_pack
versions, prompt versions, tool policy, model IDs/versions, model tier and
family, sampling settings/seeds, context-sharing policy, topology, rounds,
budget caps, evaluator/rubric, human-audit owner, output retention policy, and
stop contract`.

The manifest must record actual model IDs and versions rather than treating a
label such as “frontier” as reproducibility evidence. It must retain structured
provenance and evaluation artifacts, not raw private reasoning traces.

### Future `evaluated_output`

An evaluated output carries:

`manifest_id, output_id, supported_positions, source_entailment_audit,
counterarguments_retained, unsupported_claims, task-specific score, calibration
where applicable, unique-claim and source-root coverage, cost, latency,
evaluator_identity, evaluation_date, limitations, and stop_decision`.

Do not collapse these into one score. Accuracy, source fidelity, diversity,
calibration, cost, and usefulness answer different questions.

## Three kinds of independence

The word “independent” must be qualified.

1. **Lineage independence** asks whether positions descend from distinct
   intellectual roots. Shared citations, source corpora, coauthorship,
   institutional affiliation, funding, or a common canonical text can make
   views dependent even when the names differ.
2. **Runtime independence** asks whether the experiment separated source packs,
   prompts, model family/version, sampling, conversation history, peer
   visibility, and evaluator. Different agent labels alone do not establish it.
3. **Outcome independence** is observed after the run: do outputs add distinct
   source-supported claims or simply repeat, converge on, or inherit the same
   error?

Record runtime independence as a vector, for example:

```text
{source_pack: separate, prompt: separate, model_family: shared,
 seed: separate, history: sequestered, peer_visibility: none,
 evaluator: blinded}
```

Never infer one kind of independence from another.

## Bounded experiments over an unbounded hypothesis space

The possible space of questions, sources, rosters, prompts, models, topologies,
and evaluation criteria is unbounded. A Council experiment is not. Every run
must freeze a small, reproducible hypothesis such as:

> For this question stratum and fixed total budget, does a lineage-balanced,
> source-bound roster retain more independently supported counterarguments than
> an equal-budget single-agent baseline?

Useful factors include roster size (`1`, `2`, `4`, `6`, `8`, `16`), unit type,
grouping, model tier and family, the runtime-independence vector, topology,
rounds, and total budget. Do not run their full cross-product. Use staged,
budget-matched screening:

1. Establish an independent, no-communication baseline at sizes `1`, `2`, and
   `4`.
2. Screen one or two factors at a time using a fractional design and a frozen
   rubric.
3. Test `6`, then `8` and `16`, only if the prior size meets a predeclared
   practically meaningful improvement threshold without a fidelity regression.
4. Compare every debate topology to an equal-budget no-communication or
   self-consistency baseline.

Use controlled exposure: generate initial positions independently, then allow a
bounded critique or synthesis phase. This adapts the separation and controlled
feedback ideas of Delphi; it does not claim that LLM debate has the validity of
a human Delphi panel.

Required negative controls include:

- same model, prompt, and source pack under differently named “experts”;
- name-masked source cards that preserve true attribution but remove prestige
  cues;
- same-lineage rosters versus lineage-balanced rosters;
- generic functional prompts versus the same functions with the source pack;
- no-communication versus matched-budget debate;
- shuffled slot order and peer-visibility order; and
- evaluator blinding to experimental condition where feasible.

Do not fabricate a source-to-name swap as a control: it creates false
attribution rather than measuring it.

## Stopping, pruning, and updates

Prune or merge a representation unit when it adds no unique position, scope
condition, decision function, counterweight, or source root. Retire or retype
it when its direct-source gate no longer passes after a revision or correction.
Keep the exclusion/retyping reason and preserve historical versions for
provenance.

Stop source expansion when two consecutive search batches add no material claim
class or independent lineage, primary-source gaps have been recorded, and the
required axes are covered. Stop roster-size escalation when the next two sizes
fail the run’s predeclared practically meaningful improvement threshold, when
negative controls match the treatment, when independent-claim coverage declines
as cost rises, or when the audit/budget/latency cap is reached.

Update the library through a revisioned process:

1. State the observed failure, decision, or experimental question.
2. Add or revise source work with exact locators and date/version provenance.
3. Re-audit affected atomic positions, counterweights, lineage links, and
   `does_not_speak_for` constraints.
4. Freeze the changed units and manifest before held-out evaluation.
5. Record the evaluation result, limitation, and either adoption, retyping,
   retirement, or an explicit unresolved gap.

No update may silently change a representation unit's attributed meaning.
There is no claim of a globally optimal roster, topology, model tier, or agent
count. Local evidence can only support the bounded configuration, question
stratum, budget, and evaluation criteria it actually tested.

## Limitations

- This library improves traceability and falsifiability; it cannot prove that a
  source is true, complete, current, or representative of a population.
- A named source cannot substitute for living stakeholders, primary research,
  an actual expert elicitation, or a decision owner.
- Consensus, votes, fluent argument, and repeated citations remain weak
  evidence unless independently audited.
- Human elicitation and forecasting methods are informative analogies, not
  validation of LLM personas or multi-agent debate.
- Published debate results are mixed and benchmark- and configuration-specific;
  improvements must be demonstrated locally against strong matched-budget
  baselines.

## Source basis

The method uses these sources for narrow, stated purposes. Their use does not
make the resulting library empirically validated.

- [NRC NUREG-2255, “Guidance for Conducting Expert Elicitation in
  Risk-Informed Decisionmaking Activities”](https://www.nrc.gov/reading-rm/doc-collections/nuregs/staff/sr2255/index)
  — transparent representation of the center, body, and range of technical
  views in its risk-decision context.
- [EPA Expert Elicitation Task Force White Paper, chapters
  5–7](https://19january2021snapshot.epa.gov/sites/static/files/2013-09/documents/ee-white-paper-final.pdf)
  — selection, roles, documentation, aggregation, and limits. The document
  itself says it is not EPA policy.
- [Cochrane Handbook, chapter 4, sections 4.6.1 and
  4.6.5](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-04)
  — distinguish underlying studies from reports and preserve explicit
  exclusion reasons; adapted here for source-lineage tracking.
- [RAND, *Methodological Guidance for Conducting and Critically Appraising
  Delphi Panels*, chapter 2 and appendix
  A](https://www.rand.org/content/dam/rand/pubs/tools/TLA3000/TLA3082-1/RAND_TLA3082-1.pdf)
  — anonymity, iteration, controlled feedback, and reporting concerns in human
  panels; used only as an analogy for controlled exposure.
- [Hong and Page (2004), “Groups of diverse problem solvers can outperform
  groups of high-ability problem
  solvers”](https://doi.org/10.1073/pnas.0403723101) — a formal result under
  stated conditions; not a general claim about LLM or demographic diversity.
- [Mellers et al. (2015), “The Psychology of Intelligence Analysis”](https://faculty.wharton.upenn.edu/wp-content/uploads/2015/07/2015---the-psychology-of-intelligence-analysis.pdf)
  — human forecasting-tournament evidence; not validation of named source
  representatives as forecasters.
- [OpenAI prompting guidance, Rules of Thumb](https://help.openai.com/en/articles/6654000-how-can-i-write-better-prompts-for-generative-models),
  [OpenAI multi-agent guide, “Multi-agent
  systems”](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/),
  and [Anthropic, “Building effective agents”](https://www.anthropic.com/engineering/building-effective-agents)
  — implementation guidance for structured prompts, orchestration, and
  complexity discipline; not causal proof of superiority.
- [Du et al. (2024)](https://proceedings.mlr.press/v235/du24e.html) and
  [Smit et al. (2024)](https://proceedings.mlr.press/v235/smit24a.html) —
  conflicting multi-agent debate findings that justify matched-budget local
  evaluation rather than a presumption of benefit.
- [Taubenfeld et al. (2024)](https://aclanthology.org/2024.emnlp-main.16/)
  — evidence that persona debate simulations can track base-model social bias,
  motivating source-bound positions rather than simulated people.
- [OpenAI agent policy, section 1](https://openai.com/policies/using-chatgpt-agent-in-line-with-our-policies/)
  — platform-specific prohibition on impersonation without consent or legal
  right.
