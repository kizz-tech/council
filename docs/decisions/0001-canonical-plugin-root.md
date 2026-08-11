# ADR 0001: Council uses one canonical plugin-root repository

- Status: accepted for local implementation
- Date: 2026-08-11
- Product version: 0.1.0

## Context

Engineering Council existed as a user skill, four custom-agent files, and a
private LIFEOS evaluation package in separate roots. Council is intended to
grow into a family of domain-specific decision workflows and may later be
shared. The repository boundary, technical IDs, install direction, and domain
structure become expensive to change after external adoption.

Official OpenAI documentation supports `skills/<skill>` inside plugins,
`.agents/skills` for repository skill discovery, and `.codex/agents` for
project-scoped custom agents. Custom-agent authoring and sharing may evolve.

## Council route

An expanded, read-only Engineering Council completed four independent first
passes:

| Profile | Authenticated finding |
| --- | --- |
| `clean_boundary_architect` | `CB-20260811-01` |
| `domain_model_cartographer` | `DMC-COUNCIL-BOUNDARY-001` |
| `evolutionary_deep_pragmatist` | `EVP-20260811-01` |
| `production_systems_sentinel` | `prod-dist-20260811-a7f3` |

The only decision-changing disagreement was canonical plugin-root source versus
a custom `packs/engineering-council` source rendered through adapters. One
targeted challenge returned `CB-20260811-02` and resolved the boundary concern.

## Decision

Create `council` as a standalone sibling git repository in the owner's project
container and make it the canonical Council plugin root.

- Keep canonical skills directly under `skills/`.
- Group canonical custom-agent sources under `advisors/<domain>/`.
- Treat `.agents/skills`, `.codex/agents`, user-home copies, build output,
  receipts, and backups as one-way generated derivatives.
- Keep Engineering Council as the first domain, not a cross-product core.
- Do not create empty future councils, a shared core schema, MCP, hooks, UI, or
  registries before evidence requires them.
- Keep one SemVer in `.codex-plugin/plugin.json`; use hashes and immutable eval
  generation IDs for lower-level identity.

## Rejected alternative

Use `packs/engineering-council/**` as canonical source and render every runtime
layout through an adapter. This becomes preferable if a second domain needs an
independent lifecycle, selective installation, multiple skills, or a non-Codex
runtime. It is premature while only one Codex-native pack is evidenced.

## Consequences

- The public/install layout stays direct and inspectable.
- Advisor distribution volatility is isolated behind one materializer.
- Installed drift fails closed; there is no reverse synchronization.
- A later physical pack extraction is allowed only behind observed triggers.
- Plugin and advisor installation cannot be globally atomic.
- SHA-256 proves content integrity, not publisher identity.

## State

This ADR authorizes the local repository shape only. It does not authorize a
remote, license, marketplace entry, publication, push, or production claim.
