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

## What exists in 0.2.0

- `engineering-council`, the first evaluated domain skill;
- four read-only Engineering Council advisor profiles;
- an explicit advisor composition and prompt-evaluation specification;
- a path-neutral provenance receipt for the private generation-one evaluation;
- deterministic source verification, plugin build, target drift checking, and
  opt-in materialization tooling;
- distribution contract tests;
- a source-bound library of representative software-engineering positions;
- versioned roster configuration, including the unchanged four-advisor
  generation-one historical baseline;
- a matched-budget experiment contract for changing roster size, composition,
  independence, prompt specificity, and model tier.

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
├── knowledge/representatives/       # Source-bound positions and questions
├── rosters/                         # Versioned experimental compositions
├── schemas/                         # Reviewable JSON shape projections
├── provenance/                      # Claim-scoped immutable evidence receipts
├── tools/council_dist.py            # Verify, build, drift, materialize
├── tests/                            # Distribution contract tests
└── docs/                             # Decisions and experiment protocols
```

The plugin root follows the official multi-skill distribution layout. Knowledge
and roster records are research and experiment inputs; they are deliberately
excluded from the installable artifact until a separately evaluated runtime
design consumes them. Advisor
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

## Flexible composition

Council does not assume that today's four engineering lenses are the right
decomposition tomorrow. A candidate may replace every slot, use one, two, four,
six, eight, or sixteen slots, group several source-bound positions into one
advisor, or split one decision axis across several advisors. The configuration
is useful only when it adds supported decision coverage at an acceptable total
budget.

The representative library supplies traceable positions, questions, limits,
and counterweights. It does not supply celebrity votes or simulated people.
Lineage independence, runtime independence, and observed output independence
are measured separately. See `knowledge/representatives/README.md`,
`rosters/README.md`, and `docs/experiments/roster-evaluation.md`.

## Verification

```bash
python3 tools/council_dist.py index --write
python3 tools/council_dist.py lock --write
python3 tools/council_dist.py verify
python3 -m unittest discover -s tests -v
```

`index --write` is required only after a reviewed representative-family or
library-manifest change. The versioned manifest declares the release cutoff
and exact family set; the index records its hash plus exact family hashes and
counts. `verify` is otherwise read-only and rejects stale knowledge or source
locks.

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

Repository-local generated targets are allowed only below `.agents/`,
`.codex/agents/`, or `.council-local/`; repository-local build artifacts are
allowed only below `dist/` or `build/`. These roots are excluded from the
canonical source lock and privacy surface. The tool rejects any build or
materialization target that contains the repository, overlaps canonical
`skills/` or `advisors/`, or overlaps another materialization unit.

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

See `provenance/engineering-council/generation-1.json` for the byte-preserved
evaluation receipt,
`provenance/engineering-council/generation-1-roster-reconstruction.json` for
the later roster binding, and `advisors/engineering-council/SPEC.md` for the
unresolved prompt/roster experiments.

## Release state

This is a local pre-release project. No public remote, license, marketplace
publication, signing identity, or production adoption has been established.
The absence of a license is intentional until the owner chooses one; do not
infer redistribution permission from repository availability.
