# Contributing

Council is an evidence-bound decision system, not a collection of personas.
Contributions should begin with an observed failure, a falsifiable design
question, or a source-backed gap.

## Before opening a pull request

1. Keep canonical skills under `skills/` and advisor prompts under `advisors/`.
2. Preserve historical rosters and provenance receipts; add a new version
   instead of silently redefining an evaluated baseline.
3. Separate source facts, interpretation, runtime configuration, and measured
   outcomes.
4. Run:

   ```bash
   python3 tools/council_dist.py verify
   python3 -m unittest discover -s tests -v
   ```

5. If canonical source changed, review it and regenerate the lock with
   `python3 tools/council_dist.py lock --write` before rerunning verification.

New domain packs need distinct evidence rules, failure paths, permissions,
negative routing, and an evaluation gate. A copied roster is not a new domain.
