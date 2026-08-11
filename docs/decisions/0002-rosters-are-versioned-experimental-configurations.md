# ADR-0002: Rosters are versioned experimental configurations

- Status: accepted
- Date: 2026-08-11

## Context

Council began with one Engineering Council skill and four custom-agent
profiles. That configuration produced useful local results, but neither the
evaluation nor the external evidence establishes that four is optimal, that
those four axes are exhaustive, or that an engineering decomposition transfers
to research, product strategy, design, delivery, or other domains.

The project must support two different kinds of change:

- deepen an existing advisor prompt while preserving its decision function;
- replace the decomposition itself, including roster size, intellectual
  lineages, decision functions, model families, visibility, and topology.

Treating the current advisors as the product model would make those changes
hard to compare and would silently turn a historical choice into doctrine.

## Decision

Council separates four canonical layers:

1. a source-bound representative lens library;
2. executable advisor prompt sources;
3. versioned roster configurations, identified by `(roster_id, revision)`;
4. immutable run manifests and evaluated outputs.

The current four Engineering Council profiles are preserved as revision 1 of
the `engineering-council-generation-1` historical baseline. Its exact
repository roster digest is recorded as a post-evaluation reconstruction; it
is not presented as the private pilot's original runtime manifest. It is not
marked as the default or optimum.

Future experiments may replace every slot, use functional or source-bound
lenses, vary roster size, and change grouping or topology. Each candidate must
be explicit, versioned, budget-matched, evaluated on held-out questions, and
compared with a strong single-agent baseline. Names are provenance anchors for
admitted positions; they are not runtime identities and must not be used for
impersonation.

The representative library is research material and configuration input. It
does not become part of the installable plugin artifact or an active advisor
prompt merely by being present in the repository. Promotion to runtime requires
a separate candidate, evaluation, and decision record.

## Consequences

- The hypothesis space is intentionally open; every experiment remains bounded
  and reproducible.
- Generation-one behavior remains reversible and comparable.
- Sixteen names do not count as sixteen independent views unless lineage,
  runtime, and observed output independence are separately demonstrated.
- Additional repository structure and validation are required.
- Council can grow into multiple domain packs without forcing a premature
  universal orchestration core.

## Rejected alternatives

### Keep the four advisors as a fixed Council architecture

Rejected because it converts one locally useful configuration into an
unsupported universal constraint and prevents clean composition experiments.

### Put all admitted representatives into every run

Rejected because model agreement and role count are not evidence independence;
unbounded fan-out increases cost, correlated error, and synthesis burden.

### Generate persona prompts directly from famous names

Rejected because it encourages attribution drift and impersonation. Runtime
prompts must bind to specific positions, sources, decision questions, and
evidence limits.

### Build a universal cross-domain core now

Rejected until a second domain pack demonstrates which protocol invariants are
actually shared. The repository may host multiple packs without pretending
their truth sources, permissions, and failure paths are identical.

## Verification

- deterministic validation of every library and roster record;
- an exact immutable generation-one roster;
- matched-budget evaluation defined in
  `docs/experiments/roster-evaluation.md`;
- independent structural and semantic review before release claims.
