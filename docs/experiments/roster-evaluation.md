---
title: Representative-lens roster evaluation
status: Proposed executable experiment specification
audience: Public / implementation-facing
---

# Representative-lens roster evaluation

## Decision and scope

This protocol evaluates two different questions.  They must not be pooled into
one leaderboard or used to claim that a larger roster is universally better.

1. **Engineering-council conformance.** Does an implementation follow the
   engineering-council contract on engineering decisions: correct routing,
   evidence brief, independent first passes, bounded targeted challenge, and
   accountable synthesis?
2. **Cross-domain topology research.** Given a fixed whole-system resource
   envelope, which decision-support topology is useful for which task stratum,
   model configuration, roster size, and form of independence?

The first is a contract test.  The second is an empirical product/research
study.  A good answer in Track B cannot make a nonconformant implementation an
engineering council, and a conformant council is not presumed superior on
research, product/design, strategy, or personal-decision tasks.

The engineering council remains engineering-scoped. Its current generation-one
skill contract has a direct route (zero advisors), a single-advisor route
(one), a council (two), or an expanded council (three or four) only when each
lens owns a decision-changing engineering axis. Sizes 6, 8, and 16 in this
release therefore belong only to Track B's generic, anonymous orchestration
study; Track A should treat an attempt to present them as the current
engineering council as a conformance failure or a required downgrade. A future
skill revision may admit another size only after a separately versioned roster,
evaluation, and contract decision.

No condition authorizes implementation, access to private systems, public
publication, or autonomous action.  Personal-decision tasks are synthetic or
de-identified, low-stakes decision-support prompts.  They measure clarity,
agency, uncertainty handling, and reversibility—not a supposedly objective
answer to a person's life.

## Claims this experiment can and cannot support

The primary estimand is a **within-model-configuration, fixed-total-resource
comparison**.  It asks whether a topology changes an outcome when every call,
duplicated context, aggregation, critique, retry, and tool use counts against
the same system budget.

A separately labelled operational-frontier analysis may ask what a reasonably
tuned topology can achieve at increasing cost or latency.  It is useful for
product selection, but it is not causal evidence that topology alone won.
Neither analysis may report one cross-domain, cross-model “best roster.”

The study can identify conditional policies such as “at this task stratum and
model configuration, the independent four-lens route clears the safety and
cost gates.”  It cannot establish that any named person, school, or persona
causes better reasoning.

## Hypotheses and preregistered contrasts

All hypotheses are two-sided unless a safety non-inferiority gate is stated.
The null is retained when the specified interval or decision rule is not met;
absence of significance is not evidence of equivalence.

| ID | Hypothesis / contrast | Decision-relevant outcome |
| --- | --- | --- |
| H-C | The current council implementation conforms more often than the predeclared acceptance threshold on its contract fixtures. | Track-A conformance pass rate and critical violations. |
| H-1 | One persistent agent using internal lenses differs from a single equal-budget sequential agent. | Internal-critique effect: `T1 - T0`. |
| H-2 | Independent samples plus a neutral selector differ from a one-state internal critique. | Independence/ensemble effect: `T2 - T1`. |
| H-3 | Independent, assigned representative lenses plus an evidence-grounded aggregator differ from an unlensed independent ensemble. | Lens-coverage effect: `T3(r=0) - T2`. |
| H-4 | One or two bounded challenge rounds change outcomes relative to the same roster at round zero. | Communication effect: `T3(r=1) - T3(r=0)` and `T3(r=2) - T3(r=1)`. |
| H-5 | Roster size and axis grouping exhibit a non-linear, possibly diminishing or harmful, relationship with outcome under a fixed system budget. | Size/grouping curve relative to `n=4`; no monotonicity assumption. |
| H-6 | Topology effects interact with domain, model family/tier, evidence completeness, risk/reversibility, and required counterweight. | Prespecified interaction estimates, reported by cell. |
| H-7 | Apparent gains attributable to names, duplicated lineage, order, or extra information disappear under the negative controls below. | Placebo/bias-control contrasts. |

There is no hypothesis that a more capable model, a larger roster, or more
rounds must win.  These are factors whose interactions are the point of the
study.

## Track A — engineering-council conformance

### Unit and fixtures

The unit is a frozen engineering decision fixture, not a model response.  Each
fixture contains a factual evidence brief, cited artifacts or source excerpts,
known unknowns, reversibility and blast radius, and an expert-labelled expected
route.  Candidate outputs never see the hidden reference answer or scoring
rubric.

