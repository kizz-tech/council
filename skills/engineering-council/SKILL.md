---
name: engineering-council
description: >-
  Use for consequential software-engineering decisions with multiple credible designs or costly-to-reverse consequences involving boundaries, dependency direction, public APIs, domain workflows or invariants, schemas or data integrity, authentication or security, concurrency, infrastructure, deployment, observability, recovery, or production risk. Also use when the user explicitly requests an engineering council or named engineering advisors for an engineering decision. Do not use for routine or reversible implementation, ordinary code review, known local bug fixes, mechanical cross-file work, generic parallel workers, or life, research, product-strategy, or design questions without an engineering decision.
---

# Engineering Council

Orchestrate read-only engineering advice while keeping the parent accountable for routing, synthesis, authorization, and the final decision. A capable direct agent is the default for routine work. A council means at least two independently completed named-advisor first passes, not an internal simulation or a collection of generic workers.

Named authors or schools describe lens provenance only. Never impersonate them or treat a name, doctrine, persona, or consensus as factual proof.

## Advisors

- `clean_boundary_architect`: dependency direction, information hiding, volatility seams, ports/adapters, and testable policy.
- `domain_model_cartographer`: domain language, workflows, lifecycle, invariants, consistency boundaries, and ownership.
- `evolutionary_deep_pragmatist`: simplicity, deep modules, convention, reversibility, refactoring sequence, and anti-ceremony.
- `production_systems_sentinel`: security, reliability, data integrity, deployment, observability, recovery, and measured performance.

## Before spawning

1. Preserve the requested mode and authority. Review, audit, report, plan, and diagnose requests remain read-only. Deliberation does not authorize implementation, commits, publication, deployment, migration, production access, or other side effects. Advisors remain read-only.
2. Create one shared factual evidence brief containing the goal and exact decision, requested mode and scope, observed facts with code/test/runtime/primary-source citations, constraints, known unknowns, reversibility, and blast radius. For a bug or incident, first state the observed failure and established root cause or explicitly mark it unknown. Do not preload a preferred design unless the task explicitly reviews that design.
3. Choose exactly one route:
   - **Direct:** answer directly or use an internal checklist for routine, local, or reversible work.
   - **Single advisor:** use one named profile when one material decision axis needs specialist scrutiny. This is consultation, not a council.
   - **Council:** use two countervailing named profiles when independent disagreement could change a consequential decision.
   - **Expanded council:** use three or four only when each owns a separate decision-changing axis and the decision has high blast radius.

If the user explicitly requests a council and an engineering decision exists, select at least two available named advisors. If fewer than two named profiles successfully return, disclose that no actual council occurred.

## Independent first passes

Launch all selected custom profiles independently and in parallel. Set `agent_type` to the exact profile identifier and set `fork_turns: "none"`. Supply the shared evidence brief, only the evidence needed for that lens, and one bounded lens-specific question. Do not expose peer drafts, ask for discussion, or ask advisors to rescan the whole repository.

Require each response to begin with a unique `finding_id` and return only:

- applicable findings;
- cited observed evidence;
- clearly separated inference;
- recommendation;
- strongest countercase;
- confidence;
- missing evidence.

Maintain a consultation ledger. For every requested profile, record the exact requested profile, completion status, and—only after successful completion—the returned `finding_id`. Claim consultation only for successfully authenticated profile/result pairs. Missing, failed, or timed-out profiles are degraded evidence and lower confidence. An internal application of a lens may inform the answer, but must not be reported as that named profile or as a council.

## Integrate, challenge, and stop

Integrate the authenticated first passes once against the shared evidence. Resolve factual disputes with code, tests, runtime data, or primary sources. Do not vote, average recommendations, force consensus, or grant a profile veto. Preserve every material dissent and state whether evidence resolved it, it was deferred with an owner and needed evidence, or it became a reversible verification experiment.

After integration, allow at most one targeted challenge, and only when one named unresolved contradiction, assumption, or irreversible risk could change the decision. Send the disputed claim, competing evidence, and provisional synthesis to the most relevant successfully completed advisor. Ask only for resolution of that issue; do not rerun the review or add another debate round.

Stop when every material objection is resolved, explicitly deferred with an owner and evidence requirement, or represented by a reversible experiment, and further advisors would not change the choice.

Implement only when the user requested it, using one accountable writer after synthesis. Verify proportionally against the actual risk, binding assumptions, and reversal path. Use exact state language: proposed, implemented, locally validated, committed, pushed, deployed, observed, and outcome-proven are distinct states and must never be conflated.

## Reporting contract

Report: route; actual profiles consulted; decision; binding evidence; material dissent and disposition; strongest rejected alternative; residual risk; missing evidence and confidence; and proportional verification or reversal plan. If requested consultation degraded or no actual council occurred, say so explicitly.
