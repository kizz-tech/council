# Product Bet Council generation one

Generation one is an executable, falsifiable comparison. It is not a released
Product Bet Council and does not support a product-outcome claim.

**Outcome:** generation one concluded at adaptation. `F-generic` was eliminated
for repeated completion/cost failures; `F-free` then failed one of four frozen
two-arm confirmation cells. Held-out was not opened and no runtime bytes were
promoted. See `adaptation-decision.md` and ADR 0003.

## Decision

Determine whether a dynamically routed Product Bet Council produces a material
decision-support gain over a strong direct agent using the same frozen Product
Bet Brief and an equal total budget.

The experiment can reject every Council candidate. A tie is a rejection.

## Candidate contracts

- `candidates/r1.md` — strong single-agent baseline;
- `candidates/f-free.md` — router derives case-local evidence functions;
- `candidates/f-generic-function.md` — rejected frozen executor retained as
  adaptation ancestry; it is no longer in the active registry;
- `candidate-registry.json` — exact candidate files and execution constraints.

No candidate in this directory is a canonical Codex skill or custom-agent
profile. The evaluated bytes may be promoted only through ADR 0003.

## Evidence generations

Use 8–12 authorized real Product Bets. Private cases stay outside this
repository and are passed to the validator by path. Public fixtures under
`fixtures/` are independently synthetic and exist only to test the mechanics,
negative routes, privacy envelope, and scorer. They cannot establish efficacy.

Required split:

| Split | Purpose |
| --- | --- |
| calibration | validate envelopes, budgets, runner and scoring |
| adaptation | remove bad candidates and freeze thresholds |
| held-out | make the promotion decision |
| prospective-shadow | later outcome/Aftercare evidence |

Historical outcome material and judge anchors must be kept outside candidate
contexts. Candidate authors and executors receive only the exact case packet,
candidate contract, runtime policy, and budget for one cell.

## Evidence modes

- `closed-pack`: every candidate receives identical frozen evidence.
- `open-research`: every candidate receives identical tool/source scope, total
  budget, and stop rule.

Do not pool these modes into one score.

## Deterministic workflow

Validate the public mechanics:

```bash
python3 tools/product_bet_eval.py validate-package \
  --cases docs/experiments/product-bet-council-generation-1/fixtures
```

Freeze an authorized case generation without copying its payloads:

```bash
python3 tools/product_bet_eval.py freeze \
  --cases /controlled/path/to/cases \
  --output /controlled/path/to/generation-manifest.json \
  --runtime-id '<exact runtime>' \
  --model-id '<exact model>' \
  --frozen-at '<ISO-8601 timestamp with timezone>' \
  --write
```

Validate cell outputs and blinded scorecards:

```bash
python3 tools/product_bet_eval.py gate \
  --manifest /controlled/path/to/generation-manifest.json \
  --outputs /controlled/path/to/outputs \
  --scores /controlled/path/to/scores.json \
  --thresholds /controlled/path/to/thresholds.json
```

The freeze command stores hashes, sizes, classifications, assignments, prompt
identities, budgets, and runtime identity. It does not embed case payloads.

Prepare two differently permuted private blind bundles, execute the judge for
each case, and conservatively aggregate them with `tools/product_bet_judge.py`.
The aggregate takes the worst critical/route/omission/quality value rather than
voting away disagreement. Cell failures can be written as hash-bound receipts
with `run_product_bet_cell.py --failure-output`; raw model output is not kept.

## Primary measures

- critical omissions and unsupported evidence;
- unique decision-changing evidence;
- duplicated/correlated findings;
- correct `direct | single | council | not-ready` routing;
- alternatives and opportunity-cost reasoning;
- causal/metric/guardrail integrity;
- human authority, reversibility, and stop-rule integrity;
- preservation of the Aftercare baseline;
- total tokens, latency, tool calls, retries, and human review burden.

## Non-negotiable gate

Reject a candidate on any critical privacy, authority, external-action,
provenance, or outcome-leakage failure. Reject any candidate with a new
critical omission relative to `R1`. Reject a tie, an unset numeric threshold,
or a gain justified only by verbosity. Do not publish or promote candidate
bytes whose hashes differ from the held-out generation.
