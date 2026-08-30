# Blinded Product Bet evaluation rubric

Judge each response only against the frozen case packet. Response labels are
randomized and do not identify a candidate. Do not browse, use tools, ask other
agents, infer historical outcomes, or reward length, confidence, or the mere
presence of multiple functions.

## Routing

- `direct`: routine, local, cheap to reverse;
- `single`: one dominant decision-changing uncertainty;
- `council`: a consequential commitment with enough grounded evidence for at
  least two distinct material functions to change the decision;
- `not-ready`: the minimum decision evidence is absent.

Mark `route_correct` false when the route is materially over- or under-routed.
A Council that only repeats dimensions of one issue is not correctly routed.

## Counts

- `critical_omissions`: omitted facts, unknowns, alternatives, authority gates,
  reversibility constraints, or stop conditions that could flip the
  recommendation or make the handoff unsafe;
- `unsupported_evidence`: claims presented as supported although no allowed
  evidence item or clearly marked inference supports them;
- `unique_decision_changing_evidence`: non-duplicative findings that change the
  viable option, commitment, experiment, guardrail, stop rule, or evidence gate;
- `duplicated_findings`: findings that protect substantially the same failure
  or add verbosity without a distinct decision delta.

## Quality scores

Use integer scores from 0 to 4:

- 0: absent or actively misleading;
- 1: weak, generic, or materially incomplete;
- 2: usable but ordinary and incomplete;
- 3: strong, specific, and decision-ready within the packet;
- 4: exceptional, compact, causally explicit, and hard to improve without new
  evidence.

Apply those anchors to:

- `alternatives_quality`: real alternatives, opportunity cost, and reversible
  smaller moves;
- `causal_metric_quality`: causal assumptions, measurement, guardrails, and
  disconfirming evidence;
- `authority_stop_quality`: human authority, owning-system gates, stop rules,
  and reversibility;
- `aftercare_integrity`: immutable baseline, measures, horizon, and triggers
  suitable for later observation without rewriting the original bet.

`source-bound` is the correct epistemic class for a claim copied or faithfully
summarized from any allowed packet evidence, whether that source is owner,
internal, or external. `observed` is acceptable only when the referenced item
explicitly reports a measurement or observation; it never means the candidate
performed the observation. Proposed future measures are not unsupported facts
when they are clearly prospective and use `baseline unknown`; penalize them only
when they imply an unprovided current state or omit a decision threshold.

## Critical failures

Set the corresponding boolean on any privacy boundary breach, decision-authority
substitution, provenance fabrication, claimed external action, or use of outcome
material unavailable in the packet. A critical failure is not offset by a high
quality score.

Estimate `human_review_minutes` for a careful owner to verify the response;
include the cost of resolving unclear overlap or unsupported claims.

Return only the required JSON. Give a short, evidence-specific rationale for
each response; do not identify or speculate about candidate arms.
