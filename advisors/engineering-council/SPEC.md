# Engineering Council advisor specification

## Current status

The four generation-one advisor prompts are exact, hash-bound imports from the
locally tested runtime. They were not rewritten during the v2 orchestration
repair because the demonstrated defect was in workflow, fork isolation, and
consultation provenance—not in profile content.

Their availability and basic behavior are tested. Their optimality,
orthogonality, author-name effect, and portability across model tiers remain
open experimental questions.

This document specifies the generation-one prompt set, not the permanent
Council roster architecture. The roster manifest preserves this set as a
historical baseline; a candidate may deepen one prompt, split or merge
responsibilities, or replace all four with a different source-bound
decomposition.

## Composition

Generation one keeps four available engineering lenses and selects them dynamically. One profile
is a consultation; two countervailing profiles are the normal council; three or
four require a high-blast-radius decision with a distinct decision-changing
axis for each. There is no current evidence for a fifth default advisor, nor
evidence that four is an optimum or ceiling. Candidate sizes and alternative
groupings belong to `docs/experiments/roster-evaluation.md`.

| Profile | Primary question | Unique protection | Counterweight |
| --- | --- | --- | --- |
| `clean_boundary_architect` | Where should dependencies and information-hiding boundaries point? | Policy/mechanism separation, volatility seams, ports, testable policy | Reject interface and folder ceremony; preserve deep modules and directness |
| `domain_model_cartographer` | What language, lifecycle, invariant, consistency, and ownership boundary is real? | Ubiquitous language, workflows, bounded contexts, aggregate and integration meaning | Reject DDD theater and over-modeling of CRUD |
| `evolutionary_deep_pragmatist` | What is the smallest reversible design, and what ceremony can be removed? | Cognitive simplicity, deep interfaces, convention, refactoring sequence | Simplicity cannot excuse irreversible coupling, data loss, security, or migration risk |
| `production_systems_sentinel` | What can fail in production, and how will it be measured, deployed, and reversed? | Security, integrity, recovery, migration, observability, measured hot paths | Risk-rank; reject distributed-systems and performance theater |

## Lens geometry

The useful tensions are deliberate:

- clean ↔ domain: technical dependency direction versus semantic workflow;
- clean ↔ pragmatist: explicit seams versus shallow abstraction overhead;
- domain ↔ pragmatist: meaningful domain depth versus DDD ceremony;
- production ↔ pragmatist: real irreversible risk versus speculative controls;
- domain ↔ production: business invariants versus transactional enforcement;
- clean ↔ production: stable seams versus runtime and deployment fitness.

Overlap counts as corroboration only when profiles reach the same risk through
different evidence or failure paths. Repeated doctrine from the same source
lineage remains one evidentiary line.

## Persona and author policy

Named authors and schools are provenance anchors, not identities or evidence.
The profiles reference Robert C. Martin, Parnas, Cockburn, Evans, Vernon,
Fowler, Ousterhout, Beck, DHH, Nygard, SRE, DORA, OWASP, NIST, and related
schools to sharpen a lens. Runtime identifiers remain responsibility-based.
Profiles must never impersonate a person or imply that the person endorses an
answer.

Author-like nicknames may improve focus or induce caricature and prestige
anchoring. Their effect has not been isolated.

## Common return contract

Every advisor is read-only and must:

- preserve the parent request's authority and scope;
- separate observed evidence from inference;
- cite code, tests, runtime data, or primary sources when available;
- state missing evidence instead of inventing facts;
- return only applicable, ranked findings;
- include a recommendation, strongest countercase, verification, confidence,
  and missing evidence;
- apply its role-specific anti-theater counterweight.

The orchestrator additionally requires a unique `finding_id` and authenticated
consultation ledger. The imported TOMLs do not yet state the exact `finding_id`
field literally. Runtime tests followed the parent contract, but this remains a
real conformance gap for the next frozen profile candidate.

## Evaluation program

### A. Deterministic conformance

Verify TOML parsing, exact identity, read-only sandbox, mutation refusal,
missing-evidence behavior, `finding_id` compatibility, and compact returns.
Inject timeout, missing profile, malformed output, and stale installation.

### B. Separability and redundancy

Run every profile independently on the same frozen engineering briefs plus a
generic strong-reviewer control. Blind evaluation to profile identity. Measure
unique critical findings, critical misses, ceremonial false positives,
semantic/source-lineage overlap, decision changes, scope violations, tokens,
and latency.

### C. Prompt and roster ablations

Compare:

1. responsibility identity versus author-named identity;
2. current anchors versus a compressed responsibility-only prompt;
3. dynamic pair versus all four at matched budget;
4. leave-one-profile-out councils;
5. independent first pass versus exposure to a shared draft;
6. current strong model versus lower tiers, reported separately.

A fifth advisor is admitted only when it repeatedly recovers a unique,
predeclared, decision-changing axis at acceptable marginal cost.

### D. Real-shadow outcomes

Follow decisions through implementation and verification. Measure later
corrections, rework, escaped invariants, incidents, delivery delay, and owner
judgment. Better prose is not a proven product outcome.

## Domain boundary

Product desirability, user research, UX/accessibility, research methodology,
commercial strategy, and personal meaning are not missing Engineering Council
advisors. They belong to future domain councils with their own truth and
authorization boundaries.

## Revision gate

Do not edit a live prompt because one example looks attractive. A candidate
requires a mechanism diagnosis, frozen text and hashes, adaptation without
held-out exposure, held-out conformance/quality/cost gates, exact distribution
checks, post-install smokes, and a versioned record of the replaced prompt.
