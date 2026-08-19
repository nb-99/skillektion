# AGENTS.md

Skillektion publishes a curated flat catalog of portable agent skills.

## Contract

- `skills/<name>/` is the exact independently installable artifact.
- `sources.json` records whether each skill is `owned`, `mirror`, or `adapted`.
- Edit owned and adapted skills directly. Refresh mirrors only through
  `npm run sync`.
- Preserve complete skill directories, including scripts and references.
- Keep third-party attribution in `LICENSE.upstream`, outside `SKILL.md`, and
  document every adapted skill's changes in `SOURCE.md`.
- Do not add the reserved `agent-memory` or `nix-home-manager-expert` names.

## Validation

Run `npm test` and `npm run sync:check`. The latter requires network access to
verify mirrors against their pinned upstream commits.

See `CONTRIBUTING.md` for the update workflow.
