# Source

Adapted from the critique mode of `pstack/skills/how` — its
`references/critic-prompt.md` and `references/critique-rubric.md` — in
[`cursor/plugins`](https://github.com/cursor/plugins). Those files were
present through commit `7314f723a487ec406b6369fe5865ba034cfed166` and
upstream removed them at `5866df557357d005b3c0c9d3da0d9e739b4bdde3`, the
recorded revision, where the `pstack/skills/how` directory still exists and
verifies the license. Licensed under the MIT terms in `LICENSE.upstream`.

It also draws on `skills/engineering/improve-codebase-architecture` in
[`mattpocock/skills`](https://github.com/mattpocock/skills) at commit
`4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`: scoping by change history, the
depth lens with the deletion test and the adapter rule for seams, and respect
for documented decisions. Licensed under the MIT terms in
`LICENSE.mattpocock`.

This skill replaces this catalog's former `architecture-critique`, `how`, and
`improve-codebase-architecture` skills. It keeps the critique's rubric lenses,
severity tiers, evidence rule, and the lead-verdict vocabulary shared with
`code-review`. It inlines the explain step instead of delegating to `how`,
adds co-change coupling from Git history as a scoping and evidence source, and
uses the `codebase-design` vocabulary throughout. It omits the per-model critic
roster, Cursor task configuration, the HTML report, and the interactive
grilling, glossary, and ADR follow-up.
