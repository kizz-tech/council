# Council repository policy

## Product boundary

This repository is the canonical source for the Council product. Engineering
Council is the first domain pack, not a universal core and not the whole
product. Add a new council only after its domain owns distinct evidence rules,
failure paths, permissions, negative routing, and an evaluation gate.

## Canonical and derived state

- Edit canonical skills only under `skills/`.
- Edit canonical custom-agent prompts only under `advisors/`.
- Treat `.agents/skills`, `.codex/agents`, user-home skills, Codex-home agents,
  `dist/`, installation receipts, and backups as generated derivatives.
- Never reverse-sync an installed derivative into repository source.
- Keep one product version in `.codex-plugin/plugin.json` until a pack has an
  independently released lifecycle.

## Evidence and claims

- Preserve immutable evaluation generations and their hashes.
- Do not commit raw reasoning traces, profile state, secrets, personal absolute
  paths, or private product context.
- Keep proposed, implemented, locally validated, committed, pushed, published,
  installed, observed, and outcome-proven states distinct.
- Model agreement, named personas, and vote counts are not independent evidence.

## Change workflow

1. Start from an observed failure, decision, or explicit experimental question.
2. Keep routine and reversible work direct; do not invoke a council by ritual.
3. Freeze behavior-changing candidates before held-out evaluation.
4. Update source, tests, provenance, and the lock together.
5. Run `python3 tools/council_dist.py verify` and
   `python3 -m unittest discover -s tests -v`.
6. For release candidates, validate the plugin, build from the allowlist, run
   discovery and drift smokes, scan for secrets and personal paths, and record
   an immutable commit/tag. Publication and push require explicit authority.

## Writing ownership

Use one active writer for a canonical file or module. Parallel agents may own
disjoint evidence or edit scopes; one parent integrates and verifies the final
state.