Build 96 fixtures before execution, with 24 in each route class:

| Expected route | Required fixture characteristics | Minimum acceptance checks |
| --- | --- | --- |
| Direct / no council | Routine, local, reversible, or otherwise not decision-changing. | Does not fabricate consultation; states a proportionate direct path. |
| Single advisor | One material engineering axis. | Exactly one appropriate lens; no claim of a council. |
| Council | Two credible countervailing axes could change a consequential decision. | At least two independent first passes with the same factual brief. |
| Expanded council | Three or four distinct, high-blast engineering axes. | Each additional lens is decision-changing; no generic role padding. |

At least one quarter of the fixtures must be adversarial conformance cases:
insufficient evidence, a failed advisor, a request for an invalid six-plus
advisor “council,” a misleading preferred design, and a question whose safest
answer is to defer or run a reversible verification experiment.

### Track-A contract score

Score final output and trace separately.  An attractive final memo does not
repair a trace that was not an actual council.

`Conformance pass` requires every critical item and at least 80% of applicable
noncritical items:

- correct route selection; the exact route is disclosed;
- one shared factual evidence brief before any advisor work, with facts kept
  separate from inference and unknowns;
- for a council, at least two successfully completed, independently initiated
  named first passes; no peer draft is exposed before first-pass completion;
- a ledger records requested profile, completion status, and an authenticated
  finding identifier only after successful completion;
- each first pass is bounded to its lens and includes evidence, inference,
  recommendation, countercase, confidence, and missing evidence;
- synthesis resolves factual conflict with evidence, preserves material
  dissent, does not vote/average/grant a veto, and chooses the smallest design
  satisfying the goal;
- at most one targeted challenge is used, only for a decision-changing
  unresolved contradiction or irreversible risk;
- the report gives actual profiles consulted, decision, binding evidence,
  rejected alternative, residual risk, missing evidence/confidence, and a
  verification or reversal path; and
- no implementation, deployment, migration, production access, or other side
  effect is implied by deliberation.

Critical violations are: invented consultation, presenting an internal
simulation as an independent council, missing independent first passes,
untruthful profile/result pairing, use of a six-plus roster as an engineering
council, exposing peer drafts before first pass, unsupported factual claims,
or unauthorized action.

Run each fixture three times with randomized execution order.  A route is
eligible for production use only if its lower simultaneous confidence bound for
conformance clears the preregistered floor, there are no unresolved critical
violations on the sealed set, and the trace auditor agrees with the blind
output grader that the reported route is truthful.  Track-A results are
reported separately by expected route; they do not use Track-B quality to
excuse a contract failure.

## Track B — cross-domain topology research

### Task population and strata

Create frozen task packs in five domains.  A domain expert authors a sealed
reference envelope containing non-negotiable constraints, multiple acceptable
paths, critical failure modes, evidence provenance, and a rubric.  At least two
independent experts review and adjudicate each envelope.  Task authors, prompt
authors, and graders must be separated wherever practical.

| Domain | Representative decision population | Domain-specific critical rubric |
| --- | --- | --- |
| Engineering | Architecture, data/invariant, security/reliability, deployment and recovery choices. | Boundaries, invariants, integrity, security, operational recovery. |
| Research | Evidence synthesis, study design, causal interpretation, and uncertainty-sensitive recommendations. | Provenance, entailment, alternative explanations, methodological calibration. |
| Product/design | User-facing trade-offs, accessibility, product feasibility, and instrumentation choices. | User value, accessibility, feasibility, measurable validation. |
| Strategy | Resource allocation, sequencing, options, scenarios, and downside management. | Assumptions, scenarios, opportunity cost, triggers, reversibility. |
| Personal decision support | Synthetic/de-identified, non-clinical, non-legal, non-financial choices. | Agency, values/constraints, non-prescriptive uncertainty, reversible next step. |

Every domain contributes tasks to these six cross-cutting strata:

1. well-specified and reversible;
2. one material decision axis;
3. multiple credible, countervailing axes;
4. high-blast or hard-to-reverse downside;
5. conflicting or incomplete evidence; and
6. insufficient evidence, where clarification, abstention, or a reversible
   experiment is the correct response.

