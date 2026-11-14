# Source

Adapted from the critique mode of `pstack/skills/how` — its
`references/critic-prompt.md` and `references/critique-rubric.md` — in
[`cursor/plugins`](https://github.com/cursor/plugins). Those files were
present through commit `7314f723a487ec406b6369fe5865ba034cfed166` and
upstream removed them at `5866df557357d005b3c0c9d3da0d9e739b4bdde3`, the
recorded revision, where the `pstack/skills/how` directory still exists and
verifies the license.

Upstream removed critique mode because its `interrogate` skill absorbs the
contested-design case there; this catalog routes contested-change review to
`code-review`, so the subsystem-quality capability would otherwise be missing.
This version keeps all six rubric lenses, the three severity tiers, and the
lead-verdict vocabulary shared with `code-review`; it removes the per-model
critic roster and Cursor task configuration, requires a dependency chain or
code path as evidence for every finding, and routes the explanation step to
the `how` skill. Licensed under the MIT terms in `LICENSE.upstream`.
