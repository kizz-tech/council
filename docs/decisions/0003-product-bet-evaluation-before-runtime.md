# ADR 0003: Product Bet evaluation precedes runtime promotion

- Status: accepted; generation one concluded with runtime rejection
- Date: 2026-08-30
- Decision owner: repository maintainer
- Runtime promotion: rejected at adaptation reliability gate

## Context

Council `v0.2.0-alpha.1` contains one evaluated domain pack: Engineering
Council. Product Bet research proposes dynamic evidence functions, a frozen
Product Bet Brief, human decision authority, negative routing, and a separate
Aftercare phase. It does not contain a direct Product Bet Council outcome
dataset or an authorized held-out case generation.

The repository policy requires a new domain to establish its own evidence
rules, failure paths, permissions, negative routing, and evaluation gate. The
current distributor is intentionally specific to the Engineering skill and
four Engineering advisors.

An expanded read-only Engineering Council reviewed the change before
implementation. Authenticated first-pass findings were:

- `CBA-PBC-DIST-20260830-01` — isolate only a distribution component seam; do
  not introduce a universal Council kernel;
- `pbc-domain-20260830-a17` — keep Product Bet Brief, Council Run, and
  Aftercare state and authority distinct;
- `EVP-PBC-20260830-01` — do not promote skills, profiles, schemas, or a
  distributor refactor before a real-case comparison justifies them;
- `pss-product-bet-release-gates-20260830` — private-case ancestry,
  provenance, bounded execution, v0.2 upgrade/rollback, and artifact identity
  are publication gates.

The material dissent concerned timing. Boundary and domain analysis could
support a minimal multi-component implementation, while the evolutionary
review argued that the winning runtime shape is not yet known. The evidence
limitation resolves that dissent in favor of evaluation-first promotion.

## Decision

1. Generation-one candidate contracts live under
   `docs/experiments/product-bet-council-generation-1/`, not under canonical
   runtime `skills/` or `advisors/`.
2. The initial adaptation comparison uses:
   - `R1`: a strong direct agent with a frozen Product Bet Brief;
   - `F-free`: case-local functions derived without a library;
   - `F-generic`: the same router plus one frozen generic function-executor
     contract. Adaptation may eliminate it before held-out.
3. Fixed professions, named product schools, a seven-function roster, and
   generated profiles are not release candidates in generation one.
4. Private real cases remain outside the public repository. The repository
   stores only public-origin fixtures, schemas, prompt contracts, validation
   tooling, preregistration, and aggregate/redacted receipts.
5. Equality, ambiguous gain, prose-only gain, a new critical omission, an
   authority/privacy/provenance violation, or an unset cost ceiling rejects a
   Product Bet Council runtime.
6. Promotion follows the winning shape:
   - `R1` wins or ties: do not release Product Bet Council;
   - `F-free` wins materially: promote one Product Bet Council skill and no
     custom advisor;
   - `F-generic` wins materially: promote one skill plus one generic read-only
     evidence-function advisor and the smallest literal component declaration
     needed to install it;
   - split Product Bet Aftercare into a second skill only if real routing or
     permission evidence shows that an explicit lifecycle boundary prevents a
     demonstrated failure.
7. No generic Council superclass, pack framework, or universal domain schema is
   created by this generation.

## Required evidence before promotion

- 8–12 authorized real Product Bets across at least four archetypes;
- calibration, adaptation, sealed held-out, and prospective-shadow custody;
- frozen evidence cutoffs and no outcome leakage into candidate contexts;
- equal total budgets, fresh contexts, exact prompt/runtime/model hashes, and
  blinded factual/omission scoring;
- a numeric materiality and cost ceiling frozen before held-out execution;
- exact candidate bytes and a signed or hash-bound evaluation receipt;
- zero critical privacy, authority, provenance, or external-action failures.

## Consequences

The repository can implement and validate the experiment without claiming a
second shipped domain pack. The existing plugin manifest, Engineering skill,
advisor identities, receipts, materializer, and `v0.2.0-alpha.1` compatibility
remain unchanged until the evaluation selects a runtime that needs a change.

Rejected candidates can be removed as one experiment directory plus its
validator tests. Promotion is a separate reviewed change and must preserve the
generation-one prompt hashes.

## Generation-one outcome

Calibration and private adaptation were executed. `F-generic` was eliminated
after repeated incomplete cells at the common cost ceiling. The remaining
`F-free` candidate completed three of four final confirmation cases but did not
produce a valid frozen output for the fourth under the same 200,000-token,
300-second contract. A favorable later diagnostic reproduction cannot replace
that failed assignment.

No candidate therefore reached held-out. No Product Bet skill, advisor,
Aftercare skill, shared kernel, distribution component, or product-outcome
claim is promoted. `v0.2.0-alpha.2` publishes the evaluation machinery and
negative result only; the installable capability remains Engineering Council.

## Strongest rejected alternative

Immediately add `product-bet-council`, `product-bet-aftercare`, three public
runtime schemas, a generic advisor, and a component registry. This would create
an impressive complete surface, but it would encode the untested topology and
lifecycle split that generation one is intended to decide. It is therefore a
larger and less reversible claim than the available evidence supports.