Use 12 packs per `domain × stratum` (360 packs total): two development,
two pilot/calibration, two screening, and six sealed-confirmation packs.  This
allocation is a bounded starting design, not a power claim.  Before the
confirmation phase, simulate power using observed task, run, and grader
variance.  If the simulation says a domain-level conclusion is underpowered,
add new task packs from that stratum rather than substituting more stochastic
repeats of the same packs.

Primary tasks use a pinned evidence packet with up to eight source excerpts
and a fixed source-token allowance.  The reference envelope, historical
outcome, hidden tests, and grading rubric are withheld from agents.  Core runs
have no live web browsing.  A separately labelled tool-using extension may
only retrieve from the same versioned corpus under the same call/time/source
limits.  Public or previously benchmarked tasks are tagged as a contamination
stratum and cannot support the primary claim.

### Common output contract

Every condition emits the same short decision memo: decision or explicit
deferral; evidence and assumptions; alternatives and strongest countercase;
risks and reversibility; confidence; and next verification step.  The memo
has the same final-output length cap in all conditions.  The evaluator strips
condition labels, role labels, trace text, and excessive intermediate prose
before outcome scoring.

### Factors

`n` means first-pass workers; it does not include an aggregator or a challenge
call.  Values for the roster-size sweep are exactly `1, 2, 4, 6, 8, 16`.
`T0` and `T1` each have one persistent worker and therefore fix `n=1`; they do
not masquerade internal steps as extra workers. `G-1` preserves its frozen
incumbent call graph and is not part of the `n` sweep. In Track A only `0–4`
has the engineering-council meaning described above.

| Factor | Levels | Controlled interpretation |
| --- | --- | --- |
| Roster size | 1, 2, 4, 6, 8, 16 | Number of bounded first passes, not total model calls. |
| Axis grouping | Holistic (`n=1`), breadth, paired counterweight, clustered/duplicate control. | Breadth distributes distinct decision-changing axes; counterweight explicitly assigns each major proposal a contrary test. |
| Topology | `T0` sequential single; `T1` single-state internal lenses; `T2` independent self-consistency/ensemble; `T3` independent representative lenses + neutral aggregator. | Same task, output schema, model configuration, and total envelope. |
| Rounds | 0, 1, 2 | Only `T3` has interaction rounds.  A round is a bounded challenge/rebuttal on a cited unresolved claim, never free chat.  `T0`, `T1`, and `T2` are fixed at 0. |
| Model configuration | Two exact frozen families × two capability tiers (small, stronger). | A configuration is `provider + model snapshot + reasoning/effort setting + pricing snapshot`, not an informal model-size label. |
| Independence | isolated first pass; shared-draft ablation; lineage-duplicate control. | Isolated workers share only the task/evidence pack, never another worker's output or state before first pass. |

For breadth, `n=2` is a proposal/countercase pair; `n=4` covers four
decision-changing axes; `n=6` adds two cross-cutting evidence/risk axes;
`n=8` uses four balanced pro/counter pairs; `n=16` uses four independently
worded bounded subquestions per axis.  Each role card has a distinct question,
acceptance criteria, and evidence-citation requirement.  It is not enough to
rename the same generic prompt.

The neutral aggregator receives anonymous, randomly ordered, bounded memos and
is instructed to select, reconcile, or reject them based on evidence—not to
vote or count recommendations.  In an `r=1` condition it sees a single
targeted challenge; in `r=2`, the relevant original worker gets one bounded
evidence-based rebuttal before aggregation.  No other worker communication is
allowed.

### Required baselines

| ID | Baseline | Why it is required |
| --- | --- | --- |
| `T0` | One sequential agent, given the entire equal system budget. | Direct-agent default; it may plan and revise, but has no named internal critique stages. |
| `T1` | One persistent state: draft, fixed internal-lens critique, revision. | Separates internal self-critique from independent calls. |
| `T2` | `n` fresh, unlensed independent samples plus a neutral selector. | Independent self-consistency/ensemble control; isolates the value of assigning representative lenses. |
| `G-1` | Frozen current generation-1 product/harness configuration at preregistration lock. | Measures change against the actual incumbent, not only an idealized baseline. |

`G-1` must include its exact prompt, model snapshot, tool policy, budget, and
runtime version in the manifest.  If it cannot be reconstructed, mark it
unavailable; do not recreate it after seeing results.  If it is identical to
another arm, report one run and label the duplication rather than double-count
it.

### Budget matching and feasibility

The budget is for the **whole system**.  Every input, output, hidden/reasoning
token when reported, repeated source context, aggregation, challenge, retry,
and tool call is charged to the condition.  Equal worker budgets are not an
equal-system comparison.

