# Council

Council is an experimental system for making consequential decisions with the
smallest useful set of independent specialist lenses. It is not a default
multi-agent chat, a majority vote, or a promise that more agents are better.

The current supported topology is:

```text
route → shared factual brief → minimum independent lenses → synthesis
      → at most one targeted challenge → verification and stop contract
```

Routine and reversible work should normally stay with one capable agent. A
single material axis may justify one specialist consultation. A council begins
only when at least two countervailing, independently completed lenses could
change a consequential decision.

## What exists in 0.1.0

- `engineering-council`, the first evaluated domain skill;
- four read-only Engineering Council advisor profiles;
- an explicit advisor composition and prompt-evaluation specification;
- a path-neutral provenance receipt for the private generation-one evaluation;
- deterministic source verification, plugin build, target drift checking, and
  opt-in materialization tooling;
- distribution contract tests.

The repository is the canonical source. User skills, project loader overlays,
personal Codex agent files, plugin artifacts, and installation receipts are
derived outputs. They must never become competing masters.

## Repository structure

```text
.
├── .codex-plugin/plugin.json        # Product identity and SemVer
├── skills/                          # Canonical installable workflows
│   └── engineering-council/
├── advisors/                        # Canonical custom-agent prompt sources
│   └── engineering-council/
├── provenance/                      # Claim-scoped immutable evidence receipts
├── tools/council_dist.py            # Verify, build, drift, materialize
├── tests/                            # Distribution contract tests
└── docs/decisions/                   # Consequential architecture decisions
```

The plugin root follows the official multi-skill distribution layout. Advisor
profiles remain a separate source surface because custom-agent distribution is
not currently a declared plugin component. The tool can materialize them into
supported Codex agent locations, but does so as an explicit, drift-checked
operation.

## Product direction

Engineering Council is only the first domain pack. Council may eventually
support the full product lifecycle:

1. external research and evidence quality;
2. problem framing and product strategy;
3. interaction, service, and visual design;
4. engineering architecture and implementation risk;
5. release, operations, and learning from outcomes.

These are candidate domains, not empty folders or copied engineering personas.
Each future council needs its own truth sources, authorization boundary,
specialist error paths, negative route, and matched-budget evaluation. Shared
protocol code should be extracted only after a second domain demonstrates an
actual stable invariant.

## Verification

```bash
python3 tools/council_dist.py verify
python3 -m unittest discover -s tests -v
```

Build a clean plugin artifact into a new or empty directory:

```bash
python3 tools/council_dist.py build --output /tmp/council-plugin
```

Inspect local drift without writing:

```bash
python3 tools/council_dist.py status \
  --skill-root "$HOME/.agents/skills" \
  --agent-root "$HOME/.codex/agents"
```

Materialization is opt-in and refuses unknown drift:

```bash
python3 tools/council_dist.py materialize \
  --skill-root "$HOME/.agents/skills" \
  --agent-root "$HOME/.codex/agents" \
  --apply
```

Installation receipts are local drift metadata bound to the Council product,
component, version shape, and exact file set. They are not signatures and do
not authenticate a hostile writer with filesystem access.

Use only one active skill delivery channel in an environment. Prefer plugin
installation for eventual distribution; use user/repository skill copies only
as compatibility or development channels.

## Evidence boundary

Generation one is a private, synthetic, one-sample-per-cell evaluation. It
contains a frozen historical baseline, held-out comparisons, process telemetry,
and an independent structural audit. It supports the local v2 workflow repair
and this initial packaging decision. It does **not** prove universal council
superiority, advisor-roster optimality, small-model substitution, cross-domain
transfer, production outcomes, or public reproducibility.

See `provenance/engineering-council/generation-1.json` for the immutable receipt
and `advisors/engineering-council/SPEC.md` for the unresolved prompt/roster
experiments.

## Release state

This is a local pre-release project. No public remote, license, marketplace
publication, signing identity, or production adoption has been established.
The absence of a license is intentional until the owner chooses one; do not
infer redistribution permission from repository availability.
