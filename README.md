# Skillektion

A small, curated collection of agent skills. `skills/` always contains the
exact files users install.

## Install

Install one skill with GitHub CLI 2.91 or newer:

```sh
gh skill install nb-99/skillektion gh-cli --scope user --agent opencode
```

Install the entire collection:

```sh
gh skill install nb-99/skillektion --all --scope user --agent opencode
```

`gh skill` is currently in public preview. As a fallback, use the Skills CLI:

```sh
npx skills add nb-99/skillektion
```

Both installers support selecting skills and target agents. Pin a published
Skillektion release with `--pin <tag>` when reproducibility matters.

## Nix

Consume Skillektion as a non-flake input:

```nix
inputs.skillektion = {
  url = "github:nb-99/skillektion";
  flake = false;
};
```

Client adapters can enumerate `${inputs.skillektion}/skills` and link each
complete directory into the client's global or project skill location.

## Catalog

Every directory under `skills/` is independently installable and follows the
[Agent Skills specification](https://agentskills.io/specification).

`sources.json` records how each skill is maintained:

- `owned`: authored and maintained in this repository.
- `mirror`: copied unchanged from a pinned upstream commit by `npm run sync`.
- `adapted`: maintained directly here after reviewing the recorded upstream
  revision. Local changes are visible in Git history.

Third-party license notices are copied into each mirrored or adapted skill so
they accompany selective installations. Attribution and update metadata stay
outside `SKILL.md` and do not consume the agent's normal skill context.
The root MIT license applies to Skillektion's original content; redistributed
skills remain covered by their accompanying `LICENSE.upstream` notices.

Mirrors retain upstream client-specific metadata such as
`disable-model-invocation`. Clients that do not support a field may ignore it,
so explicitly invoked workflow skills can be more discoverable there than in
their original client. Adapted skills document their changes in `SOURCE.md`.

## Maintenance

Validate the catalog:

```sh
npm test
```

Refresh all mirrors from their pinned revisions:

```sh
npm run sync
```

Verify that mirrors match their pinned revisions and adapted skills retain
their recorded upstream license and source path:

```sh
npm run sync:check
```

To update a mirror, change its `revision`, run `npm run sync`, and review the
resulting diff. To update an adapted skill, compare it with the newer upstream
revision, incorporate the relevant changes directly, and then update the
recorded revision.