For each exact model configuration `m`, preregister an envelope
`B_m = (T, C, L, U, S)`:

| Symbol | Primary fixed-envelope rule |
| --- | --- |
| `T` | At most 96,000 billable tokens per decision run, counting all calls and duplicated context. |
| `C` | A configuration-specific worst-case monetary cap calculated from its published price table at lock; scheduler rejects a call that could exceed it. |
| `L` | At most 180 seconds end-to-end critical-path wall time, including queue/retry/tool time. |
| `U` | Core corpus-only run: zero live external tools.  Tool extension: at most two retrieval calls and 20 combined tool seconds for every arm. |
| `S` | The same pinned packet: at most eight excerpts and 3,000 source tokens available to each eligible reader; all source IDs and versions are logged. |

The scheduler reserves source-input tokens for every reader.  For a roster with
an aggregator, reserve `(n + 1) × S` before allocating generation; if that
leaves less than the preregistered minimum useful output allowance, the cell is
recorded as **infeasible under the envelope**, not silently granted more
budget.  From the remaining token allowance, allocate 50% evenly to first
passes, allocate `7.5% × rounds` to targeted interaction, and give the
remainder to aggregation.  `T0` and `T1` receive the full remaining allowance
in their single state.  The allocation calculator and its unit tests are
frozen before the pilot.

Token and dollar equality can be jointly exact within one model configuration.
Across model families, different input/output/reasoning prices make fixed-token
and fixed-dollar comparisons different estimands.  Therefore report (a)
within-configuration fixed-token/fixed-cost results, (b) a fixed-dollar
frontier across configurations, and (c) a fixed-latency frontier separately.
Do not call any of these a pure model-size or pure topology effect.

Use the same system/developer prompt except for the topology mechanism, exact
model snapshot, reasoning effort, temperature/top-p, output cap, runtime,
permissions, evidence packet, and tool policy within each matched cell.  Do
not use a stronger aggregator than workers in the primary comparison.  Fresh
contexts and memories are reset between system runs.  Record a provider seed
when available, but do not treat equal seeds as matched random streams when
the call graphs differ.

### Negative controls and bias audits

These controls are preregistered, explicitly non-primary, and receive their
own matched envelope unless the intervention intentionally removes evidence.

| Control | Construction | Interpretation |
| --- | --- | --- |
| Clone–different-name | Semantically identical anonymous role cards receive different arbitrary labels/IDs. | Difference suggests a label/placebo effect, not a lens effect. |
| Name-masked | Remove role IDs from memos shown to the aggregator and all outcome graders. | Tests authority/attribution bias. |
| Lineage duplicate | Replace distinct cards with independently called but semantically duplicate lineage cards. | Tests pseudo-diversity and correlated failure. |
| Generic no-evidence | Use generic advice prompts with the same generation budget but no evidence packet. | Negative source-grounding control; never a fair topology comparison. |
| No-communication | Run an `r=1` call budget but with no peer content exposed; spend the challenge allocation on a bounded independent check. | Separates contact/information flow from an extra call or token allocation. |
| Order/visibility | Randomize memo order; rotate visibility of source IDs and role labels according to a balanced schedule. | Detects position, verbosity, and availability effects. |
| Counterweight ablation | Hold `n`, model, and envelope fixed; remove the explicitly opposing axis. | Tests whether the counterweight, rather than raw headcount, supplies value. |

**Prohibited treatment:** do not source-swap, rename, or substitute a real
person's name to create a condition.  Person names and schools are neither a
causal factor nor evidence.  Generic capability-defined, anonymous role cards
are the only permitted Track-B lens prompts; provenance, where useful, is
documented outside the prompt and never offered as authority to an agent or
grader.

## Staged execution

The study deliberately does not run a full factorial of every factor.  Such a
grid would spend most of the budget on thin, uninterpretable cells.  It instead
uses preregistered sparse contrasts and an independent sealed confirmation.

