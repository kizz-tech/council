# Council rosters

A roster is a versioned experimental configuration. It selects a bounded set
of decision functions and prompt sources for one class of questions. It is not
the Council product, a permanent organization chart, or evidence that its size
is optimal.

Keep these layers separate:

1. `knowledge/representatives/` stores source-bound positions and questions.
2. `advisors/` stores executable custom-agent prompt sources.
3. `rosters/` records which slots and prompt sources form a candidate or
   historical configuration.
4. A run manifest records the actual model, source pack, visibility, topology,
   budget, evaluator, seed, and outputs used in one experiment.

A roster slot can use a functional lens, one or more library-bound
representations, or an explicitly documented hybrid. A named representation
must never be converted into an impersonation prompt. It contributes only the
source-bound positions, questions, counterweights, and limits admitted by the
library.

Binding is allowed only for roster-eligible library units. A
`qualified_counterweight` may be referenced in a source pack or counterweight
record, but it cannot be bound to a slot. A new roster revision does not
upgrade a representation's admission status. A `source_corpus` may be bound as
a bounded corpus without implying a person, school, or unified worldview.

## Change rules

- Preserve evaluated roster `(roster_id, revision)` pairs as immutable
  historical baselines.
- Create a new roster ID or increment `revision` before changing composition or
  prompts; multiple revisions of one roster ID may coexist.
- Record inclusion, exclusion, overlap, and shared-lineage decisions.
- Compare candidates at matched total budgets and on held-out questions.
- Test 1, 2, 4, 6, 8, or 16 slots only when the experiment can distinguish a
  useful gain from duplicated analysis and increased cost.
- Retire a slot when it adds no unique supported claim, decision function,
  counterweight, or error-path coverage.

`engineering-council/generation-1.json` preserves today's four advisors. Its
status is `historical-baseline`; it is neither a default for every decision nor
a ceiling on future Council designs. Its SHA-256 is pinned by a separate
generation-one roster-reconstruction sidecar that references the unchanged
evaluation receipt. The sidecar proves exact repository identity, not that the
private pilot executed from this later JSON file.
