# Changelog

All notable changes to Council are documented here. The project follows
Semantic Versioning for repository releases while it remains pre-1.0.

## [0.2.0-alpha.1] - 2026-08-12

This is the first public alpha release.

### Added

- A source-bound representative lens library spanning software architecture,
  design, domain modeling, distributed systems, data, reliability, languages,
  security, performance, and sociotechnical delivery.
- Versioned roster configuration and a frozen generation-one Engineering
  Council baseline.
- A separate roster-reconstruction provenance sidecar that leaves the original
  generation-one evaluation receipt byte-identical to 0.1.0.
- Reviewable JSON shape projections, deterministic standard-library knowledge
  validation, and an
  experiment protocol for roster size, composition, independence, and model
  tier.

### Changed

- Reframed the four current advisors as one evaluated historical
  configuration rather than a fixed or universally optimal Council design.
- Added admission-aware roster binding: qualified counterweights remain useful
  evidence but cannot silently become executable roster identities.

### Unchanged

- The installable `engineering-council` skill and its four runtime advisor
  prompts remain byte-identical to generation one.
- No public release, marketplace install, or remote publication is implied.

### Release boundary

- The full release bundle installs the skill and four advisor profiles through
  the drift-checked materializer.
- The Codex plugin artifact is skill-only because Codex CLI 0.146.0 does not
  declare custom-agent profiles as a plugin component.
- The published capability does not establish superiority over a strong single
  agent, roster optimality, or production-outcome improvement.

### Security

- Reject symbolic links and non-regular entries before verification, lock
  generation, release building, or materialization so an allowlisted source
  cannot read outside the canonical repository.