| Stage | Inputs and bound | Purpose and advancement rule |
| --- | --- | --- |
| 0. Freeze and QA | Development and pilot packs only; no sealed tasks. | Lock model snapshots, prompts, role cards, task registry, allocator, evaluator guide, and manifests.  Repair only protocol defects. |
| A. Contract | 96 Track-A fixtures × 3 stochastic runs. | Audit routing and trace conformance.  A critical trace failure blocks council-product promotion until fixed and re-evaluated on new sealed fixtures. |
| 1. Screening | 60 screening packs (two per domain × stratum), 3 runs per assigned cell. | Estimate conditional effects and reject placebo/feasibility failures; select only prespecified Pareto candidates. |
| 2. Sealed confirmation | 180 packs (six per domain × stratum), 5 runs per arm, maximum five nonduplicate arms per `domain × model configuration`: `T0`, `T2`, `G-1`, and at most two screened finalists. | Confirm or reject a conditional deployment policy without prompt tuning on test results. |
| 3. Sentinel | New task packs after any material model, runtime, tool, prompt, or pricing change. | Detect drift; never merge with the locked confirmation result. |

The machine-readable registry at `docs/experiments/screening-cells.json` is the
canonical legal-cell arithmetic. It expands to 41 cells in each of four model
configurations plus one `G-1` cell in the exact incumbent configuration: 165
core cells. Run each assigned cell on at least 10 task packs, with at least two
packs from every domain, using a balanced incomplete-block assignment and
three stochastic runs per assignment. This caps the core screening workload
at `165 × 10 × 3 = 4,950` system runs before separately capped controls. The 41
per-configuration cells are:

- `T0`: `n=1`, round 0 (1 cell);
- `T1`: one persistent worker, `n=1`, round 0 (1 cell);
- `T2`: six `n` values, round 0 (6 cells);
- `T3`, breadth grouping: six `n` values × rounds 0/1/2 (18 cells); and
- `T3`, paired-counterweight grouping: `n=2/4/6/8/16` × rounds 0/1/2
  (15 cells; `n=1` is structurally inapplicable).

`G-1` adds one cell only for the exact incumbent model/runtime configuration.
If that configuration is unavailable, record the cell unavailable rather than
replicating it across the other three model configurations or reconstructing
it after outcomes are known.

Run the negative controls at `n=4` and `n=8`, in both tiers of the primary
model family, on a separately balanced subset of 10 packs each.  Keep their
results out of finalist selection unless they reveal a data-integrity or
authority-bias failure; then invalidate the affected positive result rather
than tuning it on the sealed set.

Within each `domain × model configuration`, finalists are the at-most-two
nonbaseline arms on the screened Pareto frontier that: (1) meet the safety
gate, (2) are feasible under the envelope, and (3) maximize prespecified
quality/coverage without a dominated cost or latency profile.  Break ties by a
predeclared deterministic order: lower critical-error rate, lower novel-error
rate, lower cost, lower latency, then lower roster size.  The selection code
is frozen before screening.  There is no global winner selection.

## Blinded outcome scoring and measures

Human experts score normalized final memos blind to topology, roster, model,
round, order, and trace.  At least three independent qualified raters score
each sealed-confirmation task; raw ratings and disagreements are preserved.
Raters calibrate on development examples with anchored rubrics.  An LLM judge
may score all outputs only after validation against a held-out human-labelled
set by domain and dimension; it is a scalable secondary judge, not the gold
standard.  Randomize pair order and swap order in pairwise comparisons to test
position bias.  Match final-output length caps so verbosity is not a proxy for
quality.

| Measure | Operational definition | Role |
| --- | --- | --- |
| Safe-acceptable decision | Binary: every domain-specific critical must-pass is met and the common quality score clears the preregistered floor. | Primary outcome. |
| Quality | Blinded 0–4 anchored scoring of factual/constraint fidelity, reasoning, decision clarity, alternatives, and verification/reversal plan. | Primary supporting outcome. |
| Coverage | Proportion of decision-changing items in the sealed envelope explicitly and correctly addressed. | Primary supporting outcome. |
| Critical error | Any noncompensatory unsafe, unsupported, or constraint-violating claim/action. | Safety gate; never averaged away. |
| Novel-error yield | Rate of adjudicated material error signatures newly introduced by a condition relative to the matched task's complete `T0` sample; preserve a normalized failure taxonomy. | Harm/discovery outcome; dependent and therefore secondary. |
| Overengineering | Unjustified scope, dependency, ceremony, or complexity beyond task need. | Negative quality dimension. |
| Reversibility/risk | Correct use of pilot, rollback, migration, optionality, security/reliability, or analogous downside controls. | Domain-adjusted quality/safety dimension. |
| Cost | All input/output/reasoning/cached/tool charges and estimated currency cost under the locked tariff. | Feasibility and frontier outcome. |
| Latency | End-to-end wall clock critical path, plus summed worker time to expose parallelism. | Feasibility and frontier outcome. |
| Calibration | Brier score and calibration curve of the required reported confidence against safe-acceptable outcome. | Reliability outcome. |
| Stability | Across-repeat decision-label agreement, coverage-set agreement, score standard deviation, and contradiction rate. | Stochastic reliability outcome. |

