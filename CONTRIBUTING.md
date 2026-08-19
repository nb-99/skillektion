# Contributing

Keep `skills/` as the installable source of truth.

## Owned skills

Edit owned skills directly and keep their directory name equal to the `name`
field in `SKILL.md`.

## Mirrored skills

Do not edit mirrors directly. Update the pinned revision in `sources.json`, run
`npm run sync`, and review the generated content diff. Change a mirror to
`adapted` before making local modifications.

## Adapted skills

Edit adapted skills directly. The recorded revision is the latest upstream
version reviewed and incorporated, not a byte-for-byte claim. Explain the
portability difference in `notes` and preserve the upstream license notice.

The names `agent-memory` and `nix-home-manager-expert` are reserved for
host-generated or repository-local configuration and must not be added to this
catalog.

Run `npm test` and `npm run sync:check` before submitting changes.