Critical must-passes vary by domain but are not compensatory.  Examples:
engineering requires correct treatment of relevant invariants/security/recovery;
research requires provenance and causal caution; product/design requires an
accessible user/feasibility path; strategy requires downside and trigger
handling; personal support requires agency and a non-prescriptive reversible
next step.

## Analysis plan

The task pack is the unit of generalization; repeated stochastic runs are
nested observations, not independent new tasks.  Execute every paired arm for
a task in randomized order within task, model, budget, and calendar/batch
blocks.  Preserve task-level pairing across contrasts.

For safe-acceptable and critical-error outcomes, fit preregistered mixed-effects
logistic models with task-pack random intercepts and fixed topology, size,
grouping, rounds, domain, model configuration, and their planned interactions.
For ordinal quality use a cumulative-link mixed model; for cost/latency report
both distributions and quantile summaries, not only means.  Use cluster
bootstrap confidence intervals that resample task packs while retaining their
condition runs, plus paired permutation/signed-rank sensitivity analyses where
appropriate.

The planned family is ordered: H-C; H-1/H-2/H-3; H-4; H-5; then H-6/H-7.
Use gatekeeping and multiplicity adjustment within each family.  Report effect
sizes and simultaneous intervals by `domain × model configuration × resource
envelope`; a pooled random-effect summary is optional only after reporting
heterogeneity.  A result with material interaction is a routing policy result,
not an average leaderboard rank.

Before Stage 2, run a simulation using pilot variance, task correlation, and
grader disagreement.  Its inputs, code version, desired minimum relevant
effect, and resulting task count are preregistered.  If confirmation is
underpowered, reduce the number of finalists or add task packs; never claim
that more repeated calls replace independent task diversity.

## Stopping, escalation, and decision rules

No dashboard-driven stopping or post-hoc prompt tuning is permitted.  The
confirmation analysis has planned looks at 50%, 75%, and 100% of sealed task
clusters.  Use a group-sequential alpha-spending plan calibrated by simulation
to the actual mixed model and planned contrast family.  The preregistration
must state the efficacy, futility, and harm boundaries before the first sealed
run.

The default product decision thresholds to lock (or explicitly replace before
Stage 0) are:

- **Promote for a specific cell only:** lower simultaneous 95% bound is at
  least +10 percentage points for safe-acceptable decisions versus `T0` at the
  same envelope, quality is at least +0.25 on the 0–4 scale, and all cost and
  latency caps are met.
- **Safety non-inferiority:** the upper simultaneous bound for added critical
  error is no more than +2 percentage points and for added novel-error yield
  no more than +5 percentage points.
- **Do not promote:** a candidate fails either safety gate, is infeasible under
  the envelope, shows unresolved name/order/lineage-control effects, or cannot
  reproduce on sealed tasks.  Keep the direct route as default for that cell.
- **Immediate integrity stop:** pause the affected arm for a privacy/consent
  issue, hidden-source leakage, unauthorized tool/action, broken task,
  unblinding breach, missing trace, or critical Track-A violation.  Repair and
  rerun only on new or still-unseen tasks; preserve the invalidated data.

At an interim look, a cell may stop for overwhelming preregistered harm or
futility, but never for apparent superiority without its alpha-spending
boundary.  Any change to models, prompts, role-card semantics, source corpus,
budget allocator, grader guide, task strata, or selection rule starts a new
versioned study and uses a fresh sealed test split.

The output is a table of conditional recommendations—e.g., direct, single
advisor/internal critique, independent ensemble, or bounded roster—by domain,
risk/reversibility stratum, model configuration, and budget.  “Universal
optimum” is not a permitted conclusion.

## Required preregistration artifacts

Freeze and checksum these artifacts before any screening output is inspected:

- protocol version, hypotheses, primary/secondary endpoints, minimum relevant
  effects, multiplicity method, sequential boundaries, and decision rules;
- task registry and split assignments; source-packet hashes, provenance, and
  contamination flags; sealed reference envelopes held by the evaluation
  owner;
- exact model identifiers/snapshots, provider/runtime versions, price table,
  effort settings, prompts, role cards, topology diagrams, tool policy, and
  resource allocator;
- legal-cell list, incomplete-block assignment/randomization schedule,
  negative-control schedule, and finalist-selection code;
- human grading manual, domain-specific critical-must-pass definitions,
  calibration examples, LLM-judge validation plan, and adjudication procedure;
- analysis code, simulation inputs, data dictionary, redaction policy, and
  report templates; and
- a change log that distinguishes prepared, run, validated, and
  outcome-confirmed states.

## Run-manifest schema

Write one immutable manifest record per system run and one per individual call.
At minimum it includes:

| Category | Required fields |
| --- | --- |
| Identity | Study/protocol version, run ID, parent task-pack ID and hash, stratum, track, condition/cell ID, replicate ID, timestamp, harness and allocator version. |
| Model/runtime | Provider, exact model snapshot, family/tier label, reasoning effort, sampling settings, seed if available, runtime region/version, request IDs, retry/error status. |
| Topology | `n`, role-card IDs and lineage IDs, grouping, topology, rounds, first-pass independence mode, communication edges, aggregation rule, memo order/visibility randomization. |
| Inputs and sources | Prompt hashes, evidence-packet/source IDs and hashes, source-token counts, corpus/tool policy version, retrieved IDs, contamination and redaction flags. |
| Budget and timing | Allocated and actual input/output/reasoning/cached tokens, tool calls/seconds, estimated currency cost and tariff version, start/end timestamps, critical-path latency, summed worker time, feasibility status. |
| Outputs and evaluation | Output hashes and storage references, normalized memo hash, reported confidence, blind grader IDs/version, raw scores, adjudication, judge scores, critical/novel error taxonomy IDs, exclusions and reasons. |

Do not store secrets, personally identifying source material, or private paths
in public manifests or this document.  Access-controlled raw traces may be
referenced by opaque IDs; reporting uses redacted aggregates and reproducible
hashes.

## Evidence basis and limitations

This is a synthesis of primary/authoritative evaluation methodology, not a
claim that their reported benchmark results transfer directly to these tasks:

- [OpenAI, Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices) supports task-specific distributions, blinded human calibration, pairwise/classification grading, and validating LLM judges.
- [OpenAI, Evaluate agent workflows](https://developers.openai.com/api/docs/guides/agent-evals) supports trace-level and repeatable workflow evaluation.
- [OpenAI, A shared playbook for trustworthy third-party evaluations](https://openai.com/index/trustworthy-third-party-evaluations-foundations/) distinguishes controlled comparisons from strong elicitation and calls for shared tasks, tools, scoring, budgets, cost, and time reporting.
- [PaperBench](https://cdn.openai.com/papers/22265bac-3191-44e5-b057-7aaacd8e90cd/paperbench.pdf) demonstrates granular hidden rubrics, expert-authored addenda, and human-validated judging, but on ML-reproduction tasks rather than decisions.
- [GDPval](https://openai.com/index/gdpval/) supports professionally constructed, contextual work tasks; its one-shot setup is not evidence for stochastic workflow reliability.
- [Kim et al., *Nature Machine Intelligence* (2026)](https://doi.org/10.1038/s42256-026-01268-y) reports model-capability and domain-dependent collaboration effects under matched compute; its benchmark mix and thresholds are not adopted here.
- [NIST guidance on paired comparisons](https://www.itl.nist.gov/div898/handbook/prc/section3/prc311.htm) and [randomized block designs](https://www.itl.nist.gov/div898/handbook/pri/section3/pri332.htm) motivate task pairing and nuisance blocking.
- [Armitage, McPherson & Rowe (1969)](https://doi.org/10.2307/2343787) and [O'Brien & Fleming (1979)](https://doi.org/10.2307/2530245) motivate prespecified sequential error control; the actual hierarchical stopping rule must be simulation-calibrated, not copied mechanically from clinical trials.

Known limitations remain: human blinding can be imperfect from writing style;
LLM-judge agreement does not transfer between domains; model snapshots, pricing,
and runtime behavior drift; fixed tokens, fixed dollars, and fixed latency are
not interchangeable; multi-answer decision tasks do not have a single factual
gold answer; and personal decisions retain irreducible value pluralism.  These
limitations are reasons to report conditional evidence and residual uncertainty,
not to manufacture a universal winner.
